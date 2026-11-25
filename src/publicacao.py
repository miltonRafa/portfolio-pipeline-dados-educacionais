"""Estado operacional e publicação de um conjunto Gold integralmente validado."""
import csv
import hashlib
import json
import os
import shutil
import sys
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def inventory(directory, exclude_download=False):
    return {p.relative_to(directory).as_posix(): digest(p)
            for p in sorted(Path(directory).rglob("*"))
            if p.is_file() and not (exclude_download and ".download" in p.relative_to(directory).parts)}


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


@contextmanager
def execution_lock(root):
    """O bloqueio do SO é liberado inclusive quando o processo termina abruptamente."""
    directory = Path(root) / "data/execucoes"
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / "lock").open("a+b") as stream:
        stream.seek(0)
        if os.name == "nt":
            import msvcrt
            if os.fstat(stream.fileno()).st_size == 0:
                stream.write(b"0")
                stream.flush()
            stream.seek(0)
            try:
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise RuntimeError("Outra execução ou verificação está em andamento.") from exc
        else:
            import fcntl
            try:
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise RuntimeError("Outra execução ou verificação está em andamento.") from exc
        try:
            yield
        finally:
            if os.name == "nt":
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)


def recover(root):
    root = Path(root)
    scripts = str(Path(__file__).resolve().parents[1] / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    from atualizacao_raw import recover_interrupted_update

    recover_interrupted_update(root)
    latest = root / "data/execucoes/ultima.json"
    if not latest.exists():
        return
    state = read_json(latest)
    if state["estado"] != "em_andamento":
        return
    run = root / "data/execucoes" / state["id"]
    gold = root / "data/gold"
    backup = run / "gold_anterior"
    # O diário é gravado antes da primeira renomeação.
    if state.get("publicando"):
        if backup.exists():
            if gold.exists():
                os.replace(gold, run / "gold_interrompida")
            os.replace(backup, gold)
        elif not state["tinha_gold"] and gold.exists():
            os.replace(gold, run / "gold_interrompida")
    state.update(estado="malsucedida", fim=now(), erro="Execução interrompida; recuperação concluída.")
    write_json(run / "estado.json", state)
    write_json(latest, state)


def verify(root, required, allow_previous=False):
    root = Path(root)
    latest = read_json(root / "data/execucoes/ultima.json")
    manifest = read_json(root / "data/gold/publicacao.json")
    if manifest.get("estado") != "concluida" or set(manifest.get("controles", [])) != set(required):
        raise RuntimeError("Manifesto sem aprovação de todos os controles obrigatórios.")
    if not manifest.get("insumos") or not manifest.get("manifesto_raw") or not manifest.get("fim"):
        raise RuntimeError("Manifesto sem associação completa aos insumos.")
    identifier = manifest.get("id", "")
    if len(identifier) != 32 or any(c not in "0123456789abcdef" for c in identifier):
        raise RuntimeError("Identificador de publicacao invalido.")
    archived = read_json(root / "data/execucoes" / identifier / "publicacao.json")
    if manifest != archived:
        raise RuntimeError("Manifesto de publicacao diverge do registro da execucao.")
    archived_raw = root / "data/execucoes" / identifier / "fontes_dados.csv"
    if not archived_raw.is_file() or digest(archived_raw) != manifest["manifesto_raw"]:
        raise RuntimeError("Hash do manifesto Raw arquivado divergente.")
    actual = inventory(root / "data/gold")
    actual.pop("publicacao.json", None)
    if actual != manifest.get("arquivos"):
        raise RuntimeError("Inventário Gold divergente: arquivo ausente, adicional ou adulterado.")
    raw_manifest = root / "docs/fontes_dados.csv"
    fresh = (raw_manifest.is_file()
             and digest(raw_manifest) == manifest["manifesto_raw"]
             and inventory(root / "data/raw", exclude_download=True) == manifest["insumos"])
    latest_ok = (latest["estado"] == "concluida"
                 and (latest["id"] == manifest["id"] or latest.get("comando") in ("bronze", "silver")))
    status = (f"Publicação {manifest['id']} íntegra. "
              f"Atualidade em relação aos insumos: {'atual' if fresh else 'desatualizada'}. "
              f"Última tentativa {latest['id']}: {latest['estado']} "
              f"({latest.get('comando', 'comando desconhecido')}).")
    if not allow_previous and (not fresh or not latest_ok):
        raise RuntimeError(status + " Use --last-valid para verificar explicitamente a publicação anterior.")
    print(status)
    return manifest


def execute(root, command, steps, required, run_step):
    root = Path(root)
    with execution_lock(root):
        recover(root)
        source_root = root
        if command != "full":
            completed = []
            for path in (root / "data/execucoes").glob("*/estado.json"):
                record = read_json(path)
                if record.get("estado") == "concluida" and record.get("trabalho"):
                    completed.append(record)
            if completed:
                previous = max(completed, key=lambda record: record["fim"])
                source_root = Path(previous["trabalho"])
                if not source_root.is_dir():
                    raise RuntimeError("Intermediarios da ultima execucao concluida ausentes.")
        identifier = uuid.uuid4().hex
        run = root / "data/execucoes" / identifier
        work = run / "trabalho"
        work.mkdir(parents=True)
        latest = root / "data/execucoes/ultima.json"
        state = dict(id=identifier, comando=command, estado="em_andamento", inicio=now(), controles=[])
        def save():
            write_json(run / "estado.json", state)
            write_json(latest, state)
        save()
        try:
            run_step(None, root)
            # Cópias isolam os insumos efetivamente lidos de alterações externas posteriores.
            shutil.copytree(root / "data/raw", work / "data/raw",
                            ignore=shutil.ignore_patterns(".download"))
            raw = inventory(work / "data/raw")
            manifest_hash = digest(root / "docs/fontes_dados.csv")
            archived_raw = run / "fontes_dados.csv"
            shutil.copy2(root / "docs/fontes_dados.csv", archived_raw)
            if digest(archived_raw) != manifest_hash:
                raise RuntimeError("Cópia do manifesto Raw diverge do hash registrado.")
            with archived_raw.open(encoding="utf-8-sig", newline="") as stream:
                expected = {Path(row["caminho_local"]).relative_to("data/raw").as_posix(): row["sha256"]
                            for row in csv.DictReader(stream)}
            if raw != expected:
                raise RuntimeError("Snapshot Raw diverge do manifesto verificado.")
            if command != "full":
                for layer in ("bronze", "silver"):
                    source = source_root / "data" / layer
                    if not source.exists():
                        source = root / "data" / layer
                    if source.exists():
                        shutil.copytree(source, work / "data" / layer)
            for step in steps:
                run_step(step, work)
                if step.script in required:
                    state["controles"].append(step.script)
                save()
            if (inventory(work / "data/raw") != raw
                    or digest(root / "docs/fontes_dados.csv") != manifest_hash
                    or digest(archived_raw) != manifest_hash):
                raise RuntimeError("Insumos ou manifesto Raw alterados durante a execução.")
            if command in ("full", "gold"):
                if set(state["controles"]) != set(required):
                    raise RuntimeError("Controles obrigatórios incompletos.")
                gold = work / "data/gold"
                manifest = dict(id=identifier, estado="concluida", fim=now(),
                                manifesto_raw=manifest_hash, insumos=raw,
                                controles=state["controles"], arquivos=inventory(gold))
                write_json(run / "publicacao.json", manifest)
                write_json(gold / "publicacao.json", manifest)
                state.update(publicando=True, tinha_gold=(root / "data/gold").exists())
                save()
                if state["tinha_gold"]:
                    os.replace(root / "data/gold", run / "gold_anterior")
                os.replace(gold, root / "data/gold")
            state.update(estado="concluida", fim=now(), trabalho=str(work))
            print(f"Execucao {identifier}; resultados intermediarios em {work}")
            save()
        except BaseException as exc:
            # Usar a mesma recuperação para falhas normais e reinício após interrupção.
            recover(root)
            state = read_json(latest)
            state.update(erro=f"{type(exc).__name__}: {exc}")
            write_json(run / "estado.json", state)
            write_json(latest, state)
            raise
