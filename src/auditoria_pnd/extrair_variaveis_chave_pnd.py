from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import re


ARQUIVO = Path(
    "data/raw/pnd/Dicionário_arquivos_variáveis_PND_2025.xlsx"
)

ABA_XML = "xl/worksheets/sheet2.xml"


VARIAVEIS_ALVO = {
    "TP_INSCRICAO_PND",
    "IN_REAPLICACAO",
    "CO_CADERNO",
    "DS_VT_GAB_OBJ",
    "DS_VT_ESC_OBJ",
    "DS_VT_ACE_OBJ",
    "TP_PRES",
    "TP_SIT_DISC",
    "PROFICIENCIA",
    "NT_OBJ",
    "NT_DIS",
    "NT_GER",
    "QT_ACERTOS",
}


def nome_local(tag):
    return tag.split("}")[-1]


def carregar_shared_strings(z):

    caminho = "xl/sharedStrings.xml"

    if caminho not in z.namelist():
        return []

    raiz = ET.fromstring(
        z.read(caminho)
    )

    resultado = []

    for elemento in raiz.iter():

        if nome_local(elemento.tag) != "si":
            continue

        partes = []

        for filho in elemento.iter():

            if nome_local(filho.tag) == "t":
                partes.append(filho.text or "")

        resultado.append(
            "".join(partes)
        )

    return resultado


def valor_celula(celula, shared_strings):

    tipo = celula.attrib.get("t")

    if tipo == "inlineStr":

        partes = []

        for elemento in celula.iter():

            if nome_local(elemento.tag) == "t":
                partes.append(elemento.text or "")

        return "".join(partes)

    valor = None

    for filho in celula:

        if nome_local(filho.tag) == "v":
            valor = filho.text
            break

    if valor is None:
        return ""

    if tipo == "s":

        try:
            return shared_strings[int(valor)]
        except Exception:
            return valor

    return valor


def coluna_da_referencia(referencia):

    match = re.match(
        r"([A-Z]+)",
        referencia
    )

    if not match:
        return ""

    return match.group(1)


with ZipFile(ARQUIVO, "r") as z:

    shared_strings = carregar_shared_strings(z)

    raiz = ET.fromstring(
        z.read(ABA_XML)
    )

    linhas = []

    for elemento in raiz.iter():

        if nome_local(elemento.tag) != "row":
            continue

        dados = {}

        for celula in elemento:

            if nome_local(celula.tag) != "c":
                continue

            referencia = celula.attrib.get(
                "r",
                ""
            )

            coluna = coluna_da_referencia(
                referencia
            )

            dados[coluna] = valor_celula(
                celula,
                shared_strings
            )

        linhas.append(
            {
                "linha": int(
                    elemento.attrib.get("r")
                ),
                "A": dados.get("A", ""),
                "B": dados.get("B", ""),
                "C": dados.get("C", ""),
                "D": dados.get("D", ""),
                "E": dados.get("E", ""),
                "F": dados.get("F", ""),
            }
        )


print("=" * 120)
print("VARIÁVEIS-CHAVE — DICIONÁRIO PND 2025")
print("=" * 120)


for indice, registro in enumerate(linhas):

    nome = registro["A"].strip()

    if nome not in VARIAVEIS_ALVO:
        continue

    print("\n")
    print("#" * 120)
    print(f"VARIÁVEL: {nome}")
    print("#" * 120)

    # linha onde a variável começa
    j = indice

    while j < len(linhas):

        atual = linhas[j]

        # A partir da segunda linha,
        # encontrou outra variável/seção.
        if (
            j > indice
            and atual["A"].strip() != ""
        ):
            break

        print(
            f"Linha {atual['linha']}: "
            f"A={atual['A']} | "
            f"B={atual['B']} | "
            f"C={atual['C']} | "
            f"D={atual['D']} | "
            f"E={atual['E']} | "
            f"F={atual['F']}"
        )

        j += 1