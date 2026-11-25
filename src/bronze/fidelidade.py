"""Conferência posicional das células Raw, incluindo cabeçalhos e linhas de origem."""
import csv
from itertools import islice

import pandas as pd
import pyarrow.parquet as pq


def divergencia(arquivo, aba, linha, coluna, esperado, encontrado):
    raise RuntimeError(
        f"divergências RAW/Bronze: arquivo={arquivo}, aba={aba!r}, linha={linha}, "
        f"coluna={coluna}, esperado={esperado!r}, encontrado={encontrado!r}"
    )


def colunas_fonte(largura):
    return [f"col_{i:03d}" for i in range(1, largura + 1)]


def conferir_colunas(arquivo, aba, esperadas, esquema):
    encontradas = [c for c in esquema if c.startswith("col_")]
    if esperadas != encontradas:
        divergencia(arquivo, aba, "esquema", "campos de origem", esperadas, encontradas)


def comparar_bloco(arquivo, aba, esperado, bronze):
    """Compara por posição, inclusive o número físico da linha, sem sentinela ou tolerância."""
    bronze = bronze.reset_index(drop=True)
    esperado = esperado.reset_index(drop=True)
    if len(esperado) != len(bronze):
        pos = min(len(esperado), len(bronze))
        maior = esperado if len(esperado) > pos else bronze
        divergencia(arquivo, aba, maior.at[pos, "_linha_origem"], "quantidade de registros",
                    len(esperado), len(bronze))
    for coluna in esperado:
        raw, atual = esperado[coluna], bronze[coluna]
        iguais = raw.eq(atual).fillna(False) | (raw.isna() & atual.isna())
        if not iguais.all():
            pos = iguais.idxmin()
            divergencia(arquivo, aba, esperado.at[pos, "_linha_origem"], coluna,
                        raw.iat[pos], atual.iat[pos])
    return len(esperado) * (len(esperado.columns) - 1)


def comparar_planilha(arquivo, aba, raw, bronze):
    colunas = colunas_fonte(raw.shape[1])
    conferir_colunas(arquivo, aba, colunas, bronze.columns)
    # A ingestão conserva a posição Excel antes de remover linhas totalmente vazias.
    esperado = raw.dropna(how="all").astype("string")
    esperado.columns = colunas
    esperado.insert(0, "_linha_origem", esperado.index + 1)
    return comparar_bloco(arquivo, aba, esperado, bronze)


def validar_planilha(arquivo, bronze, aba=None):
    # Rendimento e TDI usam a primeira aba oficial, inclusive no XLS de 2009
    # que também contém Plan2 e Plan3. Nessas séries a ingestão infere o dtype.
    with pd.ExcelFile(arquivo, engine="calamine") as excel:
        inferir_tipos = aba is None
        if inferir_tipos:
            aba = excel.sheet_names[0]
        raw = excel.parse(aba, header=None, dtype=None if inferir_tipos else object,
                          keep_default_na=False, na_values=[""])
    abas = bronze["_aba_origem"]
    incorretas = abas.isna() | abas.ne(aba)
    if incorretas.any():
        pos = incorretas.to_numpy().nonzero()[0][0]
        divergencia(arquivo, aba, bronze["_linha_origem"].iloc[pos], "_aba_origem",
                    aba, abas.iloc[pos])
    return comparar_planilha(arquivo, aba, raw, bronze)


def validar_delimitado(arquivo, parquet, encoding, *, remover_vazias=False, bloco=8192):
    """Lê o TXT/CSV com csv.reader e avança em paralelo com os lotes Parquet."""
    fonte = pq.ParquetFile(parquet)
    total = 0
    with arquivo.open(encoding=encoding, newline="") as stream:
        leitor = csv.reader(stream, delimiter=";", strict=True)
        cabecalho = next(leitor, None)
        if not cabecalho:
            divergencia(arquivo, None, 1, "cabeçalho", "campos da fonte", cabecalho)
        colunas = colunas_fonte(len(cabecalho))
        conferir_colunas(arquivo, None, colunas, fonte.schema_arrow.names)
        campos = ["_linha_origem", *colunas]

        def registros():
            yield [1, *(campo or None for campo in cabecalho)]
            for linha, valores in enumerate(leitor, start=2):
                if remover_vazias and not any(valores):
                    continue
                if len(valores) != len(colunas):
                    divergencia(arquivo, None, linha, "quantidade de campos",
                                len(colunas), len(valores))
                yield [linha, *(v if v != "" else None for v in valores)]

        linhas = registros()
        for lote in fonte.iter_batches(batch_size=bloco, columns=campos):
            esperado = pd.DataFrame.from_records(islice(linhas, lote.num_rows), columns=campos)
            total += comparar_bloco(arquivo, None, esperado, lote.to_pandas())
        restante = next(linhas, None)
        if restante is not None:
            divergencia(arquivo, None, restante[0], "_linha_origem", restante[0], "fim do Parquet")
    return total
