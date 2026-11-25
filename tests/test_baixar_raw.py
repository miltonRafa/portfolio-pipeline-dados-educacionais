from __future__ import annotations

import hashlib
import importlib.util
import csv
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import tempfile
import sys
import threading
import time
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import atualizacao_raw as updates
import gerar_manifesto_raw as manifest
spec = importlib.util.spec_from_file_location("baixar_raw", ROOT / "scripts/baixar_raw.py")
raw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(raw)


class DownloadTest(unittest.TestCase):
    def test_downloader_threads_serialize_identical_and_equivalent_installs(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            docs = root / "docs"
            docs.mkdir()
            destination = root / "data/raw"
            (destination / ".download").mkdir(parents=True)

            old_file = destination / "pnd/alterado.txt"
            old_file.parent.mkdir()
            old_file.write_bytes(b"ano;valor\r\n2025;10\r\n")
            equivalent = root / "equivalente.txt"
            equivalent.write_bytes(b"ano;valor\n2025;10\n")

            def row_for(name, content_hash):
                row = {field: "" for field in manifest.FIELDS}
                row.update(
                    indicador="PND",
                    ano="2025",
                    nome_local=name,
                    caminho_local=f"data/raw/pnd/{name}",
                    sha256=content_hash,
                )
                return row

            changed_row = row_for(old_file.name, raw.digest(old_file))
            same_sources = []
            rows = [changed_row]
            for index in range(2):
                source = root / f"identico-{index}.txt"
                source.write_bytes(f"conteudo-{index}\n".encode("utf-8"))
                same_row = row_for(source.name, raw.digest(source))
                same_sources.append((source, same_row))
                rows.append(same_row)

            with (docs / "fontes_dados.csv").open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=manifest.FIELDS)
                writer.writeheader()
                writer.writerows(rows)
            (docs / "fontes_dados.md").write_text("anterior", encoding="utf-8")
            (docs / "raw_checksums_sha256.txt").write_text("anterior", encoding="utf-8")

            update_started = threading.Event()
            release_update = threading.Event()

            def slow_manifest(rows_to_write):
                update_started.set()
                if not release_update.wait(5):
                    raise TimeoutError("A atualização equivalente não foi liberada.")
                (manifest.DOCS_DIR / "fontes_dados.md").write_text("atualizado", encoding="utf-8")

            def call_accept(source, row):
                try:
                    return raw.accept(source, row, destination)
                except Exception as exc:
                    return exc

            with patch.object(raw, "ROOT", root), \
                    patch.object(raw, "ManifestUpdates", side_effect=lambda: updates.ManifestUpdates(root)), \
                    patch.object(manifest, "write_markdown", side_effect=slow_manifest):
                with ThreadPoolExecutor(max_workers=3) as executor:
                    changed = executor.submit(call_accept, equivalent, changed_row)
                    self.assertTrue(update_started.wait(5), "A atualização equivalente não iniciou.")
                    identical = [
                        executor.submit(call_accept, source, row)
                        for source, row in same_sources
                    ]
                    time.sleep(0.1)
                    release_update.set()
                    results = [changed.result(timeout=10)]
                    results.extend(future.result(timeout=10) for future in identical)

            self.assertEqual(results, [True, True, True])
            self.assertEqual(raw.digest(old_file), raw.digest(equivalent))
            for source, row in same_sources:
                target = destination / Path(row["caminho_local"]).relative_to("data/raw")
                self.assertEqual(raw.digest(target), raw.digest(source))

    def _rar_case(self, temp, content=b"dados oficiais"):
        temp = Path(temp)
        scratch = temp / ".download"
        scratch.mkdir()
        destination = temp / "raw"
        row = {"nome_local": "dados.csv", "indicador": "TDI",
               "caminho_local": "data/raw/tdi/dados.csv",
               "sha256": hashlib.sha256(content).hexdigest()}
        return scratch, destination, row

    def test_extracts_only_expected_content_and_uses_manifest_path(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            archive = temp / "origem.zip"
            content = b"dados oficiais"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("../../TS_UF.xlsx", content)
                z.writestr("alunos.csv", b"nao utilizado")
            row = {"nome_local": "TS_UF_2019.xlsx", "indicador": "SAEB",
                   "caminho_local": "data/raw/saeb/TS_UF_2019.xlsx",
                   "sha256": hashlib.sha256(content).hexdigest()}
            destination = temp / "raw"
            with patch.object(raw, "RemoteZip", side_effect=lambda _: archive.open("rb")):
                result = raw.process_group(("https://download.inep.gov.br/fonte.zip", [row]), destination, temp, False)
            self.assertEqual(result[0]["status"], "identico")
            self.assertEqual([p.relative_to(destination).as_posix() for p in destination.rglob("*") if p.is_file()],
                             ["saeb/TS_UF_2019.xlsx"])
            self.assertEqual(list(temp.glob("pacote-*")), [])

    def test_rejects_changed_content_and_preserves_existing_raw(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            source = temp / "fonte"
            source.write_bytes(b"novo")
            row = {"caminho_local": "data/raw/pnd/fonte.txt", "sha256": hashlib.sha256(b"antigo").hexdigest()}
            self.assertFalse(raw.accept(source, row, temp / "raw"))
            self.assertFalse((temp / "raw").exists())
            row["sha256"] = raw.digest(source)
            target = temp / "raw/pnd/fonte.txt"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"preservar")
            with self.assertRaises(FileExistsError):
                raw.accept(source, row, temp / "raw")
            self.assertEqual(target.read_bytes(), b"preservar")

    def test_ambiguous_discovery_fails(self):
        with self.assertRaises(ValueError):
            raw.unique(["a", "b"], "arquivo")

    def test_cleanup_retries_transient_windows_lock(self):
        with tempfile.TemporaryDirectory() as parent:
            original_rmtree = raw.shutil.rmtree
            attempts = []

            def remove(path):
                attempts.append(path)
                if len(attempts) == 1:
                    raise PermissionError("Arquivo temporariamente em uso")
                original_rmtree(path)

            with patch.object(raw.shutil, "rmtree", side_effect=remove), patch.object(raw.time, "sleep"):
                with raw.package_directory(Path(parent)) as directory:
                    (directory / "candidato").write_bytes(b"temporario")
            self.assertEqual(len(attempts), 2)
            self.assertFalse(directory.exists())

    def test_every_manifest_input_has_a_comparison_policy(self):
        import csv
        from compatibilidade_raw import used_sheets
        with (ROOT / "docs/fontes_dados.csv").open(encoding="utf-8-sig", newline="") as file:
            rows = list(csv.DictReader(file))
        for row in rows:
            with self.subTest(path=row["caminho_local"]):
                self.assertIn(Path(row["nome_local"]).suffix, {".xls", ".xlsx", ".xlsb", ".csv", ".txt"})
                if Path(row["nome_local"]).suffix in {".xls", ".xlsx", ".xlsb"}:
                    sheets = used_sheets(row)
                    self.assertTrue(sheets is None or (sheets and all(sheets)))

    def test_renamed_historical_member_is_selected(self):
        row = {"nome_local": "MEDIA_UF_2007.xlsx", "indicador": "SAEB"}
        self.assertEqual(raw.candidates(["DADOS/MEDIA_UF.xlsx", "DADOS/MEDIA_MUNICIPIO.xlsx"], row),
                         ["DADOS/MEDIA_UF.xlsx"])

    def test_rar_prefers_bsdtar_when_both_tools_are_available(self):
        def run(args, **kwargs):
            if args[1] == "--version":
                return subprocess.CompletedProcess(args, 0, b"bsdtar 3.7.7 - libarchive 3.7.7", b"")
            return subprocess.CompletedProcess(args, 0, b"dados.csv\n", b"")

        with patch.object(raw.shutil, "which", side_effect=lambda name: {
                "bsdtar": "C:\\tools\\bsdtar.exe", "tar": "C:\\tools\\tar.exe"}[name]), \
                patch.object(raw.subprocess, "run", side_effect=run) as run_process:
            tool, listing = raw.list_rar_members(Path("fonte.rar"))

        self.assertEqual(tool, "C:\\tools\\bsdtar.exe")
        self.assertEqual(listing, b"dados.csv\n")
        self.assertEqual([call.args[0][1] for call in run_process.call_args_list], ["--version", "-tf"])

    def test_rar_accepts_tar_exe_identified_as_libarchive(self):
        def run(args, **kwargs):
            if args[1] == "--version":
                return subprocess.CompletedProcess(args, 0, b"bsdtar 3.7.7 - libarchive 3.7.7", b"")
            return subprocess.CompletedProcess(args, 0, b"dados.csv\n", b"")

        with patch.object(raw.shutil, "which", side_effect=lambda name:
                          None if name == "bsdtar" else "C:\\Windows\\System32\\tar.exe"), \
                patch.object(raw.subprocess, "run", side_effect=run):
            tool, listing = raw.list_rar_members(Path("fonte.rar"))

        self.assertEqual(tool, "C:\\Windows\\System32\\tar.exe")
        self.assertEqual(listing, b"dados.csv\n")

    def test_rar_rejects_gnu_tar_without_attempting_listing(self):
        with patch.object(raw.shutil, "which", side_effect=lambda name:
                          None if name == "bsdtar" else "/usr/bin/tar"), \
                patch.object(raw.subprocess, "run",
                             return_value=subprocess.CompletedProcess(
                                 ["tar", "--version"], 0, b"tar (GNU tar) 1.35", b"")) as run_process:
            with self.assertRaisesRegex(RuntimeError, "GNU tar"):
                raw.list_rar_members(Path("fonte.rar"))

        self.assertEqual(run_process.call_count, 1)

    def test_rar_fails_clearly_when_no_extractor_is_available(self):
        with patch.object(raw.shutil, "which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "bsdtar.*libarchive"):
                raw.list_rar_members(Path("fonte.rar"))

    def test_rar_listing_failure_cleans_package_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            scratch, destination, row = self._rar_case(temp)

            def run(args, **kwargs):
                if args[1] == "--version":
                    return subprocess.CompletedProcess(args, 0, b"bsdtar 3.7 - libarchive 3.7", b"")
                raise subprocess.CalledProcessError(1, args, stderr=b"RAR listing failed")

            with patch.object(raw, "download", side_effect=lambda url, path: path.write_bytes(b"fake RAR")), \
                    patch.object(raw.shutil, "which", side_effect=lambda name: "bsdtar.exe" if name == "bsdtar" else None), \
                    patch.object(raw.subprocess, "run", side_effect=run):
                with self.assertRaisesRegex(RuntimeError, "falha ao listar"):
                    raw.process_group(("https://download.inep.gov.br/fonte.rar", [row]),
                                      destination, scratch, False)

            self.assertEqual(list(scratch.glob("pacote-*")), [])

    def test_rar_extraction_failure_preserves_existing_file_and_cleans_temp(self):
        with tempfile.TemporaryDirectory() as temp:
            scratch, destination, row = self._rar_case(temp)
            target = destination / "tdi" / "dados.csv"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"arquivo anteriormente aceito")

            def run(args, **kwargs):
                if args[1] == "--version":
                    return subprocess.CompletedProcess(args, 0, b"bsdtar 3.7 - libarchive 3.7", b"")
                if args[1] == "-tf":
                    return subprocess.CompletedProcess(args, 0, b"dados.csv\n", b"")
                raise subprocess.CalledProcessError(1, args, stderr=b"RAR extraction failed")

            with patch.object(raw, "download", side_effect=lambda url, path: path.write_bytes(b"fake RAR")), \
                    patch.object(raw.shutil, "which", side_effect=lambda name: "bsdtar.exe" if name == "bsdtar" else None), \
                    patch.object(raw.subprocess, "run", side_effect=run):
                with self.assertRaisesRegex(RuntimeError, "Falha ao extrair.*RAR extraction failed"):
                    raw.process_group(("https://download.inep.gov.br/fonte.rar", [row]),
                                      destination, scratch, False)

            self.assertEqual(target.read_bytes(), b"arquivo anteriormente aceito")
            self.assertEqual(list(scratch.glob("pacote-*")), [])

    def test_rar_extracts_member_and_cleans_package_directory(self):
        content = b"dados oficiais"
        with tempfile.TemporaryDirectory() as temp:
            scratch, destination, row = self._rar_case(temp, content)

            def run(args, **kwargs):
                if args[1] == "--version":
                    return subprocess.CompletedProcess(args, 0, b"bsdtar 3.7 - libarchive 3.7", b"")
                if args[1] == "-tf":
                    return subprocess.CompletedProcess(args, 0, b"pasta/dados.csv\n", b"")
                kwargs["stdout"].write(content)
                return subprocess.CompletedProcess(args, 0, b"", b"")

            with patch.object(raw, "download", side_effect=lambda url, path: path.write_bytes(b"fake RAR")), \
                    patch.object(raw.shutil, "which", side_effect=lambda name: "bsdtar.exe" if name == "bsdtar" else None), \
                    patch.object(raw.subprocess, "run", side_effect=run):
                results = raw.process_group(("https://download.inep.gov.br/fonte.rar", [row]),
                                            destination, scratch, False)

            self.assertEqual(results[0]["status"], "identico")
            self.assertEqual((destination / "tdi" / "dados.csv").read_bytes(), content)
            self.assertEqual(list(scratch.glob("pacote-*")), [])


if __name__ == "__main__":
    unittest.main()
