from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Step:
    name: str
    script: str


BRONZE_STEPS = [
    Step("Bronze Rendimento - ingestao", "src/bronze/rendimento/ingest_rendimento.py"),
    Step("Bronze Rendimento - validacao", "src/bronze/rendimento/validar_bronze_rendimento.py"),
    Step("Bronze TDI - ingestao", "src/bronze/tdi/ingest_tdi.py"),
    Step("Bronze TDI - validacao", "src/bronze/tdi/validar_bronze_tdi.py"),
    Step("Bronze IDEB - ingestao", "src/bronze/ideb/ingest_ideb.py"),
    Step("Bronze IDEB - validacao", "src/bronze/ideb/validar_bronze_ideb.py"),
    Step("Bronze SAEB - ingestao historica", "src/bronze/saeb/ingest_saeb.py"),
    Step("Bronze SAEB - validacao historica", "src/bronze/saeb/validar_bronze_saeb.py"),
    Step("Bronze SAEB 2023 UF - ingestao", "src/bronze/saeb/ingest_saeb_resultados_2023.py"),
    Step("Bronze SAEB 2023 UF - validacao", "src/bronze/saeb/validar_bronze_saeb_resultados_2023.py"),
    Step("Bronze PND - ingestao", "src/bronze/pnd/ingest_pnd.py"),
    Step("Bronze PND - validacao", "src/bronze/pnd/validar_bronze_pnd.py"),
]

SILVER_STEPS = [
    Step("Silver Rendimento - transformacao", "src/silver/rendimento/transformar_rendimento.py"),
    Step("Silver Rendimento - validacao", "src/silver/rendimento/validar_silver_rendimento.py"),
    Step("Silver TDI - transformacao", "src/silver/tdi/transformar_tdi.py"),
    Step("Silver TDI - validacao", "src/silver/tdi/validar_silver_tdi.py"),
    Step("Silver IDEB - transformacao", "src/silver/ideb/transformar_ideb.py"),
    Step("Silver IDEB - validacao", "src/silver/ideb/validar_silver_ideb.py"),
    Step("Silver SAEB - transformacao", "src/silver/saeb/transformar_saeb.py"),
    Step("Silver SAEB - validacao", "src/silver/saeb/validar_silver_saeb.py"),
    Step("Silver PND - transformacao", "src/silver/pnd/transformar_pnd.py"),
    Step("Silver PND - validacao", "src/silver/pnd/validar_silver_pnd.py"),
]

GOLD_BUILD_STEPS = [
    Step("Gold Rendimento - fato", "src/gold/rendimento/transformar_rendimento.py"),
    Step("Gold Rendimento - validacao", "src/gold/rendimento/validar_fato_rendimento.py"),
    Step("Gold TDI - fato", "src/gold/tdi/transformar_tdi.py"),
    Step("Gold TDI - validacao", "src/gold/tdi/validar_fato_tdi.py"),
    Step("Gold IDEB - fato", "src/gold/ideb/transformar_ideb.py"),
    Step("Gold IDEB - validacao", "src/gold/ideb/validar_fato_ideb.py"),
    Step("Gold SAEB - fato", "src/gold/saeb/transformar_saeb.py"),
    Step("Gold SAEB - validacao", "src/gold/saeb/validar_fato_saeb.py"),
    Step("Gold PND - fato", "src/gold/pnd/transformar_pnd.py"),
    Step("Gold PND - validacao", "src/gold/pnd/validar_fato_pnd.py"),
    Step("Gold Dimensoes - transformacao", "src/gold/dimensoes/transformar_dimensoes.py"),
    Step("Gold Dimensoes - validacao", "src/gold/dimensoes/validar_dimensoes.py"),
]

VALIDATE_GOLD_STEPS = [
    Step("Gold - validacao global", "src/gold/validar_gold.py"),
]

COMMANDS = {
    "bronze": BRONZE_STEPS,
    "silver": SILVER_STEPS,
    "gold": GOLD_BUILD_STEPS + VALIDATE_GOLD_STEPS,
    "validate-gold": VALIDATE_GOLD_STEPS,
    "full": BRONZE_STEPS + SILVER_STEPS + GOLD_BUILD_STEPS + VALIDATE_GOLD_STEPS,
}


def run_step(step: Step, dry_run: bool) -> None:
    script = ROOT / step.script

    if not script.is_file():
        raise FileNotFoundError(f"Script nao encontrado: {step.script}")

    command = [sys.executable, str(script)]
    print("=" * 100)
    print(step.name)
    print(" ".join(command))
    print("=" * 100)

    if dry_run:
        return

    subprocess.run(command, cwd=ROOT, check=True)


def list_commands() -> None:
    print("Comandos disponiveis:")
    for command, steps in COMMANDS.items():
        print(f"- {command}: {len(steps)} etapa(s)")

    print()
    print("Use --dry-run para listar a sequencia sem executar.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Orquestra scripts do pipeline educacional.",
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=sorted(COMMANDS),
        help="Etapa a executar.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Lista comandos disponiveis.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra a sequencia de scripts sem executar.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.list:
        list_commands()
        return

    if not args.command:
        list_commands()
        return

    steps = COMMANDS[args.command]

    for step in steps:
        run_step(step, dry_run=args.dry_run)

    print("=" * 100)
    print(f"Pipeline concluido: {args.command}")
    print("=" * 100)


if __name__ == "__main__":
    main()
