from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("baixar_raw", ROOT / "scripts/baixar_raw.py")
raw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(raw)


class DownloadTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
