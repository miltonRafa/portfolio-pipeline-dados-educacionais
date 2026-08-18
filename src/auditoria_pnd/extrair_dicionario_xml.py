from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import posixpath


ARQUIVO = Path(
    "data/raw/pnd/Dicionário_arquivos_variáveis_PND_2025.xlsx"
)


def nome_local(tag):
    """
    Remove qualquer namespace XML.

    Exemplo:
    {namespace}sheet -> sheet
    """
    return tag.split("}")[-1]


def atributo_local(elemento, nome):
    """
    Procura um atributo ignorando o namespace.
    """

    for chave, valor in elemento.attrib.items():
        if nome_local(chave) == nome:
            return valor

    return None


def caminho_interno(target):
    """
    Normaliza o caminho de um relacionamento do workbook.
    """

    target = target.replace("\\", "/")

    if target.startswith("/"):
        return target.lstrip("/")

    if target.startswith("xl/"):
        return target

    return posixpath.normpath(
        posixpath.join("xl", target)
    )


def carregar_shared_strings(zip_file):

    arquivo = "xl/sharedStrings.xml"

    if arquivo not in zip_file.namelist():
        return []

    raiz = ET.fromstring(
        zip_file.read(arquivo)
    )

    strings = []

    for elemento in raiz.iter():

        if nome_local(elemento.tag) != "si":
            continue

        partes = []

        for filho in elemento.iter():

            if nome_local(filho.tag) == "t":
                partes.append(filho.text or "")

        strings.append(
            "".join(partes)
        )

    return strings


def valor_celula(celula, shared_strings):

    tipo = celula.attrib.get("t")

    # --------------------------------------------------
    # Inline string
    # --------------------------------------------------

    if tipo == "inlineStr":

        partes = []

        for elemento in celula.iter():

            if nome_local(elemento.tag) == "t":
                partes.append(elemento.text or "")

        return "".join(partes)

    # --------------------------------------------------
    # Valor normal
    # --------------------------------------------------

    valor = None

    for filho in celula:

        if nome_local(filho.tag) == "v":
            valor = filho.text
            break

    if valor is None:
        return ""

    # --------------------------------------------------
    # Shared string
    # --------------------------------------------------

    if tipo == "s":

        try:
            return shared_strings[int(valor)]
        except Exception:
            return valor

    return valor


with ZipFile(ARQUIVO, "r") as z:

    print("=" * 110)
    print("DICIONÁRIO PND 2025 — LEITURA OOXML SEM NAMESPACE FIXO")
    print("=" * 110)

    # ==================================================
    # 1. WORKBOOK
    # ==================================================

    workbook = ET.fromstring(
        z.read("xl/workbook.xml")
    )

    print("\nROOT DO WORKBOOK:")
    print(workbook.tag)

    # ==================================================
    # 2. RELACIONAMENTOS
    # ==================================================

    relacoes_xml = ET.fromstring(
        z.read("xl/_rels/workbook.xml.rels")
    )

    print("\nROOT DOS RELACIONAMENTOS:")
    print(relacoes_xml.tag)

    relacoes = {}

    for elemento in relacoes_xml.iter():

        if nome_local(elemento.tag) != "Relationship":
            continue

        rel_id = elemento.attrib.get("Id")
        target = elemento.attrib.get("Target")

        if rel_id and target:
            relacoes[rel_id] = target

    print(
        f"\nRELACIONAMENTOS ENCONTRADOS: "
        f"{len(relacoes)}"
    )

    # ==================================================
    # 3. ABAS
    # ==================================================

    sheets = []

    print("\nABAS ENCONTRADAS:")

    for elemento in workbook.iter():

        if nome_local(elemento.tag) != "sheet":
            continue

        nome = elemento.attrib.get("name")

        rel_id = atributo_local(
            elemento,
            "id"
        )

        target = relacoes.get(rel_id)

        print(
            f"- nome={nome!r} | "
            f"rel={rel_id!r} | "
            f"target={target!r}"
        )

        if target:

            sheets.append(
                (
                    nome,
                    caminho_interno(target)
                )
            )

    print(
        f"\nTOTAL DE ABAS: "
        f"{len(sheets)}"
    )

    # ==================================================
    # 4. SHARED STRINGS
    # ==================================================

    shared_strings = carregar_shared_strings(z)

    print(
        f"\nSHARED STRINGS: "
        f"{len(shared_strings):,}"
    )

    # ==================================================
    # 5. CONTEÚDO
    # ==================================================

    for nome, caminho in sheets:

        print("\n" + "#" * 110)
        print(f"ABA: {nome}")
        print(f"XML: {caminho}")
        print("#" * 110)

        if caminho not in z.namelist():

            print(
                "ERRO: arquivo XML da aba "
                "não encontrado no XLSX."
            )

            continue

        raiz = ET.fromstring(
            z.read(caminho)
        )

        print("\nROOT:")
        print(raiz.tag)

        linhas = []

        for elemento in raiz.iter():

            if nome_local(elemento.tag) == "row":
                linhas.append(elemento)

        print(
            f"\nTOTAL DE LINHAS XML: "
            f"{len(linhas):,}"
        )

        print("\nPRIMEIRAS 50 LINHAS:")

        for linha in linhas[:50]:

            valores = []

            for celula in linha:

                if nome_local(celula.tag) != "c":
                    continue

                referencia = celula.attrib.get(
                    "r",
                    ""
                )

                valor = valor_celula(
                    celula,
                    shared_strings
                )

                valores.append(
                    f"{referencia}={valor}"
                )

            print(
                f"Linha {linha.attrib.get('r')}: "
                + " | ".join(valores)
            )