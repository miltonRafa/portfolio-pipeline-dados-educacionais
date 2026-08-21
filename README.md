# Pipeline de Dados Educacionais

Projeto de portfolio em engenharia de dados e BI para organizar indicadores
educacionais em camadas `raw`, `bronze`, `silver` e `gold`, com consumo final
no Power BI.

## Objetivo

Construir uma base analitica reproduzivel para comparar indicadores da
educacao publica brasileira por UF, ano e etapa de ensino, preservando a
rastreabilidade das fontes oficiais.

Fontes tratadas:

- Rendimento Escolar
- Taxa de Distorcao Idade-Serie (TDI)
- IDEB
- SAEB
- PND 2025

## Fontes dos dados

Os dados utilizados neste projeto sao provenientes de bases oficiais do
Instituto Nacional de Estudos e Pesquisas Educacionais Anisio Teixeira
(Inep/MEC):

| Base | Periodo | Link oficial |
|---|---:|---|
| SAEB — Microdados | 2007–2023 | [Inep/MEC — Microdados do SAEB](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/saeb) |
| SAEB — Resultados agregados | 2007–2023 | [Inep/MEC — Resultados do SAEB](https://www.gov.br/inep/pt-br/areas-de-atuacao/avaliacao-e-exames-educacionais/saeb/resultados) |
| IDEB — Resultados | 2007–2023 | [Inep/MEC — Resultados do IDEB](https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados) |
| Taxas de Rendimento Escolar | 2007–2023 | [Inep/MEC — Taxas de Rendimento Escolar](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais/taxas-de-rendimento-escolar) |
| Taxas de Distorcao Idade-Serie (TDI) | 2007–2023 | [Inep/MEC — Taxas de Distorcao Idade-Serie](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais/taxas-de-distorcao-idade-serie) |
| Prova Nacional Docente (PND) — Microdados | 2025 | [Inep/MEC — Microdados da PND](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/pnd) |

Os links oficiais do Inep/MEC constituem a referencia institucional e a fonte
primaria dos dados utilizados no projeto. Os arquivos armazenados localmente em
`data/raw` correspondem aos materiais obtidos dessas fontes.

Consulte [docs/fontes_dados.md](docs/fontes_dados.md) para o inventario
completo dos arquivos usados, dicionarios, arquivos auxiliares, finalidade,
hashes SHA-256 e convencao de renomeacao local.

### Copia organizada dos dados brutos

Para facilitar a reproducao do projeto, ha uma copia organizada dos arquivos da
camada `raw`:

[Google Drive - raw organizado](https://drive.google.com/file/d/1Jm2v8Er4m5dgjOLOLLcaNssn_YN1Wsja/view?usp=sharing)

Essa copia e apenas um recurso de conveniencia. As fontes primarias e oficiais
permanecem sendo as paginas do Inep/MEC indicadas na documentacao.

## Arquitetura

```text
data/raw      -> arquivos originais
data/bronze   -> ingestao tecnica, rastreavel e com hash da origem
data/silver   -> harmonizacao semantica e recorte analitico
data/gold     -> modelo dimensional para Power BI
powerbi       -> medidas DAX e arquivo PBIX
docs          -> decisoes metodologicas e auditorias
src           -> scripts de ingestao, transformacao e validacao
```

## Modelo Gold

A camada Gold contem cinco dimensoes:

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

A validacao global confirma graos, dominios e integridade referencial antes do
consumo no Power BI.

## Como reproduzir

Crie um ambiente virtual e instale as dependencias:

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

Listar comandos disponiveis:

```bash
python src/pipeline.py --list
```

## Resultado validado

A validacao global da Gold retorna:

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

## Documentacao

As decisoes metodologicas principais estao em:

- `docs/camada_bronze.md`
- `docs/camada_silver.md`
- `docs/camada_gold.md`
- `docs/definicao_rede_publica.md`
- `docs/modelagem_power_bi.md`

## Observacoes

Os arquivos de dados estao ignorados por padrao no Git por tamanho e por serem
artefatos reproduziveis ou fontes locais. O arquivo `.pbix` foi mantido como
entrega visual do portfolio; em repositorios maiores, recomenda-se Git LFS.
