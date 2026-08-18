from pathlib import Path
import hashlib
import unicodedata

import pandas as pd


RAW_DIR = Path("data/raw/rendimento")
BRONZE_DIR = Path("data/bronze/rendimento")


CONFIG = {
    2007: {
        "arquivo": "TX RENDIMENTO UFS 2007.xls",
        "aba": "REND. POR UF",
        "cabecalho_indice": 6,
    },
    2008: {
        "arquivo": "TAXAS RENDIMENTO UF 2008.xls",
        "aba": "Rendimento por UF - 2009",
        "cabecalho_indice": 6,
    },
    2009: {
        "arquivo": "TAXAS RENDIMENTO UF 2009.xls",
        "aba": "Rendimento por UF - 2009",
        "cabecalho_indice": 6,
    },
    2010: {
        "arquivo": "TAXAS RENDIMENTO UF 2010.xls",
        "aba": "RENDIMENTOS UFS 2010",
        "cabecalho_indice": 6,
    },
    2011: {
        "arquivo": "tx_rendimento_uf_2011.xls",
        "aba": "RENDIMENTOS UFS 2011",
        "cabecalho_indice": 6,
    },
    2012: {
        "arquivo": "tx_rendimento_UFs_2012.xlsx",
        "aba": "UF 2012",
        "cabecalho_indice": 6,
    },
    2013: {
        "arquivo": "TAXAS RENDIMENTOS UF 2013.xlsx",
        "aba": "UF 2013",
        "cabecalho_indice": 6,
    },
    2014: {
        "arquivo": "TAXAS RENDIMENTOS UF 2014.xlsx",
        "aba": "UF ",
        "cabecalho_indice": 6,
    },
    2015: {
        "arquivo": "TX_REND_UFS_2015.xlsx",
        "aba": "UF ",
        "cabecalho_indice": 6,
    },
    2016: {
        "arquivo": "TX_REND_UFS_2016.xlsx",
        "aba": "UF ",
        "cabecalho_indice": 5,
    },
    2017: {
        "arquivo": "TX_REND_BRASIL_REGIOES_UFS_2017.xlsx",
        "aba": "BRASIL_REGIOES_UFS ",
        "cabecalho_indice": 5,
    },
    2018: {
        "arquivo": "TX_REND_BRASIL_REGIOES_UFS_2018.xlsx",
        "aba": "BRASIL_REGIOES_UFS ",
        "cabecalho_indice": 5,
    },
    2019: {
        "arquivo": "tx_rend_brasil_regioes_ufs_2019.xlsx",
        "aba": "BRASIL_REGIOES_UFS ",
        "cabecalho_indice": 5,
    },
    2020: {
        "arquivo": "tx_rend_brasil_regioes_ufs_2020.xlsx",
        "aba": "BRASIL_REGIOES_UFS ",
        "cabecalho_indice": 5,
    },
    2021: {
        "arquivo": "tx_rend_brasil_regioes_ufs_2021.xlsx",
        "aba": "BRASIL_REGIOES_UFS ",
        "cabecalho_indice": 5,
    },
    2022: {
        "arquivo": "tx_rend_brasil_regioes_ufs_2022.xlsx",
        "aba": "BRASIL_REGIOES_UFS ",
        "cabecalho_indice": 5,
    },
    2023: {
        "arquivo": "tx_rend_brasil_regioes_ufs_2023.xlsx",
        "aba": "BRASIL_REGIOES_UFS ",
        "cabecalho_indice": 5,
    },
}


def normalizar_texto(valor):
    texto = str(valor)

    texto = unicodedata.normalize(
        "NFKD",
        texto,
    )

    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )

    return texto.lower().strip()


def calcular_sha256(caminho):
    sha256 = hashlib.sha256()

    with caminho.open("rb") as arquivo:
        while bloco := arquivo.read(1024 * 1024):
            sha256.update(bloco)

    return sha256.hexdigest()


def engine_excel(caminho):
    if caminho.suffix.lower() == ".xls":
        return "xlrd"

    if caminho.suffix.lower() == ".xlsx":
        return "openpyxl"

    raise ValueError(
        f"Extensão não suportada: {caminho.suffix}"
    )


def validar_arquivo(ano, caminho):
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado para {ano}: "
            f"{caminho}"
        )

    if caminho.stat().st_size == 0:
        raise ValueError(
            f"Arquivo vazio para {ano}: "
            f"{caminho}"
        )


def validar_aba(caminho, aba, engine):
    excel = pd.ExcelFile(
        caminho,
        engine=engine,
    )

    if aba not in excel.sheet_names:
        raise ValueError(
            "\nAba esperada não encontrada.\n"
            f"Arquivo: {caminho.name}\n"
            f"Esperada: {aba}\n"
            f"Encontradas: {excel.sheet_names}"
        )


def validar_cabecalho(
    dados,
    ano,
    indice_cabecalho,
):
    if indice_cabecalho >= len(dados):
        raise ValueError(
            f"Índice de cabeçalho inválido em {ano}: "
            f"{indice_cabecalho}"
        )

    linha = dados.iloc[
        indice_cabecalho
    ]

    valores = [
        normalizar_texto(valor)
        for valor in linha.tolist()
        if pd.notna(valor)
    ]

    texto = " | ".join(valores)

    if "ano" not in valores:
        raise ValueError(
            "\nCabeçalho esperado não reconhecido.\n"
            f"Ano: {ano}\n"
            f"Índice auditado: {indice_cabecalho}\n"
            f"Conteúdo encontrado:\n{texto}"
        )

    possui_rede = (
        "rede" in texto
        or "dependencia administrativa" in texto
    )

    if not possui_rede:
        raise ValueError(
            "\nCampo de rede/dependência não reconhecido "
            "no cabeçalho.\n"
            f"Ano: {ano}\n"
            f"Conteúdo encontrado:\n{texto}"
        )


def validar_ano_na_planilha(
    dados,
    ano,
):
    limite = min(
        15,
        len(dados),
    )

    valores = (
        dados
        .iloc[:limite]
        .astype("string")
        .stack()
        .tolist()
    )

    texto = " ".join(
        str(valor)
        for valor in valores
    )

    if str(ano) not in texto:
        raise ValueError(
            "\nAno esperado não encontrado "
            "no início da planilha.\n"
            f"Ano esperado: {ano}"
        )


def preparar_bronze(
    dados,
    ano,
    arquivo_origem,
    aba_origem,
    indice_cabecalho,
    sha256,
):
    # Guarda o número da linha original
    # antes de remover linhas vazias.
    dados = dados.copy()

    dados["_linha_origem_temp"] = (
        dados.index + 1
    )

    # Única remoção estrutural nesta etapa:
    # linhas em que todas as células da
    # planilha estão realmente vazias.
    colunas_origem = [
        coluna
        for coluna in dados.columns
        if coluna != "_linha_origem_temp"
    ]

    mascara_vazia = (
        dados[colunas_origem]
        .isna()
        .all(axis=1)
    )

    dados = dados[
        ~mascara_vazia
    ].copy()

    linhas_origem = (
        dados["_linha_origem_temp"]
        .astype("int64")
    )

    dados = dados.drop(
        columns=["_linha_origem_temp"]
    )

    # A Bronze não atribui significado
    # semântico às colunas.
    dados.columns = [
        f"col_{indice:03d}"
        for indice in range(
            1,
            len(dados.columns) + 1,
        )
    ]

    # Planilhas possuem textos, títulos,
    # códigos e números nas mesmas colunas.
    # A tipagem analítica ficará para Silver.
    for coluna in dados.columns:
        dados[coluna] = (
            dados[coluna]
            .astype("string")
        )

    dados.insert(
        0,
        "_linha_origem",
        linhas_origem.values,
    )

    dados.insert(
        0,
        "_indice_cabecalho_origem",
        indice_cabecalho,
    )

    dados.insert(
        0,
        "_ano_referencia",
        ano,
    )

    dados.insert(
        0,
        "_aba_origem",
        aba_origem,
    )

    dados.insert(
        0,
        "_arquivo_origem",
        arquivo_origem,
    )

    dados.insert(
        0,
        "_sha256_arquivo",
        sha256,
    )

    dados.insert(
        0,
        "_fonte",
        "RENDIMENTO",
    )

    return dados


def validar_parquet(
    destino,
    esperado,
    ano,
):
    if not destino.exists():
        raise RuntimeError(
            f"Parquet não foi criado: {destino}"
        )

    leitura = pd.read_parquet(
        destino,
        engine="pyarrow",
    )

    if len(leitura) != len(esperado):
        raise RuntimeError(
            "\nQuantidade de linhas divergente "
            "após gravação.\n"
            f"Ano: {ano}\n"
            f"Antes: {len(esperado):,}\n"
            f"Depois: {len(leitura):,}"
        )

    if list(leitura.columns) != list(
        esperado.columns
    ):
        raise RuntimeError(
            f"Colunas divergentes após gravação "
            f"do ano {ano}."
        )

    if leitura.empty:
        raise RuntimeError(
            f"Parquet vazio para o ano {ano}."
        )


def processar_ano(
    ano,
    configuracao,
):
    caminho = (
        RAW_DIR
        / configuracao["arquivo"]
    )

    aba = configuracao["aba"]

    indice_cabecalho = (
        configuracao[
            "cabecalho_indice"
        ]
    )

    validar_arquivo(
        ano,
        caminho,
    )

    engine = engine_excel(
        caminho
    )

    validar_aba(
        caminho,
        aba,
        engine,
    )

    dados_raw = pd.read_excel(
        caminho,
        sheet_name=aba,
        header=None,
        engine=engine,
    )

    if dados_raw.empty:
        raise ValueError(
            f"Planilha vazia para {ano}."
        )

    validar_cabecalho(
        dados_raw,
        ano,
        indice_cabecalho,
    )

    validar_ano_na_planilha(
        dados_raw,
        ano,
    )

    sha256 = calcular_sha256(
        caminho
    )

    bronze = preparar_bronze(
        dados=dados_raw,
        ano=ano,
        arquivo_origem=caminho.name,
        aba_origem=aba,
        indice_cabecalho=indice_cabecalho,
        sha256=sha256,
    )

    destino = (
        BRONZE_DIR
        / f"rendimento_{ano}.parquet"
    )

    bronze.to_parquet(
        destino,
        engine="pyarrow",
        compression="snappy",
        index=False,
    )

    validar_parquet(
        destino,
        bronze,
        ano,
    )

    print(
        f"[OK] Rendimento {ano}"
    )

    print(
        f"     Arquivo: "
        f"{caminho.name}"
    )

    print(
        f"     Aba: {aba}"
    )

    print(
        f"     Linhas Bronze: "
        f"{len(bronze):,}"
    )

    print(
        f"     Colunas fonte: "
        f"{len(dados_raw.columns):,}"
    )

    print(
        f"     Destino: {destino}"
    )

    print()


def main():
    print("=" * 100)
    print(
        "CAMADA BRONZE — "
        "INGESTÃO DO RENDIMENTO ESCOLAR"
    )
    print("=" * 100)
    print()

    BRONZE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    processados = 0

    for ano in sorted(CONFIG):
        processar_ano(
            ano,
            CONFIG[ano],
        )

        processados += 1

    print("=" * 100)

    print(
        f"ARQUIVOS PROCESSADOS: "
        f"{processados}"
    )

    print(
        f"ARQUIVOS ESPERADOS: "
        f"{len(CONFIG)}"
    )

    if processados != len(CONFIG):
        raise RuntimeError(
            "Quantidade final de arquivos "
            "processados é inválida."
        )

    print(
        "INGESTÃO DO RENDIMENTO "
        "CONCLUÍDA COM SUCESSO."
    )

    print("=" * 100)


if __name__ == "__main__":
    main()