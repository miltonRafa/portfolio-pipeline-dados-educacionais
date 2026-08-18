from pathlib import Path
import csv
import hashlib


ARQUIVO = Path(
    "data/raw/pnd/microdados2025_pnd_arq1.txt"
)

CODIFICACOES = [
    "utf-8",
    "utf-8-sig",
    "cp1252",
    "latin1",
]

TAMANHO_BLOCO = 1024 * 1024


def calcular_sha256_e_linhas(caminho):
    sha256 = hashlib.sha256()
    quebras_linha = 0
    ultimo_byte = None

    with caminho.open("rb") as arquivo:
        while bloco := arquivo.read(TAMANHO_BLOCO):
            sha256.update(bloco)
            quebras_linha += bloco.count(b"\n")
            ultimo_byte = bloco[-1:]

    linhas_fisicas = quebras_linha

    if ultimo_byte not in (None, b"\n"):
        linhas_fisicas += 1

    return sha256.hexdigest(), linhas_fisicas


def detectar_codificacao(caminho):
    amostra = caminho.read_bytes()[:65536]

    for codificacao in CODIFICACOES:
        try:
            amostra.decode(codificacao)
            return codificacao
        except UnicodeDecodeError:
            pass

    raise RuntimeError(
        "Nenhuma das codificações configuradas "
        "conseguiu decodificar a amostra."
    )


def inspecionar_estrutura(caminho, codificacao):
    with caminho.open(
        "r",
        encoding=codificacao,
        newline="",
    ) as arquivo:
        leitor = csv.reader(
            arquivo,
            delimiter=";",
            quotechar='"',
        )

        cabecalho = next(leitor)

        print()
        print("CABEÇALHO:")
        print(";".join(cabecalho))

        print()
        print(
            f"QUANTIDADE DE COLUNAS: {len(cabecalho)}"
        )

        print()
        print("COLUNAS:")

        for indice, coluna in enumerate(
            cabecalho,
            start=1,
        ):
            print(
                f"{indice:02d}. {coluna}"
            )

        print()
        print("PRIMEIROS 5 REGISTROS:")

        for numero in range(1, 6):
            registro = next(leitor)

            print(
                f"Registro {numero}: "
                f"{len(registro)} campos"
            )
            print(registro)


def main():
    print("=" * 110)
    print(
        "VERIFICAÇÃO TÉCNICA — PND 2025"
    )
    print("=" * 110)

    if not ARQUIVO.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {ARQUIVO}"
        )

    tamanho = ARQUIVO.stat().st_size

    print()
    print(f"Arquivo: {ARQUIVO.name}")
    print(
        f"Tamanho: {tamanho:,} bytes"
    )

    codificacao = detectar_codificacao(
        ARQUIVO
    )

    print(
        f"Codificação identificada: {codificacao}"
    )

    sha256, linhas_fisicas = (
        calcular_sha256_e_linhas(
            ARQUIVO
        )
    )

    print(
        f"SHA-256: {sha256}"
    )
    print(
        f"Linhas físicas: {linhas_fisicas:,}"
    )

    if linhas_fisicas > 0:
        print(
            "Registros estimados "
            "(descontando o cabeçalho): "
            f"{linhas_fisicas - 1:,}"
        )

    inspecionar_estrutura(
        ARQUIVO,
        codificacao,
    )

    print()
    print("=" * 110)
    print(
        "VERIFICAÇÃO CONCLUÍDA"
    )
    print("=" * 110)


if __name__ == "__main__":
    main()
