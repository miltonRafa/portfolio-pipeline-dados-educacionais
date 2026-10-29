"""Instala atualizações equivalentes e mantém os manifestos sincronizados."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from threading import RLock
from urllib.parse import unquote, urlparse

from compatibilidade_raw import compare_content, Incompatible
import gerar_manifesto_raw as manifesto

ROOT = Path(__file__).resolve().parents[1]
LOCK = RLock()


def digest(path):
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def atomic_bytes(path, data):
    partial = path.with_name(path.name + ".part")
    try:
        partial.write_bytes(data)
        partial.replace(path)
    finally:
        partial.unlink(missing_ok=True)


class ManifestUpdates:
    def __init__(self, root=ROOT):
        self.root = root.resolve()

    def accept_changed(self, candidate, row, destination):
        with LOCK:
            return self._accept(candidate, row, destination)

    def _accept(self, candidate, row, destination):
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
        # Uma atualização equivale ao conteúdo protegido, não a uma nova edição analítica.
        paths = [docs / n for n in ("fontes_dados.csv", "fontes_dados.md", "raw_checksums_sha256.txt")]
        previous = {p: p.read_bytes() for p in paths}
        scratch = destination / ".download"
        backup = scratch / "historico" / Path(row["caminho_local"]).relative_to("data/raw") / row["sha256"]
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists():
            shutil.copyfile(baseline, backup)
        if digest(backup) != row["sha256"]:
            raise Incompatible("backup_invalido", "O backup da referência não passou na verificação SHA-256.")
        history_path = scratch / "historico_atualizacoes.json"
        history_before = history_path.read_bytes() if history_path.exists() else None
        history = json.loads(history_before) if history_before else []
        event = {"instante_utc": datetime.now(timezone.utc).isoformat(), "caminho": row["caminho_local"],
                 "sha256_anterior": row["sha256"], "sha256_novo": new_hash,
                 "backup": str(backup), "url": url, "membro": member, "comparacao": evidence}
        history.append(event)
        # Preparação completa antes de trocar o arquivo canônico ou a documentação.
        with tempfile.TemporaryDirectory(prefix="manifesto-", dir=scratch) as directory:
            stage = Path(directory)
            old_docs = manifesto.DOCS_DIR
            try:
                manifesto.DOCS_DIR = stage
                manifesto.write_csv(rows)
                manifesto.write_checksums(rows)
                manifesto.write_markdown(rows)
            finally:
                manifesto.DOCS_DIR = old_docs
            staged_raw = target.with_name(target.name + ".part")
            try:
                shutil.copyfile(candidate, staged_raw)
                if digest(staged_raw) != new_hash:
                    raise OSError("Arquivo de instalação não corresponde ao candidato comparado")
                staged_raw.replace(target)
                for path in paths:
                    atomic_bytes(path, (stage / path.name).read_bytes())
                atomic_bytes(history_path, json.dumps(history, ensure_ascii=False, indent=2).encode("utf-8"))
            except Exception as exc:
                shutil.copyfile(backup, target)
                for path, data in previous.items():
                    atomic_bytes(path, data)
                if history_before is None:
                    history_path.unlink(missing_ok=True)
                else:
                    atomic_bytes(history_path, history_before)
                raise Incompatible("instalacao_falhou", "Falha ao instalar a atualização; arquivo anterior e documentos restaurados.",
                                   erro_original=f"{type(exc).__name__}: {exc}") from exc
            finally:
                staged_raw.unlink(missing_ok=True)
        row["_resultado"] = {"status": "historico_igual_hash_atualizado", "comparacao": evidence,
                             "sha256_anterior": row["sha256"], "sha256_novo": new_hash}
        return True
