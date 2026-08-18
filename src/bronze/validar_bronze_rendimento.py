from pathlib import Path
import hashlib

import pandas as pd


RAW_DIR = Path("data/raw/rendimento")
BRONZE_DIR = Path("data/bronze/rendimento")


ARQUIVOS_ORIGEM = {
    2007: "TX RENDIMENTO UFS 2007.xls",
    2008: "TAXAS RENDIMENTO UF 2008.xls",
    2009: "TAXAS RENDIMENTO UF 2009.xls",
    2010: "TAXAS RENDIMENTO UF 2010.xls",
    2011: "tx_rendimento_uf_2011.xls",
    2012: "tx_rendimento_UFs_2012.xlsx",
    2013: "TAXAS RENDIMENTOS UF 2013.xlsx",
    2014: "TAXAS RENDIMENTOS UF 2014.xlsx",
    2015: "TX_REND_UFS_2015.xlsx",
    2016: "TX_REND_UFS_2016.xlsx",
    2017: "TX_REND_BRASIL_REGIOES_UFS_2017.xlsx",
    2018: "TX_REND_BRASIL_REGIOES_UFS_2018.xlsx",
    2019: "tx_rend_brasil_regioes_ufs_2019.xlsx",
    2020: "tx_rend_brasil_regioes_ufs_2020.xlsx",
    2021: "tx_rend_brasil_regioes_ufs_2021.xlsx",
    2022: "tx_rend_brasil_regioes_ufs_2022.xlsx",
    2023: "tx_rend_brasil_regioes_ufs_2023.xlsx",
}


COLUNAS_TECNICAS = {
    "_fonte",
    "_sha256_arquivo",
    "_arquivo_origem",
    "_aba_origem",
    "_ano_referencia",
    "_indice_cabecalho_origem",
    "_linha_origem",
}


def sha256(caminho):
    hash_arquivo = hashlib.sha256()

    with caminho.open("rb") as arquivo:
        while bloco := arquivo.read(1024 * 1024):
            hash_arquivo.update(bloco)

    return hash_arquivo.hexdigest()


print("=" * 110)
print("VALIDAÇÃO FINAL — BRONZE RENDIMENTO ESCOLAR")
print("=" * 110)


erros = []
total_linhas = 0


for ano, arquivo_origem in ARQUIVOS_ORIGEM.items():

    origem = RAW_DIR / arquivo_origem

    parquet = (
        BRONZE_DIR
        / f"rendimento_{ano}.parquet"
    )

    print(f"\nANO {ano}")
    print("-" * 80)

    # -----------------------------------------------------
    # EXISTÊNCIA
    # -----------------------------------------------------

    if not origem.exists():
        erros.append(
            f"{ano}: arquivo RAW ausente"
        )

        print("[ERRO] RAW ausente")
        continue

    if not parquet.exists():
        erros.append(
            f"{ano}: arquivo Bronze ausente"
        )

        print("[ERRO] Parquet ausente")
        continue

    # -----------------------------------------------------
    # LEITURA
    # -----------------------------------------------------

    dados = pd.read_parquet(
        parquet,
        engine="pyarrow",
    )

    if dados.empty:
        erros.append(
            f"{ano}: Parquet vazio"
        )

    total_linhas += len(dados)

    # -----------------------------------------------------
    # COLUNAS TÉCNICAS
    # -----------------------------------------------------

    faltantes = (
        COLUNAS_TECNICAS
        - set(dados.columns)
    )

    if faltantes:
        erros.append(
            f"{ano}: colunas técnicas ausentes "
            f"{sorted(faltantes)}"
        )

    # -----------------------------------------------------
    # FONTE
    # -----------------------------------------------------

    fontes = set(
        dados["_fonte"]
        .dropna()
        .unique()
    )

    if fontes != {"RENDIMENTO"}:
        erros.append(
            f"{ano}: _fonte inválida {fontes}"
        )

    # -----------------------------------------------------
    # ANO
    # -----------------------------------------------------

    anos = set(
        dados["_ano_referencia"]
        .dropna()
        .unique()
    )

    if anos != {ano}:
        erros.append(
            f"{ano}: _ano_referencia inválido "
            f"{anos}"
        )

    # -----------------------------------------------------
    # ARQUIVO DE ORIGEM
    # -----------------------------------------------------

    arquivos = set(
        dados["_arquivo_origem"]
        .dropna()
        .unique()
    )

    if arquivos != {arquivo_origem}:
        erros.append(
            f"{ano}: arquivo de origem divergente "
            f"{arquivos}"
        )

    # -----------------------------------------------------
    # HASH
    # -----------------------------------------------------

    hash_raw = sha256(origem)

    hashes_bronze = set(
        dados["_sha256_arquivo"]
        .dropna()
        .unique()
    )

    if hashes_bronze != {hash_raw}:
        erros.append(
            f"{ano}: SHA-256 divergente"
        )

    # -----------------------------------------------------
    # LINHA DE ORIGEM
    # -----------------------------------------------------

    if dados["_linha_origem"].isna().any():
        erros.append(
            f"{ano}: _linha_origem possui nulos"
        )

    if dados["_linha_origem"].duplicated().any():
        erros.append(
            f"{ano}: _linha_origem duplicada"
        )

    # -----------------------------------------------------
    # COLUNAS DA FONTE
    # -----------------------------------------------------

    colunas_fonte = [
        coluna
        for coluna in dados.columns
        if coluna.startswith("col_")
    ]

    if not colunas_fonte:
        erros.append(
            f"{ano}: nenhuma coluna de origem"
        )

    # -----------------------------------------------------
    # RESULTADO
    # -----------------------------------------------------

    print(
        f"Linhas: {len(dados):,}"
    )

    print(
        f"Colunas da fonte: "
        f"{len(colunas_fonte)}"
    )

    print(
        f"Aba: "
        f"{dados['_aba_origem'].iloc[0]!r}"
    )

    print(
        f"SHA-256: OK"
        if hashes_bronze == {hash_raw}
        else "SHA-256: ERRO"
    )

    if not any(
        erro.startswith(f"{ano}:")
        for erro in erros
    ):
        print("Status: OK")
    else:
        print("Status: ERRO")


print("\n" + "=" * 110)
print("RESUMO")
print("=" * 110)

parquets = list(
    BRONZE_DIR.glob(
        "rendimento_*.parquet"
    )
)

print(
    f"\nParquets encontrados: "
    f"{len(parquets)}"
)

print(
    f"Parquets esperados: "
    f"{len(ARQUIVOS_ORIGEM)}"
)

print(
    f"Total de linhas Bronze: "
    f"{total_linhas:,}"
)


if len(parquets) != len(
    ARQUIVOS_ORIGEM
):
    erros.append(
        "Quantidade total de Parquets "
        "é diferente de 17"
    )


if erros:

    print("\nERROS ENCONTRADOS:")

    for erro in erros:
        print(f"- {erro}")

    raise RuntimeError(
        "\nValidação da Bronze "
        "do Rendimento falhou."
    )


print(
    "\nTODOS OS 17 ARQUIVOS "
    "FORAM VALIDADOS."
)

print(
    "BRONZE DO RENDIMENTO: OK"
)