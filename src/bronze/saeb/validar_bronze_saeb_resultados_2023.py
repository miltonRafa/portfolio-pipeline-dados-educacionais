from pathlib import Path
import hashlib

import pandas as pd


RAW_FILE = Path(
    "data/raw/saeb/Resultados_Saeb_2023_Brasil_Estados_Municipios.xlsb"
)

BRONZE_FILE = Path(
    "data/bronze/saeb/saeb_2023_resultados_uf.parquet"
)

SHEET_NAME = "Estados"

UF_CODIGOS = {
    11, 12, 13, 14, 15, 16, 17,
    21, 22, 23, 24, 25, 26, 27, 28, 29,
    31, 32, 33, 35,
    41, 42, 43,
    50, 51, 52, 53,
}


def sha256_arquivo(caminho):
    hash_obj = hashlib.sha256()

    with caminho.open("rb") as arquivo:
        for bloco in iter(
            lambda: arquivo.read(1024 * 1024),
            b"",
        ):
            hash_obj.update(bloco)

    return hash_obj.hexdigest()


def normalizar_celula_para_texto(valor):
    if pd.isna(valor):
        return pd.NA

    return str(valor)


def numero(valor):
    if pd.isna(valor):
        return None

    texto = str(valor).strip()

    if texto in {"", "-", "--"}:
        return None

    texto = texto.replace(",", ".")

    try:
        return float(texto)
    except ValueError:
        return None


def carregar_raw():
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"RAW ausente: {RAW_FILE}"
        )

    return pd.read_excel(
        RAW_FILE,
        sheet_name=SHEET_NAME,
        header=None,
        engine="pyxlsb",
        dtype=object,
    )


def normalizar_raw(raw):
    """
    Reproduz exatamente a regra usada na ingestão Bronze:
    células preenchidas viram texto e células realmente vazias
    permanecem ausentes.

    A normalização é feita coluna a coluna, mas a comparação final
    é vetorizada. Isso evita o acesso célula a célula com iloc,
    que é desnecessariamente lento em Pandas.
    """
    resultado = raw.copy()

    for coluna in resultado.columns:
        resultado[coluna] = (
            resultado[coluna]
            .map(normalizar_celula_para_texto)
            .astype("string")
        )

    resultado.columns = [
        f"col_{indice:03d}"
        for indice in range(
            1,
            len(resultado.columns) + 1,
        )
    ]

    return resultado


def validar_reproducao_integral(raw, bronze):
    raw_normalizado = normalizar_raw(
        raw
    )

    source_cols = list(
        raw_normalizado.columns
    )

    bronze_origem = bronze[
        source_cols
    ].copy()

    if len(bronze_origem) != len(raw_normalizado):
        raise RuntimeError(
            "Quantidade de linhas diferente entre RAW e Bronze."
        )

    if list(bronze_origem.columns) != source_cols:
        raise RuntimeError(
            "Ordem das colunas de origem diferente entre RAW e Bronze."
        )

    # Padroniza os tipos antes da comparação.
    for coluna in source_cols:
        bronze_origem[coluna] = (
            bronze_origem[coluna]
            .astype("string")
        )

    marcador_ausencia = "__AUSENTE_SAEB_2023__"

    esperado = (
        raw_normalizado
        .fillna(marcador_ausencia)
    )

    atual = (
        bronze_origem
        .fillna(marcador_ausencia)
    )

    mascara_igualdade = esperado.eq(
        atual
    )

    total_celulas = (
        len(esperado)
        * len(source_cols)
    )

    total_iguais = int(
        mascara_igualdade
        .to_numpy()
        .sum()
    )

    if total_iguais != total_celulas:
        divergencias = []

        linhas, colunas = (
            ~mascara_igualdade
        ).to_numpy().nonzero()

        for i, j in zip(
            linhas[:20],
            colunas[:20],
        ):
            coluna = source_cols[j]

            divergencias.append(
                (
                    int(i) + 1,
                    coluna,
                    esperado.iloc[i, j],
                    atual.iloc[i, j],
                )
            )

        texto = "\n".join(
            (
                f"linha={linha} | coluna={coluna} | "
                f"RAW_normalizado={raw_val!r} | "
                f"Bronze={bronze_val!r}"
            )
            for (
                linha,
                coluna,
                raw_val,
                bronze_val,
            ) in divergencias
        )

        raise RuntimeError(
            "Foram encontradas divergências RAW → Bronze:\n"
            + texto
        )

    return total_celulas


def validar_proveniencia(bronze, sha):
    regras = {
        "_sha256_arquivo": sha,
        "_arquivo_origem": RAW_FILE.name,
        "_aba_origem": SHEET_NAME,
        "_ano_referencia": 2023,
        "_indice_cabecalho_origem": 0,
        "_granularidade_origem": "UF",
    }

    for coluna, esperado in regras.items():
        valores = set(
            bronze[coluna]
            .dropna()
            .tolist()
        )

        if valores != {esperado}:
            raise RuntimeError(
                f"Proveniência inválida em {coluna}: {valores}"
            )

    esperado_linhas = list(
        range(
            1,
            len(bronze) + 1,
        )
    )

    atual_linhas = (
        bronze["_linha_origem"]
        .astype(int)
        .tolist()
    )

    if atual_linhas != esperado_linhas:
        raise RuntimeError(
            "_linha_origem não reproduz a sequência física da fonte."
        )


def validar_colunas_origem_textuais(bronze):
    colunas = [
        coluna
        for coluna in bronze.columns
        if str(coluna).startswith("col_")
    ]

    invalidas = []

    for coluna in colunas:
        serie = bronze[
            coluna
        ].dropna()

        if not serie.map(
            lambda valor: isinstance(
                valor,
                str,
            )
        ).all():
            invalidas.append(
                coluna
            )

    if invalidas:
        raise RuntimeError(
            "Há colunas de origem com valores não textuais: "
            + ", ".join(invalidas)
        )

    return len(colunas)


def validar_estrato_publico(bronze):
    header = bronze.iloc[0]

    mapa = {
        str(header[coluna]).strip(): coluna
        for coluna in bronze.columns
        if str(coluna).startswith("col_")
        and not pd.isna(header[coluna])
    }

    obrigatorias = {
        "ANO_SAEB",
        "CO_UF",
        "NO_UF",
        "DEPENDENCIA_ADM",
        "LOCALIZACAO",
        "CAPITAL",
        "MEDIA_5_LP",
        "MEDIA_5_MT",
        "MEDIA_9_LP",
        "MEDIA_9_MT",
    }

    faltantes = sorted(
        obrigatorias.difference(mapa)
    )

    if faltantes:
        raise RuntimeError(
            f"Variáveis oficiais ausentes: {faltantes}"
        )

    dados = bronze.iloc[1:].copy()

    alvo = dados[
        (
            dados[mapa["ANO_SAEB"]]
            .astype(str)
            .str.strip()
            == "2023"
        )
        & (
            dados[mapa["DEPENDENCIA_ADM"]]
            .astype(str)
            .str.strip()
            == "Total - Federal, Estadual e Municipal"
        )
        & (
            dados[mapa["LOCALIZACAO"]]
            .astype(str)
            .str.strip()
            == "Total"
        )
        & (
            dados[mapa["CAPITAL"]]
            .astype(str)
            .str.strip()
            == "Total"
        )
    ].copy()

    alvo["_CO_UF"] = (
        alvo[mapa["CO_UF"]]
        .map(numero)
        .map(
            lambda x: int(x)
            if x is not None
            else None
        )
    )

    codigos = set(
        alvo["_CO_UF"].dropna()
    )

    if len(alvo) != 27:
        raise RuntimeError(
            f"Estrato público oficial deveria ter 27 linhas; atual={len(alvo)}."
        )

    if codigos != UF_CODIGOS:
        raise RuntimeError(
            "Conjunto de UFs do estrato público oficial é diferente das 27 UFs."
        )

    if alvo["_CO_UF"].duplicated().any():
        raise RuntimeError(
            "Há UF duplicada no estrato público oficial."
        )

    metricas = [
        "MEDIA_5_LP",
        "MEDIA_5_MT",
        "MEDIA_9_LP",
        "MEDIA_9_MT",
    ]

    resumo = {}

    for metrica in metricas:
        serie = alvo[
            mapa[metrica]
        ].map(numero)

        ausentes = int(
            serie.isna().sum()
        )

        if ausentes:
            raise RuntimeError(
                f"{metrica}: {ausentes} valores ausentes no estrato oficial."
            )

        resumo[metrica] = {
            "min": float(serie.min()),
            "max": float(serie.max()),
        }

    return resumo


def main():
    print("=" * 110)
    print(
        "VALIDAÇÃO BRONZE — SAEB 2023 RESULTADOS OFICIAIS AGREGADOS DE UF"
    )
    print("=" * 110)
    print()

    if not BRONZE_FILE.exists():
        raise FileNotFoundError(
            f"Bronze ausente: {BRONZE_FILE}"
        )

    print("1/5 Lendo RAW oficial...")
    raw = carregar_raw()

    print("2/5 Lendo Bronze...")
    bronze = pd.read_parquet(
        BRONZE_FILE
    )

    print("3/5 Validando proveniência e tipagem...")
    sha = sha256_arquivo(
        RAW_FILE
    )

    validar_proveniencia(
        bronze,
        sha,
    )

    quantidade_colunas_texto = (
        validar_colunas_origem_textuais(
            bronze
        )
    )

    print("4/5 Comparando RAW ↔ Bronze de forma vetorizada...")
    celulas = validar_reproducao_integral(
        raw,
        bronze,
    )

    print("5/5 Validando o estrato público oficial de UF...")
    resumo = validar_estrato_publico(
        bronze
    )

    print()
    print(f"RAW: {RAW_FILE}")
    print(f"Bronze: {BRONZE_FILE}")
    print(f"SHA-256: {sha}")
    print(f"Linhas RAW/Bronze: {len(raw):,}")
    print(
        f"Colunas de origem RAW/Bronze: {len(raw.columns):,}"
    )
    print(
        f"Colunas de origem textuais validadas: {quantidade_colunas_texto:,}"
    )
    print(
        f"Células de origem comparadas RAW ↔ Bronze: {celulas:,}"
    )
    print(
        "Reprodução integral do conteúdo da aba Estados após normalização textual: OK"
    )
    print(
        "Proveniência arquivo/aba/linha/cabeçalho/granularidade: OK"
    )
    print(
        "Estrato oficial público/Total/Total: 27 UFs, sem duplicidade"
    )

    for metrica, valores in resumo.items():
        print(
            f"{metrica}: "
            f"mín={valores['min']:.2f} | "
            f"máx={valores['max']:.2f}"
        )

    print()
    print(
        "BRONZE SAEB 2023 RESULTADOS OFICIAIS DE UF: OK"
    )
    print("=" * 110)


if __name__ == "__main__":
    main()
