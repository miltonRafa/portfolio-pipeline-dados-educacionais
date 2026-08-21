# Pipeline de Dados Educacionais

Projeto de portfólio em engenharia de dados e BI para organizar indicadores
educacionais em camadas `raw`, `bronze`, `silver` e `gold`, com consumo final
no Power BI.

## Objetivo

Construir uma base analítica reproduzível para comparar indicadores da
educação pública brasileira por UF, ano e etapa de ensino, preservando a
rastreabilidade das fontes oficiais.

Fontes tratadas:

- Rendimento Escolar
- Taxa de Distorção Idade-Série (TDI)
- IDEB
- SAEB
- PND 2025

## Fontes dos dados

Os dados utilizados neste projeto são provenientes de bases oficiais do
Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira
(Inep/MEC):

| Base | Período | Link oficial |
|---|---:|---|
| SAEB — Microdados | 2007–2023 | [Inep/MEC — Microdados do SAEB](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/saeb) |
| SAEB — Resultados agregados | 2007–2023 | [Inep/MEC — Resultados do SAEB](https://www.gov.br/inep/pt-br/areas-de-atuacao/avaliacao-e-exames-educacionais/saeb/resultados) |
| IDEB — Resultados | 2007–2023 | [Inep/MEC — Resultados do IDEB](https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados) |
| Taxas de Rendimento Escolar | 2007–2023 | [Inep/MEC — Taxas de Rendimento Escolar](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais/taxas-de-rendimento-escolar) |
| Taxas de Distorção Idade-Série (TDI) | 2007–2023 | [Inep/MEC — Taxas de Distorção Idade-Série](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais/taxas-de-distorcao-idade-serie) |
| Prova Nacional Docente (PND) — Microdados | 2025 | [Inep/MEC — Microdados da PND](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/pnd) |

Os links oficiais do Inep/MEC constituem a referência institucional e a fonte
primária dos dados utilizados no projeto. Os arquivos armazenados localmente em
`data/raw` correspondem aos materiais obtidos dessas fontes.

Consulte [docs/fontes_dados.md](docs/fontes_dados.md) para o inventário
completo dos arquivos usados, dicionários, arquivos auxiliares, finalidade,
hashes SHA-256 e convenção de renomeação local.

### Cópia organizada dos dados brutos

Para facilitar a reprodução do projeto, há uma cópia organizada dos arquivos da
camada `raw`:

[Google Drive - raw organizado](https://drive.google.com/file/d/1Jm2v8Er4m5dgjOLOLLcaNssn_YN1Wsja/view?usp=sharing)

Essa cópia é apenas um recurso de conveniência. As fontes primárias e oficiais
permanecem sendo as páginas do Inep/MEC indicadas na documentação.

## Arquitetura

```text
data/raw      -> arquivos originais
data/bronze   -> ingestão técnica, rastreável e com hash da origem
data/silver   -> harmonização semântica e recorte analítico
data/gold     -> modelo dimensional para Power BI
powerbi       -> medidas DAX e arquivo PBIX
docs          -> decisões metodológicas e auditorias
src           -> scripts de ingestão, transformação e validação
```

## Modelo Gold

A camada Gold contém cinco dimensões:

- `dim_uf`
- `dim_tempo`
- `dim_etapa`
- `dim_area_pnd`
- `dim_municipio`

E cinco fatos:

- `fato_rendimento`
- `fato_tdi`
- `fato_ideb`
- `fato_saeb`
- `fato_pnd`

A validação global confirma grãos, domínios e integridade referencial antes do
consumo no Power BI.

## Como reproduzir

Crie um ambiente virtual e instale as dependências:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Valide o modelo dimensional Gold:

```bash
python src/pipeline.py validate-gold
```

Recrie e valide toda a camada Gold a partir das tabelas Silver:

```bash
python src/pipeline.py gold
```

Listar comandos disponíveis:

```bash
python src/pipeline.py --list
```

## Resultado validado

A validação global da Gold retorna:

```text
MODELO DIMENSIONAL GOLD: OK
```

Cardinalidades confirmadas:

- `DIM_UF`: 27
- `DIM_TEMPO`: 18
- `DIM_ETAPA`: 2
- `DIM_AREA_PND`: 17
- `DIM_MUNICIPIO`: 750
- `FATO_RENDIMENTO`: 2.754
- `FATO_TDI`: 918
- `FATO_IDEB`: 486
- `FATO_SAEB`: 972
- `FATO_PND`: 759.140

## Documentação

As decisões metodológicas principais estão em:

- `docs/camada_bronze.md`
- `docs/camada_silver.md`
- `docs/camada_gold.md`
- `docs/definicao_rede_publica.md`
- `docs/modelagem_power_bi.md`

## Observações

Os arquivos de dados estão ignorados por padrão no Git por tamanho e por serem
artefatos reproduzíveis ou fontes locais. O arquivo `.pbix` foi mantido como
entrega visual do portfólio; em repositórios maiores, recomenda-se Git LFS.
