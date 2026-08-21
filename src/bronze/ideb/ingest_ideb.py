from pathlib import Path
import hashlib
import re

import pandas as pd


RAW_DIR = Path("data/raw/ideb")
BRONZE_DIR = Path("data/bronze/ideb")

ARQUIVO_ORIGEM = "divulgacao_regioes_ufs_ideb.xlsx"

PADRAO_OBSERVADO = re.compile(r"^VL_OBSERVADO_(\d{4})$")

CONFIG_ABAS = {
    "AI": {
        "aba": "UF e Regiões (AI)",
    },
    "AF": {
        "aba": "UF e Regiões (AF)",
    },
    "EM": {
        "aba": "UF e Regiões (EM)",
    },
}


def calcular_sha256(caminho):
    sha256 = hashlib.sha256()

    with caminho.open("rb") as arquivo:
        while bloco := arquivo.read(1024 * 1024):
            sha256.update(bloco)

    return sha256.hexdigest()


def validar_arquivo(caminho):
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo RAW não encontrado: {caminho}"
        )

    if not caminho.is_file():
        raise RuntimeError(
            f"O caminho RAW não representa um arquivo: {caminho}"
        )


def validar_abas(caminho):
    excel = pd.ExcelFile(
        caminho,
        engine="openpyxl",
    )

    abas_encontradas = excel.sheet_names

    abas_esperadas = [
        configuracao["aba"]
        for configuracao in CONFIG_ABAS.values()
    ]

    abas_ausentes = [
        aba
        for aba in abas_esperadas
        if aba not in abas_encontradas
    ]

    if abas_ausentes:
        raise RuntimeError(
            "\nAbas obrigatórias do IDEB ausentes.\n"
            f"Esperadas: {abas_esperadas}\n"
            f"Ausentes: {abas_ausentes}\n"
            f"Encontradas: {abas_encontradas}"
        )

    return abas_encontradas


def localizar_cabecalho_tecnico(
    dados,
    aba,
):
    if dados.empty:
        raise RuntimeError(
            f"A aba {aba!r} está vazia."
        )

    candidatos = []

    for indice, linha in dados.iterrows():
        valores = (
            linha
            .dropna()
            .astype(str)
            .str.strip()
            .tolist()
        )

        observados = [
            valor
            for valor in valores
            if PADRAO_OBSERVADO.fullmatch(valor)
        ]

        if observados:
            candidatos.append((indice, observados))

    if len(candidatos) != 1:
        resumo = [
            {
                "indice": indice,
                "quantidade_vl_observado": len(observados),
                "primeiro": observados[0] if observados else None,
                "ultimo": observados[-1] if observados else None,
            }
            for indice, observados in candidatos
        ]

        raise RuntimeError(
            f"A aba {aba!r} deveria possuir exatamente uma linha "
            "com variáveis VL_OBSERVADO_YYYY. "
            f"Encontradas: {resumo}"
        )

    cabecalho_indice, observados = candidatos[0]
    anos_observados = sorted(
        {
            int(PADRAO_OBSERVADO.fullmatch(valor).group(1))
            for valor in observados
        }
    )

    marcadores_obrigatorios = [
        "VL_OBSERVADO_2007",
        "VL_OBSERVADO_2023",
    ]

    for marcador in marcadores_obrigatorios:
        if marcador not in observados:
            raise RuntimeError(
                f"A aba {aba!r} não contém o marcador "
                f"técnico esperado {marcador!r}."
            )

    return cabecalho_indice, anos_observados


def preparar_bronze(
    dados,
    arquivo_origem,
    aba,
    etapa,
    sha256_arquivo,
    cabecalho_indice,
    ano_referencia,
):
    quantidade_colunas_fonte = len(dados.columns)

    # Remove apenas linhas completamente vazias.
    dados = dados.dropna(
        axis=0,
        how="all",
    ).copy()

    # Preserva a posição original da linha na planilha.
    dados["_linha_origem"] = (
        dados.index + 1
    )

    # Nomes técnicos neutros para as colunas da planilha.
    dados.columns = [
        *[
            f"col_{indice:03d}"
            for indice in range(
                1,
                quantidade_colunas_fonte + 1,
            )
        ],
        "_linha_origem",
    ]

    # As células da fonte são armazenadas como texto,
    # preservando a estrutura heterogênea do workbook.
    colunas_fonte = [
        coluna
        for coluna in dados.columns
        if coluna.startswith("col_")
    ]

    for coluna in colunas_fonte:
        dados[coluna] = (
            dados[coluna]
            .astype("string")
        )

    # Metadados de rastreabilidade.
    dados.insert(
        0,
        "_fonte",
        "IDEB",
    )

    dados.insert(
        1,
        "_sha256_arquivo",
        sha256_arquivo,
    )

    dados.insert(
        2,
        "_arquivo_origem",
        arquivo_origem,
    )

    dados.insert(
        3,
        "_aba_origem",
        aba,
    )

    dados.insert(
        4,
        "_etapa_origem",
        etapa,
    )

    dados.insert(
        5,
        "_ano_referencia",
        ano_referencia,
    )

    dados.insert(
        6,
        "_indice_cabecalho_origem",
        cabecalho_indice,
    )

    return dados


def validar_parquet(
    caminho,
    linhas_esperadas,
    colunas_fonte_esperadas,
):
    if not caminho.exists():
        raise RuntimeError(
            f"Parquet não foi criado: {caminho}"
        )

    dados = pd.read_parquet(
        caminho,
        engine="pyarrow",
    )

    if dados.empty:
        raise RuntimeError(
            f"Parquet criado, mas vazio: {caminho}"
        )

    if len(dados) != linhas_esperadas:
        raise RuntimeError(
            f"Quantidade de linhas divergente em {caminho}.\n"
            f"Esperado: {linhas_esperadas}\n"
            f"Encontrado: {len(dados)}"
        )

    colunas_fonte = [
        coluna
        for coluna in dados.columns
        if coluna.startswith("col_")
    ]

    if len(colunas_fonte) != colunas_fonte_esperadas:
        raise RuntimeError(
            f"Quantidade de colunas da fonte divergente em "
            f"{caminho}.\n"
            f"Esperado: {colunas_fonte_esperadas}\n"
            f"Encontrado: {len(colunas_fonte)}"
        )


def processar_aba(
    caminho_raw,
    etapa,
    configuracao,
    sha256_arquivo,
):
    aba = configuracao["aba"]

    dados = pd.read_excel(
        caminho_raw,
        sheet_name=aba,
        header=None,
        engine="openpyxl",
        dtype=object,
    )

    cabecalho_indice, anos_observados = localizar_cabecalho_tecnico(
        dados=dados,
        aba=aba,
    )

    quantidade_colunas_fonte = len(
        dados.columns
    )

    bronze = preparar_bronze(
        dados=dados,
        arquivo_origem=ARQUIVO_ORIGEM,
        aba=aba,
        etapa=etapa,
        sha256_arquivo=sha256_arquivo,
        cabecalho_indice=cabecalho_indice,
        ano_referencia=max(anos_observados),
    )

    destino = (
        BRONZE_DIR
        / f"ideb_{etapa.lower()}.parquet"
    )

    bronze.to_parquet(
        destino,
        engine="pyarrow",
        compression="snappy",
        index=False,
    )

    validar_parquet(
        caminho=destino,
        linhas_esperadas=len(bronze),
        colunas_fonte_esperadas=quantidade_colunas_fonte,
    )

    print(
        f"[OK] IDEB — {etapa}"
    )
    print(
        f"     Arquivo: {ARQUIVO_ORIGEM}"
    )
    print(
        f"     Aba: {aba}"
    )
    print(
        f"     Linhas Bronze: {len(bronze):,}"
    )
    print(
        "     Colunas fonte: "
        f"{quantidade_colunas_fonte}"
    )
    print(
        f"     Destino: {destino}"
    )
    print()


def main():
    print("=" * 100)
    print(
        "CAMADA BRONZE — INGESTÃO DO IDEB"
    )
    print("=" * 100)
    print()

    caminho_raw = (
        RAW_DIR / ARQUIVO_ORIGEM
    )

    validar_arquivo(caminho_raw)

    BRONZE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    abas = validar_abas(
        caminho_raw
    )

    sha256_arquivo = calcular_sha256(
        caminho_raw
    )

    print(
        f"Arquivo RAW: {ARQUIVO_ORIGEM}"
    )
    print(
        f"SHA-256: {sha256_arquivo}"
    )
    print(
        f"Abas confirmadas: {len(abas)}"
    )
    print()

    for etapa, configuracao in CONFIG_ABAS.items():
        processar_aba(
            caminho_raw=caminho_raw,
            etapa=etapa,
            configuracao=configuracao,
            sha256_arquivo=sha256_arquivo,
        )

    parquets = sorted(
        BRONZE_DIR.glob(
            "ideb_*.parquet"
        )
    )

    if len(parquets) != 3:
        raise RuntimeError(
            "Quantidade de arquivos Bronze do IDEB "
            f"divergente. Esperados: 3. "
            f"Encontrados: {len(parquets)}."
        )

    print("=" * 100)
    print(
        "ARQUIVOS PROCESSADOS: 3"
    )
    print(
        "ARQUIVOS ESPERADOS: 3"
    )
    print(
        "INGESTÃO DO IDEB CONCLUÍDA COM SUCESSO."
    )
    print("=" * 100)


if __name__ == "__main__":
    main()
