from pathlib import Path
import pandas as pd


ARQUIVO = Path(
    "data/raw/pnd/microdados2025_pnd_arq1.txt"
)

COLUNAS = [
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


contagens = {}
total = 0
com_resultado = 0
sem_resultado = 0

inconsistencias_notas = 0


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

    total += len(chunk)

    campos_resultado = [
        "PROFICIENCIA",
        "NT_OBJ",
        "NT_DIS",
        "NT_GER",
        "QT_ACERTOS",
    ]

    preenchidos = chunk[campos_resultado].notna()

    todos_preenchidos = preenchidos.all(axis=1)
    todos_ausentes = (~preenchidos).all(axis=1)

    com_resultado += todos_preenchidos.sum()
    sem_resultado += todos_ausentes.sum()

    inconsistencias_notas += (
        ~(todos_preenchidos | todos_ausentes)
    ).sum()

    chunk["_TEM_RESULTADO"] = todos_preenchidos

    agrupado = (
        chunk.groupby(
            [
                "TP_INSCRICAO_PND",
                "IN_REAPLICACAO",
                "CO_CADERNO",
                "TP_PRES",
                "TP_SIT_DISC",
                "_TEM_RESULTADO",
            ],
            dropna=False
        )
        .size()
    )

    for chave, quantidade in agrupado.items():
        contagens[chave] = (
            contagens.get(chave, 0)
            + int(quantidade)
        )


print("=" * 120)
print("AUDITORIA DA POPULAÇÃO — PND 2025")
print("=" * 120)

print(f"\nTOTAL DE REGISTROS: {total:,}")
print(f"COM TODOS OS RESULTADOS: {com_resultado:,}")
print(f"COM TODOS AUSENTES: {sem_resultado:,}")
print(
    f"RESULTADOS PARCIALMENTE PREENCHIDOS: "
    f"{inconsistencias_notas:,}"
)


resultado = pd.DataFrame(
    [
        {
            "TP_INSCRICAO_PND": chave[0],
            "IN_REAPLICACAO": chave[1],
            "CO_CADERNO": chave[2],
            "TP_PRES": chave[3],
            "TP_SIT_DISC": chave[4],
            "TEM_RESULTADO": chave[5],
            "REGISTROS": quantidade,
        }
        for chave, quantidade in contagens.items()
    ]
)


resultado = resultado.sort_values(
    [
        "TEM_RESULTADO",
        "TP_PRES",
        "TP_SIT_DISC",
        "TP_INSCRICAO_PND",
        "IN_REAPLICACAO",
        "CO_CADERNO",
    ],
    ascending=[
        False,
        True,
        True,
        True,
        True,
        True,
    ]
)


print("\n" + "=" * 120)
print("COMBINAÇÕES DOS CÓDIGOS")
print("=" * 120)

print(
    resultado.to_string(
        index=False
    )
)


print("\n" + "=" * 120)
print("RESUMO POR TP_PRES × TP_SIT_DISC × RESULTADO")
print("=" * 120)

resumo = (
    resultado.groupby(
        [
            "TP_PRES",
            "TP_SIT_DISC",
            "TEM_RESULTADO",
        ],
        as_index=False
    )["REGISTROS"]
    .sum()
)

print(
    resumo.to_string(
        index=False
    )
)