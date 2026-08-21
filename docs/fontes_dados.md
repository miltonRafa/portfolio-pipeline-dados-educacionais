# Fontes dos dados

Este documento e a referencia canonica do projeto para origem dos dados,
arquivos `raw`, finalidade dos insumos e reprodutibilidade.

Os dados utilizados sao provenientes de bases oficiais do Instituto Nacional de
Estudos e Pesquisas Educacionais Anisio Teixeira (Inep/MEC).

## Fontes oficiais

| Base | Periodo | Link oficial |
|---|---:|---|
| SAEB — Microdados | 2007–2023 | [Inep/MEC — Microdados do SAEB](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/saeb) |
| SAEB — Resultados agregados | 2007–2023 | [Inep/MEC — Resultados do SAEB](https://www.gov.br/inep/pt-br/areas-de-atuacao/avaliacao-e-exames-educacionais/saeb/resultados) |
| IDEB — Resultados | 2007–2023 | [Inep/MEC — Resultados do IDEB](https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados) |
| Taxas de Rendimento Escolar | 2007–2023 | [Inep/MEC — Taxas de Rendimento Escolar](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais/taxas-de-rendimento-escolar) |
| Taxas de Distorcao Idade-Serie (TDI) | 2007–2023 | [Inep/MEC — Taxas de Distorcao Idade-Serie](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais/taxas-de-distorcao-idade-serie) |
| Prova Nacional Docente (PND) — Microdados | 2025 | [Inep/MEC — Microdados da PND](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/pnd) |

Os links oficiais do Inep/MEC constituem a referencia institucional e a fonte
primaria dos dados utilizados no projeto. O projeto nao substitui a fonte
oficial do Inep.

## Copia organizada dos dados brutos

Para facilitar a reproducao, ha uma copia organizada dos arquivos utilizados na
camada `raw`:

[https://drive.google.com/file/d/1Jm2v8Er4m5dgjOLOLLcaNssn_YN1Wsja/view?usp=sharing](https://drive.google.com/file/d/1Jm2v8Er4m5dgjOLOLLcaNssn_YN1Wsja/view?usp=sharing)

Essa copia e apenas um recurso de conveniencia. As fontes primarias e oficiais
permanecem sendo as paginas do Inep/MEC indicadas acima.

A copia de conveniencia deve conter somente arquivos de `data/raw`, preservando
a estrutura interna `data/raw/...`. Ela nao deve incluir arquivos Parquet,
Bronze, Silver, Gold, notebooks executados ou outros artefatos derivados.

## Convencao de nomenclatura da Raw

Sempre que o nome original disponibilizado pelo Inep nao indicava claramente o
ano de referencia, o arquivo foi renomeado localmente para incluir o ano.

Essa padronizacao:

- alterou somente o nome local;
- nao modificou conteudo;
- nao modificou estrutura;
- nao modificou valores;
- foi feita para facilitar organizacao temporal e rastreabilidade.

O campo `Nome original` do manifesto so e preenchido quando ha evidencia no
repositorio. Quando essa evidencia nao existe, ele permanece como
`nao registrado no repositorio`.

## Criterio de selecao por UF

Sempre que o Inep disponibiliza resultado oficial agregado por Unidade
Federativa, o projeto prioriza esses arquivos para representar o resultado
estadual publicado.

Microdados sao preservados e utilizados quando necessarios para rastreabilidade,
auditoria ou quando nao existe agregado oficial equivalente. No SAEB 2023, a
tentativa de reconstruir medias estaduais a partir de escolas foi usada como
auditoria metodologica, mas nao foi adotada como resultado final porque divergiu
do agregado oficial.

### Observacao sobre a pagina atual do SAEB

A pagina oficial de Resultados do SAEB e atualizada pelo Inep conforme novas
edicoes sao divulgadas. Atualmente, essa pagina ja lista a edicao de 2025, alem
das edicoes anteriores.

A versao atual deste projeto utiliza a serie SAEB de 2007 a 2023. Portanto,
baixar hoje um pacote mais recente do SAEB nao reproduz automaticamente os
insumos usados nesta versao. Para reproducao exata, utilize os arquivos locais
inventariados abaixo, identificados pelos respectivos hashes SHA-256.

A edicao SAEB 2025 nao foi incorporada nesta versao do projeto. Uma atualizacao
futura para incluir nova edicao devera ser tratada como nova versao, com
revisao coordenada das fontes, auditorias, pipeline, Gold, validacoes e Power BI.

### IDEB — arquivo utilizado

A pagina oficial de Resultados do IDEB e atualizada pelo Inep conforme novas
edicoes sao divulgadas. A rota atual para obter o arquivo usado pelo projeto e:

```text
Resultados do IDEB
→ PLANILHAS DO IDEB | Taxa de aprovacao, notas do SAEB, IDEB e projecoes
→ Regioes e estados
→ Ensino Fundamental Regular e Ensino Medio Regular
```

| Fonte | Pagina/secao oficial | Pacote oficial atual | Arquivo dentro do pacote | Nome local usado pelo projeto |
|---|---|---|---|---|
| IDEB | Resultados do IDEB → Planilhas do IDEB → Regioes e estados → Ensino Fundamental Regular e Ensino Medio Regular | `divulgacao_regioes_ufs_ideb_2025.zip`* | `divulgacao_regioes_ufs_ideb_2025.xlsx`* | `data/raw/ideb/divulgacao_regioes_ufs_ideb.xlsx` |

*O ano presente no nome do pacote oficial acompanha a edicao mais recente
disponibilizada pelo Inep e pode mudar em futuras atualizacoes. O projeto
utiliza localmente o nome estavel `divulgacao_regioes_ufs_ideb.xlsx`, evitando
dependencia do ano no caminho do arquivo.*

*A versao atual do projeto mantem o recorte historico de 2007-2023. Embora o
workbook atualmente publicado pelo Inep contenha tambem a edicao de 2025
(`VL_OBSERVADO_2025`), essa edicao nao e incorporada automaticamente as camadas
analiticas.*

O IDEB e uma excecao intencional a regra geral de nomenclatura da Raw. Nos demais
arquivos, quando o nome original ja traz o ano de referencia, ele e preservado;
quando o nome original nao traz o ano de referencia, o ano pode ser acrescentado
localmente para organizacao. No IDEB, existe um unico workbook corrente de
divulgacao utilizado pelo projeto, e a serie historica e identificada pelo
conteudo interno do arquivo, em colunas `VL_OBSERVADO_YYYY`, como
`VL_OBSERVADO_2007`, `VL_OBSERVADO_2009`, `VL_OBSERVADO_2023` e
`VL_OBSERVADO_2025`.

Para reproducao exata, utilize o arquivo local estavel identificado no manifesto
pelo hash SHA-256. Para atualizar a fonte em uma execucao futura, substitua
deliberadamente esse arquivo local por uma nova versao oficial antes de executar
o pipeline; durante cada execucao, porem, o arquivo Raw e tratado como imutavel.
Substituir o arquivo-fonte nao altera automaticamente o escopo analitico, que e
controlado separadamente pelo pipeline e pela metodologia do projeto.

### Rendimento Escolar — arquivos utilizados

Para cada ano da serie de 2007 a 2023, foi selecionada a respectiva edicao anual
na pagina oficial de Taxas de Rendimento Escolar e utilizado o item `Brasil,
regioes e UFs`. Os nomes apresentados abaixo correspondem aos arquivos
armazenados em `data/raw/rendimento` e efetivamente consumidos pelo pipeline.

Rota de obtencao:

```text
Taxas de Rendimento Escolar
→ selecionar o ANO desejado
→ Brasil, regioes e UFs
→ baixar o arquivo daquele ano
```

| Ano | Item oficial | Arquivo local utilizado |
|---:|---|---|
| 2007 | Brasil, regioes e UFs | `TX RENDIMENTO UFS 2007.xls` |
| 2008 | Brasil, regioes e UFs | `TAXAS RENDIMENTO UF 2008.xls` |
| 2009 | Brasil, regioes e UFs | `TAXAS RENDIMENTO UF 2009.xls` |
| 2010 | Brasil, regioes e UFs | `TAXAS RENDIMENTO UF 2010.xls` |
| 2011 | Brasil, regioes e UFs | `tx_rendimento_uf_2011.xls` |
| 2012 | Brasil, regioes e UFs | `tx_rendimento_UFs_2012.xlsx` |
| 2013 | Brasil, regioes e UFs | `TAXAS RENDIMENTOS UF 2013.xlsx` |
| 2014 | Brasil, regioes e UFs | `TAXAS RENDIMENTOS UF 2014.xlsx` |
| 2015 | Brasil, regioes e UFs | `TX_REND_UFS_2015.xlsx` |
| 2016 | Brasil, regioes e UFs | `TX_REND_UFS_2016.xlsx` |
| 2017 | Brasil, regioes e UFs | `TX_REND_BRASIL_REGIOES_UFS_2017.xlsx` |
| 2018 | Brasil, regioes e UFs | `TX_REND_BRASIL_REGIOES_UFS_2018.xlsx` |
| 2019 | Brasil, regioes e UFs | `tx_rend_brasil_regioes_ufs_2019.xlsx` |
| 2020 | Brasil, regioes e UFs | `tx_rend_brasil_regioes_ufs_2020.xlsx` |
| 2021 | Brasil, regioes e UFs | `tx_rend_brasil_regioes_ufs_2021.xlsx` |
| 2022 | Brasil, regioes e UFs | `tx_rend_brasil_regioes_ufs_2022.xlsx` |
| 2023 | Brasil, regioes e UFs | `tx_rend_brasil_regioes_ufs_2023.xlsx` |

O projeto utiliza 17/17 anos entre 2007 e 2023. Os itens `Municipios` e
`Escolas` nao sao utilizados como fonte da serie estadual atual.

### Taxa de Distorcao Idade-Serie — arquivos utilizados

Para cada ano da serie de 2007 a 2023, foi selecionada a respectiva edicao anual
na pagina oficial de Taxas de Distorcao Idade-Serie e utilizado o item `Brasil,
regioes e UFs`. Os nomes apresentados abaixo correspondem aos arquivos
armazenados em `data/raw/tdi` e efetivamente consumidos pelo pipeline.

Rota de obtencao:

```text
Taxas de Distorcao Idade-Serie
→ selecionar o ANO desejado
→ Brasil, regioes e UFs
→ baixar o arquivo daquele ano
```

| Ano | Item oficial | Arquivo local utilizado |
|---:|---|---|
| 2007 | Brasil, regioes e UFs | `TDI UFS 2007.xls` |
| 2008 | Brasil, regioes e UFs | `TDI UFS 2008.xls` |
| 2009 | Brasil, regioes e UFs | `DADOS TDI UF - 2009.xls` |
| 2010 | Brasil, regioes e UFs | `DADOS TDI UF - 2010.xls` |
| 2011 | Brasil, regioes e UFs | `tdi_UFs_2011.xls` |
| 2012 | Brasil, regioes e UFs | `tdi_UFs_2012.xls` |
| 2013 | Brasil, regioes e UFs | `TDI UF - 2013.xls` |
| 2014 | Brasil, regioes e UFs | `TDI UF - 2014.xls` |
| 2015 | Brasil, regioes e UFs | `TDI_UFS_2015.xlsx` |
| 2016 | Brasil, regioes e UFs | `TDI_UFS_2016.xlsx` |
| 2017 | Brasil, regioes e UFs | `TDI_BRASIL_REGIOES_UFS_2017.xlsx` |
| 2018 | Brasil, regioes e UFs | `TDI_BRASIL_REGIOES_UFS_2018.xlsx` |
| 2019 | Brasil, regioes e UFs | `TDI_BRASIL_REGIOES_UFS_2019.xlsx` |
| 2020 | Brasil, regioes e UFs | `TDI_BRASIL_REGIOES_UFS_2020.xlsx` |
| 2021 | Brasil, regioes e UFs | `TDI_BRASIL_REGIOES_UFS_2021.xlsx` |
| 2022 | Brasil, regioes e UFs | `TDI_BRASIL_REGIOES_UFS_2022.xlsx` |
| 2023 | Brasil, regioes e UFs | `TDI_BRASIL_REGIOES_UFS_2023.xlsx` |

O projeto utiliza 17/17 anos entre 2007 e 2023. Os itens `Municipios` e
`Escolas` nao sao utilizados como fonte da serie estadual atual.

### PND 2025 — pacote e arquivos utilizados

Na pagina oficial da PND, a edicao utilizada e `2025` e o item de download e
`Microdados da Prova Nacional Docente`. Atualmente, esse item aponta para o
pacote oficial `microdados_pnd_2025.zip`.

Rota de obtencao:

```text
PND
→ 2025
→ Microdados da Prova Nacional Docente
→ baixar microdados_pnd_2025.zip
```

Orientacao pratica:

1. acessar a pagina da PND;
2. abrir a edicao 2025;
3. clicar em `Microdados da Prova Nacional Docente`;
4. baixar o pacote;
5. extrair os arquivos necessarios;
6. manter os nomes locais esperados pelo pipeline.

| Tipo | Item/pacote oficial | Arquivo local | Funcao |
|---|---|---|---|
| Microdados | Microdados da Prova Nacional Docente / `microdados_pnd_2025.zip` | `microdados2025_pnd_arq1.txt` | fonte analitica individual transformada pela Bronze e Silver |
| Dicionario | mesmo pacote | `Dicionario_arquivos_variaveis_PND_2025.xlsx` | interpretacao das variaveis, campos e categorias |
| Auxiliar | mesmo pacote | `microdados2025_parametros_itens.xlsx` | arquivo auxiliar disponibilizado no pacote; nao e lido pelas transformacoes Bronze/Silver/Gold |

O arquivo `microdados2025_pnd_arq1.txt` e a fonte analitica individual utilizada
para construir a Silver e, posteriormente, a FATO_PND. O dicionario e
documentacao de campos e categorias, nao uma observacao analitica. O arquivo
`microdados2025_parametros_itens.xlsx` e preservado como auxiliar do pacote, mas
nao e lido pelas transformacoes Bronze/Silver/Gold desta versao.

Nao ha Manual do Usuario da PND preservado em `data/raw` nem inventariado neste
projeto. Por isso, nenhum caminho local de manual e documentado aqui.

As tres fontes documentadas nesta secao tem modos de distribuicao diferentes:
Rendimento e TDI usam um arquivo por ano, obtido no item `Brasil, regioes e UFs`
de cada edicao anual; a PND usa um pacote unico da edicao 2025, do qual o projeto
preserva microdados, dicionario e arquivo auxiliar.

## Inventario dos arquivos

| Indicador | Ano | Nome local | Nome original | Tipo | Finalidade | Dicionario/apoio |
|---|---:|---|---|---|---|---|
| IDEB | 2007-2023 | `divulgacao_regioes_ufs_ideb.xlsx` | nao registrado no repositorio | resultado agregado | workbook oficial com nome local estavel; fonte fisica identificada por SHA-256 | nao utilizado |
| PND | 2025 | `Dicionario_arquivos_variaveis_PND_2025.xlsx` | nao registrado no repositorio | dicionario | interpretacao de variaveis, codigos e areas da PND | nao se aplica |
| PND | 2025 | `microdados2025_parametros_itens.xlsx` | nao registrado no repositorio | arquivo auxiliar | parametros de itens preservados no Raw; nao e fonte da fato analitica principal | nao se aplica |
| PND | 2025 | `microdados2025_pnd_arq1.txt` | nao registrado no repositorio | microdados | arquivo principal transformado na Bronze e na Silver da PND | Dicionario_arquivos_variaveis_PND_2025.xlsx |
| Rendimento Escolar | 2007 | `TX RENDIMENTO UFS 2007.xls` | nao registrado no repositorio | dado analitico | taxas oficiais por UF; fonte da serie analitica | nao utilizado |
| Rendimento Escolar | 2008 | `TAXAS RENDIMENTO UF 2008.xls` | nao registrado no repositorio | dado analitico | taxas oficiais por UF; fonte da serie analitica | nao utilizado |
| Rendimento Escolar | 2009 | `TAXAS RENDIMENTO UF 2009.xls` | nao registrado no repositorio | dado analitico | taxas oficiais por UF; fonte da serie analitica | nao utilizado |
| Rendimento Escolar | 2010 | `TAXAS RENDIMENTO UF 2010.xls` | nao registrado no repositorio | dado analitico | taxas oficiais por UF; fonte da serie analitica | nao utilizado |
| Rendimento Escolar | 2011 | `tx_rendimento_uf_2011.xls` | nao registrado no repositorio | dado analitico | taxas oficiais por UF; fonte da serie analitica | nao utilizado |
| Rendimento Escolar | 2012 | `tx_rendimento_UFs_2012.xlsx` | nao registrado no repositorio | dado analitico | taxas oficiais por UF; fonte da serie analitica | nao utilizado |
| Rendimento Escolar | 2013 | `TAXAS RENDIMENTOS UF 2013.xlsx` | nao registrado no repositorio | dado analitico | taxas oficiais por UF; fonte da serie analitica | nao utilizado |
| Rendimento Escolar | 2014 | `TAXAS RENDIMENTOS UF 2014.xlsx` | nao registrado no repositorio | dado analitico | taxas oficiais por UF; fonte da serie analitica | nao utilizado |
| Rendimento Escolar | 2015 | `TX_REND_UFS_2015.xlsx` | nao registrado no repositorio | dado analitico | taxas oficiais por UF; fonte da serie analitica | nao utilizado |
| Rendimento Escolar | 2016 | `TX_REND_UFS_2016.xlsx` | nao registrado no repositorio | dado analitico | taxas oficiais por UF; fonte da serie analitica | nao utilizado |
| Rendimento Escolar | 2017 | `TX_REND_BRASIL_REGIOES_UFS_2017.xlsx` | nao registrado no repositorio | dado analitico | taxas oficiais por UF; fonte da serie analitica | nao utilizado |
| Rendimento Escolar | 2018 | `TX_REND_BRASIL_REGIOES_UFS_2018.xlsx` | nao registrado no repositorio | dado analitico | taxas oficiais por UF; fonte da serie analitica | nao utilizado |
| Rendimento Escolar | 2019 | `tx_rend_brasil_regioes_ufs_2019.xlsx` | nao registrado no repositorio | dado analitico | taxas oficiais por UF; fonte da serie analitica | nao utilizado |
| Rendimento Escolar | 2020 | `tx_rend_brasil_regioes_ufs_2020.xlsx` | nao registrado no repositorio | dado analitico | taxas oficiais por UF; fonte da serie analitica | nao utilizado |
| Rendimento Escolar | 2021 | `tx_rend_brasil_regioes_ufs_2021.xlsx` | nao registrado no repositorio | dado analitico | taxas oficiais por UF; fonte da serie analitica | nao utilizado |
| Rendimento Escolar | 2022 | `tx_rend_brasil_regioes_ufs_2022.xlsx` | nao registrado no repositorio | dado analitico | taxas oficiais por UF; fonte da serie analitica | nao utilizado |
| Rendimento Escolar | 2023 | `tx_rend_brasil_regioes_ufs_2023.xlsx` | nao registrado no repositorio | dado analitico | taxas oficiais por UF; fonte da serie analitica | nao utilizado |
| SAEB | 2007 | `Dicionario_SAEB_2007.xlsx` | nao registrado no repositorio | dicionario | interpretacao de codigos e estrutura da fonte | nao se aplica |
| SAEB | 2007 | `MEDIA_UF_2007.xlsx` | nao registrado no repositorio | resultado agregado | resultado agregado oficial por UF; fonte da serie analitica | Dicionario_SAEB_2007.xlsx |
| SAEB | 2007 | `TS_ESCOLA_2007.csv` | nao registrado no repositorio | arquivo de auditoria | microdados escolares preservados; nao usados na Silver final | Dicionario_SAEB_2007.xlsx |
| SAEB | 2009 | `Dicionario_SAEB_2009.xlsx` | nao registrado no repositorio | dicionario | interpretacao de codigos e estrutura da fonte | nao se aplica |
| SAEB | 2009 | `MEDIA_UF_2009.xlsx` | nao registrado no repositorio | resultado agregado | resultado agregado oficial por UF; fonte da serie analitica | Dicionario_SAEB_2009.xlsx |
| SAEB | 2009 | `TS_ESCOLA_2009.csv` | nao registrado no repositorio | arquivo de auditoria | microdados escolares preservados; nao usados na Silver final | Dicionario_SAEB_2009.xlsx |
| SAEB | 2011 | `Dicionario_SAEB_2011.xlsx` | nao registrado no repositorio | dicionario | interpretacao de codigos e estrutura da fonte | nao se aplica |
| SAEB | 2011 | `TS_RESULTADO_UF_2011.csv` | nao registrado no repositorio | resultado agregado | resultado agregado oficial por UF; fonte da serie analitica | Dicionario_SAEB_2011.xlsx |
| SAEB | 2013 | `TS_UF_2013.xlsx` | nao registrado no repositorio | resultado agregado | resultado agregado oficial por UF; fonte da serie analitica | nao utilizado |
| SAEB | 2015 | `TS_UF_2015.xlsx` | nao registrado no repositorio | resultado agregado | resultado agregado oficial por UF; fonte da serie analitica | nao utilizado |
| SAEB | 2017 | `TS_UF_2017.xlsx` | nao registrado no repositorio | resultado agregado | resultado agregado oficial por UF; fonte da serie analitica | nao utilizado |
| SAEB | 2019 | `TS_UF_2019.xlsx` | nao registrado no repositorio | resultado agregado | resultado agregado oficial por UF; fonte da serie analitica | nao utilizado |
| SAEB | 2021 | `TS_UF_2021.xlsx` | nao registrado no repositorio | resultado agregado | resultado agregado oficial por UF; fonte da serie analitica | nao utilizado |
| SAEB | 2023 | `Dicionario_Saeb_2023.xlsx` | nao registrado no repositorio | dicionario | interpretacao de codigos e estrutura da fonte | nao se aplica |
| SAEB | 2023 | `Resultados_Saeb_2023_Brasil_Estados_Municipios.xlsb` | nao registrado no repositorio | resultado agregado | resultado agregado oficial por UF; fonte final da serie analitica | Dicionario_Saeb_2023.xlsx |
| SAEB | 2023 | `TS_ESCOLA_2023.csv` | nao registrado no repositorio | microdados | microdados escolares preservados e usados em auditoria da agregacao; nao adotados como resultado analitico final | Dicionario_Saeb_2023.xlsx |
| TDI | 2007 | `TDI UFS 2007.xls` | nao registrado no repositorio | dado analitico | taxa oficial por UF; fonte da serie analitica | nao utilizado |
| TDI | 2008 | `TDI UFS 2008.xls` | nao registrado no repositorio | dado analitico | taxa oficial por UF; fonte da serie analitica | nao utilizado |
| TDI | 2009 | `DADOS TDI UF - 2009.xls` | nao registrado no repositorio | dado analitico | taxa oficial por UF; fonte da serie analitica | nao utilizado |
| TDI | 2010 | `DADOS TDI UF - 2010.xls` | nao registrado no repositorio | dado analitico | taxa oficial por UF; fonte da serie analitica | nao utilizado |
| TDI | 2011 | `tdi_UFs_2011.xls` | nao registrado no repositorio | dado analitico | taxa oficial por UF; fonte da serie analitica | nao utilizado |
| TDI | 2012 | `tdi_UFs_2012.xls` | nao registrado no repositorio | dado analitico | taxa oficial por UF; fonte da serie analitica | nao utilizado |
| TDI | 2013 | `TDI UF - 2013.xls` | nao registrado no repositorio | dado analitico | taxa oficial por UF; fonte da serie analitica | nao utilizado |
| TDI | 2014 | `TDI UF - 2014.xls` | nao registrado no repositorio | dado analitico | taxa oficial por UF; fonte da serie analitica | nao utilizado |
| TDI | 2015 | `TDI_UFS_2015.xlsx` | nao registrado no repositorio | dado analitico | taxa oficial por UF; fonte da serie analitica | nao utilizado |
| TDI | 2016 | `TDI_UFS_2016.xlsx` | nao registrado no repositorio | dado analitico | taxa oficial por UF; fonte da serie analitica | nao utilizado |
| TDI | 2017 | `TDI_BRASIL_REGIOES_UFS_2017.xlsx` | nao registrado no repositorio | dado analitico | taxa oficial por UF; fonte da serie analitica | nao utilizado |
| TDI | 2018 | `TDI_BRASIL_REGIOES_UFS_2018.xlsx` | nao registrado no repositorio | dado analitico | taxa oficial por UF; fonte da serie analitica | nao utilizado |
| TDI | 2019 | `TDI_BRASIL_REGIOES_UFS_2019.xlsx` | nao registrado no repositorio | dado analitico | taxa oficial por UF; fonte da serie analitica | nao utilizado |
| TDI | 2020 | `TDI_BRASIL_REGIOES_UFS_2020.xlsx` | nao registrado no repositorio | dado analitico | taxa oficial por UF; fonte da serie analitica | nao utilizado |
| TDI | 2021 | `TDI_BRASIL_REGIOES_UFS_2021.xlsx` | nao registrado no repositorio | dado analitico | taxa oficial por UF; fonte da serie analitica | nao utilizado |
| TDI | 2022 | `TDI_BRASIL_REGIOES_UFS_2022.xlsx` | nao registrado no repositorio | dado analitico | taxa oficial por UF; fonte da serie analitica | nao utilizado |
| TDI | 2023 | `TDI_BRASIL_REGIOES_UFS_2023.xlsx` | nao registrado no repositorio | dado analitico | taxa oficial por UF; fonte da serie analitica | nao utilizado |

## Manifesto estruturado e hashes

O manifesto machine-readable esta em:

`docs/fontes_dados.csv`

Os hashes SHA-256 dos arquivos brutos inventariados estao em:

`docs/raw_checksums_sha256.txt`

Ambos sao gerados por:

`python scripts/gerar_manifesto_raw.py`

O script percorre somente os arquivos explicitamente inventariados, calcula os
hashes, falha se algum arquivo estiver ausente e nao modifica nenhum arquivo
Raw.

## Termos de redistribuicao

A pagina oficial de Dados Abertos do Inep informa que as principais bases e o
Plano de Dados Abertos sao divulgados naquela secao. A pagina tambem exibe a
licenca do conteudo do site gov.br/Inep como Creative Commons
Atribuicao-SemDerivacoes 3.0 Nao Adaptada.

Mesmo assim, a copia no Drive e documentada apenas como conveniencia de
reproducao. A referencia oficial e primaria permanece sendo o Inep/MEC.
