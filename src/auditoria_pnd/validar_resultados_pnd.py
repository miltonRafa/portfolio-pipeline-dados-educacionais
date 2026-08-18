from pathlib import Path
import pandas as pd


ARQUIVO = Path(
    "data/raw/pnd/microdados2025_pnd_arq1.txt"
)

COLUNAS = [
    "CO_GRUPO",
    "SG_UF_MUNICIPIO_PROVA",
    "TP_INSCRICAO_PND",
    "IN_REAPLICACAO",
    "CO_CADERNO",
    "TP_PRES",
    "TP_SIT_DISC",
    "PROFICIENCIA",
    "NT_OBJ",
    "NT_DIS",
    "NT_GER",
    "QT_ACERTOS",
]


total_validos = 0

ausentes = {
    "PROFICIENCIA": 0,
    "NT_OBJ": 0,
    "NT_DIS": 0,
    "NT_GER": 0,
    "QT_ACERTOS": 0,
}

fora_faixa = {
    "PROFICIENCIA": 0,
    "NT_OBJ": 0,
    "NT_DIS": 0,
    "NT_GER": 0,
    "QT_ACERTOS": 0,
}

formula_divergente = 0

situacoes_disc = {}
tipos_inscricao = {}
reaplicacao = {}
cadernos = {}
ufs = {}
grupos = {}


for chunk in pd.read_csv(
    ARQUIVO,
    sep=";",
    decimal=",",
    na_values=["NA"],
    usecols=COLUNAS,
    chunksize=100_000,
    low_memory=False,
    encoding="utf-8"
):

    # =====================================================
    # POPULAÇÃO ANALÍTICA OFICIAL
    # =====================================================

    dados = chunk[
        chunk["TP_PRES"] == 555
    ].copy()

    total_validos += len(dados)

    # =====================================================
    # AUSÊNCIAS
    # =====================================================

    for coluna in ausentes:

        ausentes[coluna] += int(
            dados[coluna].isna().sum()
        )

    # =====================================================
    # FAIXAS DEFINIDAS PELO DICIONÁRIO
    # =====================================================

    fora_faixa["PROFICIENCIA"] += int(
        (
            dados["PROFICIENCIA"].notna()
            &
            ~dados["PROFICIENCIA"].between(
                -9.999,
                9.999
            )
        ).sum()
    )

    fora_faixa["NT_OBJ"] += int(
        (
            dados["NT_OBJ"].notna()
            &
            ~dados["NT_OBJ"].between(
                0,
                100
            )
        ).sum()
    )

    fora_faixa["NT_DIS"] += int(
        (
            dados["NT_DIS"].notna()
            &
            ~dados["NT_DIS"].between(
                0,
                10
            )
        ).sum()
    )

    fora_faixa["NT_GER"] += int(
        (
            dados["NT_GER"].notna()
            &
            ~dados["NT_GER"].between(
                0,
                100
            )
        ).sum()
    )

    fora_faixa["QT_ACERTOS"] += int(
        (
            dados["QT_ACERTOS"].notna()
            &
            ~dados["QT_ACERTOS"].between(
                0,
                80
            )
        ).sum()
    )

    # =====================================================
    # VALIDAÇÃO DA FÓRMULA DA NOTA GERAL
    #
    # Dicionário:
    # NT_GER = NT_OBJ * 0.8 + 2 * NT_DIS
    #
    # tolerância por arredondamento
    # =====================================================

    calculada = (
        dados["NT_OBJ"] * 0.8
        +
        dados["NT_DIS"] * 2
    )

    diferenca = (
        dados["NT_GER"]
        -
        calculada
    ).abs()

    formula_divergente += int(
        (diferenca > 0.11).sum()
    )

    # =====================================================
    # CONTAGENS CATEGÓRICAS
    # =====================================================

    for valor, quantidade in (
        dados["TP_SIT_DISC"]
        .value_counts(dropna=False)
        .items()
    ):

        situacoes_disc[valor] = (
            situacoes_disc.get(valor, 0)
            +
            int(quantidade)
        )

    for valor, quantidade in (
        dados["TP_INSCRICAO_PND"]
        .value_counts(dropna=False)
        .items()
    ):

        tipos_inscricao[valor] = (
            tipos_inscricao.get(valor, 0)
            +
            int(quantidade)
        )

    for valor, quantidade in (
        dados["IN_REAPLICACAO"]
        .value_counts(dropna=False)
        .items()
    ):

        reaplicacao[valor] = (
            reaplicacao.get(valor, 0)
            +
            int(quantidade)
        )

    for valor, quantidade in (
        dados["CO_CADERNO"]
        .value_counts(dropna=False)
        .items()
    ):

        cadernos[valor] = (
            cadernos.get(valor, 0)
            +
            int(quantidade)
        )

    for valor, quantidade in (
        dados["SG_UF_MUNICIPIO_PROVA"]
        .value_counts(dropna=False)
        .items()
    ):

        ufs[valor] = (
            ufs.get(valor, 0)
            +
            int(quantidade)
        )

    for valor, quantidade in (
        dados["CO_GRUPO"]
        .value_counts(dropna=False)
        .items()
    ):

        grupos[valor] = (
            grupos.get(valor, 0)
            +
            int(quantidade)
        )


# =========================================================
# RESULTADO
# =========================================================

print("=" * 110)
print("VALIDAÇÃO DA POPULAÇÃO ANALÍTICA — PND 2025")
print("=" * 110)

print(
    f"\nPARTICIPANTES COM RESULTADO VÁLIDO: "
    f"{total_validos:,}"
)

print("\nVALORES AUSENTES:")

for coluna, quantidade in ausentes.items():
    print(
        f"{coluna}: {quantidade:,}"
    )


print("\nVALORES FORA DA FAIXA DO DICIONÁRIO:")

for coluna, quantidade in fora_faixa.items():
    print(
        f"{coluna}: {quantidade:,}"
    )


print(
    "\nDIVERGÊNCIAS NA FÓRMULA DA NT_GER "
    "(tolerância 0,11):"
)

print(f"{formula_divergente:,}")


print("\nTP_SIT_DISC:")

for chave in sorted(
    situacoes_disc,
    key=str
):
    print(
        f"{chave}: "
        f"{situacoes_disc[chave]:,}"
    )


print("\nTP_INSCRICAO_PND:")

for chave in sorted(
    tipos_inscricao,
    key=str
):
    print(
        f"{chave}: "
        f"{tipos_inscricao[chave]:,}"
    )


print("\nIN_REAPLICACAO:")

for chave in sorted(
    reaplicacao,
    key=str
):
    print(
        f"{chave}: "
        f"{reaplicacao[chave]:,}"
    )


print("\nCO_CADERNO:")

for chave in sorted(
    cadernos,
    key=str
):
    print(
        f"{chave}: "
        f"{cadernos[chave]:,}"
    )


print(
    f"\nUFs: {len(ufs)}"
)

for chave in sorted(
    ufs,
    key=str
):
    print(
        f"{chave}: "
        f"{ufs[chave]:,}"
    )


print(
    f"\nGRUPOS: {len(grupos)}"
)

for chave in sorted(
    grupos,
    key=str
):
    print(
        f"{chave}: "
        f"{grupos[chave]:,}"
    )