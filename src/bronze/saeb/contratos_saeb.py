"""Inventário estrito dos dois grupos de arquivos da Bronze SAEB."""
from pathlib import Path


NOME_AGREGADO_2023 = "saeb_2023_resultados_uf.parquet"


def validar_inventario_bronze(
    diretorio: Path,
    nomes_historicos,
    *,
    exigir_agregado_2023: bool = False,
) -> bool:
    """Exige os históricos e admite somente o agregado oficial adicional.

    Na primeira construção, o agregado ainda será produzido pela próxima
    etapa. Em uma reexecução ele pode existir. A validação do conteúdo desse
    arquivo pertence ao seu validador específico, não a esta enumeração.
    Retorna se o agregado está presente; não aceita aliases ou cópias.
    """
    historicos = list(nomes_historicos)
    if len(historicos) != len(set(historicos)) or NOME_AGREGADO_2023 in historicos:
        raise RuntimeError("Configuração de nomes históricos duplicada ou confundida com o agregado.")

    obrigatorios = set(historicos)
    permitidos = obrigatorios | {NOME_AGREGADO_2023}
    if exigir_agregado_2023:
        obrigatorios.add(NOME_AGREGADO_2023)

    entradas = list(diretorio.iterdir()) if diretorio.is_dir() else []
    encontrados = {p.name for p in entradas if p.is_file()}
    faltantes = obrigatorios - encontrados
    inesperados = {p.name for p in entradas if p.name not in permitidos or not p.is_file()}
    if faltantes or inesperados:
        raise RuntimeError(
            "Conjunto de arquivos da Bronze SAEB diferente do contrato.\n"
            f"Históricos obrigatórios: {sorted(historicos)}\n"
            f"Agregado oficial separado: {NOME_AGREGADO_2023} "
            f"(obrigatório={exigir_agregado_2023})\n"
            f"Ausentes: {sorted(faltantes)}\n"
            f"Inesperados ou inválidos: {sorted(inesperados)}"
        )
    return NOME_AGREGADO_2023 in encontrados
