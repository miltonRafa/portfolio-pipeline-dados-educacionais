from pathlib import Path
import hashlib

import pyarrow.parquet as pq


RAW_DIR = Path("data/raw/pnd")
BRONZE_DIR = Path("data/bronze/pnd")

ARQUIVO_RAW = "microdados2025_pnd_arq1.txt"
ARQUIVO_BRONZE = "pnd_2025.parquet"

FONTE = "PND"
ANO_REFERENCIA = 2025
GRANULARIDADE = "REGISTRO_INDIVIDUAL"

SHA256_ESPERADO = (
    "b15968a19e309bca6b63c6f6d7af094efdc13d900645dc7385872a6a50dd7baf"
)

LINHAS_FISICAS_ESPERADAS = 1_087_360
REGISTROS_DADOS_ESPERADOS = 1_087_359
LINHAS_BRONZE_ESPERADAS = 1_087_360

CABECALHO_INDICE = 0

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


def nomes_colunas_fonte():
    return [
        f"col_{indice:03d}"
        for indice in range(
            1,
            len(COLUNAS_ESPERADAS) + 1,
        )
    ]


def validar_raw(caminho):
    if not caminho.exists():
        raise RuntimeError(
            f"RAW ausente: {caminho}"
        )

    sha256_atual, linhas_fisicas = calcular_sha256_e_linhas(
        caminho
    )

    if sha256_atual != SHA256_ESPERADO:
        raise RuntimeError(
            "\nSHA-256 do RAW diferente do esperado.\n"
            f"Esperado: {SHA256_ESPERADO}\n"
            f"Atual:    {sha256_atual}"
        )

    if linhas_fisicas != LINHAS_FISICAS_ESPERADAS:
        raise RuntimeError(
            "\nQuantidade de linhas físicas do RAW diferente do esperado.\n"
            f"Esperado: {LINHAS_FISICAS_ESPERADAS:,}\n"
            f"Atual:    {linhas_fisicas:,}"
        )


def validar_esquema(parquet):
    colunas_esperadas = [
        "_fonte",
        "_sha256_arquivo",
        "_arquivo_origem",
        "_aba_origem",
        "_ano_referencia",
        "_granularidade_origem",
        "_indice_cabecalho_origem",
        "_linha_origem",
        *nomes_colunas_fonte(),
    ]

    encontradas = parquet.schema_arrow.names

    if encontradas != colunas_esperadas:
        raise RuntimeError(
            "\nEsquema do Parquet diferente do esperado.\n"
            f"Esperado: {colunas_esperadas}\n"
            f"Atual:    {encontradas}"
        )


def validar_primeira_linha(parquet):
    colunas = [
        "_fonte",
        "_sha256_arquivo",
        "_arquivo_origem",
        "_aba_origem",
        "_ano_referencia",
        "_granularidade_origem",
        "_indice_cabecalho_origem",
        "_linha_origem",
        *nomes_colunas_fonte(),
    ]

    lote = next(
        parquet.iter_batches(
            batch_size=1,
            columns=colunas,
        )
    )

    dados = lote.to_pydict()

    if dados["_fonte"][0] != FONTE:
        raise RuntimeError(
            "_fonte inválida."
        )

    if dados["_sha256_arquivo"][0] != SHA256_ESPERADO:
        raise RuntimeError(
            "_sha256_arquivo inválido."
        )

    if dados["_arquivo_origem"][0] != ARQUIVO_RAW:
        raise RuntimeError(
            "_arquivo_origem inválido."
        )

    if dados["_aba_origem"][0] is not None:
        raise RuntimeError(
            "_aba_origem deve ser ausente para o TXT."
        )

    if dados["_ano_referencia"][0] != ANO_REFERENCIA:
        raise RuntimeError(
            "_ano_referencia inválido."
        )

    if (
        dados["_granularidade_origem"][0]
        != GRANULARIDADE
    ):
        raise RuntimeError(
            "_granularidade_origem inválida."
        )

    if (
        dados["_indice_cabecalho_origem"][0]
        != CABECALHO_INDICE
    ):
        raise RuntimeError(
            "_indice_cabecalho_origem inválido."
        )

    if dados["_linha_origem"][0] != 1:
        raise RuntimeError(
            "_linha_origem inicial inválida."
        )

    cabecalho = [
        dados[f"col_{indice:03d}"][0]
        for indice in range(
            1,
            len(COLUNAS_ESPERADAS) + 1,
        )
    ]

    if cabecalho != COLUNAS_ESPERADAS:
        raise RuntimeError(
            "\nCabeçalho preservado na Bronze diferente do auditado.\n"
            f"Esperado: {COLUNAS_ESPERADAS}\n"
            f"Atual:    {cabecalho}"
        )


def validar_metadados_e_linhas(parquet):
    esperado_linha = 1
    total = 0

    colunas = [
        "_fonte",
        "_sha256_arquivo",
        "_arquivo_origem",
        "_aba_origem",
        "_ano_referencia",
        "_granularidade_origem",
        "_indice_cabecalho_origem",
        "_linha_origem",
    ]

    for lote in parquet.iter_batches(
        batch_size=100_000,
        columns=colunas,
    ):
        dados = lote.to_pydict()
        quantidade = lote.num_rows

        if set(dados["_fonte"]) != {FONTE}:
            raise RuntimeError(
                "_fonte inconsistente em lote do Parquet."
            )

        if set(dados["_sha256_arquivo"]) != {SHA256_ESPERADO}:
            raise RuntimeError(
                "_sha256_arquivo inconsistente em lote do Parquet."
            )

        if set(dados["_arquivo_origem"]) != {ARQUIVO_RAW}:
            raise RuntimeError(
                "_arquivo_origem inconsistente em lote do Parquet."
            )

        if any(
            valor is not None
            for valor in dados["_aba_origem"]
        ):
            raise RuntimeError(
                "_aba_origem deve permanecer ausente para o TXT."
            )

        if set(dados["_ano_referencia"]) != {ANO_REFERENCIA}:
            raise RuntimeError(
                "_ano_referencia inconsistente em lote do Parquet."
            )

        if set(
            dados["_granularidade_origem"]
        ) != {GRANULARIDADE}:
            raise RuntimeError(
                "_granularidade_origem inconsistente em lote do Parquet."
            )

        if set(
            dados["_indice_cabecalho_origem"]
        ) != {CABECALHO_INDICE}:
            raise RuntimeError(
                "_indice_cabecalho_origem inconsistente em lote do Parquet."
            )

        linhas = dados["_linha_origem"]

        if not linhas:
            raise RuntimeError(
                "Lote vazio encontrado durante a validação."
            )

        if linhas[0] != esperado_linha:
            raise RuntimeError(
                "\nQuebra na sequência de _linha_origem.\n"
                f"Esperado no início do lote: {esperado_linha}\n"
                f"Atual: {linhas[0]}"
            )

        for anterior, atual in zip(
            linhas,
            linhas[1:],
        ):
            if atual != anterior + 1:
                raise RuntimeError(
                    "\n_linha_origem não é contígua.\n"
                    f"Anterior: {anterior}\n"
                    f"Atual:    {atual}"
                )

        esperado_linha = linhas[-1] + 1
        total += quantidade

    if total != LINHAS_BRONZE_ESPERADAS:
        raise RuntimeError(
            "\nTotal percorrido no Parquet diferente do esperado.\n"
            f"Esperado: {LINHAS_BRONZE_ESPERADAS:,}\n"
            f"Atual:    {total:,}"
        )

    if esperado_linha - 1 != LINHAS_BRONZE_ESPERADAS:
        raise RuntimeError(
            "\nÚltima _linha_origem diferente do esperado.\n"
            f"Esperado: {LINHAS_BRONZE_ESPERADAS:,}\n"
            f"Atual:    {esperado_linha - 1:,}"
        )


def main():
    print("=" * 110)
    print("VALIDAÇÃO FINAL — BRONZE PND 2025")
    print("=" * 110)
    print()

    caminho_raw = RAW_DIR / ARQUIVO_RAW
    caminho_parquet = BRONZE_DIR / ARQUIVO_BRONZE

    validar_raw(
        caminho_raw
    )

    if not caminho_parquet.exists():
        raise RuntimeError(
            f"Parquet ausente: {caminho_parquet}"
        )

    parquet = pq.ParquetFile(
        caminho_parquet
    )

    if parquet.metadata.num_rows != LINHAS_BRONZE_ESPERADAS:
        raise RuntimeError(
            "\nQuantidade de linhas do Parquet diferente do esperado.\n"
            f"Esperado: {LINHAS_BRONZE_ESPERADAS:,}\n"
            f"Atual:    {parquet.metadata.num_rows:,}"
        )

    validar_esquema(
        parquet
    )

    validar_primeira_linha(
        parquet
    )

    validar_metadados_e_linhas(
        parquet
    )

    print(f"Arquivo RAW: {ARQUIVO_RAW}")
    print(f"Arquivo Bronze: {ARQUIVO_BRONZE}")
    print(f"Registros de dados: {REGISTROS_DADOS_ESPERADOS:,}")
    print(
        "Linhas Bronze "
        "(incluindo o cabeçalho preservado): "
        f"{LINHAS_BRONZE_ESPERADAS:,}"
    )
    print(f"Colunas da fonte: {len(COLUNAS_ESPERADAS)}")
    print(f"Granularidade: {GRANULARIDADE}")
    print("SHA-256: OK")
    print("Cabeçalho preservado: OK")
    print("_linha_origem contígua: OK")
    print("Metadados de rastreabilidade: OK")
    print()
    print("BRONZE DA PND 2025: OK")
    print("=" * 110)


if __name__ == "__main__":
    main()
