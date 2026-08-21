from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"

DRIVE_RAW_ZIP_URL = (
    "https://drive.google.com/file/d/"
    "1Jm2v8Er4m5dgjOLOLLcaNssn_YN1Wsja/view?usp=sharing"
)

URLS = {
    "saeb_microdados": (
        "https://www.gov.br/inep/pt-br/acesso-a-informacao/"
        "dados-abertos/microdados/saeb"
    ),
    "saeb_resultados": (
        "https://www.gov.br/inep/pt-br/areas-de-atuacao/"
        "avaliacao-e-exames-educacionais/saeb/resultados"
    ),
    "ideb": (
        "https://www.gov.br/inep/pt-br/areas-de-atuacao/"
        "pesquisas-estatisticas-e-indicadores/ideb/resultados"
    ),
    "rendimento": (
        "https://www.gov.br/inep/pt-br/acesso-a-informacao/"
        "dados-abertos/indicadores-educacionais/"
        "taxas-de-rendimento-escolar"
    ),
    "tdi": (
        "https://www.gov.br/inep/pt-br/acesso-a-informacao/"
        "dados-abertos/indicadores-educacionais/"
        "taxas-de-distorcao-idade-serie"
    ),
    "pnd": (
        "https://www.gov.br/inep/pt-br/acesso-a-informacao/"
        "dados-abertos/microdados/pnd"
    ),
}

FIELDS = [
    "indicador",
    "ano",
    "caminho_local",
    "nome_local",
    "nome_original",
    "tipo",
    "finalidade",
    "dicionario_associado",
    "url_oficial",
    "url_historica_download",
    "edicao_fonte",
    "anos_disponiveis",
    "observacao",
    "sha256",
]


def item(
    indicador: str,
    ano: str,
    caminho: str,
    tipo: str,
    finalidade: str,
    url: str,
    dicionario: str = "não utilizado",
    nome_original: str = "não registrado no repositório",
    url_historica_download: str = "",
    edicao_fonte: str = "",
    anos_disponiveis: str = "",
    observacao: str = "",
) -> dict[str, str]:
    return {
        "indicador": indicador,
        "ano": str(ano),
        "caminho_local": caminho,
        "nome_local": Path(caminho).name,
        "nome_original": nome_original,
        "tipo": tipo,
        "finalidade": finalidade,
        "dicionario_associado": dicionario,
        "url_oficial": url,
        "url_historica_download": url_historica_download,
        "edicao_fonte": edicao_fonte,
        "anos_disponiveis": anos_disponiveis,
        "observacao": observacao,
        "sha256": "",
    }


INVENTORY = [
    item(
        "SAEB",
        "2007",
        "data/raw/saeb/MEDIA_UF_2007.xlsx",
        "resultado agregado",
        "resultado agregado oficial por UF; fonte da série analítica",
        URLS["saeb_resultados"],
        "Dicionario_SAEB_2007.xlsx",
    ),
    item(
        "SAEB",
        "2009",
        "data/raw/saeb/MEDIA_UF_2009.xlsx",
        "resultado agregado",
        "resultado agregado oficial por UF; fonte da série analítica",
        URLS["saeb_resultados"],
        "Dicionario_SAEB_2009.xlsx",
    ),
    item(
        "SAEB",
        "2011",
        "data/raw/saeb/TS_RESULTADO_UF_2011.csv",
        "resultado agregado",
        "resultado agregado oficial por UF; fonte da série analítica",
        URLS["saeb_resultados"],
        "Dicionario_SAEB_2011.xlsx",
    ),
    item(
        "SAEB",
        "2013",
        "data/raw/saeb/TS_UF_2013.xlsx",
        "resultado agregado",
        "resultado agregado oficial por UF; fonte da série analítica",
        URLS["saeb_resultados"],
    ),
    item(
        "SAEB",
        "2015",
        "data/raw/saeb/TS_UF_2015.xlsx",
        "resultado agregado",
        "resultado agregado oficial por UF; fonte da série analítica",
        URLS["saeb_resultados"],
    ),
    item(
        "SAEB",
        "2017",
        "data/raw/saeb/TS_UF_2017.xlsx",
        "resultado agregado",
        "resultado agregado oficial por UF; fonte da série analítica",
        URLS["saeb_resultados"],
    ),
    item(
        "SAEB",
        "2019",
        "data/raw/saeb/TS_UF_2019.xlsx",
        "resultado agregado",
        "resultado agregado oficial por UF; fonte da série analítica",
        URLS["saeb_resultados"],
    ),
    item(
        "SAEB",
        "2021",
        "data/raw/saeb/TS_UF_2021.xlsx",
        "resultado agregado",
        "resultado agregado oficial por UF; fonte da série analítica",
        URLS["saeb_resultados"],
    ),
    item(
        "SAEB",
        "2023",
        "data/raw/saeb/Resultados_Saeb_2023_Brasil_Estados_Municipios.xlsb",
        "resultado agregado",
        "resultado agregado oficial por UF; fonte final da série analítica",
        URLS["saeb_resultados"],
        "Dicionario_Saeb_2023.xlsx",
    ),
    item(
        "SAEB",
        "2007",
        "data/raw/saeb/TS_ESCOLA_2007.csv",
        "arquivo de auditoria",
        "microdados escolares preservados; não usados na Silver final",
        URLS["saeb_microdados"],
        "Dicionario_SAEB_2007.xlsx",
    ),
    item(
        "SAEB",
        "2009",
        "data/raw/saeb/TS_ESCOLA_2009.csv",
        "arquivo de auditoria",
        "microdados escolares preservados; não usados na Silver final",
        URLS["saeb_microdados"],
        "Dicionario_SAEB_2009.xlsx",
    ),
    item(
        "SAEB",
        "2023",
        "data/raw/saeb/TS_ESCOLA_2023.csv",
        "microdados",
        (
            "microdados escolares preservados e usados em auditoria da "
            "agregação; não adotados como resultado analítico final"
        ),
        URLS["saeb_microdados"],
        "Dicionario_Saeb_2023.xlsx",
    ),
    item(
        "SAEB",
        "2007",
        "data/raw/saeb/Dicionario_SAEB_2007.xlsx",
        "dicionário",
        "interpretação de códigos e estrutura da fonte",
        URLS["saeb_microdados"],
        "não se aplica",
    ),
    item(
        "SAEB",
        "2009",
        "data/raw/saeb/Dicionario_SAEB_2009.xlsx",
        "dicionário",
        "interpretação de códigos e estrutura da fonte",
        URLS["saeb_microdados"],
        "não se aplica",
    ),
    item(
        "SAEB",
        "2011",
        "data/raw/saeb/Dicionario_SAEB_2011.xlsx",
        "dicionário",
        "interpretação de códigos e estrutura da fonte",
        URLS["saeb_microdados"],
        "não se aplica",
    ),
    item(
        "SAEB",
        "2023",
        "data/raw/saeb/Dicionario_Saeb_2023.xlsx",
        "dicionário",
        "interpretação de códigos e estrutura da fonte",
        URLS["saeb_microdados"],
        "não se aplica",
    ),
    item(
        "IDEB",
        "2007-2023",
        "data/raw/ideb/divulgacao_regioes_ufs_ideb.xlsx",
        "resultado agregado",
        "workbook oficial com nome local estavel; fonte fisica identificada por SHA-256",
        URLS["ideb"],
        url_historica_download=(
            "https://download.inep.gov.br/ideb/resultados/"
            "divulgacao_regioes_ufs_ideb_2023.zip"
        ),
        edicao_fonte="arquivo fisico atual contem VL_OBSERVADO_2025",
        anos_disponiveis="2005, 2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021, 2023, 2025",
        observacao=(
            "A pagina oficial pode apontar para edicao posterior; "
            "a reproducao exata usa o arquivo local estavel e seu SHA-256."
        ),
    ),
]


RENDIMENTO = {
    2007: "TX RENDIMENTO UFS 2007.xls",
    2008: "TAXAS RENDIMENTO UF 2008.xls",
    2009: "TAXAS RENDIMENTO UF 2009.xls",
    2010: "TAXAS RENDIMENTO UF 2010.xls",
    2011: "tx_rendimento_uf_2011.xls",
    2012: "tx_rendimento_UFs_2012.xlsx",
    2013: "TAXAS RENDIMENTOS UF 2013.xlsx",
    2014: "TAXAS RENDIMENTOS UF 2014.xlsx",
    2015: "TX_REND_UFS_2015.xlsx",
    2016: "TX_REND_UFS_2016.xlsx",
    2017: "TX_REND_BRASIL_REGIOES_UFS_2017.xlsx",
    2018: "TX_REND_BRASIL_REGIOES_UFS_2018.xlsx",
    2019: "tx_rend_brasil_regioes_ufs_2019.xlsx",
    2020: "tx_rend_brasil_regioes_ufs_2020.xlsx",
    2021: "tx_rend_brasil_regioes_ufs_2021.xlsx",
    2022: "tx_rend_brasil_regioes_ufs_2022.xlsx",
    2023: "tx_rend_brasil_regioes_ufs_2023.xlsx",
}

TDI = {
    2007: "TDI UFS 2007.xls",
    2008: "TDI UFS 2008.xls",
    2009: "DADOS TDI UF - 2009.xls",
    2010: "DADOS TDI UF - 2010.xls",
    2011: "tdi_UFs_2011.xls",
    2012: "tdi_UFs_2012.xls",
    2013: "TDI UF - 2013.xls",
    2014: "TDI UF - 2014.xls",
    2015: "TDI_UFS_2015.xlsx",
    2016: "TDI_UFS_2016.xlsx",
    2017: "TDI_BRASIL_REGIOES_UFS_2017.xlsx",
    2018: "TDI_BRASIL_REGIOES_UFS_2018.xlsx",
    2019: "TDI_BRASIL_REGIOES_UFS_2019.xlsx",
    2020: "TDI_BRASIL_REGIOES_UFS_2020.xlsx",
    2021: "TDI_BRASIL_REGIOES_UFS_2021.xlsx",
    2022: "TDI_BRASIL_REGIOES_UFS_2022.xlsx",
    2023: "TDI_BRASIL_REGIOES_UFS_2023.xlsx",
}

for year, name in RENDIMENTO.items():
    INVENTORY.append(
        item(
            "Rendimento Escolar",
            str(year),
            f"data/raw/rendimento/{name}",
            "dado analítico",
            "taxas oficiais por UF; fonte da série analítica",
            URLS["rendimento"],
        )
    )

for year, name in TDI.items():
    INVENTORY.append(
        item(
            "TDI",
            str(year),
            f"data/raw/tdi/{name}",
            "dado analítico",
            "taxa oficial por UF; fonte da série analítica",
            URLS["tdi"],
        )
    )

INVENTORY.extend(
    [
        item(
            "PND",
            "2025",
            "data/raw/pnd/microdados2025_pnd_arq1.txt",
            "microdados",
            "arquivo principal transformado na Bronze e na Silver da PND",
            URLS["pnd"],
            "Dicionário_arquivos_variáveis_PND_2025.xlsx",
        ),
        item(
            "PND",
            "2025",
            "data/raw/pnd/Dicionário_arquivos_variáveis_PND_2025.xlsx",
            "dicionário",
            "interpretação de variáveis, códigos e áreas da PND",
            URLS["pnd"],
            "não se aplica",
        ),
        item(
            "PND",
            "2025",
            "data/raw/pnd/microdados2025_parametros_itens.xlsx",
            "arquivo auxiliar",
            (
                "parâmetros de itens preservados no Raw; não é fonte da "
                "fato analítica principal"
            ),
            URLS["pnd"],
            "não se aplica",
        ),
    ]
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inventory_with_hashes() -> list[dict[str, str]]:
    rows = []
    missing = []

    for row in INVENTORY:
        full_path = ROOT / row["caminho_local"]
        if not full_path.is_file():
            missing.append(row["caminho_local"])
            continue

        output = dict(row)
        output["sha256"] = sha256(full_path)
        rows.append(output)

    if missing:
        missing_text = "\n".join(f"- {path}" for path in missing)
        raise FileNotFoundError(
            "Arquivos do manifesto ausentes:\n" + missing_text
        )

    return sorted(
        rows,
        key=lambda row: (
            row["indicador"],
            row["ano"],
            row["caminho_local"],
        ),
    )


def write_csv(rows: list[dict[str, str]]) -> None:
    path = DOCS_DIR / "fontes_dados.csv"
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_checksums(rows: list[dict[str, str]]) -> None:
    path = DOCS_DIR / "raw_checksums_sha256.txt"
    lines = [
        f"{row['sha256']}  {row['caminho_local']}"
        for row in sorted(rows, key=lambda row: row["caminho_local"])
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def markdown_table(rows: list[dict[str, str]]) -> str:
    header = (
        "| Indicador | Ano | Nome local | Nome original | Tipo | Finalidade | "
        "Dicionário/apoio |\n"
        "|---|---:|---|---|---|---|---|"
    )
    body = []
    for row in rows:
        display = dict(row)
        if display["nome_original"] != "não registrado no repositório":
            display["nome_original"] = f"`{display['nome_original']}`"
        body.append(
            "| {indicador} | {ano} | `{nome_local}` | {nome_original} | "
            "{tipo} | {finalidade} | {dicionario_associado} |".format(
                **display,
            )
        )
    return "\n".join([header, *body])


def write_markdown(rows: list[dict[str, str]]) -> None:
    path = DOCS_DIR / "fontes_dados.md"
    content = f"""# Fontes dos dados

Este documento é a referência canônica do projeto para origem dos dados,
arquivos `raw`, finalidade dos insumos e reprodutibilidade.

Os dados utilizados são provenientes de bases oficiais do Instituto Nacional de
Estudos e Pesquisas Educacionais Anísio Teixeira (Inep/MEC).

## Fontes oficiais

| Base | Período | Link oficial |
|---|---:|---|
| SAEB — Microdados | 2007–2023 | [Inep/MEC — Microdados do SAEB]({URLS['saeb_microdados']}) |
| SAEB — Resultados agregados | 2007–2023 | [Inep/MEC — Resultados do SAEB]({URLS['saeb_resultados']}) |
| IDEB — Resultados | 2007–2023 | [Inep/MEC — Resultados do IDEB]({URLS['ideb']}) |
| Taxas de Rendimento Escolar | 2007–2023 | [Inep/MEC — Taxas de Rendimento Escolar]({URLS['rendimento']}) |
| Taxas de Distorção Idade-Série (TDI) | 2007–2023 | [Inep/MEC — Taxas de Distorção Idade-Série]({URLS['tdi']}) |
| Prova Nacional Docente (PND) — Microdados | 2025 | [Inep/MEC — Microdados da PND]({URLS['pnd']}) |

Os links oficiais do Inep/MEC constituem a referência institucional e a fonte
primária dos dados utilizados no projeto. O projeto não substitui a fonte
oficial do Inep.

## Cópia organizada dos dados brutos

Para facilitar a reprodução, há uma cópia organizada dos arquivos utilizados na
camada `raw`:

[{DRIVE_RAW_ZIP_URL}]({DRIVE_RAW_ZIP_URL})

Essa cópia é apenas um recurso de conveniência. As fontes primárias e oficiais
permanecem sendo as páginas do Inep/MEC indicadas acima.

A cópia de conveniência deve conter somente arquivos de `data/raw`, preservando
a estrutura interna `data/raw/...`. Ela não deve incluir arquivos Parquet,
Bronze, Silver, Gold, notebooks executados ou outros artefatos derivados.

## Convenção de nomenclatura da Raw

Sempre que o nome original disponibilizado pelo Inep não indicava claramente o
ano de referência, o arquivo foi renomeado localmente para incluir o ano.

Essa padronização:

- alterou somente o nome local;
- não modificou conteúdo;
- não modificou estrutura;
- não modificou valores;
- foi feita para facilitar organização temporal e rastreabilidade.

O campo `Nome original` do manifesto só é preenchido quando há evidência no
repositório. Quando essa evidência não existe, ele permanece como
`não registrado no repositório`.

## Critério de seleção por UF

Sempre que o Inep disponibiliza resultado oficial agregado por Unidade
Federativa, o projeto prioriza esses arquivos para representar o resultado
estadual publicado.

Microdados são preservados e utilizados quando necessários para rastreabilidade,
auditoria ou quando não existe agregado oficial equivalente. No SAEB 2023, a
tentativa de reconstruir médias estaduais a partir de escolas foi usada como
auditoria metodológica, mas não foi adotada como resultado final porque divergiu
do agregado oficial.

### Observação sobre a página atual do SAEB

A página oficial de Resultados do SAEB é atualizada pelo Inep conforme novas
edições são divulgadas. Atualmente, essa página já lista a edição de 2025, além
das edições anteriores.

A versão atual deste projeto utiliza a série SAEB de 2007 a 2023. Portanto,
baixar hoje um pacote mais recente do SAEB não reproduz automaticamente os
insumos usados nesta versão. Para reprodução exata, utilize os arquivos locais
inventariados abaixo, identificados pelos respectivos hashes SHA-256.

A edição SAEB 2025 não foi incorporada nesta versão do projeto. Uma atualização
futura para incluir nova edição deverá ser tratada como nova versão, com
revisão coordenada das fontes, auditorias, pipeline, Gold, validações e Power BI.

### Observação sobre a página atual do IDEB

A página oficial de Resultados do IDEB é atualizada pelo Inep conforme novas
edições são divulgadas. A obtenção da versão mais recente no Inep e a
reprodução exata desta versão do projeto não são a mesma operação.

O arquivo local do IDEB usa o nome estável
`data/raw/ideb/divulgacao_regioes_ufs_ideb.xlsx` porque o workbook concentra a
série histórica em colunas identificadas por variáveis técnicas
`VL_OBSERVADO_YYYY`. O ano da edição física não deve ser inferido pelo nome do
arquivo local.

Nesta revisão, o arquivo físico canônico contém dados observados até 2025
(`VL_OBSERVADO_2025`). O recorte analítico adotado por esta versão do projeto
permanece 2007-2023.

Para reprodução exata, utilize o arquivo local estável identificado no manifesto
pelo hash SHA-256. Para atualizar a fonte em uma execução futura, substitua
deliberadamente esse arquivo local por uma nova versão oficial antes de executar
o pipeline; a Bronze detectará a estrutura e os anos observados disponíveis,
enquanto a Silver manterá o recorte analítico declarado de 2007 a 2023 até que o
projeto seja versionado para incorporar nova edição. Substituir o arquivo-fonte
não altera automaticamente o escopo analítico.

## Inventário dos arquivos

{markdown_table(rows)}

## Manifesto estruturado e hashes

O manifesto machine-readable está em:

`docs/fontes_dados.csv`

Os hashes SHA-256 dos arquivos brutos inventariados estão em:

`docs/raw_checksums_sha256.txt`

Ambos são gerados por:

`python scripts/gerar_manifesto_raw.py`

O script percorre somente os arquivos explicitamente inventariados, calcula os
hashes, falha se algum arquivo estiver ausente e não modifica nenhum arquivo
Raw.

## Termos de redistribuição

A página oficial de Dados Abertos do Inep informa que as principais bases e o
Plano de Dados Abertos são divulgados naquela seção. A página também exibe a
licença do conteúdo do site gov.br/Inep como Creative Commons
Atribuição-SemDerivações 3.0 Não Adaptada.

Mesmo assim, a cópia no Drive é documentada apenas como conveniência de
reprodução. A referência oficial e primária permanece sendo o Inep/MEC.
"""
    path.write_text(content, encoding="utf-8")


def main() -> None:
    DOCS_DIR.mkdir(exist_ok=True)
    rows = inventory_with_hashes()
    write_csv(rows)
    write_checksums(rows)
    write_markdown(rows)
    print(f"Arquivos inventariados: {len(rows)}")
    print("Gerado: docs/fontes_dados.md")
    print("Gerado: docs/fontes_dados.csv")
    print("Gerado: docs/raw_checksums_sha256.txt")


if __name__ == "__main__":
    main()
