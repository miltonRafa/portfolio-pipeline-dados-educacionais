"""Instala atualizações equivalentes e mantém os manifestos sincronizados."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import uuid
from threading import RLock
from urllib.parse import unquote, urlparse

from compatibilidade_raw import compare_content, Incompatible
import gerar_manifesto_raw as manifesto

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
LOCK = RLock()
JOURNAL_NAME = "atualizacao_pendente.json"
TRANSACTIONS_NAME = "transacoes"


def digest(path):
    with Path(path).open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def _fsync_directory(path):
    if os.name != "nt":
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


def atomic_bytes(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".part")
    try:
        with partial.open("wb") as file:
            file.write(data)
            file.flush()
            os.fsync(file.fileno())
        os.replace(partial, path)
        _fsync_directory(path.parent)
    finally:
        partial.unlink(missing_ok=True)


def promote_file(source, destination):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    os.replace(source, destination)
    _fsync_directory(destination.parent)


def _write_json_atomic(path, value):
    data = json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8")
    atomic_bytes(path, data)


def _sync_file(path):
    with Path(path).open("rb+") as file:
        os.fsync(file.fileno())


def _copy_durable(source, destination):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    _sync_file(destination)
    _fsync_directory(destination.parent)


def _safe_child(base, relative):
    relative = Path(relative)
    if relative.is_absolute() or ".." in relative.parts:
        raise RuntimeError(f"Caminho inválido no diário de atualização: {relative}")
    base = Path(base).resolve()
    result = (base / relative).resolve()
    try:
        result.relative_to(base)
    except ValueError as exc:
        raise RuntimeError(f"Caminho fora do diretório autorizado: {relative}") from exc
    return result


def _remove_orphan_transactions(scratch):
    journal_partial = scratch / f"{JOURNAL_NAME}.part"
    journal_partial.unlink(missing_ok=True)
    transactions = scratch / TRANSACTIONS_NAME
    if not transactions.exists():
        return
    for path in transactions.iterdir():
        if path.is_dir() and re.fullmatch(r"[0-9a-f]{32}", path.name):
            shutil.rmtree(path)


def _atomic_restore(source, destination, expected_hash, transaction_id):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_name(
        f"{destination.name}.restore-{transaction_id}.part"
    )
    try:
        shutil.copyfile(source, partial)
        with partial.open("rb+") as file:
            os.fsync(file.fileno())
        if digest(partial) != expected_hash:
            raise RuntimeError(f"Backup de recuperação inválido: {source}")
        os.replace(partial, destination)
        _fsync_directory(destination.parent)
    finally:
        partial.unlink(missing_ok=True)


def recover_interrupted_update(root=ROOT):
    """Reverte uma instalação interrompida usando o diário e backups verificados."""
    root = Path(root).resolve()
    scratch = root / "data/raw/.download"
    journal_path = scratch / JOURNAL_NAME
    if not journal_path.is_file():
        _remove_orphan_transactions(scratch)
        return False

    try:
        journal = json.loads(journal_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Diário de atualização Raw ilegível: {journal_path}") from exc
    transaction_id = journal.get("id")
    if (journal.get("version") != 1
            or not isinstance(transaction_id, str)
            or not re.fullmatch(r"[0-9a-f]{32}", transaction_id)
            or not isinstance(journal.get("entries"), list)
            or not journal["entries"]):
        raise RuntimeError(f"Diário de atualização Raw inválido: {journal_path}")

    transaction = scratch / TRANSACTIONS_NAME / transaction_id
    restore = []
    seen = set()
    for entry in journal["entries"]:
        relative = entry.get("path")
        if not isinstance(relative, str) or relative in seen:
            raise RuntimeError("Diário de atualização Raw contém destinos inválidos ou duplicados.")
        seen.add(relative)
        destination = _safe_child(root, relative)
        old_exists = entry.get("old_exists")
        if not isinstance(old_exists, bool):
            raise RuntimeError(f"Estado anterior inválido no diário: {relative}")
        if old_exists:
            old_hash = entry.get("old_sha256")
            backup = entry.get("old_backup")
            if (not isinstance(old_hash, str)
                    or not re.fullmatch(r"[0-9a-f]{64}", old_hash)
                    or not isinstance(backup, dict)):
                raise RuntimeError(f"Backup anterior inválido no diário: {relative}")
            scope = backup.get("scope")
            base = root if scope == "root" else transaction if scope == "transaction" else None
            if base is None or not isinstance(backup.get("path"), str):
                raise RuntimeError(f"Origem do backup inválida no diário: {relative}")
            backup_path = _safe_child(base, backup["path"])
            if not backup_path.is_file() or digest(backup_path) != old_hash:
                raise RuntimeError(f"Backup anterior ausente ou divergente: {backup_path}")
        else:
            old_hash = None
            backup_path = None
        new_hash = entry.get("new_sha256")
        if not isinstance(new_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", new_hash):
            raise RuntimeError(f"Hash novo inválido no diário: {relative}")
        restore.append((destination, old_exists, backup_path, old_hash))

    for destination, old_exists, backup_path, old_hash in restore:
        if old_exists:
            _atomic_restore(backup_path, destination, old_hash, transaction_id)
        else:
            destination.unlink(missing_ok=True)
            _fsync_directory(destination.parent)

    for destination, old_exists, _, old_hash in restore:
        if old_exists and (not destination.is_file() or digest(destination) != old_hash):
            raise RuntimeError(f"Recuperação não restaurou o arquivo anterior: {destination}")
        if not old_exists and destination.exists():
            raise RuntimeError(f"Recuperação não removeu o arquivo novo: {destination}")
        destination.with_name(destination.name + ".part").unlink(missing_ok=True)

    journal_path.unlink()
    _fsync_directory(scratch)
    if transaction.exists():
        shutil.rmtree(transaction)
    _remove_orphan_transactions(scratch)
    return True


class ManifestUpdates:
    def __init__(self, root=ROOT):
        self.root = Path(root).resolve()

    def accept_changed(self, candidate, row, destination):
        with LOCK:
            from src.publicacao import execution_lock

            with execution_lock(self.root):
                recover_interrupted_update(self.root)
                return self._accept(candidate, row, destination)

    def _accept(self, candidate, row, destination):
        candidate = Path(candidate)
        destination = Path(destination)
        target = destination / Path(row["caminho_local"]).relative_to("data/raw")
        canonical = self.root / row["caminho_local"]
        baseline = target if target.is_file() and digest(target) == row["sha256"] else canonical
        if not baseline.is_file() or digest(baseline) != row["sha256"]:
            raise Incompatible("referencia_indisponivel", "Hash diferente e cópia anterior validada indisponível. Não é possível provar equivalência.",
                               esperado=row["sha256"], recebido=digest(candidate), acao="Restaure a versão identificada pelo manifesto e execute novamente.")
        if destination.resolve() != (self.root / "data/raw").resolve():
            raise Incompatible("destino_alternativo", "A atualização automática do manifesto exige a Raw canônica do projeto.",
                               acao="Execute com o destino padrão data/raw; outros destinos permitem reprodução exata.")
        if target.exists() and digest(target) != row["sha256"]:
            raise Incompatible("raw_local_divergente", "A cópia local não corresponde ao manifesto e foi preservada.")
        try:
            evidence = compare_content(baseline, candidate, row)
        except Incompatible:
            raise
        except Exception as exc:
            raise Incompatible("comparacao_falhou", "Não foi possível ler ou comparar integralmente o conteúdo.",
                               erro_original=f"{type(exc).__name__}: {exc}",
                               acao="Confira formato, abas, codificação e dependências; a Raw e o manifesto foram preservados.") from exc
        new_hash = digest(candidate)
        if digest(baseline) != row["sha256"]:
            raise Incompatible("referencia_alterada", "A referência mudou durante a comparação; nenhuma instalação foi feita.")
        docs = self.root / "docs"
        with (docs / "fontes_dados.csv").open(encoding="utf-8-sig", newline="") as file:
            rows = list(csv.DictReader(file))
        record = next(r for r in rows if r["caminho_local"] == row["caminho_local"])
        if record["sha256"] != row["sha256"]:
            raise Incompatible("manifesto_alterado", "O manifesto mudou durante a operação. Execute novamente.")
        record["sha256"] = new_hash
        if evidence.get("anos_observados_nova_fonte"):
            years = evidence["anos_observados_nova_fonte"]
            record["anos_disponiveis"] = ", ".join(map(str, years))
            record["edicao_fonte"] = f"arquivo fisico contem edicoes ate {max(years)}; recorte analitico preservado em 2007-2023"
        url = row.get("_url_download")
        if url:
            record["url_historica_download"] = url
            if url.lower().endswith((".zip", ".rar")):
                record["pacote_oficial_atual"] = unquote(Path(urlparse(url).path).name)
        member = row.get("_membro")
        if member:
            record["arquivo_pacote_atual"] = member.replace("\\", "/").split("/")[-1]
            record["nome_original"] = record["arquivo_pacote_atual"]

        paths = [docs / name for name in (
            "fontes_dados.csv", "fontes_dados.md", "raw_checksums_sha256.txt"
        )]
        scratch = destination / ".download"
        backup = scratch / "historico" / Path(row["caminho_local"]).relative_to("data/raw") / row["sha256"]
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists():
            _atomic_restore(baseline, backup, row["sha256"], uuid.uuid4().hex)
        if digest(backup) != row["sha256"]:
            raise Incompatible("backup_invalido", "O backup da referência não passou na verificação SHA-256.")
        history_path = scratch / "historico_atualizacoes.json"
        history_before = history_path.read_bytes() if history_path.exists() else None
        history = json.loads(history_before) if history_before else []
        event = {"instante_utc": datetime.now(timezone.utc).isoformat(), "caminho": row["caminho_local"],
                 "sha256_anterior": row["sha256"], "sha256_novo": new_hash,
                 "backup": str(backup), "url": url, "membro": member, "comparacao": evidence}
        history.append(event)

        transaction_id = uuid.uuid4().hex
        transaction = scratch / TRANSACTIONS_NAME / transaction_id
        new_dir = transaction / "new"
        old_dir = transaction / "old"
        journal_path = scratch / JOURNAL_NAME
        old_docs_dir = manifesto.DOCS_DIR
        committed = False
        try:
            new_dir.mkdir(parents=True)
            old_dir.mkdir()
            manifesto.DOCS_DIR = new_dir
            manifesto.write_csv(rows)
            manifesto.write_checksums(rows)
            manifesto.write_markdown(rows)
            for path in new_dir.iterdir():
                if path.is_file():
                    _sync_file(path)
            _fsync_directory(new_dir)
            manifesto.DOCS_DIR = old_docs_dir

            staged_raw = new_dir / "raw"
            _copy_durable(candidate, staged_raw)
            if digest(staged_raw) != new_hash:
                raise OSError("Arquivo preparado não corresponde ao candidato comparado")

            staged_history = new_dir / "historico_atualizacoes.json"
            atomic_bytes(
                staged_history,
                json.dumps(history, ensure_ascii=False, indent=2).encode("utf-8"),
            )
            outputs = [(target, staged_raw, "raw", backup)]
            outputs.extend(
                (path, new_dir / path.name, "manifest", None)
                for path in paths
            )
            outputs.append((history_path, staged_history, "history", None))

            entries = []
            for index, (path, staged, _, raw_backup) in enumerate(outputs):
                old_exists = path.is_file()
                old_hash = digest(path) if old_exists else None
                if raw_backup is not None:
                    old_backup = {"scope": "root", "path": raw_backup.resolve().relative_to(self.root).as_posix()}
                elif old_exists:
                    backup_path = old_dir / str(index)
                    _copy_durable(path, backup_path)
                    if digest(backup_path) != old_hash:
                        raise OSError(f"Backup temporário divergente: {path}")
                    old_backup = {"scope": "transaction", "path": backup_path.relative_to(transaction).as_posix()}
                else:
                    old_backup = None
                entries.append({
                    "path": path.resolve().relative_to(self.root).as_posix(),
                    "old_exists": old_exists,
                    "old_sha256": old_hash,
                    "old_backup": old_backup,
                    "new_sha256": digest(staged),
                })

            _write_json_atomic(journal_path, {
                "version": 1,
                "id": transaction_id,
                "entries": entries,
            })

            for (path, staged, kind, _), entry in zip(outputs, entries):
                if kind == "raw":
                    promote_file(staged, path)
                else:
                    atomic_bytes(path, staged.read_bytes())
                if digest(path) != entry["new_sha256"]:
                    raise OSError(f"Arquivo promovido diverge do conteúdo preparado: {path}")

            journal_path.unlink()
            committed = True
            _fsync_directory(scratch)
        except Exception as exc:
            if committed:
                raise Incompatible(
                    "atualizacao_confirmada_limpeza_pendente",
                    "Raw e manifestos foram promovidos e verificados, mas a confirmação/limpeza do diário falhou.",
                    erro_original=f"{type(exc).__name__}: {exc}",
                ) from exc
            if journal_path.exists():
                try:
                    recover_interrupted_update(self.root)
                except Exception as recovery_error:
                    raise Incompatible(
                        "recuperacao_falhou",
                        "A instalação falhou e a recuperação automática também falhou; o diário e os backups foram preservados.",
                        erro_instalacao=f"{type(exc).__name__}: {exc}",
                        erro_recuperacao=f"{type(recovery_error).__name__}: {recovery_error}",
                    ) from recovery_error
            raise Incompatible(
                "instalacao_falhou",
                "Falha ao instalar a atualização; os arquivos anteriores foram restaurados ou não chegaram a ser substituídos.",
                erro_original=f"{type(exc).__name__}: {exc}",
            ) from exc
        finally:
            manifesto.DOCS_DIR = old_docs_dir
            if not journal_path.exists() and not committed and transaction.exists():
                shutil.rmtree(transaction)

        try:
            shutil.rmtree(transaction)
        except OSError as exc:
            raise Incompatible(
                "temporarios_nao_removidos",
                "A atualização está consistente, mas os backups temporários não foram removidos.",
                diretorio=str(transaction),
                erro_original=f"{type(exc).__name__}: {exc}",
            ) from exc

        row["_resultado"] = {"status": "historico_igual_hash_atualizado", "comparacao": evidence,
                             "sha256_anterior": row["sha256"], "sha256_novo": new_hash}
        return True
