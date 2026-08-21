from __future__ import annotations

import csv
import importlib.util
import re
import sys
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_pipeline_module():
    path = ROOT / "src" / "pipeline.py"
    spec = importlib.util.spec_from_file_location("pipeline", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível importar {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def measure_names() -> list[str]:
    path = ROOT / "powerbi" / "medidas_power_bi.dax"
    names: list[str] = []

    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        if stripped.startswith("VAR ") or stripped == "RETURN":
            continue
        if stripped.endswith("="):
            names.append(stripped[:-1].strip())

    return names


class PipelineContractsTest(unittest.TestCase):
    def test_expected_commands_exist(self) -> None:
        pipeline = load_pipeline_module()
        self.assertEqual(
            set(pipeline.COMMANDS),
            {"bronze", "silver", "gold", "validate-gold", "full"},
        )

    def test_all_pipeline_scripts_exist(self) -> None:
        pipeline = load_pipeline_module()
        for command, steps in pipeline.COMMANDS.items():
            with self.subTest(command=command):
                self.assertGreater(len(steps), 0)
                for step in steps:
                    self.assertTrue(
                        (ROOT / step.script).is_file(),
                        f"Script ausente em {command}: {step.script}",
                    )

    def test_full_sequence_is_expected_composition(self) -> None:
        pipeline = load_pipeline_module()
        expected = (
            pipeline.BRONZE_STEPS
            + pipeline.SILVER_STEPS
            + pipeline.GOLD_BUILD_STEPS
            + pipeline.VALIDATE_GOLD_STEPS
        )
        self.assertEqual(pipeline.COMMANDS["full"], expected)


class ManifestContractsTest(unittest.TestCase):
    def setUp(self) -> None:
        path = ROOT / "docs" / "fontes_dados.csv"
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            self.rows = list(csv.DictReader(file))

    def test_manifest_record_counts(self) -> None:
        self.assertEqual(len(self.rows), 54)
        counts = Counter(row["indicador"] for row in self.rows)
        self.assertEqual(counts["Rendimento Escolar"], 17)
        self.assertEqual(counts["TDI"], 17)
        self.assertEqual(counts["IDEB"], 1)
        self.assertEqual(counts["PND"], 3)
        self.assertEqual(counts["SAEB"], 16)

    def test_manifest_paths_are_unique(self) -> None:
        paths = [row["caminho_local"] for row in self.rows]
        duplicates = [path for path, count in Counter(paths).items() if count > 1]
        self.assertEqual(duplicates, [])

    def test_manifest_hashes_are_sha256(self) -> None:
        for row in self.rows:
            with self.subTest(path=row["caminho_local"]):
                self.assertRegex(row["sha256"], r"^[0-9a-f]{64}$")


class PowerBiDocumentationContractsTest(unittest.TestCase):
    def test_dax_measure_count(self) -> None:
        self.assertEqual(len(measure_names()), 27)

    def test_dax_measures_are_documented_exactly(self) -> None:
        documentation = (ROOT / "docs" / "modelagem_power_bi.md").read_text(
            encoding="utf-8-sig",
        )
        missing = [name for name in measure_names() if name not in documentation]
        self.assertEqual(missing, [])

    def test_unaccented_measure_names_are_not_used_as_substitutes(self) -> None:
        documentation = (ROOT / "docs" / "modelagem_power_bi.md").read_text(
            encoding="utf-8-sig",
        )
        forbidden = [
            "Taxa de Aprovacao",
            "Taxa de Reprovacao",
            "TDI Media",
            "IDEB Medio",
            "Proficiencia Media SAEB",
            "Nao Proficientes",
            "Padrao 1",
            "Variacao IDEB",
        ]
        found = [name for name in forbidden if name in documentation]
        self.assertEqual(found, [])


class ReadmeContractsTest(unittest.TestCase):
    def test_readme_image_paths_exist(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        image_paths = re.findall(r'<img\s+src="([^"]+)"', readme)
        self.assertGreaterEqual(len(image_paths), 4)

        for image_path in image_paths:
            relative_path = image_path.replace("%20", " ")
            with self.subTest(image=relative_path):
                self.assertTrue((ROOT / relative_path).is_file())


if __name__ == "__main__":
    unittest.main()
