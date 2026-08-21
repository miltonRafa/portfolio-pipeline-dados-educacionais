from pathlib import Path
import hashlib
import re
import unicodedata

import pandas as pd


RAW_DIR = Path("data/raw/ideb")
BRONZE_DIR = Path("data/bronze/ideb")

ARQUIVO_ORIGEM = "divulgacao_regioes_ufs_ideb.xlsx"
PADRAO_OBSERVADO = re.compile(r"^VL_OBSERVADO_(\d{4})$")

CONFIG = {
    "AI": {
        "arquivo_bronze": "ideb_ai.parquet",
        "aba": "UF e Regiões (AI)",
    },
    "AF": {
        "arquivo_bronze": "ideb_af.parquet",
        "aba": "UF e Regiões (AF)",
    },
    "EM": {
        "arquivo_bronze": "ideb_em.parquet",
        "aba": "UF e Regiões (EM)",
    },
}

COLUNAS_TECNICAS = {
    "_fonte",
    "_sha256_arquivo",
    "_arquivo_origem",
    "_aba_origem",
    "_etapa_origem",
    "_ano_referencia",
    "_indice_cabecalho_origem",
    "_linha_origem",
}

UF_MAP = {
    "acre": "AC", "alagoas": "AL", "amapa": "AP", "amazonas": "AM",
    "bahia": "BA", "ceara": "CE", "distrito federal": "DF",
    "espirito santo": "ES", "goias": "GO", "maranhao": "MA",
    "mato grosso": "MT", "mato grosso do sul": "MS", "m. g. do sul": "MS",
    "minas gerais": "MG", "para": "PA", "paraiba": "PB", "parana": "PR",
    "pernambuco": "PE", "piaui": "PI", "rio de janeiro": "RJ",
    "rio grande do norte": "RN", "r. g. do norte": "RN",
    "rio grande do sul": "RS", "r. g. do sul": "RS", "rondonia": "RO",
    "roraima": "RR", "santa catarina": "SC", "sao paulo": "SP",
    "sergipe": "SE", "tocantins": "TO",
}

UFS = set(UF_MAP.values())


def normalizar(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )
    texto = re.sub(r"\s+", " ", texto)
    return texto.casefold()


def calcular_sha256(caminho):
    sha256 = hashlib.sha256()

    with caminho.open("rb") as arquivo:
        while bloco := arquivo.read(1024 * 1024):
            sha256.update(bloco)

    return sha256.hexdigest()


def colunas_fonte(df):
    return [
        coluna
        for coluna in df.columns
        if re.fullmatch(r"col_\d{3}", str(coluna))
    ]


def localizar_cabecalho_tecnico_raw(dados, etapa):
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
        raise RuntimeError(
            f"{etapa}: esperada uma única linha técnica com "
            f"VL_OBSERVADO_YYYY; encontradas {len(candidatos)}."
        )

    indice, observados = candidatos[0]
    anos = sorted(
        int(PADRAO_OBSERVADO.fullmatch(valor).group(1))
        for valor in observados
    )

    if not {2007, 2023}.issubset(anos):
        raise RuntimeError(
            f"{etapa}: anos observados obrigatórios ausentes: {anos}"
        )

    return indice, anos


def estrutura_raw(caminho_raw):
    excel = pd.ExcelFile(caminho_raw, engine="openpyxl")
    encontradas = excel.sheet_names
    esperadas = [config["aba"] for config in CONFIG.values()]
    ausentes = [aba for aba in esperadas if aba not in encontradas]

    if ausentes:
        raise RuntimeError(
            f"Abas IDEB ausentes no RAW: {ausentes}; encontradas={encontradas}"
        )

    estrutura = {}

    for etapa, config in CONFIG.items():
        dados = pd.read_excel(
            caminho_raw,
            sheet_name=config["aba"],
            header=None,
            engine="openpyxl",
            dtype=object,
        )
        dados_sem_vazias = dados.dropna(axis=0, how="all")
        indice, anos = localizar_cabecalho_tecnico_raw(dados, etapa)
        estrutura[etapa] = {
            "linhas": len(dados_sem_vazias),
            "colunas_fonte": len(dados.columns),
            "indice_cabecalho": indice,
            "ano_referencia": max(anos),
            "anos_observados": anos,
        }

    return estrutura


def registrar_erro(erros, etapa, mensagem):
    erros.append(f"{etapa}: {mensagem}")


def validar_etapa(etapa, configuracao, esperado, hash_raw, erros):
    caminho_bronze = BRONZE_DIR / configuracao["arquivo_bronze"]

    print()
    print(f"ETAPA {etapa}")
    print("-" * 100)

    if not caminho_bronze.exists():
        registrar_erro(erros, etapa, "arquivo Parquet ausente")
        print("[ERRO] Arquivo Parquet ausente")
        return

    try:
        dados = pd.read_parquet(caminho_bronze, engine="pyarrow")
    except Exception as erro:
        registrar_erro(erros, etapa, f"falha ao ler Parquet: {erro}")
        print("[ERRO] Falha ao ler Parquet")
        return

    if dados.empty:
        registrar_erro(erros, etapa, "Parquet vazio")

    if len(dados) != esperado["linhas"]:
        registrar_erro(
            erros,
            etapa,
            "quantidade de linhas divergente: "
            f"esperado={esperado['linhas']}, encontrado={len(dados)}",
        )

    faltantes = COLUNAS_TECNICAS - set(dados.columns)
    if faltantes:
        registrar_erro(erros, etapa, f"colunas técnicas ausentes: {sorted(faltantes)}")
        print("[ERRO] Colunas técnicas ausentes")
        return

    if set(dados["_fonte"].dropna().unique()) != {"IDEB"}:
        registrar_erro(erros, etapa, "_fonte inválida")

    if set(dados["_arquivo_origem"].dropna().unique()) != {ARQUIVO_ORIGEM}:
        registrar_erro(erros, etapa, "_arquivo_origem divergente")

    if set(dados["_aba_origem"].dropna().unique()) != {configuracao["aba"]}:
        registrar_erro(erros, etapa, "_aba_origem divergente")

    if set(dados["_etapa_origem"].dropna().unique()) != {etapa}:
        registrar_erro(erros, etapa, "_etapa_origem divergente")

    if set(dados["_ano_referencia"].dropna().unique()) != {esperado["ano_referencia"]}:
        registrar_erro(erros, etapa, "_ano_referencia divergente")

    if set(dados["_indice_cabecalho_origem"].dropna().unique()) != {esperado["indice_cabecalho"]}:
        registrar_erro(erros, etapa, "_indice_cabecalho_origem divergente")

    if set(dados["_sha256_arquivo"].dropna().unique()) != {hash_raw}:
        registrar_erro(erros, etapa, "SHA-256 divergente")

    if dados["_linha_origem"].isna().any():
        registrar_erro(erros, etapa, "_linha_origem possui valores ausentes")

    if dados["_linha_origem"].duplicated().any():
        registrar_erro(erros, etapa, "_linha_origem possui duplicidades")

    if not dados["_linha_origem"].is_monotonic_increasing:
        registrar_erro(erros, etapa, "_linha_origem não está em ordem crescente")

    cols = colunas_fonte(dados)
    if len(cols) != esperado["colunas_fonte"]:
        registrar_erro(
            erros,
            etapa,
            "quantidade de colunas da fonte divergente: "
            f"esperado={esperado['colunas_fonte']}, encontrado={len(cols)}",
        )

    colunas_esperadas = [
        f"col_{indice:03d}"
        for indice in range(1, len(cols) + 1)
    ]
    if cols != colunas_esperadas:
        registrar_erro(erros, etapa, "sequência das colunas técnicas inválida")

    linha_origem_tecnica = esperado["indice_cabecalho"] + 1
    linha_tecnica = dados[dados["_linha_origem"] == linha_origem_tecnica]

    if len(linha_tecnica) != 1:
        registrar_erro(erros, etapa, "linha técnica original não encontrada")
    else:
        linha = linha_tecnica.iloc[0]
        anos_detectados = sorted(
            int(PADRAO_OBSERVADO.fullmatch(str(linha[coluna]).strip()).group(1))
            for coluna in cols
            if PADRAO_OBSERVADO.fullmatch(str(linha[coluna]).strip())
        )
        if anos_detectados != esperado["anos_observados"]:
            registrar_erro(
                erros,
                etapa,
                "anos VL_OBSERVADO_YYYY divergentes: "
                f"esperado={esperado['anos_observados']}, encontrado={anos_detectados}",
            )

    if etapa in {"AI", "AF"}:
        trabalho = dados.copy()
        trabalho["_UF"] = trabalho["col_001"].map(lambda valor: UF_MAP.get(normalizar(valor)))
        trabalho["_REDE"] = trabalho["col_002"].map(normalizar)
        publicas = trabalho[
            trabalho["_UF"].notna()
            & (trabalho["_REDE"] == "publica (4)")
        ]
        encontradas = set(publicas["_UF"])
        if len(publicas) != 27 or encontradas != UFS or publicas["_UF"].duplicated().any():
            registrar_erro(
                erros,
                etapa,
                "recorte público por UF inválido: "
                f"linhas={len(publicas)}, faltantes={sorted(UFS - encontradas)}, "
                f"extras={sorted(encontradas - UFS)}",
            )

    erros_etapa = [erro for erro in erros if erro.startswith(f"{etapa}:")]

    print(f"Linhas: {len(dados):,}")
    print(f"Colunas da fonte: {len(cols)}")
    print(f"Aba: {configuracao['aba']!r}")
    print("Anos observados: " + ", ".join(str(ano) for ano in esperado["anos_observados"]))
    print("SHA-256: " + ("OK" if set(dados["_sha256_arquivo"].dropna().unique()) == {hash_raw} else "ERRO"))

    if not erros_etapa:
        print("Status: OK")
    else:
        print("Status: ERRO")
        for erro in erros_etapa:
            print(f"     {erro}")


def main():
    print("=" * 110)
    print("VALIDAÇÃO FINAL — BRONZE IDEB")
    print("=" * 110)

    caminho_raw = RAW_DIR / ARQUIVO_ORIGEM
    if not caminho_raw.exists():
        raise FileNotFoundError(f"Arquivo RAW ausente: {caminho_raw}")

    hash_raw = calcular_sha256(caminho_raw)
    estrutura = estrutura_raw(caminho_raw)
    erros = []

    for etapa, configuracao in CONFIG.items():
        validar_etapa(
            etapa=etapa,
            configuracao=configuracao,
            esperado=estrutura[etapa],
            hash_raw=hash_raw,
            erros=erros,
        )

    parquets = sorted(BRONZE_DIR.glob("ideb_*.parquet"))
    nomes_encontrados = {arquivo.name for arquivo in parquets}
    nomes_esperados = {configuracao["arquivo_bronze"] for configuracao in CONFIG.values()}

    if nomes_encontrados != nomes_esperados:
        erros.append(
            "GERAL: conjunto de Parquets diferente do esperado. "
            f"Esperados={sorted(nomes_esperados)}; "
            f"Encontrados={sorted(nomes_encontrados)}"
        )

    print()
    print("=" * 110)
    print("RESUMO")
    print("=" * 110)
    print()
    print(f"Parquets encontrados: {len(parquets)}")
    print(f"Parquets esperados: {len(CONFIG)}")
    print(f"SHA-256 RAW: {hash_raw}")

    if erros:
        print()
        print("ERROS ENCONTRADOS:")
        for erro in erros:
            print(f"- {erro}")
        raise RuntimeError("\nValidação da Bronze do IDEB falhou.")

    print()
    print("TODAS AS 3 ABAS FORAM VALIDADAS.")
    print("BRONZE DO IDEB: OK")


if __name__ == "__main__":
    main()
