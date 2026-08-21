# Fontes dos dados

Este documento é a referência canônica do projeto para origem dos dados,
arquivos `raw`, finalidade dos insumos e reprodutibilidade.

Os dados utilizados são provenientes de bases oficiais do Instituto Nacional de
Estudos e Pesquisas Educacionais Anísio Teixeira (Inep/MEC).

## Fontes oficiais

| Base | Período | Link oficial |
|---|---:|---|
| SAEB — Microdados | 2007–2023 | [Inep/MEC — Microdados do SAEB](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/saeb) |
| SAEB — Resultados agregados | 2007–2023 | [Inep/MEC — Resultados do SAEB](https://www.gov.br/inep/pt-br/areas-de-atuacao/avaliacao-e-exames-educacionais/saeb/resultados) |
| IDEB — Resultados | 2007–2023 | [Inep/MEC — Resultados do IDEB](https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados) |
| Taxas de Rendimento Escolar | 2007–2023 | [Inep/MEC — Taxas de Rendimento Escolar](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais/taxas-de-rendimento-escolar) |
| Taxas de Distorção Idade-Série (TDI) | 2007–2023 | [Inep/MEC — Taxas de Distorção Idade-Série](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais/taxas-de-distorcao-idade-serie) |
| Prova Nacional Docente (PND) — Microdados | 2025 | [Inep/MEC — Microdados da PND](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/pnd) |

Os links oficiais do Inep/MEC constituem a referência institucional e a fonte
primária dos dados utilizados no projeto. O projeto não substitui a fonte
oficial do Inep.

## Cópia organizada dos dados brutos

Para facilitar a reprodução, há uma cópia organizada dos arquivos utilizados na
camada `raw`:

[https://drive.google.com/file/d/1Jm2v8Er4m5dgjOLOLLcaNssn_YN1Wsja/view?usp=sharing](https://drive.google.com/file/d/1Jm2v8Er4m5dgjOLOLLcaNssn_YN1Wsja/view?usp=sharing)

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

| Indicador | Ano | Nome local | Nome original | Tipo | Finalidade | Dicionário/apoio |
|---|---:|---|---|---|---|---|
| IDEB | 2007-2023 | `divulgacao_regioes_ufs_ideb.xlsx` | não registrado no repositório | resultado agregado | workbook oficial com nome local estavel; fonte fisica identificada por SHA-256 | não utilizado |
| PND | 2025 | `Dicionário_arquivos_variáveis_PND_2025.xlsx` | não registrado no repositório | dicionário | interpretação de variáveis, códigos e áreas da PND | não se aplica |
| PND | 2025 | `microdados2025_parametros_itens.xlsx` | não registrado no repositório | arquivo auxiliar | parâmetros de itens preservados no Raw; não é fonte da fato analítica principal | não se aplica |
| PND | 2025 | `microdados2025_pnd_arq1.txt` | não registrado no repositório | microdados | arquivo principal transformado na Bronze e na Silver da PND | Dicionário_arquivos_variáveis_PND_2025.xlsx |
| Rendimento Escolar | 2007 | `TX RENDIMENTO UFS 2007.xls` | não registrado no repositório | dado analítico | taxas oficiais por UF; fonte da série analítica | não utilizado |
| Rendimento Escolar | 2008 | `TAXAS RENDIMENTO UF 2008.xls` | não registrado no repositório | dado analítico | taxas oficiais por UF; fonte da série analítica | não utilizado |
| Rendimento Escolar | 2009 | `TAXAS RENDIMENTO UF 2009.xls` | não registrado no repositório | dado analítico | taxas oficiais por UF; fonte da série analítica | não utilizado |
| Rendimento Escolar | 2010 | `TAXAS RENDIMENTO UF 2010.xls` | não registrado no repositório | dado analítico | taxas oficiais por UF; fonte da série analítica | não utilizado |
| Rendimento Escolar | 2011 | `tx_rendimento_uf_2011.xls` | não registrado no repositório | dado analítico | taxas oficiais por UF; fonte da série analítica | não utilizado |
| Rendimento Escolar | 2012 | `tx_rendimento_UFs_2012.xlsx` | não registrado no repositório | dado analítico | taxas oficiais por UF; fonte da série analítica | não utilizado |
| Rendimento Escolar | 2013 | `TAXAS RENDIMENTOS UF 2013.xlsx` | não registrado no repositório | dado analítico | taxas oficiais por UF; fonte da série analítica | não utilizado |
| Rendimento Escolar | 2014 | `TAXAS RENDIMENTOS UF 2014.xlsx` | não registrado no repositório | dado analítico | taxas oficiais por UF; fonte da série analítica | não utilizado |
| Rendimento Escolar | 2015 | `TX_REND_UFS_2015.xlsx` | não registrado no repositório | dado analítico | taxas oficiais por UF; fonte da série analítica | não utilizado |
| Rendimento Escolar | 2016 | `TX_REND_UFS_2016.xlsx` | não registrado no repositório | dado analítico | taxas oficiais por UF; fonte da série analítica | não utilizado |
| Rendimento Escolar | 2017 | `TX_REND_BRASIL_REGIOES_UFS_2017.xlsx` | não registrado no repositório | dado analítico | taxas oficiais por UF; fonte da série analítica | não utilizado |
| Rendimento Escolar | 2018 | `TX_REND_BRASIL_REGIOES_UFS_2018.xlsx` | não registrado no repositório | dado analítico | taxas oficiais por UF; fonte da série analítica | não utilizado |
| Rendimento Escolar | 2019 | `tx_rend_brasil_regioes_ufs_2019.xlsx` | não registrado no repositório | dado analítico | taxas oficiais por UF; fonte da série analítica | não utilizado |
| Rendimento Escolar | 2020 | `tx_rend_brasil_regioes_ufs_2020.xlsx` | não registrado no repositório | dado analítico | taxas oficiais por UF; fonte da série analítica | não utilizado |
| Rendimento Escolar | 2021 | `tx_rend_brasil_regioes_ufs_2021.xlsx` | não registrado no repositório | dado analítico | taxas oficiais por UF; fonte da série analítica | não utilizado |
| Rendimento Escolar | 2022 | `tx_rend_brasil_regioes_ufs_2022.xlsx` | não registrado no repositório | dado analítico | taxas oficiais por UF; fonte da série analítica | não utilizado |
| Rendimento Escolar | 2023 | `tx_rend_brasil_regioes_ufs_2023.xlsx` | não registrado no repositório | dado analítico | taxas oficiais por UF; fonte da série analítica | não utilizado |
| SAEB | 2007 | `Dicionario_SAEB_2007.xlsx` | não registrado no repositório | dicionário | interpretação de códigos e estrutura da fonte | não se aplica |
| SAEB | 2007 | `MEDIA_UF_2007.xlsx` | não registrado no repositório | resultado agregado | resultado agregado oficial por UF; fonte da série analítica | Dicionario_SAEB_2007.xlsx |
| SAEB | 2007 | `TS_ESCOLA_2007.csv` | não registrado no repositório | arquivo de auditoria | microdados escolares preservados; não usados na Silver final | Dicionario_SAEB_2007.xlsx |
| SAEB | 2009 | `Dicionario_SAEB_2009.xlsx` | não registrado no repositório | dicionário | interpretação de códigos e estrutura da fonte | não se aplica |
| SAEB | 2009 | `MEDIA_UF_2009.xlsx` | não registrado no repositório | resultado agregado | resultado agregado oficial por UF; fonte da série analítica | Dicionario_SAEB_2009.xlsx |
| SAEB | 2009 | `TS_ESCOLA_2009.csv` | não registrado no repositório | arquivo de auditoria | microdados escolares preservados; não usados na Silver final | Dicionario_SAEB_2009.xlsx |
| SAEB | 2011 | `Dicionario_SAEB_2011.xlsx` | não registrado no repositório | dicionário | interpretação de códigos e estrutura da fonte | não se aplica |
| SAEB | 2011 | `TS_RESULTADO_UF_2011.csv` | não registrado no repositório | resultado agregado | resultado agregado oficial por UF; fonte da série analítica | Dicionario_SAEB_2011.xlsx |
| SAEB | 2013 | `TS_UF_2013.xlsx` | não registrado no repositório | resultado agregado | resultado agregado oficial por UF; fonte da série analítica | não utilizado |
| SAEB | 2015 | `TS_UF_2015.xlsx` | não registrado no repositório | resultado agregado | resultado agregado oficial por UF; fonte da série analítica | não utilizado |
| SAEB | 2017 | `TS_UF_2017.xlsx` | não registrado no repositório | resultado agregado | resultado agregado oficial por UF; fonte da série analítica | não utilizado |
| SAEB | 2019 | `TS_UF_2019.xlsx` | não registrado no repositório | resultado agregado | resultado agregado oficial por UF; fonte da série analítica | não utilizado |
| SAEB | 2021 | `TS_UF_2021.xlsx` | não registrado no repositório | resultado agregado | resultado agregado oficial por UF; fonte da série analítica | não utilizado |
| SAEB | 2023 | `Dicionario_Saeb_2023.xlsx` | não registrado no repositório | dicionário | interpretação de códigos e estrutura da fonte | não se aplica |
| SAEB | 2023 | `Resultados_Saeb_2023_Brasil_Estados_Municipios.xlsb` | não registrado no repositório | resultado agregado | resultado agregado oficial por UF; fonte final da série analítica | Dicionario_Saeb_2023.xlsx |
| SAEB | 2023 | `TS_ESCOLA_2023.csv` | não registrado no repositório | microdados | microdados escolares preservados e usados em auditoria da agregação; não adotados como resultado analítico final | Dicionario_Saeb_2023.xlsx |
| TDI | 2007 | `TDI UFS 2007.xls` | não registrado no repositório | dado analítico | taxa oficial por UF; fonte da série analítica | não utilizado |
| TDI | 2008 | `TDI UFS 2008.xls` | não registrado no repositório | dado analítico | taxa oficial por UF; fonte da série analítica | não utilizado |
| TDI | 2009 | `DADOS TDI UF - 2009.xls` | não registrado no repositório | dado analítico | taxa oficial por UF; fonte da série analítica | não utilizado |
| TDI | 2010 | `DADOS TDI UF - 2010.xls` | não registrado no repositório | dado analítico | taxa oficial por UF; fonte da série analítica | não utilizado |
| TDI | 2011 | `tdi_UFs_2011.xls` | não registrado no repositório | dado analítico | taxa oficial por UF; fonte da série analítica | não utilizado |
| TDI | 2012 | `tdi_UFs_2012.xls` | não registrado no repositório | dado analítico | taxa oficial por UF; fonte da série analítica | não utilizado |
| TDI | 2013 | `TDI UF - 2013.xls` | não registrado no repositório | dado analítico | taxa oficial por UF; fonte da série analítica | não utilizado |
| TDI | 2014 | `TDI UF - 2014.xls` | não registrado no repositório | dado analítico | taxa oficial por UF; fonte da série analítica | não utilizado |
| TDI | 2015 | `TDI_UFS_2015.xlsx` | não registrado no repositório | dado analítico | taxa oficial por UF; fonte da série analítica | não utilizado |
| TDI | 2016 | `TDI_UFS_2016.xlsx` | não registrado no repositório | dado analítico | taxa oficial por UF; fonte da série analítica | não utilizado |
| TDI | 2017 | `TDI_BRASIL_REGIOES_UFS_2017.xlsx` | não registrado no repositório | dado analítico | taxa oficial por UF; fonte da série analítica | não utilizado |
| TDI | 2018 | `TDI_BRASIL_REGIOES_UFS_2018.xlsx` | não registrado no repositório | dado analítico | taxa oficial por UF; fonte da série analítica | não utilizado |
| TDI | 2019 | `TDI_BRASIL_REGIOES_UFS_2019.xlsx` | não registrado no repositório | dado analítico | taxa oficial por UF; fonte da série analítica | não utilizado |
| TDI | 2020 | `TDI_BRASIL_REGIOES_UFS_2020.xlsx` | não registrado no repositório | dado analítico | taxa oficial por UF; fonte da série analítica | não utilizado |
| TDI | 2021 | `TDI_BRASIL_REGIOES_UFS_2021.xlsx` | não registrado no repositório | dado analítico | taxa oficial por UF; fonte da série analítica | não utilizado |
| TDI | 2022 | `TDI_BRASIL_REGIOES_UFS_2022.xlsx` | não registrado no repositório | dado analítico | taxa oficial por UF; fonte da série analítica | não utilizado |
| TDI | 2023 | `TDI_BRASIL_REGIOES_UFS_2023.xlsx` | não registrado no repositório | dado analítico | taxa oficial por UF; fonte da série analítica | não utilizado |

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
