from pathlib import Path
import hashlib

import pandas as pd


RAW_FILE = Path(
    "data/raw/saeb/Resultados_Saeb_2023_Brasil_Estados_Municipios.xlsb"
)

BRONZE_DIR = Path("data/bronze/saeb")
OUTPUT_FILE = BRONZE_DIR / "saeb_2023_resultados_uf.parquet"

SHEET_NAME = "Estados"
ANO_REFERENCIA = 2023
INDICE_CABECALHO_ORIGEM = 0
GRANULARIDADE_ORIGEM = "UF"
FONTE = "INEP - Saeb 2023 - Resultados Brasil, Estados e Municípios"


def sha256_arquivo(caminho):
    hash_obj = hashlib.sha256()

    with caminho.open("rb") as arquivo:
        for bloco in iter(
            lambda: arquivo.read(1024 * 1024),
            b"",
        ):
            hash_obj.update(bloco)

    return hash_obj.hexdigest()


def ler_fonte():
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Arquivo RAW não encontrado: {RAW_FILE}"
        )

    try:
        return pd.read_excel(
            RAW_FILE,
            sheet_name=SHEET_NAME,
            header=None,
            engine="pyxlsb",
            dtype=object,
        )
    except ImportError as exc:
        raise RuntimeError(
            "O pacote pyxlsb é necessário. "
            "Instale com: python -m pip install pyxlsb"
        ) from exc


def renomear_colunas(df):
    quantidade = len(df.columns)

    nomes = [
        f"col_{indice:03d}"
        for indice in range(
            1,
            quantidade + 1,
        )
    ]

    resultado = df.copy()
    resultado.columns = nomes

    return resultado


def normalizar_celula_para_texto(valor):
    """
    Preserva o conteúdo lógico da célula em formato textual.

    Motivo:
    a aba 'Estados' contém na primeira linha os nomes técnicos
    das variáveis e, nas mesmas colunas, valores numéricos nas
    linhas seguintes. O Parquet/Arrow exige um tipo lógico
    homogêneo por coluna. A Bronze não deve inferir tipos
    analíticos nem remover a linha de cabeçalho; por isso,
    todas as colunas de origem são armazenadas como texto
    anulável. A tipagem numérica ocorre apenas na Silver.
    """
    if pd.isna(valor):
        return pd.NA

    return str(valor)


def normalizar_colunas_origem(df):
    resultado = df.copy()

    for coluna in resultado.columns:
        resultado[coluna] = (
            resultado[coluna]
            .map(normalizar_celula_para_texto)
            .astype("string")
        )

    return resultado


def adicionar_proveniencia(df, sha256):
    resultado = df.copy()

    resultado["_fonte"] = FONTE
    resultado["_sha256_arquivo"] = sha256
    resultado["_arquivo_origem"] = RAW_FILE.name
    resultado["_aba_origem"] = SHEET_NAME
    resultado["_ano_referencia"] = ANO_REFERENCIA
    resultado["_indice_cabecalho_origem"] = (
        INDICE_CABECALHO_ORIGEM
    )
    resultado["_linha_origem"] = range(
        1,
        len(resultado) + 1,
    )
    resultado["_granularidade_origem"] = (
        GRANULARIDADE_ORIGEM
    )

    return resultado


def validar_cabecalho_preservado(df):
    esperados = {
        "col_001": "ANO_SAEB",
        "col_002": "CO_UF",
        "col_003": "NO_UF",
        "col_004": "DEPENDENCIA_ADM",
        "col_005": "LOCALIZACAO",
        "col_006": "CAPITAL",
        "col_010": "MEDIA_5_LP",
        "col_011": "MEDIA_5_MT",
        "col_014": "MEDIA_9_LP",
        "col_015": "MEDIA_9_MT",
    }

    primeira = df.iloc[0]

    erros = []

    for coluna, esperado in esperados.items():
        atual = primeira[coluna]

        if pd.isna(atual):
            atual = ""
        else:
            atual = str(atual).strip()

        if atual != esperado:
            erros.append(
                f"{coluna}: esperado={esperado!r}; atual={atual!r}"
            )

    if erros:
        raise RuntimeError(
            "Cabeçalho da aba Estados diferente do esperado:\n"
            + "\n".join(erros)
        )


def main():
    print("=" * 110)
    print(
        "BRONZE SAEB 2023 — RESULTADOS OFICIAIS AGREGADOS DE UF"
    )
    print("=" * 110)
    print()
    print(
        "A ingestão preserva integralmente a aba 'Estados' do arquivo oficial."
    )
    print(
        "Nenhuma filtragem de rede, localização, etapa ou indicador é feita na Bronze."
    )
    print(
        "As colunas de origem são armazenadas como texto anulável para preservar "
        "cabeçalho e valores heterogêneos sem inferência analítica na Bronze."
    )
    print()

    bruto = ler_fonte()

    if bruto.empty:
        raise RuntimeError(
            "A aba Estados está vazia."
        )

    bronze = renomear_colunas(
        bruto
    )

    bronze = normalizar_colunas_origem(
        bronze
    )

    validar_cabecalho_preservado(
        bronze
    )

    sha = sha256_arquivo(
        RAW_FILE
    )

    bronze = adicionar_proveniencia(
        bronze,
        sha,
    )

    BRONZE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    bronze.to_parquet(
        OUTPUT_FILE,
        index=False,
        engine="pyarrow",
        compression="snappy",
    )

    releitura = pd.read_parquet(
        OUTPUT_FILE
    )

    if len(releitura) != len(bronze):
        raise RuntimeError(
            "Quantidade de linhas mudou após gravação do Parquet."
        )

    if list(releitura.columns) != list(bronze.columns):
        raise RuntimeError(
            "Esquema mudou após gravação do Parquet."
        )

    colunas_origem = [
        coluna
        for coluna in bronze.columns
        if coluna.startswith("col_")
    ]

    tipos_origem = sorted(
        {
            str(releitura[coluna].dtype)
            for coluna in colunas_origem
        }
    )

    print(f"Arquivo RAW: {RAW_FILE}")
    print(f"Aba: {SHEET_NAME}")
    print(f"SHA-256: {sha}")
    print(f"Linhas preservadas: {len(bronze):,}")
    print(
        f"Colunas de origem preservadas: {len(bruto.columns):,}"
    )
    print(
        f"Tipos Parquet das colunas de origem: {tipos_origem}"
    )
    print(
        f"_indice_cabecalho_origem: {INDICE_CABECALHO_ORIGEM}"
    )
    print(
        f"_linha_origem inicial: {int(bronze['_linha_origem'].min())}"
    )
    print(
        f"_linha_origem final: {int(bronze['_linha_origem'].max())}"
    )
    print(
        f"Granularidade de origem: {GRANULARIDADE_ORIGEM}"
    )
    print(f"Arquivo Bronze: {OUTPUT_FILE}")
    print()
    print(
        "BRONZE OFICIAL AGREGADA DO SAEB 2023 GERADA COM SUCESSO."
    )
    print("=" * 110)


if __name__ == "__main__":
    main()
