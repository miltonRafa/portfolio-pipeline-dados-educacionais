# Camada Bronze — Ingestao dos Dados Educacionais

## 1. Objetivo

A camada Bronze e a primeira camada de dados processados do projeto.

Sua funcao e transformar os arquivos originais armazenados em `data/raw/` em estruturas legiveis e reutilizaveis pelo pipeline, preservando o maximo possivel da informacao da fonte.

A Bronze nao e responsavel por harmonizar conceitos entre bases.

Portanto, nesta etapa nao serao aplicadas decisoes analiticas como:

- selecao definitiva da rede publica;
- padronizacao de etapas de ensino;
- calculo de medias por UF;
- consolidacao de categorias;
- exclusao de registros apenas por nao integrarem o recorte analitico final;
- reconstrucao de indicadores;
- alteracao dos valores publicados pela fonte.

Essas transformacoes pertencem as camadas posteriores.

---

## 2. Relacao entre Raw e Bronze

### Raw

A camada Raw contem os arquivos obtidos das fontes oficiais e utilizados como
insumos do pipeline.

Quando o nome original de um arquivo nao identificava claramente o ano de
referencia, ele pode ser renomeado localmente antes de sua incorporacao a pasta
`data/raw`, exclusivamente para padronizacao da nomenclatura e melhor
organizacao temporal. Essa renomeacao nao altera o conteudo, a estrutura ou os
valores do arquivo.

Uma vez incorporado a pasta `data/raw`, o arquivo passa a ser considerado
imutavel.

O pipeline pode ler os arquivos da camada Raw, mas nao deve sobrescreve-los,
renomea-los, exclui-los ou modificar seu conteudo. As transformacoes realizadas
pelo pipeline devem gerar novos artefatos nas camadas subsequentes, comecando
pela Bronze.

A convencao de nomenclatura e o inventario canonico dos arquivos utilizados
estao documentados em `docs/fontes_dados.md`.

### Bronze

A pasta:

`data/bronze/`

contera representacoes estruturadas dos arquivos originais.

A Bronze podera:

- ler XLS, XLSX, CSV e TXT;
- identificar explicitamente a aba utilizada;
- identificar a linha de cabecalho ou referencia estrutural;
- converter tecnicamente os dados para DataFrame;
- remover apenas linhas completamente vazias produzidas pelo layout da planilha;
- adicionar metadados tecnicos de origem;
- persistir os resultados em Parquet.

A informacao substantiva da fonte devera ser preservada.

---

## 3. Por que utilizar Parquet

Os arquivos originais apresentam diferentes formatos:

- XLS;
- XLSX;
- CSV;
- TXT.

A camada Bronze utilizara preferencialmente o formato:

`Parquet`

porque ele:

- preserva tipos de dados de forma mais eficiente que CSV;
- possui leitura e escrita rapidas;
- ocupa menos espaco em disco;
- e adequado para pipelines analiticos;
- funciona bem com Python, Pandas, DuckDB e ferramentas de engenharia de dados;
- reduz problemas recorrentes de delimitador e codificacao encontrados em CSV.

O uso de Parquet na Bronze nao altera o significado dos dados.

Ele apenas padroniza o formato tecnico de armazenamento.

---

## 4. Metadados de rastreabilidade

Cada tabela Bronze devera possuir, quando aplicavel, metadados tecnicos que permitam rastrear o registro ate sua origem.

Os campos adotados no projeto sao:

- `_fonte`;
- `_sha256_arquivo`;
- `_arquivo_origem`;
- `_aba_origem`;
- `_ano_referencia`;
- `_indice_cabecalho_origem`;
- `_linha_origem`.

Algumas fontes poderao exigir metadados adicionais.

No IDEB foi acrescentado:

- `_etapa_origem`.

No SAEB foi acrescentado:

- `_granularidade_origem`.

Na PND 2025 tambem sera utilizado:

- `_granularidade_origem`.

No SAEB, esse campo registra a granularidade efetivamente preservada em cada tabela Bronze. Em 2023 coexistem duas tabelas oficiais preservadas separadamente: uma em nivel de `ESCOLA` e outra em nivel de `UF`.

Na PND, `_granularidade_origem = REGISTRO_INDIVIDUAL` registra que o arquivo principal preserva registros individuais da prova.

O campo nao harmoniza a granularidade; apenas torna explicita a granularidade efetivamente preservada na Bronze.

Esses campos nao substituem variaveis originais da fonte.

Sua finalidade e:

- identificar a fonte e o arquivo exato utilizado;
- registrar a aba de origem, quando aplicavel;
- registrar o ano ou edicao tecnica do arquivo;
- permitir localizacao da linha original;
- registrar a referencia estrutural utilizada pela ingestao;
- permitir verificacao de integridade do RAW por SHA-256.

Exemplo:

| _fonte | _arquivo_origem | _ano_referencia |
|---|---|---:|
| RENDIMENTO | TX_REND_BRASIL_REGIOES_UFS_2023.xlsx | 2023 |

O campo `_sha256_arquivo` registra o hash do arquivo de origem utilizado na ingestao.

A validacao independente da Bronze devera comparar esse valor com o hash calculado diretamente a partir do arquivo RAW.

---

## 5. O que nao sera feito na Bronze

A Bronze nao devera:

1. substituir `Publico` por `PUBLICA`;
2. transformar `Publica (4)` em `PUBLICA`;
3. agregar Federal, Estadual e Municipal;
4. selecionar apenas Anos Iniciais ou Anos Finais;
5. converter nomes de estados para siglas;
6. excluir rede privada;
7. remover registros apenas porque nao serao utilizados no dashboard;
8. calcular medias analiticas;
9. imputar valores ausentes;
10. recalcular indicadores;
11. aplicar a populacao analitica da PND;
12. alterar os arquivos originais.

Essas operacoes pertencem principalmente a Silver ou a Gold.

---

## 6. Tratamento permitido

Algumas operacoes tecnicas sao necessarias para tornar os arquivos utilizaveis.

Sao permitidas:

- identificacao da aba correta;
- identificacao da linha real de cabecalho ou referencia estrutural;
- remocao de linhas completamente vazias geradas pela estrutura da planilha;
- leitura correta de delimitador, decimal e codificacao;
- conversao tecnica de arquivos para DataFrame;
- criacao de nomes tecnicos temporarios quando a biblioteca de leitura exigir;
- conversao tecnica de celulas para texto quando necessaria a persistencia estavel da estrutura;
- adicao de metadados de origem;
- persistencia em Parquet.

Essas operacoes devem permanecer distinguiveis de transformacoes semanticas.

### 6.1 Tipagem tecnica das celulas na Bronze

Algumas planilhas de origem possuem titulos, cabecalhos hierarquicos, codigos tecnicos e valores numericos ocupando as mesmas colunas.

Por esse motivo, na ingestao de planilhas cuja estrutura completa e preservada, as celulas de origem poderao ser armazenadas como texto na camada Bronze.

Essa conversao possui finalidade exclusivamente tecnica: garantir que a estrutura heterogenea da planilha possa ser persistida de forma estavel em Parquet sem perda dos valores publicados.

A conversao para tipos analiticos, como inteiro, decimal ou categoria, sera realizada somente na camada Silver, apos a identificacao explicita da estrutura de cada fonte.

Valores especiais existentes na fonte, como `--`, nao serao convertidos automaticamente em nulos na Bronze.

As celulas realmente vazias permanecerao como valores ausentes.

A Bronze tambem preservara a linha de origem para permitir rastreabilidade ate a posicao original da informacao na planilha.

---

## 7. Particularidades das fontes

### 7.1 IDEB

O arquivo de origem utilizado e:

`divulgacao_regioes_ufs_ideb.xlsx`

Ele possui tres abas correspondentes as etapas:

- `UF e Regioes (AI)`;
- `UF e Regioes (AF)`;
- `UF e Regioes (EM)`.

Diferentemente das bases anuais de Rendimento Escolar e TDI, o arquivo do IDEB concentra em um unico workbook a serie historica de diferentes edicoes do indicador.

As planilhas contem informacoes anteriores ao recorte analitico do projeto, incluindo dados de 2005.

#### Decisao de ingestao

A Bronze preserva integralmente as tres abas do arquivo de origem, inclusive os dados referentes a 2005 e a aba do Ensino Medio.

Nao sao aplicados na Bronze:

- filtro do periodo 2007–2023;
- exclusao do Ensino Medio;
- selecao apenas dos Anos Iniciais e Anos Finais;
- filtro da rede publica;
- normalizacao de categorias como `Publica (4)`;
- selecao exclusiva das colunas do IDEB;
- remocao das colunas de aprovacao, SAEB ou metas existentes no workbook.

A justificativa e que essas operacoes modificariam semanticamente o conteudo publicado e pertencem as etapas posteriores do pipeline.

A Silver sera responsavel por aplicar o recorte analitico do projeto, selecionando:

- periodo de 2007 a 2023;
- Anos Iniciais e Anos Finais;
- definicao metodologica de rede publica registrada em `docs/definicao_rede_publica.md`.

Na Bronze, cada aba e persistida separadamente em Parquet, preservando sua estrutura e sua identificacao de origem.

#### Cabecalho hierarquico do IDEB

As planilhas do IDEB nao possuem um cabecalho simples em uma unica linha.

A estrutura auditada utiliza:

- indice 6: identificacao dos grandes blocos de indicadores;
- indice 7: subdivisoes das notas do SAEB;
- indice 8: series ou anos escolares e demais subdivisoes;
- indice 9: nomes tecnicos das variaveis disponibilizados pelo Inep.

A Bronze preserva todas essas linhas.

Para fins de rastreabilidade tecnica, `_indice_cabecalho_origem` registra a linha identificada no workbook como referencia tecnica, localizada pela presenca unica de variaveis `VL_OBSERVADO_YYYY`.

Como `_linha_origem` utiliza numeracao iniciada em um, o valor de `_indice_cabecalho_origem` corresponde ao indice interno zero-based da linha tecnica detectada.

Esse registro nao significa que as linhas anteriores do cabecalho sejam descartadas.

A interpretacao e reconstrucao semantica do cabecalho ocorrerao somente na Silver.

#### Ano de referencia tecnico

No IDEB:

`_ano_referencia = 2023`

representa a maior edicao observada no arquivo fisico utilizado na ingestao, detectada a partir das variaveis `VL_OBSERVADO_YYYY`.

Esse campo nao significa que todas as observacoes armazenadas sejam referentes a 2023.

Os anos substantivos da serie historica permanecem nas celulas da fonte e serao transformados em dimensao temporal analitica na Silver.

---

### 7.2 SAEB

A estrutura do SAEB varia significativamente entre as edicoes.

No conjunto RAW utilizado pelo projeto existem:

- arquivos agregados por Unidade da Federacao;
- arquivos em nivel escolar;
- arquivos XLSX;
- arquivos CSV;
- arquivo XLSB de resultados oficiais agregados;
- dicionarios de dados auxiliares.

A Bronze respeita a estrutura e a granularidade de cada fonte selecionada, sem harmonizacao forcada.

#### Decisao de selecao das fontes

Quando o Inep disponibiliza resultado oficial agregado por Unidade da Federacao, essa tabela e preferida para representar o resultado estadual publicado.

A estrutura RAW utilizada inicialmente permitiu empregar fontes agregadas por UF em todas as edicoes de 2007 a 2021. Em 2023, a primeira fonte ingerida foi `TS_ESCOLA_2023.csv`, em nivel escolar.

Durante a construcao da Silver, a tentativa de reproduzir os resultados estaduais de 2023 a partir das medias escolares ponderadas por `NU_PRESENTES` nao reproduziu os valores oficiais: foram obtidas `0/108` coincidencias apos arredondamento para duas casas decimais.

Como consequencia, foi incorporada ao RAW uma segunda fonte oficial de 2023:

`data/raw/saeb/Resultados_Saeb_2023_Brasil_Estados_Municipios.xlsb`

A aba utilizada e:

`Estados`

Essa fonte foi ingerida como uma Bronze adicional, preservando o resultado agregado oficial de UF sem substituir nem alterar a Bronze escolar ja existente.

A configuracao final do SAEB na Bronze e:

| Ano | Arquivo de origem | Aba | Granularidade | Papel |
|---:|---|---|---|---|
| 2007 | `MEDIA_UF_2007.xlsx` | `MEDIA_ESTADOS` | UF | resultado oficial agregado |
| 2009 | `MEDIA_UF_2009.xlsx` | `MEDIA_ESTADOS` | UF | resultado oficial agregado |
| 2011 | `TS_RESULTADO_UF_2011.csv` | nao se aplica | UF | resultado oficial agregado |
| 2013 | `TS_UF_2013.xlsx` | `UF` | UF | resultado oficial agregado |
| 2015 | `TS_UF_2015.xlsx` | `UFs` | UF | resultado oficial agregado |
| 2017 | `TS_UF_2017.xlsx` | `TS_UF` | UF | resultado oficial agregado |
| 2019 | `TS_UF_2019.xlsx` | `Estados` | UF | resultado oficial agregado |
| 2021 | `TS_UF_2021.xlsx` | `Estados` | UF | resultado oficial agregado |
| 2023 | `TS_ESCOLA_2023.csv` | nao se aplica | ESCOLA | microdados escolares preservados |
| 2023 | `Resultados_Saeb_2023_Brasil_Estados_Municipios.xlsb` | `Estados` | UF | resultado oficial agregado preservado |

A existencia de duas tabelas Bronze em 2023 e deliberada.

A Bronze escolar preserva o arquivo oficial em nivel de escola. A Bronze agregada preserva outra publicacao oficial do Inep em nivel de UF. Nenhuma delas e derivada da outra dentro da camada Bronze.

A decisao nao representa uma agregacao realizada na Bronze. Trata-se da ingestao separada de duas fontes oficiais com granularidades distintas.

#### Arquivos escolares de 2007 e 2009

Tambem existem no RAW:

- `TS_ESCOLA_2007.csv`;
- `TS_ESCOLA_2009.csv`.

Esses arquivos nao sao utilizados como fonte principal da serie analitica porque os respectivos anos ja possuem os arquivos oficiais agregados:

- `MEDIA_UF_2007.xlsx`;
- `MEDIA_UF_2009.xlsx`.

Os arquivos escolares permanecem preservados na camada Raw e nao sao alterados ou excluidos.

#### Dicionarios de dados

Os seguintes arquivos de dicionario tambem estao preservados no RAW:

- `Dicionario_SAEB_2007.xlsx`;
- `Dicionario_SAEB_2009.xlsx`;
- `Dicionario_SAEB_2011.xlsx`;
- `Dicionario_Saeb_2023.xlsx`.

Eles sao fontes auxiliares de documentacao e interpretacao estrutural.

Nao constituem tabelas de resultados do indicador e, por isso, nao sao tratados como fatos da Bronze do SAEB.

Seu conteudo pode ser consultado pelo pipeline ou pela documentacao sempre que necessario para interpretar codigos, campos e categorias.

#### Estruturas confirmadas nas fontes agregadas

Para 2007 e 2009, os arquivos `MEDIA_UF_*.xlsx` utilizam a aba `MEDIA_ESTADOS` e apresentam diretamente variaveis como `ANO_SAEB`, `CO_UF`, `NO_UF`, `DEPENDENCIA_ADM`, `LOCALIZACAO`, `CAPITAL` e medias de Lingua Portuguesa e Matematica.

Em 2011, `TS_RESULTADO_UF_2011.csv` possui estrutura tabular em CSV e utiliza codigos como `ID_UF`, `ID_SERIE`, `ID_TIPO_REDE`, `ID_LOCALIZACAO`, `ID_CAPITAL`, `NU_PARTICIPANTES`, `MEDIA_LP` e `MEDIA_MT`.

Para 2013 e 2015, o cabecalho e hierarquico e ocupa multiplas linhas. A auditoria confirmou:

- em 2013, a primeira linha semantica do cabecalho esta no indice `3`, correspondente a linha de origem `4`;
- em 2015, a primeira linha semantica do cabecalho esta no indice `2`, correspondente a linha de origem `3`.

A estrutura analitica preservada nessas duas edicoes foi confirmada nas posicoes:

- `col_001`: UF;
- `col_002`: rede;
- `col_003`: localizacao;
- `col_004`: capital;
- `col_005`: Anos Iniciais / Lingua Portuguesa;
- `col_006`: Anos Iniciais / Matematica;
- `col_007`: Anos Finais / Lingua Portuguesa;
- `col_008`: Anos Finais / Matematica.

Essa diferenca estrutural e preservada explicitamente e nao e substituida por nomes tecnicos inexistentes na fonte.

Para 2017, 2019 e 2021, os arquivos de UF utilizam cabecalhos tecnicos proprios das respectivas edicoes. Em 2019 e 2021, a aba e `Estados` e as fontes incluem, alem das medias de proficiencia, variaveis de niveis de proficiencia e outras etapas avaliadas.

Na nova fonte agregada de 2023, a aba `Estados` possui 177 colunas, entre elas `ANO_SAEB`, `CO_UF`, `NO_UF`, `DEPENDENCIA_ADM`, `LOCALIZACAO`, `CAPITAL`, `MEDIA_5_LP`, `MEDIA_5_MT`, `MEDIA_9_LP` e `MEDIA_9_MT`.

A primeira linha fisica contem os nomes tecnicos das variaveis e e preservada na Bronze.

#### Tipagem da fonte agregada de 2023

Na primeira tentativa de persistencia da aba `Estados` de 2023, o PyArrow identificou tipos heterogeneos nas mesmas colunas, pois a primeira linha contem nomes tecnicos e as linhas seguintes contem numeros ou categorias.

Por isso, as 177 colunas de origem sao persistidas como texto anulavel na Bronze agregada de 2023.

Essa decisao e exclusivamente tecnica:

- preserva a linha de cabecalho;
- evita coercao indevida entre texto e numero;
- mantem celulas realmente vazias como `null`;
- adia a tipagem analitica para a Silver.

#### Preservacao da granularidade

A Bronze nao forca uma unica granularidade para o SAEB.

A configuracao final e:

- 2007 a 2021: tabelas principais em nivel de UF;
- 2023: uma tabela em nivel de ESCOLA e uma tabela oficial adicional em nivel de UF.

O arquivo escolar de 2023 nao e agregado pela Bronze.

O arquivo de UF de 2023 tambem nao e calculado pela Bronze: ele e uma publicacao oficial independente do Inep e e apenas estruturado e rastreado em Parquet.

Na Silver historica, o resultado estadual de 2023 utiliza a Bronze oficial de UF porque a reconstrucao a partir das escolas por `NU_PRESENTES` nao reproduziu os resultados publicados.

#### Rede publica

Nenhum filtro de rede e aplicado na Bronze.

Sao preservados, conforme a estrutura de cada edicao:

- categorias de `DEPENDENCIA_ADM`;
- codigos de `ID_TIPO_REDE`;
- o indicador `IN_PUBLICA`;
- demais categorias originais de rede.

A definicao canonica `REDE = PUBLICA` e aplicada somente na Silver, seguindo `docs/definicao_rede_publica.md`.

A Bronze nao transforma o agregado geral que inclui rede privada em rede publica e nao calcula media simples entre redes Federal, Estadual e Municipal.

#### Proficiencias, etapas e variaveis adicionais

A Bronze nao seleciona exclusivamente Anos Iniciais, Anos Finais, Lingua Portuguesa ou Matematica.

Quando a fonte possui 2º ano, Ensino Medio, Ciencias Humanas, Ciencias da Natureza, niveis de proficiencia, participacao, erros-padrao ou outras variaveis publicadas, essas informacoes permanecem preservadas na estrutura Bronze correspondente.

A selecao das medidas necessarias ao modelo analitico e responsabilidade da Silver.

#### CSV, delimitador e codificacao

Os CSV do SAEB nao tem sua codificacao presumida silenciosamente.

Para `TS_RESULTADO_UF_2011.csv`, foi confirmado:

- codificacao: `utf-8`;
- delimitador: `;`;
- 12 delimitadores na linha de cabecalho;
- 13 campos na estrutura tabular.

Para `TS_ESCOLA_2023.csv`, foi confirmado:

- falha de leitura com `utf-8`;
- falha de leitura com `utf-8-sig`;
- leitura valida com `cp1252`;
- delimitador: `;`;
- 136 delimitadores na linha de cabecalho;
- 137 campos na estrutura tabular.

A configuracao da ingestao utiliza diretamente esses parametros. Se a estrutura esperada mudar, a execucao deve falhar explicitamente.

#### Situacao da ingestao

A Bronze do SAEB esta concluida e validada.

A extensao oficial agregada de 2023 e reproduzida por:

`src/bronze/saeb/ingest_saeb_resultados_2023.py`

e validada independentemente por:

`src/bronze/saeb/validar_bronze_saeb_resultados_2023.py`

A nova tabela produzida e:

`data/bronze/saeb/saeb_2023_resultados_uf.parquet`

Ela coexiste com:

`data/bronze/saeb/saeb_2023.parquet`

que preserva os registros escolares.

---

### 7.3 Rendimento Escolar

Os arquivos de Taxas de Rendimento Escolar apresentam mudancas estruturais ao longo da serie de 2007 a 2023.

Foram identificadas alteracoes relacionadas a:

- formato dos arquivos, entre XLS e XLSX;
- nomes das abas;
- posicao do cabecalho;
- quantidade de colunas;
- nomenclatura das redes de ensino;
- organizacao das dimensoes geograficas;
- existencia de espacos finais em nomes de determinadas abas.

Por esse motivo, a ingestao nao utiliza uma rotina que tente descobrir automaticamente qual aba ou estrutura deve ser utilizada.

Cada edicao possui configuracao explicita, definida a partir da auditoria realizada anteriormente.

#### Decisao de ingestao

A Bronze preserva a estrutura completa da planilha correspondente a Unidade da Federacao em cada edicao.

Os arquivos sao lidos com `header=None`, de forma que titulos, cabecalhos, subcabecalhos e registros publicados na planilha sejam mantidos.

Nao ocorre promocao automatica de uma linha para cabecalho analitico na Bronze.

A linha identificada durante a auditoria como referencia estrutural e registrada apenas no metadado `_indice_cabecalho_origem`.

A reconstrucao do cabecalho analitico sera responsabilidade da Silver.

#### Preservacao das celulas

As colunas provenientes da planilha recebem nomes tecnicos neutros:

`col_001`, `col_002`, `col_003`, etc.

Essa nomenclatura nao representa alteracao semantica da fonte.

Ela e utilizada porque a planilha contem titulos, cabecalhos e valores ocupando as mesmas posicoes fisicas ao longo das linhas.

As celulas de origem sao persistidas como texto para permitir armazenamento estavel em Parquet.

Valores especiais publicados pela fonte, como `--`, sao preservados.

A conversao para numeros, categorias ou outros tipos analiticos sera realizada somente na Silver.

#### Linhas vazias

Durante a ingestao sao removidas apenas linhas em que todas as celulas da planilha estao efetivamente vazias.

Nenhum registro e removido por pertencer a uma rede, localizacao, etapa ou categoria que nao sera utilizada posteriormente no dashboard.

#### Rede e localizacao

Nenhum filtro analitico de rede ou localizacao e aplicado na Bronze.

Permanecem preservadas categorias como:

- Federal;
- Estadual;
- Municipal;
- Particular ou Privada;
- `Publico` ou `Publica`;
- Total;
- Rural;
- Urbana.

A selecao do agregado oficial da rede publica combinado com `Localizacao = Total` sera realizada somente na Silver, conforme a decisao registrada em `docs/definicao_rede_publica.md`.

A Bronze nao reconstroi a rede publica a partir de medias das redes Federal, Estadual e Municipal.

#### Etapas e indicadores

A Bronze nao seleciona apenas Anos Iniciais e Anos Finais.

Tambem nao seleciona previamente apenas aprovacao, reprovacao ou abandono.

Toda a estrutura publicada na aba utilizada e preservada.

O recorte de etapa e a identificacao das colunas correspondentes aos indicadores serao realizados na Silver.

#### Estruturas auditadas e utilizadas

| Ano | Aba |
|---:|---|
| 2007 | `REND. POR UF` |
| 2008 | `Rendimento por UF - 2009` |
| 2009 | `Rendimento por UF - 2009` |
| 2010 | `RENDIMENTOS UFS 2010` |
| 2011 | `RENDIMENTOS UFS 2011` |
| 2012 | `UF 2012` |
| 2013 | `UF 2013` |
| 2014 | `UF ` |
| 2015 | `UF ` |
| 2016 | `UF ` |
| 2017 | `BRASIL_REGIOES_UFS ` |
| 2018 | `BRASIL_REGIOES_UFS ` |
| 2019 | `BRASIL_REGIOES_UFS ` |
| 2020 | `BRASIL_REGIOES_UFS ` |
| 2021 | `BRASIL_REGIOES_UFS ` |
| 2022 | `BRASIL_REGIOES_UFS ` |
| 2023 | `BRASIL_REGIOES_UFS ` |

#### Espacos finais em nomes de abas

Durante a implementacao da Bronze foram identificados espacos finais existentes nos proprios nomes das abas dos arquivos de origem.

Foram confirmados:

- 2014: `UF `;
- 2015: `UF `;
- 2016: `UF `;
- 2017 a 2023: `BRASIL_REGIOES_UFS `.

Esses espacos fazem parte dos nomes efetivamente armazenados nos workbooks, embora sejam pouco perceptiveis visualmente no Excel.

A ingestao utiliza os nomes exatos encontrados na fonte.

Nao foi utilizado `.strip()` para corrigir automaticamente esses nomes.

Essa escolha e deliberada: uma alteracao inesperada na estrutura da fonte deve provocar falha explicita no pipeline, em vez de ser silenciosamente normalizada.

#### Rastreabilidade

Cada registro produzido na Bronze do Rendimento possui metadados que permitem retornar a sua origem:

- `_fonte`;
- `_sha256_arquivo`;
- `_arquivo_origem`;
- `_aba_origem`;
- `_ano_referencia`;
- `_indice_cabecalho_origem`;
- `_linha_origem`.

O campo `_sha256_arquivo` identifica a versao exata do arquivo RAW utilizada na geracao do Parquet.

O campo `_linha_origem` registra a posicao da linha na planilha original.

O campo `_indice_cabecalho_origem` registra a referencia estrutural identificada durante a auditoria, sem transformar essa linha em cabecalho analitico da Bronze.

#### Resultado metodologico

A Bronze do Rendimento Escolar representa uma copia estruturada e rastreavel das planilhas de origem.

Nenhuma decisao de selecao da populacao analitica e aplicada nessa camada.

O fluxo adotado e:

```text
RAW
planilha original
    ↓
BRONZE
estrutura integral e rastreavel
    ↓
SILVER
selecao de UF + rede publica + localizacao total + AI/AF
e reconstrucao dos indicadores
```

---

### 7.4 TDI

A Taxa de Distorcao Idade-Serie apresenta mudancas estruturais entre os periodos, incluindo variacao entre formatos XLS e XLSX, nomes de abas e quantidade de colunas.

Assim como no Rendimento Escolar, a ingestao utiliza configuracao explicita por edicao e nao tenta selecionar automaticamente uma aba semelhante.

#### Decisao de ingestao

A Bronze preserva a estrutura integral da aba de UF identificada na auditoria para cada edicao.

Nao sao aplicados na Bronze:

- filtro de rede publica;
- filtro de `Localizacao = Total`;
- selecao apenas de AI/AF;
- normalizacao de rede;
- normalizacao de UF;
- reconstrucao ou recalculo da TDI.

#### Estruturas utilizadas

| Ano | Aba |
|---:|---|
| 2007 | `POR UF` |
| 2008 | `TDI UF 2008` |
| 2009 | `TDI por UF` |
| 2010 | `TDI UFS` |
| 2011 | `TDI UFS` |
| 2012 | `TDI UFS` |
| 2013 | `TDI UFS` |
| 2014 | `TDI UFS` |
| 2015 | `UF` |
| 2016 | `UF` |
| 2017 | `BRASIL_REGIOES_UFS` |
| 2018 | `BRASIL_REGIOES_UFS` |
| 2019 | `BRASIL_REGIOES_UFS` |
| 2020 | `BRASIL_REGIOES_UFS` |
| 2021 | `BRASIL_REGIOES_UFS` |
| 2022 | `BRASIL_REGIOES_UFS` |
| 2023 | `BRASIL_REGIOES_UFS` |

Durante a leitura dos arquivos XLSX de 2015 a 2023, o `openpyxl` emitiu o aviso:

`Cannot parse header or footer so it will be ignored`

O aviso se refere ao cabecalho ou rodape de impressao do workbook e nao impediu a leitura das celulas utilizadas na ingestao.

A validacao independente posterior confirmou os Parquets produzidos, inclusive quanto a rastreabilidade e a correspondencia do SHA-256 com os arquivos RAW.

#### Rede e localizacao

Embora a auditoria tenha confirmado a existencia do agregado `Publica + Localizacao Total`, essa selecao nao e aplicada na Bronze.

Ela sera aplicada somente na Silver, conforme `docs/definicao_rede_publica.md`.

---

### 7.5 PND 2025

A PND 2025 esta representada no RAW por tres arquivos:

- `Dicionario_arquivos_variaveis_PND_2025.xlsx`;
- `microdados2025_parametros_itens.xlsx`;
- `microdados2025_pnd_arq1.txt`.

#### Selecao da fonte principal

O arquivo `microdados2025_pnd_arq1.txt` e a tabela principal de registros individuais utilizada para a ingestao Bronze.

Os dois arquivos XLSX permanecem no RAW como fontes auxiliares de documentacao e parametros:

- o dicionario apoia a interpretacao das variaveis;
- a planilha de parametros de itens preserva informacoes tecnicas de calibracao e itens.

Eles nao serao convertidos, nesta etapa, em tabelas factuais da Bronze porque a ingestao analitica principal da PND utiliza o arquivo individual. Permanecem preservados integralmente no RAW e poderao ser utilizados em etapas posteriores se alguma transformacao exigir essas informacoes.

Essa decisao evita criar tabelas Bronze sem uso definido apenas por existirem no pacote de microdados, sem perder a rastreabilidade ou a disponibilidade dos arquivos originais.

#### Estrutura tecnica confirmada do TXT

A verificacao tecnica do arquivo `microdados2025_pnd_arq1.txt` confirmou:

- tamanho: `371.539.465 bytes`;
- codificacao: `utf-8`;
- delimitador: `;`;
- 26 colunas;
- 1.087.360 linhas fisicas;
- 1.087.359 registros de dados, descontada a linha de cabecalho;
- SHA-256: `b15968a19e309bca6b63c6f6d7af094efdc13d900645dc7385872a6a50dd7baf`.

O cabecalho possui, na ordem original:

`NU_ANO;CO_GRUPO;CO_MUNICIPIO_PROVA;SG_UF_MUNICIPIO_PROVA;TP_INSCRICAO_PND;IN_REAPLICACAO;CO_CADERNO;DS_VT_GAB_OBJ;DS_VT_ESC_OBJ;DS_VT_ACE_OBJ;TP_PRES;TP_SIT_DISC;PROFICIENCIA;NT_OBJ;NT_DIS;NT_GER;QT_ACERTOS;CO_RS_I1;CO_RS_I2;CO_RS_I3;CO_RS_I4;CO_RS_I5;CO_RS_I6;CO_RS_I7;CO_RS_I8;CO_RS_I9`

#### Preservacao do cabecalho

Para manter a mesma logica de rastreabilidade adotada nas demais fontes Bronze, o TXT sera lido com `header=None`.

Assim, a linha fisica do cabecalho sera preservada como a primeira linha da Bronze:

- `_indice_cabecalho_origem = 0`;
- `_linha_origem = 1`.

Consequentemente:

- registros substantivos de dados: `1.087.359`;
- linhas Bronze esperadas, incluindo o cabecalho preservado: `1.087.360`.

Essa diferenca de uma linha nao representa criacao de um participante adicional. Ela decorre exclusivamente da preservacao da linha fisica de cabecalho como parte da rastreabilidade da fonte.

#### Tipagem e valores especiais

As 26 colunas da fonte serao armazenadas como texto tecnico na Bronze, utilizando `col_001` a `col_026`.

O uso de texto evita interpretar semanticamente, nesta camada:

- numeros com virgula decimal;
- codigos;
- vetores de respostas;
- indicadores de presenca;
- notas;
- proficiencia.

O literal `NA` sera preservado como texto quando estiver presente na fonte.

Somente campos realmente vazios serao representados como valores ausentes.

A conversao de `PROFICIENCIA`, `NT_OBJ`, `NT_DIS`, `NT_GER`, `QT_ACERTOS` e demais variaveis para tipos analiticos ocorrera na Silver.

#### Leitura em blocos

Como o TXT possui aproximadamente 371,5 MB e mais de um milhao de registros, a ingestao sera realizada em blocos (`chunks`), e nao por carregamento integral do arquivo em memoria.

Essa e uma decisao de eficiencia operacional e nao altera a informacao substantiva.

Cada bloco sera convertido para o mesmo esquema Bronze e escrito sequencialmente em um unico arquivo Parquet com compressao Snappy.

Como o `pandas.read_csv(..., chunksize=...)` preserva no indice interno de cada bloco a posicao acumulada do arquivo, cada chunk sera submetido a `reset_index(drop=True)` antes da criacao dos metadados tecnicos. Alem disso, as `Series` utilizadas na insercao dos metadados serao criadas com o mesmo indice do chunk.

Essa regra evita o alinhamento automatico por indice do pandas, que poderia produzir valores ausentes nos metadados a partir do segundo bloco mesmo quando os valores atribuidos estivessem corretos. Trata-se exclusivamente de uma correcao tecnica de escrita por blocos; nao altera nenhuma variavel substantiva da PND.

#### Populacao preservada

Na Bronze serao preservados todos os registros do arquivo principal.

Nao sera aplicada nessa camada a populacao analitica de 759.140 participantes.

Tambem nao serao removidos:

- registros `TP_PRES = 888`;
- registros `TP_PRES = 555` sem resultados completos;
- registros apenas por nao integrarem posteriormente a populacao analitica.

A Bronze preservara a granularidade individual da prova.

A definicao da populacao analitica sera aplicada somente na Silver.

---

## 8. Granularidade

A Bronze devera manter a granularidade disponivel na fonte selecionada.

Nao sera utilizada uma granularidade unica artificial para todas as bases.

Exemplos:

- SAEB pode possuir dados agregados por UF ou em nivel escolar, conforme a edicao;
- IDEB possui tabelas agregadas;
- Rendimento e TDI possuem agregados geograficos;
- PND possui registros individuais da prova.

A harmonizacao de granularidade sera feita somente quando necessaria para a analise.

---

## 9. Estrutura prevista

```text
data/
├── raw/
│   ├── ideb/
│   ├── saeb/
│   ├── rendimento/
│   ├── tdi/
│   └── pnd/
│
└── bronze/
    ├── ideb/
    ├── saeb/
    ├── rendimento/
    ├── tdi/
    └── pnd/
```

Os arquivos Bronze serao preferencialmente armazenados como:

`.parquet`

---

## 10. Validacoes da Bronze

Cada processo de ingestao devera verificar pelo menos:

- existencia do arquivo de origem;
- existencia de registros;
- quantidade de linhas lidas;
- quantidade de colunas;
- ano ou edicao esperada, quando aplicavel;
- arquivo e aba de origem registrados;
- presenca das colunas tecnicas obrigatorias;
- consistencia de `_linha_origem`, quando aplicavel;
- integridade do arquivo RAW por comparacao do SHA-256;
- sucesso da gravacao e releitura do Parquet.

A Bronze nao devera considerar uma ingestao valida apenas porque o arquivo foi criado.

Sempre que aplicavel, a validacao final devera ser executada por script independente do script de ingestao.

Essa separacao reduz o risco de a propria rotina que produziu o arquivo considerar automaticamente sua saida valida.

O pipeline devera produzir mensagens de controle.

Exemplo:

```text
[OK] Rendimento 2023
Arquivo: TX_REND_BRASIL_REGIOES_UFS_2023.xlsx
Linhas lidas: 596
Colunas da fonte: 58
Destino: data/bronze/rendimento/rendimento_2023.parquet
```

---

## 11. Reprodutibilidade

Nenhum arquivo da Bronze devera depender de transformacao manual em Excel ou Power BI.

A partir dos arquivos existentes em:

`data/raw/`

todo o conteudo de:

`data/bronze/`

devera poder ser reconstruido executando o pipeline.

Isso significa que a Bronze e descartavel e reproduzivel.

A camada Raw nao e descartavel.

---

## 12. Regra de falha

Se o pipeline nao reconhecer corretamente:

- uma aba;
- um cabecalho ou estrutura;
- um ano;
- uma codificacao;
- um delimitador;
- uma estrutura esperada;

a execucao devera falhar de forma explicita.

Nao devera selecionar silenciosamente outra aba, codificacao ou estrutura semelhante.

E preferivel interromper o pipeline do que produzir dados aparentemente validos a partir de uma interpretacao incorreta da fonte.

---

## 13. Separacao de responsabilidades

O projeto adotara a seguinte divisao:

### RAW

Arquivo original, imutavel.

### BRONZE

Arquivo original estruturado e rastreavel, com minima transformacao tecnica.

### SILVER

Dados limpos, tipados, normalizados e semanticamente harmonizados.

### GOLD

Dados organizados para analise, indicadores, modelo dimensional e Power BI.

A regra pode ser resumida como:

```text
RAW
arquivo como publicado
       ↓
BRONZE
arquivo estruturado e rastreavel
       ↓
SILVER
dado limpo e harmonizado
       ↓
GOLD
dado analitico
```

---

## 14. Resultado da ingestao — Rendimento Escolar

A ingestao Bronze do Rendimento Escolar foi executada para as 17 edicoes compreendidas entre 2007 e 2023.

Apos a geracao dos arquivos Parquet, foi realizada validacao independente por meio de:

`src/bronze/validar_bronze_rendimento.py`

### Resultado

- arquivos RAW esperados: 17;
- arquivos Parquet encontrados: 17;
- periodo: 2007–2023;
- total de linhas armazenadas na Bronze: 9.012;
- arquivos vazios: nenhum;
- divergencias de ano de referencia: nenhuma;
- divergencias no arquivo de origem: nenhuma;
- ausencia de colunas tecnicas obrigatorias: nenhuma;
- duplicidades em `_linha_origem`: nenhuma;
- divergencias entre o SHA-256 armazenado na Bronze e o arquivo RAW: nenhuma.

Todos os arquivos foram aprovados na validacao independente.

### Quantidade de linhas por edicao

| Ano | Linhas | Colunas da fonte |
|---:|---:|---:|
| 2007 | 480 | 59 |
| 2008 | 480 | 58 |
| 2009 | 483 | 58 |
| 2010 | 483 | 58 |
| 2011 | 486 | 58 |
| 2012 | 486 | 58 |
| 2013 | 486 | 58 |
| 2014 | 486 | 58 |
| 2015 | 489 | 58 |
| 2016 | 487 | 59 |
| 2017 | 595 | 58 |
| 2018 | 595 | 58 |
| 2019 | 595 | 58 |
| 2020 | 595 | 58 |
| 2021 | 595 | 58 |
| 2022 | 595 | 58 |
| 2023 | 596 | 58 |

### Conclusao

A camada Bronze do Rendimento Escolar foi considerada valida.

Os arquivos originais foram convertidos para Parquet sem aplicacao de filtros analiticos ou harmonizacoes semanticas.

A rastreabilidade foi preservada por arquivo, aba, ano, linha de origem e SHA-256.

Status:

`RENDIMENTO ESCOLAR — BRONZE ✅`

---

## 15. Resultado da ingestao — TDI

A ingestao Bronze da Taxa de Distorcao Idade-Serie foi executada para as 17 edicoes compreendidas entre 2007 e 2023 por meio de:

`src/bronze/ingest_tdi.py`

Apos a geracao dos arquivos Parquet, foi realizada validacao independente por meio de:

`src/bronze/validar_bronze_tdi.py`

### Resultado

- arquivos RAW esperados: 17;
- arquivos Parquet encontrados: 17;
- periodo: 2007–2023;
- total de linhas armazenadas na Bronze: 8.989;
- arquivos vazios: nenhum;
- divergencias de ano de referencia: nenhuma;
- divergencias no arquivo de origem: nenhuma;
- ausencia de colunas tecnicas obrigatorias: nenhuma;
- duplicidades em `_linha_origem`: nenhuma;
- divergencias na sequencia das colunas tecnicas: nenhuma;
- divergencias entre o SHA-256 armazenado na Bronze e o arquivo RAW: nenhuma.

Todos os arquivos foram aprovados na validacao independente.

### Quantidade de linhas por edicao

| Ano | Linhas | Colunas da fonte |
|---:|---:|---:|
| 2007 | 478 | 22 |
| 2008 | 480 | 22 |
| 2009 | 482 | 22 |
| 2010 | 482 | 22 |
| 2011 | 486 | 22 |
| 2012 | 484 | 22 |
| 2013 | 486 | 22 |
| 2014 | 485 | 22 |
| 2015 | 486 | 23 |
| 2016 | 484 | 22 |
| 2017 | 593 | 21 |
| 2018 | 592 | 21 |
| 2019 | 594 | 21 |
| 2020 | 594 | 21 |
| 2021 | 594 | 21 |
| 2022 | 594 | 21 |
| 2023 | 595 | 21 |

### Conclusao

A camada Bronze da TDI foi considerada valida.

Os arquivos originais foram convertidos para Parquet sem aplicacao do filtro analitico de rede publica, selecao de localizacao, harmonizacao das etapas ou alteracao dos valores publicados.

A rastreabilidade foi preservada por arquivo, aba, ano, linha de origem e SHA-256.

Status:

`TDI — BRONZE ✅`

---

## 16. Resultado da ingestao — IDEB

A ingestao Bronze do Indice de Desenvolvimento da Educacao Basica foi realizada a partir do arquivo:

`divulgacao_regioes_ufs_ideb.xlsx`

Foram preservadas integralmente as tres abas existentes no arquivo:

- `UF e Regioes (AI)`;
- `UF e Regioes (AF)`;
- `UF e Regioes (EM)`.

Cada aba foi persistida separadamente em Parquet.

Apos a ingestao, foi realizada validacao independente por meio de:

`src/bronze/validar_bronze_ideb.py`

### Resultado

| Etapa de origem | Aba | Linhas Bronze | Colunas da fonte |
|---|---|---:|---:|
| AI | `UF e Regioes (AI)` | 150 | 120 |
| AF | `UF e Regioes (AF)` | 149 | 110 |
| EM | `UF e Regioes (EM)` | 117 | 110 |

Foram encontrados os tres arquivos Parquet esperados:

- `ideb_ai.parquet`;
- `ideb_af.parquet`;
- `ideb_em.parquet`.

Nenhum dos arquivos estava vazio.

A validacao confirmou:

- identificacao correta da fonte;
- arquivo de origem correto;
- aba de origem correta;
- etapa de origem correta;
- presenca dos metadados tecnicos;
- consistencia de `_linha_origem`;
- quantidade esperada de colunas da fonte;
- sequencia das colunas tecnicas `col_001`, `col_002`, etc.;
- presenca dos marcadores tecnicos esperados na linha de cabecalho;
- correspondencia entre o SHA-256 armazenado na Bronze e o arquivo RAW.

O SHA-256 confirmado para o arquivo de origem foi:

`e7cdb12afa3c0d2e4435aa914316d84e5ac1e31865fa56ad238ad48f778b1bd5`

### Preservacao da estrutura historica

O workbook contem informacoes fora do periodo analitico definido para o projeto, podendo incluir dados anteriores a 2007 e edicoes posteriores preservadas na fonte fisica.

Essas informacoes foram mantidas na Bronze.

Tambem foi preservada a aba correspondente ao Ensino Medio, embora o recorte analitico posterior utilize apenas Anos Iniciais e Anos Finais do Ensino Fundamental.

Nao foram aplicados na Bronze:

- filtro de 2007–2023;
- exclusao de 2005;
- exclusao do Ensino Medio;
- filtro da rede publica;
- normalizacao de `Publica (4)` para `PUBLICA`;
- remocao de informacoes de aprovacao, SAEB ou metas;
- transformacao da estrutura historica em formato analitico.

### Conclusao

A camada Bronze do IDEB foi considerada valida.

A estrutura original do workbook foi preservada em tres arquivos Parquet rastreaveis ate o arquivo, a aba e a linha de origem.

Status:

`IDEB — BRONZE ✅`

---

## 17. Resultado da ingestao — SAEB

A ingestao Bronze do Sistema de Avaliacao da Educacao Basica cobre 9 edicoes entre 2007 e 2023.

Apos a extensao metodologica de 2023, essas 9 edicoes sao representadas por **10 arquivos Parquet**, porque 2023 possui duas fontes oficiais preservadas separadamente.

A ingestao principal foi realizada por meio de:

`src/bronze/saeb/ingest_saeb.py`

e validada independentemente por:

`src/bronze/saeb/validar_bronze_saeb.py`

A fonte agregada adicional de 2023 e ingerida por:

`src/bronze/saeb/ingest_saeb_resultados_2023.py`

e validada independentemente por:

`src/bronze/saeb/validar_bronze_saeb_resultados_2023.py`

### Resultado

| Ano | Arquivo de origem | Aba | Granularidade | Linhas Bronze | Colunas da fonte |
|---:|---|---|---|---:|---:|
| 2007 | `MEDIA_UF_2007.xlsx` | `MEDIA_ESTADOS` | UF | 269 | 12 |
| 2009 | `MEDIA_UF_2009.xlsx` | `MEDIA_ESTADOS` | UF | 269 | 12 |
| 2011 | `TS_RESULTADO_UF_2011.csv` | nao se aplica | UF | 4.375 | 13 |
| 2013 | `TS_UF_2013.xlsx` | `UF` | UF | 1.706 | 10 |
| 2015 | `TS_UF_2015.xlsx` | `UFs` | UF | 1.706 | 10 |
| 2017 | `TS_UF_2017.xlsx` | `TS_UF` | UF | 1.702 | 70 |
| 2019 | `TS_UF_2019.xlsx` | `Estados` | UF | 1.551 | 156 |
| 2021 | `TS_UF_2021.xlsx` | `Estados` | UF | 1.517 | 156 |
| 2023 | `TS_ESCOLA_2023.csv` | nao se aplica | ESCOLA | 70.152 | 137 |
| 2023 | `Resultados_Saeb_2023_Brasil_Estados_Municipios.xlsb` | `Estados` | UF | 1.553 | 177 |

O conjunto original das nove Bronzes totalizava `83.247 linhas`.

A inclusao da Bronze agregada oficial de 2023 acrescentou 1.553 linhas.

O total atual das tabelas Bronze do SAEB e:

`84.800 linhas`

Esse total representa linhas fisicas preservadas em 10 Parquets e nao deve ser interpretado como quantidade de observacoes analiticas comparaveis entre si, pois as fontes possuem granularidades e estruturas distintas.

### Validacao das nove Bronzes originais

A validacao confirmou para as nove tabelas originais:

- presenca dos Parquets esperados;
- ausencia de arquivos vazios;
- quantidade esperada de linhas e colunas;
- identificacao correta do arquivo e da aba;
- granularidade de origem;
- consistencia de `_ano_referencia`, `_indice_cabecalho_origem` e `_linha_origem`;
- sequencia das colunas tecnicas;
- marcadores estruturais esperados;
- correspondencia entre SHA-256 da Bronze e o RAW atual.

### Validacao da Bronze agregada oficial de 2023

A Bronze adicional:

`data/bronze/saeb/saeb_2023_resultados_uf.parquet`

foi comparada diretamente com:

`data/raw/saeb/Resultados_Saeb_2023_Brasil_Estados_Municipios.xlsb`

na aba `Estados`.

A validacao independente confirmou:

- SHA-256: `e593b547f608b2377ac3d90491d02097326d3b276d4539a93201922466207a01`;
- 1.553 linhas RAW/Bronze;
- 177 colunas de origem;
- 177 colunas de origem persistidas como texto;
- 274.881 celulas comparadas RAW ↔ Bronze;
- reproducao integral do conteudo da aba apos normalizacao textual;
- proveniencia de arquivo, aba, linha, cabecalho e granularidade;
- `_indice_cabecalho_origem = 0`;
- `_linha_origem` de 1 a 1.553;
- `_granularidade_origem = UF`.

Tambem foi validado o estrato oficial `Total - Federal, Estadual e Municipal`, com `LOCALIZACAO = Total` e `CAPITAL = Total`:

- 27 UFs;
- nenhuma duplicidade;
- nenhum valor ausente nas quatro proficiencias utilizadas pela Silver.

Faixas observadas:

- `MEDIA_5_LP`: 185,22 a 225,51;
- `MEDIA_5_MT`: 193,75 a 239,52;
- `MEDIA_9_LP`: 230,61 a 265,44;
- `MEDIA_9_MT`: 230,17 a 264,71.

Resultado:

`BRONZE SAEB 2023 RESULTADOS OFICIAIS DE UF: OK`

### Justificativa da extensao de 2023

A Bronze escolar de 2023 foi mantida intacta.

Durante a auditoria da Silver, foi testada a hipotese de reproduzir os resultados estaduais utilizando as medias escolares ponderadas por `NU_PRESENTES`.

Foram comparados `27 UFs × 2 etapas × 2 disciplinas = 108 valores`.

A comparacao apresentou:

- `0/108` coincidencias apos arredondamento para duas casas;
- diferenca absoluta media: `1,389714`;
- diferenca absoluta mediana: `1,092905`;
- maior diferenca absoluta: `6,150034`.

Por isso, `NU_PRESENTES` foi rejeitado como regra de reconstrucao do resultado estadual.

A solucao adotada nao foi agregar as escolas na Bronze, mas incorporar a publicacao oficial agregada de UF como uma segunda fonte Bronze de 2023.

### Diferenca estrutural entre 2013 e 2015

Em 2013:

- `_indice_cabecalho_origem = 3`;
- a primeira linha semantica do cabecalho corresponde a `_linha_origem = 4`.

Em 2015:

- `_indice_cabecalho_origem = 2`;
- a primeira linha semantica do cabecalho corresponde a `_linha_origem = 3`.

Essa diferenca permanece explicitamente documentada e preservada.

### Codificacao e delimitador dos CSV

Foram utilizados:

- 2011: `utf-8` com delimitador `;`;
- 2023 escolar: `cp1252` com delimitador `;`.

### Granularidade

A Bronze preserva as granularidades efetivamente publicadas:

- 2007 a 2021: UF;
- 2023 escolar: ESCOLA;
- 2023 agregado oficial: UF.

A tabela escolar de 2023 nao e agregada pela Bronze.

A tabela agregada de 2023 e outra publicacao oficial, ingerida diretamente e sem reconstrucao.

### Conclusao

A camada Bronze do SAEB foi considerada valida apos a extensao controlada de 2023.

A rastreabilidade foi preservada por arquivo, aba, ano, granularidade, linha de origem e SHA-256.

Status:

`SAEB — BRONZE ✅`

---

## 18. Resultado da ingestao — PND 2025

A ingestao Bronze da PND 2025 foi executada por meio de:

`src/bronze/ingest_pnd.py`

A validacao independente foi executada por meio de:

`src/bronze/validar_bronze_pnd.py`

### Fonte principal

Foi utilizada como tabela factual da Bronze:

`microdados2025_pnd_arq1.txt`

Os arquivos auxiliares:

- `Dicionario_arquivos_variaveis_PND_2025.xlsx`;
- `microdados2025_parametros_itens.xlsx`;

permanecem preservados no RAW como documentacao e parametros tecnicos.

### Resultado da ingestao

A execucao confirmou:

- codificacao: `utf-8`;
- delimitador: `;`;
- 26 colunas na fonte;
- 1.087.359 registros de dados;
- 1.087.360 linhas Bronze, incluindo a linha fisica do cabecalho preservada;
- granularidade: `REGISTRO_INDIVIDUAL`;
- SHA-256 do RAW: `b15968a19e309bca6b63c6f6d7af094efdc13d900645dc7385872a6a50dd7baf`.

A ingestao foi processada em 11 chunks:

- 10 chunks de 100.000 linhas;
- 1 chunk final de 87.360 linhas.

O arquivo produzido foi:

`data/bronze/pnd/pnd_2025.parquet`

### Validacao independente

A validacao confirmou:

- correspondencia do SHA-256 com o arquivo RAW;
- presenca das 26 colunas esperadas;
- preservacao do cabecalho fisico;
- sequencia contigua de `_linha_origem`;
- consistencia dos metadados de rastreabilidade;
- granularidade `REGISTRO_INDIVIDUAL`;
- total de 1.087.360 linhas na Bronze.

O resultado final foi:

`BRONZE DA PND 2025: OK`

### Correcao tecnica durante a implementacao

Na primeira execucao da validacao foi detectada inconsistencia em `_fonte` a partir dos chunks posteriores ao primeiro.

A causa foi o alinhamento automatico por indice do pandas durante a insercao das `Series` de metadados tecnicos.

A correcao aplicada foi:

- `reset_index(drop=True)` em cada chunk antes da criacao dos metadados;
- criacao das `Series` tecnicas com `index=chunk.index`.

Apos a correcao, a ingestao foi refeita integralmente e a validacao independente passou em todos os controles.

Essa correcao nao alterou nenhuma variavel substantiva da PND; afetava exclusivamente o preenchimento tecnico dos metadados da Bronze.

### Conclusao

A camada Bronze da PND 2025 foi considerada valida.

Todos os registros do arquivo principal foram preservados, sem aplicacao da populacao analitica de 759.140 participantes e sem exclusao de registros por condicao de presenca ou completude dos resultados.

Status:

`PND 2025 — BRONZE ✅`

---

## 19. Situacao atual da camada Bronze

Ate esta atualizacao:

| Fonte | Ingestao | Validacao independente |
|---|---|---|
| Rendimento Escolar | ✅ concluida | ✅ concluida |
| TDI | ✅ concluida | ✅ concluida |
| IDEB | ✅ concluida | ✅ concluida |
| SAEB | ✅ concluida | ✅ concluida |
| PND 2025 | ✅ concluida | ✅ concluida |

As decisoes metodologicas documentadas nas auditorias e em `docs/definicao_rede_publica.md` sao aplicadas na Silver. Na Bronze permanecem apenas transformacoes tecnicas, preservacao estrutural e metadados de rastreabilidade. A inclusao do resultado agregado oficial do SAEB 2023 nao altera essa separacao: trata-se de uma segunda fonte oficial, nao de uma agregacao calculada na Bronze.

---

## 20. Conclusao

A camada Bronze funciona como fronteira entre os arquivos heterogeneos publicados pelas fontes e o pipeline analitico.

Seu principal compromisso e com:

- fidelidade;
- rastreabilidade;
- reprodutibilidade;
- minima transformacao semantica.

A Bronze nao e a camada em que as diferentes fontes se tornam semanticamente iguais.

Seu papel e produzir representacoes estruturadas, verificaveis e reconstruiveis a partir dos arquivos RAW.

Com a conclusao e validacao independente de Rendimento Escolar, TDI, IDEB, SAEB e PND 2025, a camada Bronze do projeto encontra-se integralmente concluida.

A etapa subsequente do pipeline e a camada Silver, responsavel pelas harmonizacoes semanticas, recortes analiticos, normalizacoes de rede, etapa, indicadores e granularidade. A camada Bronze permanece encerrada e reproduzivel, salvo a incorporacao futura de nova fonte oficial que exija extensao documentada.

---

## 21. Historico de atualizacao

| Data | Alteracao |
|---|---|
| 18/08/2026 | Definicao inicial da arquitetura da camada Bronze |
| 18/08/2026 | Definidos limites entre Raw, Bronze, Silver e Gold |
| 18/08/2026 | Definida adocao de Parquet e metadados de rastreabilidade |
| 18/08/2026 | Documentada a tipagem tecnica das celulas na Bronze |
| 18/08/2026 | Documentadas irregularidades nos nomes de abas do Rendimento Escolar |
| 18/08/2026 | Concluida e validada independentemente a ingestao Bronze do Rendimento Escolar (2007–2023) |
| 18/08/2026 | Concluida e validada independentemente a ingestao Bronze da TDI (2007–2023) |
| 18/08/2026 | Concluida e validada independentemente a ingestao Bronze do IDEB |
| 18/08/2026 | Reorganizada a documentacao para separar decisoes metodologicas, particularidades das fontes e resultados de execucao |
| 18/08/2026 | Corrigida a selecao das fontes SAEB: agregados oficiais por UF confirmados de 2007 a 2021 e fonte escolar apenas para 2023 |
| 18/08/2026 | Confirmados delimitador e codificacao dos CSV selecionados do SAEB: UTF-8/`;` em 2011 e CP1252/`;` em 2023 |
| 18/08/2026 | Corrigida a referencia estrutural do cabecalho SAEB 2015 para indice 2 (linha de origem 3), conforme diferenca auditada em relacao a 2013 |
| 18/08/2026 | Concluida e validada independentemente a ingestao Bronze do SAEB (2007–2023), com 9 edicoes e 83.247 linhas |
| 18/08/2026 | Confirmada a estrutura tecnica da PND 2025 e definida a ingestao Bronze em blocos do TXT principal: UTF-8, `;`, 26 colunas, 1.087.359 registros e preservacao da linha fisica de cabecalho |
| 18/08/2026 | Corrigida a escrita em chunks da PND para resetar o indice de cada bloco e impedir alinhamento automatico do pandas nos metadados tecnicos |
| 18/08/2026 | Concluida e validada independentemente a ingestao Bronze da PND 2025, com 1.087.359 registros de dados e 1.087.360 linhas Bronze incluindo o cabecalho preservado |
| 18/08/2026 | Camada Bronze concluida integralmente para Rendimento Escolar, TDI, IDEB, SAEB e PND 2025 |
| 19/08/2026 | Comparacao da Bronze escolar do SAEB 2023 com os resultados estaduais oficiais mostrou 0/108 coincidencias quando as medias escolares foram ponderadas por `NU_PRESENTES`; a regra de agregacao foi rejeitada |
| 19/08/2026 | Incorporado ao RAW `Resultados_Saeb_2023_Brasil_Estados_Municipios.xlsb` e criada uma segunda Bronze de 2023 em granularidade UF, preservando separadamente a Bronze escolar existente |
| 19/08/2026 | Bronze agregada oficial do SAEB 2023 validada integralmente: 1.553 linhas, 177 colunas, 274.881 celulas RAW ↔ Bronze e SHA-256 `e593b547f608b2377ac3d90491d02097326d3b276d4539a93201922466207a01` |
| 19/08/2026 | Atualizado o total do SAEB Bronze para 10 Parquets e 84.800 linhas fisicas, mantendo 9 edicoes e duas fontes oficiais distintas em 2023 |
