"""RAW-02: falhas isoladas, publicação e recuperação sem insumos externos."""
import csv
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from src import publicacao as pub


class PublicacaoTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (self.root / "data/raw").mkdir(parents=True)
        (self.root / "docs").mkdir()
        (self.root / "data/raw/fonte").write_bytes(b"fonte")
        with (self.root / "docs/fontes_dados.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=["caminho_local", "sha256"])
            writer.writeheader()
            writer.writerow(dict(caminho_local="data/raw/fonte",
                                 sha256=pub.digest(self.root / "data/raw/fonte")))
        self.required = ["bronze", "silver", "dimensoes", "fato", "global"]
        self.steps = [SimpleNamespace(script=name) for name in self.required]
        self.fail = None
        self.payload = b"primeira"

    def runner(self, step, work):
        if step is None:
            if self.fail == "raw":
                raise RuntimeError("raw")
            return
        gold = work / "data/gold"
        gold.mkdir(parents=True, exist_ok=True)
        (gold / (step.script + ".parquet")).write_bytes(self.payload)
        if self.fail == step.script:
            raise RuntimeError(step.script)

    def execute(self):
        pub.execute(self.root, "full", self.steps, self.required, self.runner)

    def verify(self, previous=False):
        return pub.verify(self.root, self.required, previous)

    def test_success(self):
        self.execute()
        self.assertEqual(self.verify()["estado"], "concluida")

    def test_every_failure_preserves_previous_and_identifies_it(self):
        self.execute()
        original = pub.inventory(self.root / "data/gold")
        for failure in ["raw", *self.required]:
            with self.subTest(failure=failure):
                self.fail = failure
                with self.assertRaises(RuntimeError):
                    self.execute()
                self.assertEqual(pub.inventory(self.root / "data/gold"), original)
                with self.assertRaisesRegex(RuntimeError, "anterior"):
                    self.verify()
                self.verify(previous=True)

    def test_failure_without_previous(self):
        self.fail = "fato"
        with self.assertRaises(RuntimeError):
            self.execute()
        self.assertFalse((self.root / "data/gold").exists())
        self.assertEqual(pub.read_json(self.root / "data/execucoes/ultima.json")["estado"], "malsucedida")

    def test_recovery_after_failure(self):
        self.fail = "silver"
        with self.assertRaises(RuntimeError):
            self.execute()
        self.fail = None
        self.execute()
        self.verify()

    def test_missing_file(self):
        self.execute()
        (self.root / "data/gold/fato.parquet").unlink()
        with self.assertRaisesRegex(RuntimeError, "Inventário"):
            self.verify()

    def test_changed_file_and_mixed_generation(self):
        self.execute()
        old = (self.root / "data/gold/fato.parquet").read_bytes()
        self.payload = b"segunda"
        self.execute()
        (self.root / "data/gold/fato.parquet").write_bytes(old)
        with self.assertRaisesRegex(RuntimeError, "Inventário"):
            self.verify()

    def test_missing_manifest(self):
        self.execute()
        (self.root / "data/gold/publicacao.json").unlink()
        with self.assertRaises(FileNotFoundError):
            self.verify()

    def test_inconsistent_manifest(self):
        self.execute()
        path = self.root / "data/gold/publicacao.json"
        manifest = pub.read_json(path)
        manifest["insumos"] = {"falso": "hash"}
        pub.write_json(path, manifest)
        with self.assertRaisesRegex(RuntimeError, "registro"):
            self.verify()

    def test_global_alone_cannot_publish(self):
        self.steps = self.steps[-1:]
        with self.assertRaisesRegex(RuntimeError, "incompletos"):
            self.execute()
        self.assertFalse((self.root / "data/gold").exists())

    def test_failure_between_directory_moves_restores_previous(self):
        self.execute()
        before = pub.inventory(self.root / "data/gold")
        replace = pub.os.replace
        def interrupt(source, target):
            if Path(source).name == "gold" and "trabalho" in Path(source).parts:
                raise OSError("publicação interrompida")
            return replace(source, target)
        with patch.object(pub.os, "replace", side_effect=interrupt):
            with self.assertRaises(OSError):
                self.execute()
        self.assertEqual(pub.inventory(self.root / "data/gold"), before)
        self.verify(previous=True)

    def test_abrupt_interruption_after_install_rolls_back_on_recovery(self):
        self.execute()
        before = pub.inventory(self.root / "data/gold")
        identifier = "a" * 32
        run = self.root / "data/execucoes" / identifier
        run.mkdir()
        pub.write_json(self.root / "data/execucoes/ultima.json",
                       dict(id=identifier, estado="em_andamento", publicando=True, tinha_gold=True))
        pub.os.replace(self.root / "data/gold", run / "gold_anterior")
        (self.root / "data/gold").mkdir()
        (self.root / "data/gold/parcial").write_bytes(b"novo")
        pub.recover(self.root)
        self.assertEqual(pub.inventory(self.root / "data/gold"), before)
        self.verify(previous=True)

    def test_first_publication_interrupted_is_not_valid(self):
        identifier = "b" * 32
        (self.root / "data/execucoes" / identifier).mkdir(parents=True)
        (self.root / "data/gold").mkdir()
        pub.write_json(self.root / "data/execucoes/ultima.json",
                       dict(id=identifier, estado="em_andamento", publicando=True, tinha_gold=False))
        pub.recover(self.root)
        self.assertFalse((self.root / "data/gold").exists())

    def test_lock_blocks_concurrent_execution(self):
        with pub.execution_lock(self.root):
            with self.assertRaises(RuntimeError):
                with pub.execution_lock(self.root):
                    pass

    def test_snapshot_must_match_manifest(self):
        (self.root / "data/raw/fonte").write_bytes(b"mudou")
        with self.assertRaisesRegex(RuntimeError, "Snapshot"):
            self.execute()


    def test_partial_commands_reuse_isolated_intermediates(self):
        def bronze(step, work):
            if step:
                path = work / "data/bronze/a.parquet"
                path.parent.mkdir(parents=True)
                path.write_bytes(b"nova bronze")
        pub.execute(self.root, "bronze", self.steps[:1], self.required, bronze)
        def silver(step, work):
            if step:
                self.assertEqual((work / "data/bronze/a.parquet").read_bytes(), b"nova bronze")
        pub.execute(self.root, "silver", self.steps[1:2], self.required, silver)
        self.assertFalse((self.root / "data/gold").exists())

    def test_manifest_without_required_control(self):
        self.execute()
        path = self.root / "data/gold/publicacao.json"
        manifest = pub.read_json(path)
        manifest["controles"].remove("fato")
        pub.write_json(path, manifest)
        with self.assertRaisesRegex(RuntimeError, "controles"):
            self.verify()

    def test_changed_raw_is_not_current(self):
        self.execute()
        (self.root / "data/raw/fonte").write_bytes(b"fonte alterada")
        with self.assertRaisesRegex(RuntimeError, "desatualizada"):
            self.verify()
        self.verify(previous=True)

    def test_changed_raw_manifest_is_not_current(self):
        self.execute()
        with (self.root / "docs/fontes_dados.csv").open("a") as stream:
            stream.write("\n")
        with self.assertRaisesRegex(RuntimeError, "desatualizada"):
            self.verify()
        self.verify(previous=True)

    def test_download_directory_does_not_make_raw_stale(self):
        self.execute()
        scratch = self.root / "data/raw/.download"
        scratch.mkdir()
        (scratch / "relatorio.json").write_text("temporario")
        self.verify()

    def test_partial_success_preserves_gold_and_reports_latest_attempt(self):
        self.execute()
        publication = pub.read_json(self.root / "data/gold/publicacao.json")["id"]
        for command in ("bronze", "silver"):
            pub.execute(self.root, command, self.steps[:1], self.required, lambda step, work: None)
            latest = pub.read_json(self.root / "data/execucoes/ultima.json")
            self.assertEqual((latest["estado"], latest["comando"]), ("concluida", command))
            self.assertEqual(self.verify()["id"], publication)
            self.assertEqual(pub.read_json(self.root / "data/gold/publicacao.json")["id"],
                             publication)

    def test_failed_attempt_then_partial_reuses_last_completed_intermediates(self):
        def completed_full(step, work):
            if step is None:
                return
            bronze = work / "data/bronze"
            bronze.mkdir(parents=True, exist_ok=True)
            (bronze / "intermediario.parquet").write_bytes(b"ultimo completo")
            gold = work / "data/gold"
            gold.mkdir(parents=True, exist_ok=True)
            (gold / "publicado.parquet").write_bytes(b"gold anterior")

        pub.execute(self.root, "full", self.steps, self.required, completed_full)
        stale = self.root / "data/bronze/intermediario.parquet"
        stale.parent.mkdir(parents=True)
        stale.write_bytes(b"copia obsoleta")
        self.fail = "silver"
        with self.assertRaises(RuntimeError):
            self.execute()

        def check_intermediate(step, work):
            if step is not None:
                intermediate = work / "data/bronze/intermediario.parquet"
                self.assertEqual(intermediate.read_bytes(), b"ultimo completo")

        pub.execute(self.root, "silver", self.steps[1:2], self.required, check_intermediate)

    def test_archived_raw_manifest_hash_is_verified(self):
        self.execute()
        identifier = pub.read_json(self.root / "data/gold/publicacao.json")["id"]
        archived = self.root / "data/execucoes" / identifier / "fontes_dados.csv"
        archived.write_bytes(b"manifesto arquivado divergente")
        with self.assertRaisesRegex(RuntimeError, "manifesto Raw arquivado"):
            self.verify(previous=True)

    def test_manifest_copy_race_cannot_publish(self):
        copy = pub.shutil.copy2

        def alter_copy(source, target, **kwargs):
            result = copy(source, target, **kwargs)
            if Path(target).name == "fontes_dados.csv":
                with Path(target).open("a") as stream:
                    stream.write("\n")
            return result

        with patch.object(pub.shutil, "copy2", side_effect=alter_copy):
            with self.assertRaisesRegex(RuntimeError, "Cópia do manifesto Raw"):
                self.execute()
        self.assertFalse((self.root / "data/gold").exists())
