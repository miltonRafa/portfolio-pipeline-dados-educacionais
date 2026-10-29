"""Obtém os insumos oficiais e valida hash ou equivalência do conteúdo usado.

Baixa e prepara data/raw, usando temporários dentro da própria Raw.
Hashes diferentes só são incorporados após comparação com referência validada.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import csv
from functools import lru_cache
import hashlib
from html.parser import HTMLParser
import io
import json
import locale
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
from urllib.parse import urljoin, urlparse
import zipfile

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from atualizacao_raw import ManifestUpdates
from compatibilidade_raw import Incompatible

ROOT = Path(__file__).resolve().parents[1]
MICRO_SAEB = "https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/saeb"


def session():
    client = requests.Session()
    client.mount("http://", HTTPAdapter(max_retries=Retry(total=3, backoff_factor=1)))
    client.mount("https://", HTTPAdapter(max_retries=Retry(total=3, backoff_factor=1)))
    return client


class Links(HTMLParser):
    def __init__(self, body):
        super().__init__()
        self.links = []
        self.tabs = []
        self.feed(body)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if attrs.get("data-url"):
            self.tabs.append(attrs["data-url"])


@lru_cache(maxsize=None)
def page(url):
    with session() as client:
        response = client.get(url, timeout=(20, 90))
        response.raise_for_status()
        response.encoding = "utf-8"
        return Links(response.text)


def downloads(url):
    return sorted(set(urljoin(url, link) for link in page(url).links
                      if urlparse(link).hostname == "download.inep.gov.br"
                      and re.search(r"\.(zip|rar|xlsx|xlsb|xls|csv)$", link, re.I)))


def unique(items, description):
    if len(items) != 1:
        raise ValueError(f"Seleção ambígua/ausente ({description}): {items}")
    return items[0]


def discover(row):
    """Segue abas reais; o IDEB pode receber nova edição física da série."""
    base, year = row["url_oficial"], row["ano"]
    indicator = row["indicador"]
    if indicator == "SAEB" and year != "2023":
        return unique([u for u in downloads(MICRO_SAEB) if year in u and "infantil" not in u], f"SAEB {year}"), MICRO_SAEB
    if indicator == "SAEB" and ("ESCOLA" in row["nome_local"] or "Dicionario" in row["nome_local"]):
        return unique([u for u in downloads(MICRO_SAEB) if "2023" in u and "infantil" not in u], "SAEB 2023"), MICRO_SAEB
    if indicator == "IDEB":
        tabs = [(max(map(int, re.findall(r"20\d{2}", u))), u) for u in page(base).tabs if re.findall(r"20\d{2}", u)]
        if not tabs:
            raise ValueError("Nenhuma aba anual encontrada na página oficial do IDEB")
        newest = max(year for year, _ in tabs)
        source = unique([u for year, u in tabs if year == newest], "IDEB edição física mais recente")
        return unique([u for u in downloads(source) if re.search(r"/divulgacao_regioes_ufs_ideb_\d{4}\.(zip|rar|xlsx)$", u, re.I)], "IDEB"), source
    if indicator == "PND":
        return unique([u for u in downloads(base) if "2025" in u and "pnd" in u], "PND 2025"), base
    source = unique([u for u in page(base).tabs if u.rstrip("/").endswith("/" + year)], f"aba {year}")
    links = downloads(source)
    if indicator == "SAEB":
        return unique([u for u in links if "planilha_de_resultados_2023" in u], "SAEB resultados 2023"), source
    return unique([u for u in links if "uf" in u.lower() and "brasil" in u.lower()], f"{indicator} {year}"), source


class RemoteZip(io.RawIOBase):
    """Arquivo seekable por HTTP Range: baixa só diretório e membros escolhidos."""
    def __init__(self, url):
        self.url = url
        self.client = session()
        self.position = 0
        self.start = 0
        self.buffer = b""
        with self.client.get(url, headers={"Range": "bytes=0-0", "Accept-Encoding": "identity"},
                             timeout=(20, 90), stream=True) as response:
            response.raise_for_status()
            if response.status_code != 206:
                raise ValueError("Servidor não oferece HTTP Range; use download integral")
            self.size = int(response.headers["Content-Range"].split("/")[-1])

    def seekable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=0):
        self.position = offset + (self.position if whence == 1 else self.size if whence == 2 else 0)
        if self.position < 0:
            raise ValueError("Offset negativo")
        return self.position

    def read(self, size=-1):
        if size < 0:
            size = self.size - self.position
        size = min(size, self.size - self.position)
        if size <= 0:
            return b""
        end = self.position + size
        if not (self.start <= self.position and end <= self.start + len(self.buffer)):
            last = min(self.size, self.position + max(size, 128 * 1024)) - 1
            with self.client.get(self.url, headers={"Range": f"bytes={self.position}-{last}",
                                                  "Accept-Encoding": "identity"}, timeout=(20, 180)) as response:
                response.raise_for_status()
                expected = f"bytes {self.position}-{last}/{self.size}"
                if response.status_code != 206 or response.headers.get("Content-Range") != expected:
                    raise ValueError("Resposta Range inválida")
                self.start, self.buffer = self.position, response.content
                if len(self.buffer) != last - self.start + 1:
                    raise ValueError("Resposta Range truncada")
        result = self.buffer[self.position - self.start:end - self.start]
        self.position = end
        return result

    def close(self):
        self.client.close()
        super().close()


def digest(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def normalize(name):
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", re.sub(r"20\d{2}", "", name))


def candidates(names, row):
    target = row["nome_local"]
    ext = Path(target).suffix.lower()
    names = [n for n in names if not n.endswith("/") and Path(n).suffix.lower() == ext]
    exact = [n for n in names if normalize(n.replace("\\", "/").split("/")[-1]) == normalize(target)]
    if exact:
        return exact
    if "dicion" in normalize(target):
        return [n for n in names if "dicion" in normalize(n)]
    if row["indicador"] in ("TDI", "Rendimento Escolar", "IDEB"):
        return names
    return [n for n in names if any(s in normalize(n.replace("\\", "/").split("/")[-1])
                                   for s in ("uf", "estado"))]


def download(url, destination):
    partial = destination.with_suffix(destination.suffix + ".part")
    try:
        with session() as client, client.get(url, stream=True, timeout=(20, 180)) as response:
            response.raise_for_status()
            with partial.open("wb") as output:
                for chunk in response.iter_content(1024 * 1024):
                    output.write(chunk)
        partial.replace(destination)
    finally:
        partial.unlink(missing_ok=True)


def accept(source, row, destination):
    source_hash = digest(source)
    if source_hash != row["sha256"]:
        try:
            if row.get("_estrito"):
                raise Incompatible("hash_diferente_modo_estrito", "SHA-256 diferente; comparação de conteúdo desativada por --estrito.")
            return ManifestUpdates().accept_changed(source, row, destination)
        except Incompatible as exc:
            row["_rejeicao"] = {**exc.details, "sha256_esperado": row["sha256"], "sha256_recebido": source_hash,
                                "fallback": "Arquivo atual e manifesto preservados; nenhuma atualização deste candidato foi aceita."}
            return False
    target = destination / Path(row["caminho_local"]).relative_to("data/raw")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if digest(target) != source_hash:
            raise FileExistsError(f"Destino divergente preservado: {target}")
    else:
        staging = target.with_suffix(target.suffix + ".part")
        try:
            shutil.copyfile(source, staging)
            staging.replace(target)
        finally:
            staging.unlink(missing_ok=True)
    return True


@contextmanager
def package_directory(scratch):
    """Limpa o diretório exclusivo; tolera bloqueios breves de arquivos no Windows."""
    parent = scratch.resolve()
    directory = Path(tempfile.mkdtemp(prefix="pacote-", dir=parent)).resolve()
    if directory.parent != parent:
        raise ValueError("Diretório temporário fora da Raw de trabalho")
    try:
        yield directory
    finally:
        for attempt in range(5):
            try:
                shutil.rmtree(directory)
                break
            except PermissionError:
                if attempt == 4:
                    raise
                time.sleep(0.2 * (attempt + 1))


def process_group(item, destination, scratch, http):
    official_url, rows = item
    url = official_url.replace("https://", "http://", 1) if http else official_url
    results = []
    for row in rows:
        row["_url_download"] = official_url
    with package_directory(scratch) as temp:
        if url.lower().endswith(".zip"):
            try:
                remote = RemoteZip(url)
            except ValueError as exc:
                print(f"Fallback ZIP integral: {official_url}: {exc}", flush=True)
                local = temp / "fonte.zip"
                download(url, local)
                remote = local.open("rb")
            with remote, zipfile.ZipFile(remote) as archive:
                for row in rows:
                    attempts = []
                    for member in candidates(archive.namelist(), row):
                        row["_membro"] = member
                        candidate = temp / ("candidato" + Path(row["nome_local"]).suffix)
                        with archive.open(member) as src, candidate.open("wb") as dst:
                            shutil.copyfileobj(src, dst)
                        if accept(candidate, row, destination):
                            break
                        attempts.append({"membro": member, "sha256": digest(candidate), "erro": row.get("_rejeicao")})
                    else:
                        results.append({"caminho": row["caminho_local"], "status": "nao_reproduzido", "candidatos": attempts,
                                        "motivo": "Nenhum membro compatível foi encontrado; consulte os candidatos e seus motivos de rejeição.",
                                        "fallback": "Raw e manifesto preservados para este arquivo."})
                        continue
                    results.append({"caminho": row["caminho_local"], "status": "identico", "membro": member,
                                    **row.get("_resultado", {}),
                                    "sha256": digest(candidate), "sha256_manifesto": row["sha256"]})
        elif url.lower().endswith(".rar"):
            local = temp / "fonte.rar"
            download(url, local)
            tar = shutil.which("tar")
            if not tar:
                raise RuntimeError("RAR exige tar com suporte libarchive (disponível no Windows) no PATH")
            listing_bytes = subprocess.run([tar, "-tf", str(local)], capture_output=True, check=True).stdout
            try:
                listing = listing_bytes.decode("utf-8").splitlines()
            except UnicodeDecodeError:
                listing = listing_bytes.decode(locale.getpreferredencoding(False)).splitlines()
            for row in rows:
                attempts = []
                for member in candidates(listing, row):
                    row["_membro"] = member
                    candidate = temp / ("candidato" + Path(row["nome_local"]).suffix)
                    with candidate.open("wb") as dst:
                        subprocess.run([tar, "-xOf", str(local), "--", member], stdout=dst, stderr=subprocess.PIPE, check=True)
                    if accept(candidate, row, destination):
                        break
                    attempts.append({"membro": member, "sha256": digest(candidate), "erro": row.get("_rejeicao")})
                else:
                    results.append({"caminho": row["caminho_local"], "status": "nao_reproduzido", "candidatos": attempts,
                                    "motivo": "Nenhum membro compatível foi encontrado; consulte os candidatos e seus motivos de rejeição.",
                                    "fallback": "Raw e manifesto preservados para este arquivo."})
                    continue
                results.append({"caminho": row["caminho_local"], "status": "identico", "membro": member,
                                **row.get("_resultado", {}),
                                "sha256": digest(candidate), "sha256_manifesto": row["sha256"]})
        else:
            local = temp / "fonte"
            download(url, local)
            for row in rows:
                ok = accept(local, row, destination)
                results.append({"caminho": row["caminho_local"], "status": "identico" if ok else "nao_reproduzido",
                                **row.get("_resultado", {}), "erro": row.get("_rejeicao"), "sha256": digest(local)})
    for result in results:
        result.update(url_oficial=official_url, url_transferencia=url)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destino", type=Path, default=ROOT / "data/raw", help="Raw de destino (padrão: data/raw no projeto)")
    parser.add_argument("--indicador", choices=["tdi", "rendimento", "saeb", "ideb", "pnd"], action="append")
    parser.add_argument("--ano", action="append")
    parser.add_argument("--http", action="store_true", help="Usa HTTP no servidor download.inep.gov.br; SHA-256 continua obrigatório")
    parser.add_argument("--planejar", action="store_true", help="Descobre links sem baixar pacotes")
    parser.add_argument("--rebaixar", action="store_true", help="Consulta e transfere novamente arquivos já validados no destino")
    parser.add_argument("--estrito", action="store_true", help="Exige identidade binária; desativa atualização automática por conteúdo equivalente")
    args = parser.parse_args()
    destination = args.destino.resolve()
    scratch = destination / ".download"
    scratch.mkdir(parents=True, exist_ok=True)
    with (ROOT / "docs/fontes_dados.csv").open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    rows = [r for r in rows if (not args.indicador or Path(r["caminho_local"]).parts[2] in args.indicador)
            and (not args.ano or r["ano"] in args.ano)]
    if not rows:
        parser.error("Nenhum arquivo selecionado")
    for row in rows:
        row["_estrito"] = args.estrito
    report, groups, plan = [], {}, []
    # A descoberta é independente para cada arquivo; baixar agrupa por pacote.
    def resolve(row):
        try:
            target = destination / Path(row["caminho_local"]).relative_to("data/raw")
            if target.exists() and not args.rebaixar and not args.planejar:
                if digest(target) != row["sha256"]:
                    raise FileExistsError(f"Destino divergente preservado: {target}")
                return row, None, None, None
            url, source = discover(row)
            return row, url, source, None
        except Exception as exc:
            return row, None, None, str(exc)
    with ThreadPoolExecutor(max_workers=4) as executor:
        for row, url, source, error in executor.map(resolve, rows):
            if error:
                report.append({"caminho": row["caminho_local"], "status": "erro", "erro": error,
                               "fallback": "Arquivo local preservado. Confira URL, edição, conexão e integridade da Raw; tente --http em caso de falha HTTPS no servidor de downloads."})
                continue
            if url is None:
                target_hash = digest(destination / Path(row["caminho_local"]).relative_to("data/raw"))
                report.append({"caminho": row["caminho_local"], "status": "identico", "origem": "destino_validado",
                               "sha256": target_hash, "sha256_manifesto": row["sha256"]})
                continue
            plan.append({"caminho": row["caminho_local"], "pagina": source, "url": url, "sha256": row["sha256"]})
            groups.setdefault(url, []).append(row)
    plan_path = scratch / "plano_download.json"
    previous = json.loads(plan_path.read_text(encoding="utf-8")) if plan_path.exists() else []
    combined = {r["caminho"]: r for r in previous}
    combined.update({r["caminho"]: r for r in plan})
    plan_path.write_text(json.dumps(list(combined.values()), ensure_ascii=False, indent=2), encoding="utf-8")
    if not args.planejar:
        def run(item):
            print(f"Obtendo {item[0]}", flush=True)
            try:
                return process_group(item, destination, scratch, args.http)
            except Exception as exc:
                detail = f"{type(exc).__name__}: {exc}"
                if isinstance(exc, subprocess.CalledProcessError) and exc.stderr:
                    stderr = exc.stderr.decode(locale.getpreferredencoding(False), errors="replace") if isinstance(exc.stderr, bytes) else exc.stderr
                    detail += f"; stderr: {stderr[:2000]}"
                return [{"caminho": r["caminho_local"], "status": "erro", "url_oficial": item[0],
                         "erro": detail,
                         "fallback": "Transferência/extração não concluída. Arquivos já aceitos permanecem válidos. Confira conexão, formato do pacote, tar/libarchive e permissões; para falha HTTPS use --http."} for r in item[1]]
        with ThreadPoolExecutor(max_workers=3) as executor:
            for result in executor.map(run, groups.items()):
                report.extend(result)
    output = {"destino": str(destination), "selecionados": len(rows), "planejamento": args.planejar,
              "links_resolvidos": len(plan), "resumo": dict(Counter(r["status"] for r in report)), "arquivos": report}
    report_name = "relatorio_planejamento.json" if args.planejar else "relatorio_download.json"
    (scratch / report_name).write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(output["resumo"], ensure_ascii=False))
    for result in report:
        if result["status"] != "identico":
            print(json.dumps(result, ensure_ascii=False), flush=True)
    return int(any(r["status"] not in ("identico", "historico_igual_hash_atualizado") for r in report))


if __name__ == "__main__":
    # Alguns nomes originais dos ZIPs contêm caracteres fora da página de
    # códigos do terminal Windows; o relatório JSON em UTF-8 permanece íntegro.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")
    try:
        sys.exit(main())
    except Exception as exc:
        print(json.dumps({"status": "erro", "erro": f"{type(exc).__name__}: {exc}",
                          "fallback": "Execução interrompida. Confira o manifesto, os relatórios em data/raw/.download e as permissões. Não regenere hashes para ocultar uma falha de comparação."}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
