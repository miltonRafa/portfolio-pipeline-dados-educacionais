from pathlib import Path
import csv
import hashlib

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


RAW_DIR = Path("data/raw/pnd")
BRONZE_DIR = Path("data/bronze/pnd")

ARQUIVO_RAW = "microdados2025_pnd_arq1.txt"
ARQUIVO_BRONZE = "pnd_2025.parquet"

ANO_REFERENCIA = 2025
FONTE = "PND"
GRANULARIDADE = "REGISTRO_INDIVIDUAL"

ENCODING = "utf-8"
SEP = ";"
QUOTECHAR = '"'

COLUNAS_ESPERADAS = [
    "NU_ANO",
    "CO_GRUPO",
    "CO_MUNICIPIO_PROVA",
    "SG_UF_MUNICIPIO_PROVA",
    "TP_INSCRICAO_PND",
    "IN_REAPLICACAO",
    "CO_CADERNO",
    "DS_VT_GAB_OBJ",
    "DS_VT_ESC_OBJ",
    "DS_VT_ACE_OBJ",
    "TP_PRES",
    "TP_SIT_DISC",
    "PROFICIENCIA",
    "NT_OBJ",
    "NT_DIS",
    "NT_GER",
    "QT_ACERTOS",
    "CO_RS_I1",
    "CO_RS_I2",
    "CO_RS_I3",
    "CO_RS_I4",
    "CO_RS_I5",
    "CO_RS_I6",
    "CO_RS_I7",
    "CO_RS_I8",
    "CO_RS_I9",
]

QUANTIDADE_COLUNAS_FONTE = 26

SHA256_ESPERADO = (
    "b15968a19e309bca6b63c6f6d7af094efdc13d900645dc7385872a6a50dd7baf"
)

LINHAS_FISICAS_ESPERADAS = 1_087_360
REGISTROS_DADOS_ESPERADOS = 1_087_359

# A Bronze preserva a linha física de cabeçalho como primeira linha,
# portanto terá 1 linha a mais que o número de registros de dados.
LINHAS_BRONZE_ESPERADAS = 1_087_360

CABECALHO_INDICE = 0
LINHA_CABECALHO_ORIGEM = 1

CHUNKSIZE = 100_000
COMPRESSION = "snappy"


def calcular_sha256_e_linhas(caminho):
    sha256 = hashlib.sha256()
    quebras_linha = 0
    ultimo_byte = None

    with caminho.open("rb") as arquivo:
        while bloco := arquivo.read(1024 * 1024):
            sha256.update(bloco)
            quebras_linha += bloco.count(b"\n")
            ultimo_byte = bloco[-1:]

    linhas_fisicas = quebras_linha

    if ultimo_byte not in (None, b"\n"):
        linhas_fisicas += 1

    return sha256.hexdigest(), linhas_fisicas


def validar_raw(caminho):
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo RAW não encontrado: {caminho}"
        )

    if not caminho.is_file():
        raise RuntimeError(
            f"O caminho RAW não representa um arquivo: {caminho}"
        )

    sha256_atual, linhas_fisicas = calcular_sha256_e_linhas(
        caminho
    )

    if sha256_atual != SHA256_ESPERADO:
        raise RuntimeError(
            "\nSHA-256 do arquivo PND diferente do auditado.\n"
            f"Esperado: {SHA256_ESPERADO}\n"
            f"Atual:    {sha256_atual}"
        )

    if linhas_fisicas != LINHAS_FISICAS_ESPERADAS:
        raise RuntimeError(
            "\nQuantidade de linhas físicas diferente da auditada.\n"
            f"Esperado: {LINHAS_FISICAS_ESPERADAS:,}\n"
            f"Atual:    {linhas_fisicas:,}"
        )

    return sha256_atual


def validar_cabecalho(caminho):
    with caminho.open(
        "r",
        encoding=ENCODING,
        newline="",
    ) as arquivo:
        leitor = csv.reader(
            arquivo,
            delimiter=SEP,
            quotechar=QUOTECHAR,
        )

        cabecalho = next(leitor)

    if cabecalho != COLUNAS_ESPERADAS:
        raise RuntimeError(
            "\nCabeçalho da PND diferente do auditado.\n"
            f"Esperado: {COLUNAS_ESPERADAS}\n"
            f"Atual:    {cabecalho}"
        )

    if len(cabecalho) != QUANTIDADE_COLUNAS_FONTE:
        raise RuntimeError(
            "\nQuantidade de colunas do cabeçalho diferente da auditada.\n"
            f"Esperado: {QUANTIDADE_COLUNAS_FONTE}\n"
            f"Atual:    {len(cabecalho)}"
        )


def nomes_colunas_bronze():
    return [
        f"col_{indice:03d}"
        for indice in range(
            1,
            QUANTIDADE_COLUNAS_FONTE + 1,
        )
    ]


def preparar_chunk(
    chunk,
    linha_inicial,
    sha256_arquivo,
):
    colunas_fonte = nomes_colunas_bronze()

    if len(chunk.columns) != QUANTIDADE_COLUNAS_FONTE:
        raise RuntimeError(
            "\nQuantidade de colunas diferente da auditada durante a leitura.\n"
            f"Esperado: {QUANTIDADE_COLUNAS_FONTE}\n"
            f"Atual:    {len(chunk.columns)}"
        )

    chunk = chunk.copy()
    chunk.columns = colunas_fonte

    # O literal textual "NA" pertence à fonte e deve ser preservado.
    # Apenas campos realmente vazios são convertidos para ausência.
    chunk = chunk.replace("", pd.NA)

    for coluna in colunas_fonte:
        chunk[coluna] = chunk[coluna].astype("string")

    quantidade = len(chunk)

    # Resetar o índice de cada chunk evita alinhamento indevido de Series
    # pelo índice original do pandas a partir do segundo bloco.
    chunk = chunk.reset_index(drop=True)

    chunk.insert(
        0,
        "_fonte",
        pd.Series(
            [FONTE] * quantidade,
            index=chunk.index,
            dtype="string",
        ),
    )

    chunk.insert(
        1,
        "_sha256_arquivo",
        pd.Series(
            [sha256_arquivo] * quantidade,
            index=chunk.index,
            dtype="string",
        ),
    )

    chunk.insert(
        2,
        "_arquivo_origem",
        pd.Series(
            [ARQUIVO_RAW] * quantidade,
            index=chunk.index,
            dtype="string",
        ),
    )

    chunk.insert(
        3,
        "_aba_origem",
        pd.Series(
            [pd.NA] * quantidade,
            index=chunk.index,
            dtype="string",
        ),
    )

    chunk.insert(
        4,
        "_ano_referencia",
        pd.Series(
            [ANO_REFERENCIA] * quantidade,
            index=chunk.index,
            dtype="Int64",
        ),
    )

    chunk.insert(
        5,
        "_granularidade_origem",
        pd.Series(
            [GRANULARIDADE] * quantidade,
            index=chunk.index,
            dtype="string",
        ),
    )

    chunk.insert(
        6,
        "_indice_cabecalho_origem",
        pd.Series(
            [CABECALHO_INDICE] * quantidade,
            index=chunk.index,
            dtype="Int64",
        ),
    )

    chunk.insert(
        7,
        "_linha_origem",
        pd.Series(
            range(
                linha_inicial,
                linha_inicial + quantidade,
            ),
            index=chunk.index,
            dtype="Int64",
        ),
    )

    return chunk


def validar_primeiro_chunk(chunk):
    colunas_fonte = nomes_colunas_bronze()

    primeira_linha = [
        valor
        for valor in chunk.loc[
            chunk["_linha_origem"] == LINHA_CABECALHO_ORIGEM,
            colunas_fonte,
        ].iloc[0].tolist()
    ]

    if primeira_linha != COLUNAS_ESPERADAS:
        raise RuntimeError(
            "\nA linha de cabeçalho preservada na Bronze "
            "não corresponde ao cabeçalho auditado.\n"
            f"Esperado: {COLUNAS_ESPERADAS}\n"
            f"Atual:    {primeira_linha}"
        )


def escrever_parquet(
    caminho_raw,
    caminho_temporario,
    sha256_arquivo,
):
    leitor = pd.read_csv(
        caminho_raw,
        sep=SEP,
        encoding=ENCODING,
        quotechar=QUOTECHAR,
        header=None,
        dtype="string",
        keep_default_na=False,
        na_filter=False,
        chunksize=CHUNKSIZE,
        low_memory=False,
    )

    writer = None
    linha_inicial = 1
    total_linhas = 0
    primeiro_chunk = True

    try:
        for numero_chunk, chunk in enumerate(
            leitor,
            start=1,
        ):
            bronze = preparar_chunk(
                chunk=chunk,
                linha_inicial=linha_inicial,
                sha256_arquivo=sha256_arquivo,
            )

            if primeiro_chunk:
                validar_primeiro_chunk(bronze)
                primeiro_chunk = False

            tabela = pa.Table.from_pandas(
                bronze,
                preserve_index=False,
            )

            if writer is None:
                writer = pq.ParquetWriter(
                    caminho_temporario,
                    tabela.schema,
                    compression=COMPRESSION,
                )

            writer.write_table(tabela)

            total_linhas += len(bronze)
            linha_inicial += len(bronze)

            print(
                f"[OK] Chunk {numero_chunk:02d} "
                f"— {len(bronze):,} linhas "
                f"— acumulado {total_linhas:,}"
            )

    finally:
        if writer is not None:
            writer.close()

    if total_linhas != LINHAS_BRONZE_ESPERADAS:
        raise RuntimeError(
            "\nQuantidade total de linhas Bronze diferente da esperada.\n"
            f"Esperado: {LINHAS_BRONZE_ESPERADAS:,}\n"
            f"Atual:    {total_linhas:,}"
        )

    return total_linhas


def validar_releitura(
    caminho_parquet,
    sha256_arquivo,
):
    parquet = pq.ParquetFile(
        caminho_parquet
    )

    if parquet.metadata.num_rows != LINHAS_BRONZE_ESPERADAS:
        raise RuntimeError(
            "\nQuantidade de linhas divergente após releitura do Parquet.\n"
            f"Esperado: {LINHAS_BRONZE_ESPERADAS:,}\n"
            f"Atual:    {parquet.metadata.num_rows:,}"
        )

    colunas_esperadas = [
        "_fonte",
        "_sha256_arquivo",
        "_arquivo_origem",
        "_aba_origem",
        "_ano_referencia",
        "_granularidade_origem",
        "_indice_cabecalho_origem",
        "_linha_origem",
        *nomes_colunas_bronze(),
    ]

    colunas_atuais = parquet.schema_arrow.names

    if colunas_atuais != colunas_esperadas:
        raise RuntimeError(
            "\nEsquema do Parquet diferente do esperado.\n"
            f"Esperado: {colunas_esperadas}\n"
            f"Atual:    {colunas_atuais}"
        )

    primeira_linha = pq.read_table(
        caminho_parquet,
        columns=[
            "_fonte",
            "_sha256_arquivo",
            "_arquivo_origem",
            "_ano_referencia",
            "_granularidade_origem",
            "_indice_cabecalho_origem",
            "_linha_origem",
            *nomes_colunas_bronze(),
        ],
    ).slice(0, 1).to_pydict()

    if primeira_linha["_fonte"][0] != FONTE:
        raise RuntimeError(
            "_fonte inválida após releitura."
        )

    if primeira_linha["_sha256_arquivo"][0] != sha256_arquivo:
        raise RuntimeError(
            "_sha256_arquivo inválido após releitura."
        )

    if primeira_linha["_arquivo_origem"][0] != ARQUIVO_RAW:
        raise RuntimeError(
            "_arquivo_origem inválido após releitura."
        )

    if primeira_linha["_ano_referencia"][0] != ANO_REFERENCIA:
        raise RuntimeError(
            "_ano_referencia inválido após releitura."
        )

    if (
        primeira_linha["_granularidade_origem"][0]
        != GRANULARIDADE
    ):
        raise RuntimeError(
            "_granularidade_origem inválida após releitura."
        )

    if (
        primeira_linha["_indice_cabecalho_origem"][0]
        != CABECALHO_INDICE
    ):
        raise RuntimeError(
            "_indice_cabecalho_origem inválido após releitura."
        )

    if primeira_linha["_linha_origem"][0] != 1:
        raise RuntimeError(
            "_linha_origem inicial inválida após releitura."
        )

    cabecalho_preservado = [
        primeira_linha[f"col_{indice:03d}"][0]
        for indice in range(
            1,
            QUANTIDADE_COLUNAS_FONTE + 1,
        )
    ]

    if cabecalho_preservado != COLUNAS_ESPERADAS:
        raise RuntimeError(
            "Cabeçalho preservado diferente do auditado após releitura."
        )


def main():
    print("=" * 110)
    print("CAMADA BRONZE — INGESTÃO DA PND 2025")
    print("=" * 110)
    print()

    caminho_raw = RAW_DIR / ARQUIVO_RAW
    destino = BRONZE_DIR / ARQUIVO_BRONZE
    temporario = BRONZE_DIR / f"{ARQUIVO_BRONZE}.tmp"

    BRONZE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if temporario.exists():
        temporario.unlink()

    sha256_arquivo = validar_raw(
        caminho_raw
    )

    validar_cabecalho(
        caminho_raw
    )

    print(f"Arquivo: {ARQUIVO_RAW}")
    print(f"Codificação: {ENCODING}")
    print(f"Delimitador: {SEP!r}")
    print(f"Colunas da fonte: {QUANTIDADE_COLUNAS_FONTE}")
    print(f"Registros de dados: {REGISTROS_DADOS_ESPERADOS:,}")
    print(
        "Linhas Bronze esperadas "
        "(incluindo o cabeçalho preservado): "
        f"{LINHAS_BRONZE_ESPERADAS:,}"
    )
    print(f"SHA-256: {sha256_arquivo}")
    print()

    total_linhas = escrever_parquet(
        caminho_raw=caminho_raw,
        caminho_temporario=temporario,
        sha256_arquivo=sha256_arquivo,
    )

    validar_releitura(
        caminho_parquet=temporario,
        sha256_arquivo=sha256_arquivo,
    )

    temporario.replace(destino)

    print()
    print("=" * 110)
    print("RESULTADO")
    print("=" * 110)
    print(f"Arquivo RAW: {ARQUIVO_RAW}")
    print(f"Arquivo Bronze: {destino}")
    print(f"Registros de dados: {REGISTROS_DADOS_ESPERADOS:,}")
    print(f"Linhas Bronze: {total_linhas:,}")
    print(f"Colunas da fonte: {QUANTIDADE_COLUNAS_FONTE}")
    print(f"Granularidade: {GRANULARIDADE}")
    print(f"SHA-256: {sha256_arquivo}")
    print()
    print("INGESTÃO DA PND 2025 CONCLUÍDA COM SUCESSO.")
    print("=" * 110)


if __name__ == "__main__":
    main()
