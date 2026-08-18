from pathlib import Path
import unicodedata

import pandas as pd


BRONZE_DIR = Path("data/bronze/tdi")

ANOS = list(range(2007, 2024))

CONFIG = {
    **{
        ano: {
            "uf": "col_003",
            "localizacao": "col_004",
            "rede": "col_005",
        }
        for ano in range(2007, 2015)
    },
    2015: {
        "uf": "col_004",
        "localizacao": "col_005",
        "rede": "col_006",
    },
    2016: {
        "uf": "col_003",
        "localizacao": "col_004",
        "rede": "col_005",
    },
    **{
        ano: {
            "uf": "col_002",
            "localizacao": "col_003",
            "rede": "col_004",
        }
        for ano in range(2017, 2024)
    },
}


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

    return texto.casefold()


def categorias_ordenadas(serie):
    valores = {
        str(valor).strip()
        for valor in serie.dropna()
        if str(valor).strip()
    }

    return sorted(
        valores,
        key=lambda valor: normalizar(valor),
    )


def main():
    print("=" * 120)
    print("VERIFICAÇÃO FOCADA — EXISTÊNCIA DE AGREGADO PÚBLICO NA TDI")
    print("=" * 120)
    print()

    if set(CONFIG) != set(ANOS):
        raise RuntimeError(
            "CONFIG não corresponde exatamente a 2007–2023."
        )

    sem_publico = []

    for ano in ANOS:
        caminho = BRONZE_DIR / f"tdi_{ano}.parquet"

        if not caminho.exists():
            raise FileNotFoundError(
                f"Bronze ausente: {caminho}"
            )

        df = pd.read_parquet(caminho)
        config = CONFIG[ano]

        obrigatorias = {
            "col_001",
            config["uf"],
            config["localizacao"],
            config["rede"],
        }

        faltantes = sorted(
            obrigatorias.difference(df.columns)
        )

        if faltantes:
            raise RuntimeError(
                f"TDI {ano}: colunas ausentes: {faltantes}"
            )

        # Mantém somente registros de dados do próprio ano,
        # excluindo cabeçalhos, notas e linhas estruturais.
        dados = df[
            df["col_001"].map(normalizar) == str(ano)
        ].copy()

        if dados.empty:
            raise RuntimeError(
                f"TDI {ano}: nenhum registro de dados localizado."
            )

        categorias_rede = categorias_ordenadas(
            dados[config["rede"]]
        )
        categorias_localizacao = categorias_ordenadas(
            dados[config["localizacao"]]
        )

        rede_normalizada = dados[config["rede"]].map(normalizar)
        localizacao_normalizada = dados[
            config["localizacao"]
        ].map(normalizar)

        mascara_publico = rede_normalizada.isin(
            {"publico", "publica"}
        )
        mascara_total = rede_normalizada.eq("total")
        mascara_privada = rede_normalizada.isin(
            {"privada", "particular"}
        )

        publico_total = dados[
            mascara_publico
            & localizacao_normalizada.eq("total")
        ]

        total_total = dados[
            mascara_total
            & localizacao_normalizada.eq("total")
        ]

        privada_total = dados[
            mascara_privada
            & localizacao_normalizada.eq("total")
        ]

        existe_publico = bool(mascara_publico.any())

        if not existe_publico:
            sem_publico.append(ano)

        print(f"TDI {ano}")
        print(
            "  Categorias de rede: "
            + " | ".join(categorias_rede)
        )
        print(
            "  Categorias de localização: "
            + " | ".join(categorias_localizacao)
        )
        print(
            "  Agregado explícito Público/Pública: "
            + ("SIM" if existe_publico else "NÃO")
        )
        print(
            "  Linhas Público/Pública + Localização Total: "
            f"{len(publico_total)}"
        )
        print(
            "  Linhas Rede Total + Localização Total: "
            f"{len(total_total)}"
        )
        print(
            "  Linhas Privada/Particular + Localização Total: "
            f"{len(privada_total)}"
        )
        print()

    print("=" * 120)
    print("RESUMO")
    print("=" * 120)

    if sem_publico:
        intervalos = ", ".join(str(ano) for ano in sem_publico)
        print(
            "Anos sem agregado explícito Público/Pública: "
            f"{intervalos}"
        )
    else:
        print(
            "Todos os anos possuem agregado explícito Público/Pública."
        )

    print()
    print(
        "IMPORTANTE: este script somente verifica categorias existentes "
        "na Bronze. Nenhum arquivo foi alterado."
    )
    print("=" * 120)


if __name__ == "__main__":
    main()
