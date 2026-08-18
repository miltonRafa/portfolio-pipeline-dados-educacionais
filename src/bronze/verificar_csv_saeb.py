from pathlib import Path


RAW_DIR = Path("data/raw/saeb")

ARQUIVOS = [
    "TS_RESULTADO_UF_2011.csv",
    "TS_ESCOLA_2023.csv",
]

CODIFICACOES = [
    "utf-8",
    "utf-8-sig",
    "cp1252",
    "latin1",
]


def testar_arquivo(caminho):
    print("=" * 100)
    print(f"ARQUIVO: {caminho.name}")
    print("=" * 100)

    bytes_iniciais = caminho.read_bytes()[:20000]

    codificacao_valida = None
    texto = None

    for codificacao in CODIFICACOES:
        try:
            texto = bytes_iniciais.decode(codificacao)
            codificacao_valida = codificacao
            print(f"[OK] CODIFICAÇÃO: {codificacao}")
            break
        except UnicodeDecodeError:
            print(f"[FALHA] CODIFICAÇÃO: {codificacao}")

    if codificacao_valida is None:
        raise RuntimeError(
            f"Nenhuma codificação configurada conseguiu ler {caminho.name}"
        )

    primeira_linha = texto.splitlines()[0]

    print()
    print("PRIMEIRA LINHA:")
    print(primeira_linha)

    print()
    print("CONTAGEM DE DELIMITADORES NA PRIMEIRA LINHA:")
    print(f";  -> {primeira_linha.count(';')}")
    print(f",  -> {primeira_linha.count(',')}")
    print(f"\\t -> {primeira_linha.count(chr(9))}")

    print()
    print(
        f"CODIFICAÇÃO SELECIONADA: {codificacao_valida}"
    )
    print()


def main():
    for nome in ARQUIVOS:
        caminho = RAW_DIR / nome

        if not caminho.exists():
            raise FileNotFoundError(
                f"Arquivo não encontrado: {caminho}"
            )

        testar_arquivo(caminho)


if __name__ == "__main__":
    main()