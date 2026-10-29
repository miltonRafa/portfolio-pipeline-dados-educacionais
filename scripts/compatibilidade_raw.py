"""Comparação integral e conservadora dos insumos, sem executar o pipeline."""
from __future__ import annotations

import ast
import csv
from itertools import zip_longest
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


class Incompatible(ValueError):
    def __init__(self, code, message, **details):
        super().__init__(message)
        self.details = {"codigo": code, "motivo": message, **details}


def config(source, variable):
    """Lê constantes do pipeline sem importar/executar as transformações."""
    tree = ast.parse((ROOT / source).read_text(encoding="utf-8-sig"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == variable for t in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError(f"Configuração ausente: {source}:{variable}")


def used_sheets(row):
    indicator = row["indicador"]
    if indicator == "IDEB":
        return [c["aba"] for c in config("src/bronze/ideb/ingest_ideb.py", "CONFIG_ABAS").values()]
    if indicator in ("TDI", "Rendimento Escolar"):
        folder = "tdi" if indicator == "TDI" else "rendimento"
        return [config(f"src/bronze/{folder}/ingest_{folder}.py", "CONFIG")[int(row["ano"])]["aba"]]
    if indicator == "SAEB" and row["tipo"] == "resultado agregado":
        if row["ano"] == "2023":
            return [config("src/bronze/saeb/ingest_saeb_resultados_2023.py", "SHEET_NAME")]
        return [config("src/bronze/saeb/ingest_saeb.py", "CONFIG")[int(row["ano"])]["aba"]]
    # Dicionários e parâmetros também precisam preservar todo o conteúdo.
    return None


def snippet(value):
    return repr(value)[:180]


def compare_records(before, after, context):
    sentinel = object()
    count = 0
    for index, (left, right) in enumerate(zip_longest(before, after, fillvalue=sentinel), 1):
        if left is sentinel or right is sentinel:
            raise Incompatible("quantidade_linhas", "Quantidade de linhas do conteúdo protegido mudou.",
                               contexto=context, linha=index, lado_ausente="anterior" if left is sentinel else "novo")
        if len(left) != len(right):
            raise Incompatible("quantidade_colunas", "Quantidade de colunas do conteúdo protegido mudou.",
                               contexto=context, linha=index, anterior=len(left), novo=len(right))
        for column, (a, b) in enumerate(zip(left, right), 1):
            if a != b:
                raise Incompatible("conteudo_alterado", "Valor histórico ou conteúdo de apoio foi alterado.",
                                   contexto=context, linha=index, coluna=column,
                                   anterior=snippet(a), novo=snippet(b))
        count += 1
    return count


def ideb_projection(frame, sheet):
    """Protege identidades e todas as colunas históricas até 2023 nas três etapas."""
    headers = [i for i, values in enumerate(frame.itertuples(index=False, name=None))
               if "VL_OBSERVADO_2007" in values and "VL_OBSERVADO_2023" in values]
    if len(headers) != 1:
        raise Incompatible("cabecalho_ideb", "Esperado um único cabeçalho técnico histórico do IDEB.",
                           aba=sheet, encontrados=len(headers))
    index = headers[0]
    labels = list(frame.iloc[index])
    expected = [f"VL_OBSERVADO_{year}" for year in range(2007, 2024, 2)]
    for name in expected:
        if labels.count(name) != 1:
            raise Incompatible("ano_ausente_duplicado", "Ano obrigatório ausente ou duplicado no IDEB.", aba=sheet, campo=name)
    selected, names = [0, 1], ["GEOGRAFIA", "REDE"]
    for column, value in enumerate(labels[2:], 2):
        if not value:
            continue
        years = [int(y) for y in re.findall(r"(?<!\d)(20\d{2})(?!\d)", str(value))]
        if not years or max(years) <= 2023:
            selected.append(column)
            names.append(str(value))
    # A publicação atual repete alguns rótulos de rendimento. Compara-se a
    # sequência inteira por posição, preservando repetições sem colapsá-las.
    data = frame.iloc[index + 1:, selected]
    # Ordenação de colunas é protegida; linhas vazias finais não são observações.
    return names, [tuple(r) for r in data.itertuples(index=False, name=None) if any(v != "" for v in r)]


def compare_content(original, candidate, row):
    suffix = Path(row["nome_local"]).suffix.lower()
    if suffix in (".txt", ".csv"):
        encoding = "cp1252" if row["indicador"] == "SAEB" and row["ano"] != "2011" else "utf-8"
        with original.open(encoding=encoding, newline="") as a, candidate.open(encoding=encoding, newline="") as b:
            count = compare_records(csv.reader(a, delimiter=";", strict=True), csv.reader(b, delimiter=";", strict=True), "arquivo inteiro")
        return {"politica": "todas_as_linhas_e_campos", "linhas_comparadas": count, "encoding": encoding}
    if suffix not in (".xlsx", ".xls", ".xlsb"):
        raise Incompatible("formato_nao_suportado", "Não há comparador seguro para este formato.", formato=suffix)
    import pandas as pd
    engine = {".xlsx": "openpyxl", ".xls": "xlrd", ".xlsb": "pyxlsb"}[suffix]
    with pd.ExcelFile(original, engine=engine) as a, pd.ExcelFile(candidate, engine=engine) as b:
        sheets = used_sheets(row)
        if sheets is None:
            if a.sheet_names != b.sheet_names:
                raise Incompatible("abas_alteradas", "As abas do arquivo de apoio mudaram.", anterior=a.sheet_names, novo=b.sheet_names)
            sheets = a.sheet_names
        if not sheets:
            raise Incompatible("planilha_sem_abas", "Nenhuma aba legível; não é possível comprovar equivalência.")
        compared = []
        observed_years = set()
        for sheet in sheets:
            if sheet not in a.sheet_names or sheet not in b.sheet_names:
                raise Incompatible("aba_ausente", "Aba usada pelo projeto ausente.", aba=sheet, abas_novas=b.sheet_names)
            left = pd.read_excel(a, sheet_name=sheet, header=None, dtype=object, keep_default_na=False).fillna("")
            right = pd.read_excel(b, sheet_name=sheet, header=None, dtype=object, keep_default_na=False).fillna("")
            if row["indicador"] == "IDEB":
                l_names, l_rows = ideb_projection(left, sheet)
                r_names, r_rows = ideb_projection(right, sheet)
                if l_names != r_names:
                    raise Incompatible("estrutura_historica", "As colunas históricas ou sua ordem mudaram.", aba=sheet, anterior=l_names, novo=r_names)
                for values in right.itertuples(index=False, name=None):
                    for value in values:
                        match = re.fullmatch(r"VL_OBSERVADO_(\d{4})", str(value))
                        if match:
                            observed_years.add(int(match.group(1)))
            else:
                l_rows, r_rows = left.itertuples(index=False, name=None), right.itertuples(index=False, name=None)
            count = compare_records(l_rows, r_rows, sheet)
            compared.append({"aba": sheet, "linhas_comparadas": count})
    evidence = {"politica": "ideb_ate_2023" if row["indicador"] == "IDEB" else "abas_usadas_integrais", "abas": compared}
    if observed_years:
        evidence["anos_observados_nova_fonte"] = sorted(observed_years)
    return evidence
