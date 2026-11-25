"""Referências de validação da PND 2025, baseadas nas publicações do Inep."""
from pathlib import Path
import re

import pandas as pd


DICIONARIO = Path("data/raw/pnd/Dicionário_arquivos_variáveis_PND_2025.xlsx")


def ler_areas_oficiais():
    dados = pd.read_excel(DICIONARIO, sheet_name="DICIONÁRIO_DE_VARIAVÉIS", header=None,
                          usecols=[0, 4], names=["variavel", "categoria"])
    # As categorias seguintes de CO_GRUPO continuam em linhas com a variável vazia.
    categorias = dados.loc[dados["variavel"].ffill().eq("CO_GRUPO"), "categoria"]
    areas = {}
    for categoria in categorias:
        par = re.fullmatch(r"\s*(\d+)\s*=\s*(.+?)\s*", str(categoria))
        if not par:
            raise RuntimeError(f"Categoria CO_GRUPO inválida no dicionário: {categoria!r}.")
        codigo = int(par[1])
        # A Silver padroniza o espaçamento de Letras nas entradas 905 e 6407.
        nome = re.sub(r"\s*-\s*", " - ", " ".join(par[2].split()))
        if codigo in areas or nome in areas.values():
            raise RuntimeError(f"Categoria CO_GRUPO ambígua no dicionário: {categoria!r}.")
        areas[codigo] = nome
    if len(areas) != 17:
        raise RuntimeError(f"Dicionário PND 2025: esperadas 17 áreas; encontradas {len(areas)}.")
    return areas


def validar_dim_area_oficial(dim):
    areas = ler_areas_oficiais()
    if set(dim["CO_GRUPO"]) != set(areas) or dim["CO_GRUPO"].duplicated().any():
        raise RuntimeError("DIM_AREA_PND: códigos diferentes das 17 áreas oficiais.")
    esperados = dim["CO_GRUPO"].map(areas)
    divergentes = ~dim["AREA_PROVA"].eq(esperados).fillna(False)
    if divergentes.any():
        i = dim.index[divergentes][0]
        raise RuntimeError(f"DIM_AREA_PND: CO_GRUPO={dim.at[i, 'CO_GRUPO']}, "
                           f"nome={dim.at[i, 'AREA_PROVA']!r}, dicionário={esperados.at[i]!r}.")


def validar_intervalos_oficiais(fato):
    """Nota Técnica 44/2025, item 9.3, Tabela 2: audita a faixa do rótulo gravado."""
    nota = pd.to_numeric(fato["NT_GER"], errors="raise")
    rotulo = fato["PADRAO_DESEMPENHO"]
    valido = (
        (rotulo.eq("ABAIXO_DO_BASICO") & nota.lt(50))
        | (rotulo.eq("BASICO") & nota.between(50, 70, inclusive="left"))
        | (rotulo.eq("ADEQUADO") & nota.ge(70))
    ) & nota.between(0, 100)
    divergentes = ~valido.fillna(False)
    if divergentes.any():
        amostra = fato.loc[divergentes, ["NT_GER", "PADRAO_DESEMPENHO"]].head(5)
        raise RuntimeError(f"{divergentes.sum()} classificações divergem da Tabela 2 "
                           f"da Nota Técnica 44/2025:\n{amostra.to_string(index=False)}")
