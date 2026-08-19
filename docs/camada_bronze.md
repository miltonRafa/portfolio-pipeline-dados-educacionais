# Camada Bronze — Ingestão dos Dados Educacionais

## 1. Objetivo

A camada Bronze é a primeira camada de dados processados do projeto.

Sua função é transformar os arquivos originais armazenados em `data/raw/` em estruturas legíveis e reutilizáveis pelo pipeline, preservando o máximo possível da informação da fonte.

A Bronze não é responsável por harmonizar conceitos entre bases.

Portanto, nesta etapa não serão aplicadas decisões analíticas como:

- seleção definitiva da rede pública;
- padronização de etapas de ensino;
- cálculo de médias por UF;
- consolidação de categorias;
- exclusão de registros apenas por não integrarem o recorte analítico final;
- reconstrução de indicadores;
- alteração dos valores publicados pela fonte.

Essas transformações pertencem às camadas posteriores.

---

## 2. Relação entre Raw e Bronze

### Raw

A pasta:

`data/raw/`

contém os arquivos originais obtidos das fontes.

Esses arquivos são considerados imutáveis.

O pipeline não deverá sobrescrevê-los, renomeá-los ou modificar seu conteúdo.

### Bronze

A pasta:

`data/bronze/`

conterá representações estruturadas dos arquivos originais.

A Bronze poderá:

- ler XLS, XLSX, CSV e TXT;
- identificar explicitamente a aba utilizada;
- identificar a linha de cabeçalho ou referência estrutural;
- converter tecnicamente os dados para DataFrame;
- remover apenas linhas completamente vazias produzidas pelo layout da planilha;
- adicionar metadados técnicos de origem;
- persistir os resultados em Parquet.

A informação substantiva da fonte deverá ser preservada.

---

## 3. Por que utilizar Parquet

Os arquivos originais apresentam diferentes formatos:

- XLS;
- XLSX;
- CSV;
- TXT.

A camada Bronze utilizará preferencialmente o formato:

`Parquet`

porque ele:

- preserva tipos de dados de forma mais eficiente que CSV;
- possui leitura e escrita rápidas;
- ocupa menos espaço em disco;
- é adequado para pipelines analíticos;
- funciona bem com Python, Pandas, DuckDB e ferramentas de engenharia de dados;
- reduz problemas recorrentes de delimitador e codificação encontrados em CSV.

O uso de Parquet na Bronze não altera o significado dos dados.

Ele apenas padroniza o formato técnico de armazenamento.

---

## 4. Metadados de rastreabilidade

Cada tabela Bronze deverá possuir, quando aplicável, metadados técnicos que permitam rastrear o registro até sua origem.

Os campos adotados no projeto são:

- `_fonte`;
- `_sha256_arquivo`;
- `_arquivo_origem`;
- `_aba_origem`;
- `_ano_referencia`;
- `_indice_cabecalho_origem`;
- `_linha_origem`.

Algumas fontes poderão exigir metadados adicionais.

No IDEB foi acrescentado:

- `_etapa_origem`.

No SAEB foi acrescentado:

- `_granularidade_origem`.

Na PND 2025 também será utilizado:

- `_granularidade_origem`.

No SAEB, esse campo registra a granularidade efetivamente preservada em cada tabela Bronze. Em 2023 coexistem duas tabelas oficiais preservadas separadamente: uma em nível de `ESCOLA` e outra em nível de `UF`.

Na PND, `_granularidade_origem = REGISTRO_INDIVIDUAL` registra que o arquivo principal preserva registros individuais da prova.

O campo não harmoniza a granularidade; apenas torna explícita a granularidade efetivamente preservada na Bronze.

Esses campos não substituem variáveis originais da fonte.

Sua finalidade é:

- identificar a fonte e o arquivo exato utilizado;
- registrar a aba de origem, quando aplicável;
- registrar o ano ou edição técnica do arquivo;
- permitir localização da linha original;
- registrar a referência estrutural utilizada pela ingestão;
- permitir verificação de integridade do RAW por SHA-256.

Exemplo:

| _fonte | _arquivo_origem | _ano_referencia |
|---|---|---:|
| RENDIMENTO | TX_REND_BRASIL_REGIOES_UFS_2023.xlsx | 2023 |

O campo `_sha256_arquivo` registra o hash do arquivo de origem utilizado na ingestão.

A validação independente da Bronze deverá comparar esse valor com o hash calculado diretamente a partir do arquivo RAW.

---

## 5. O que não será feito na Bronze

A Bronze não deverá:

1. substituir `Publico` por `PUBLICA`;
2. transformar `Pública (4)` em `PUBLICA`;
3. agregar Federal, Estadual e Municipal;
4. selecionar apenas Anos Iniciais ou Anos Finais;
5. converter nomes de estados para siglas;
6. excluir rede privada;
7. remover registros apenas porque não serão utilizados no dashboard;
8. calcular médias analíticas;
9. imputar valores ausentes;
10. recalcular indicadores;
11. aplicar a população analítica da PND;
12. alterar os arquivos originais.

Essas operações pertencem principalmente à Silver ou à Gold.

---

## 6. Tratamento permitido

Algumas operações técnicas são necessárias para tornar os arquivos utilizáveis.

São permitidas:

- identificação da aba correta;
- identificação da linha real de cabeçalho ou referência estrutural;
- remoção de linhas completamente vazias geradas pela estrutura da planilha;
- leitura correta de delimitador, decimal e codificação;
- conversão técnica de arquivos para DataFrame;
- criação de nomes técnicos temporários quando a biblioteca de leitura exigir;
- conversão técnica de células para texto quando necessária à persistência estável da estrutura;
- adição de metadados de origem;
- persistência em Parquet.

Essas operações devem permanecer distinguíveis de transformações semânticas.

### 6.1 Tipagem técnica das células na Bronze

Algumas planilhas de origem possuem títulos, cabeçalhos hierárquicos, códigos técnicos e valores numéricos ocupando as mesmas colunas.

Por esse motivo, na ingestão de planilhas cuja estrutura completa é preservada, as células de origem poderão ser armazenadas como texto na camada Bronze.

Essa conversão possui finalidade exclusivamente técnica: garantir que a estrutura heterogênea da planilha possa ser persistida de forma estável em Parquet sem perda dos valores publicados.

A conversão para tipos analíticos, como inteiro, decimal ou categoria, será realizada somente na camada Silver, após a identificação explícita da estrutura de cada fonte.

Valores especiais existentes na fonte, como `--`, não serão convertidos automaticamente em nulos na Bronze.

As células realmente vazias permanecerão como valores ausentes.

A Bronze também preservará a linha de origem para permitir rastreabilidade até a posição original da informação na planilha.

---

## 7. Particularidades das fontes

### 7.1 IDEB

O arquivo de origem utilizado é:

`divulgacao_regioes_ufs_ideb_2023.xlsx`

Ele possui três abas correspondentes às etapas:

- `UF e Regiões (AI)`;
- `UF e Regiões (AF)`;
- `UF e Regiões (EM)`.

Diferentemente das bases anuais de Rendimento Escolar e TDI, o arquivo do IDEB concentra em um único workbook a série histórica de diferentes edições do indicador.

As planilhas contêm informações anteriores ao recorte analítico do projeto, incluindo dados de 2005.

#### Decisão de ingestão

A Bronze preserva integralmente as três abas do arquivo de origem, inclusive os dados referentes a 2005 e a aba do Ensino Médio.

Não são aplicados na Bronze:

- filtro do período 2007–2023;
- exclusão do Ensino Médio;
- seleção apenas dos Anos Iniciais e Anos Finais;
- filtro da rede pública;
- normalização de categorias como `Pública (4)`;
- seleção exclusiva das colunas do IDEB;
- remoção das colunas de aprovação, SAEB ou metas existentes no workbook.

A justificativa é que essas operações modificariam semanticamente o conteúdo publicado e pertencem às etapas posteriores do pipeline.

A Silver será responsável por aplicar o recorte analítico do projeto, selecionando:

- período de 2007 a 2023;
- Anos Iniciais e Anos Finais;
- definição metodológica de rede pública registrada em `docs/definicao_rede_publica.md`.

Na Bronze, cada aba é persistida separadamente em Parquet, preservando sua estrutura e sua identificação de origem.

#### Cabeçalho hierárquico do IDEB

As planilhas do IDEB não possuem um cabeçalho simples em uma única linha.

A estrutura auditada utiliza:

- índice 6: identificação dos grandes blocos de indicadores;
- índice 7: subdivisões das notas do SAEB;
- índice 8: séries ou anos escolares e demais subdivisões;
- índice 9: nomes técnicos das variáveis disponibilizados pelo Inep.

A Bronze preserva todas essas linhas.

Para fins de rastreabilidade técnica, `_indice_cabecalho_origem = 9` registra a linha utilizada como referência técnica pelo código.

Como `_linha_origem` utiliza numeração iniciada em um, o índice interno `9` corresponde à linha de origem `10`.

Esse registro não significa que as linhas anteriores do cabeçalho sejam descartadas.

A interpretação e reconstrução semântica do cabeçalho ocorrerão somente na Silver.

#### Ano de referência técnico

No IDEB:

`_ano_referencia = 2023`

representa a edição do arquivo de divulgação utilizada na ingestão.

Esse campo não significa que todas as observações armazenadas sejam referentes a 2023.

Os anos substantivos da série histórica permanecem nas células da fonte e serão transformados em dimensão temporal analítica na Silver.

---

### 7.2 SAEB

A estrutura do SAEB varia significativamente entre as edições.

No conjunto RAW utilizado pelo projeto existem:

- arquivos agregados por Unidade da Federação;
- arquivos em nível escolar;
- arquivos XLSX;
- arquivos CSV;
- arquivo XLSB de resultados oficiais agregados;
- dicionários de dados auxiliares.

A Bronze respeita a estrutura e a granularidade de cada fonte selecionada, sem harmonização forçada.

#### Decisão de seleção das fontes

Quando o Inep disponibiliza resultado oficial agregado por Unidade da Federação, essa tabela é preferida para representar o resultado estadual publicado.

A estrutura RAW utilizada inicialmente permitiu empregar fontes agregadas por UF em todas as edições de 2007 a 2021. Em 2023, a primeira fonte ingerida foi `TS_ESCOLA_2023.csv`, em nível escolar.

Durante a construção da Silver, a tentativa de reproduzir os resultados estaduais de 2023 a partir das médias escolares ponderadas por `NU_PRESENTES` não reproduziu os valores oficiais: foram obtidas `0/108` coincidências após arredondamento para duas casas decimais.

Como consequência, foi incorporada ao RAW uma segunda fonte oficial de 2023:

`data/raw/saeb/Resultados_Saeb_2023_Brasil_Estados_Municipios.xlsb`

A aba utilizada é:

`Estados`

Essa fonte foi ingerida como uma Bronze adicional, preservando o resultado agregado oficial de UF sem substituir nem alterar a Bronze escolar já existente.

A configuração final do SAEB na Bronze é:

| Ano | Arquivo de origem | Aba | Granularidade | Papel |
|---:|---|---|---|---|
| 2007 | `MEDIA_UF_2007.xlsx` | `MEDIA_ESTADOS` | UF | resultado oficial agregado |
| 2009 | `MEDIA_UF_2009.xlsx` | `MEDIA_ESTADOS` | UF | resultado oficial agregado |
| 2011 | `TS_RESULTADO_UF_2011.csv` | não se aplica | UF | resultado oficial agregado |
| 2013 | `TS_UF_2013.xlsx` | `UF` | UF | resultado oficial agregado |
| 2015 | `TS_UF_2015.xlsx` | `UFs` | UF | resultado oficial agregado |
| 2017 | `TS_UF_2017.xlsx` | `TS_UF` | UF | resultado oficial agregado |
| 2019 | `TS_UF_2019.xlsx` | `Estados` | UF | resultado oficial agregado |
| 2021 | `TS_UF_2021.xlsx` | `Estados` | UF | resultado oficial agregado |
| 2023 | `TS_ESCOLA_2023.csv` | não se aplica | ESCOLA | microdados escolares preservados |
| 2023 | `Resultados_Saeb_2023_Brasil_Estados_Municipios.xlsb` | `Estados` | UF | resultado oficial agregado preservado |

A existência de duas tabelas Bronze em 2023 é deliberada.

A Bronze escolar preserva o arquivo oficial em nível de escola. A Bronze agregada preserva outra publicação oficial do Inep em nível de UF. Nenhuma delas é derivada da outra dentro da camada Bronze.

A decisão não representa uma agregação realizada na Bronze. Trata-se da ingestão separada de duas fontes oficiais com granularidades distintas.

#### Arquivos escolares de 2007 e 2009

Também existem no RAW:

- `TS_ESCOLA_2007.csv`;
- `TS_ESCOLA_2009.csv`.

Esses arquivos não são utilizados como fonte principal da série analítica porque os respectivos anos já possuem os arquivos oficiais agregados:

- `MEDIA_UF_2007.xlsx`;
- `MEDIA_UF_2009.xlsx`.

Os arquivos escolares permanecem preservados na camada Raw e não são alterados ou excluídos.

#### Dicionários de dados

Os seguintes arquivos de dicionário também estão preservados no RAW:

- `Dicionario_SAEB_2007.xlsx`;
- `Dicionario_SAEB_2009.xlsx`;
- `Dicionario_SAEB_2011.xlsx`;
- `Dicionario_Saeb_2023.xlsx`.

Eles são fontes auxiliares de documentação e interpretação estrutural.

Não constituem tabelas de resultados do indicador e, por isso, não são tratados como fatos da Bronze do SAEB.

Seu conteúdo pode ser consultado pelo pipeline ou pela documentação sempre que necessário para interpretar códigos, campos e categorias.

#### Estruturas confirmadas nas fontes agregadas

Para 2007 e 2009, os arquivos `MEDIA_UF_*.xlsx` utilizam a aba `MEDIA_ESTADOS` e apresentam diretamente variáveis como `ANO_SAEB`, `CO_UF`, `NO_UF`, `DEPENDENCIA_ADM`, `LOCALIZACAO`, `CAPITAL` e médias de Língua Portuguesa e Matemática.

Em 2011, `TS_RESULTADO_UF_2011.csv` possui estrutura tabular em CSV e utiliza códigos como `ID_UF`, `ID_SERIE`, `ID_TIPO_REDE`, `ID_LOCALIZACAO`, `ID_CAPITAL`, `NU_PARTICIPANTES`, `MEDIA_LP` e `MEDIA_MT`.

Para 2013 e 2015, o cabeçalho é hierárquico e ocupa múltiplas linhas. A auditoria confirmou:

- em 2013, a primeira linha semântica do cabeçalho está no índice `3`, correspondente à linha de origem `4`;
- em 2015, a primeira linha semântica do cabeçalho está no índice `2`, correspondente à linha de origem `3`.

A estrutura analítica preservada nessas duas edições foi confirmada nas posições:

- `col_001`: UF;
- `col_002`: rede;
- `col_003`: localização;
- `col_004`: capital;
- `col_005`: Anos Iniciais / Língua Portuguesa;
- `col_006`: Anos Iniciais / Matemática;
- `col_007`: Anos Finais / Língua Portuguesa;
- `col_008`: Anos Finais / Matemática.

Essa diferença estrutural é preservada explicitamente e não é substituída por nomes técnicos inexistentes na fonte.

Para 2017, 2019 e 2021, os arquivos de UF utilizam cabeçalhos técnicos próprios das respectivas edições. Em 2019 e 2021, a aba é `Estados` e as fontes incluem, além das médias de proficiência, variáveis de níveis de proficiência e outras etapas avaliadas.

Na nova fonte agregada de 2023, a aba `Estados` possui 177 colunas, entre elas `ANO_SAEB`, `CO_UF`, `NO_UF`, `DEPENDENCIA_ADM`, `LOCALIZACAO`, `CAPITAL`, `MEDIA_5_LP`, `MEDIA_5_MT`, `MEDIA_9_LP` e `MEDIA_9_MT`.

A primeira linha física contém os nomes técnicos das variáveis e é preservada na Bronze.

#### Tipagem da fonte agregada de 2023

Na primeira tentativa de persistência da aba `Estados` de 2023, o PyArrow identificou tipos heterogêneos nas mesmas colunas, pois a primeira linha contém nomes técnicos e as linhas seguintes contêm números ou categorias.

Por isso, as 177 colunas de origem são persistidas como texto anulável na Bronze agregada de 2023.

Essa decisão é exclusivamente técnica:

- preserva a linha de cabeçalho;
- evita coerção indevida entre texto e número;
- mantém células realmente vazias como `null`;
- adia a tipagem analítica para a Silver.

#### Preservação da granularidade

A Bronze não força uma única granularidade para o SAEB.

A configuração final é:

- 2007 a 2021: tabelas principais em nível de UF;
- 2023: uma tabela em nível de ESCOLA e uma tabela oficial adicional em nível de UF.

O arquivo escolar de 2023 não é agregado pela Bronze.

O arquivo de UF de 2023 também não é calculado pela Bronze: ele é uma publicação oficial independente do Inep e é apenas estruturado e rastreado em Parquet.

Na Silver histórica, o resultado estadual de 2023 utiliza a Bronze oficial de UF porque a reconstrução a partir das escolas por `NU_PRESENTES` não reproduziu os resultados publicados.

#### Rede pública

Nenhum filtro de rede é aplicado na Bronze.

São preservados, conforme a estrutura de cada edição:

- categorias de `DEPENDENCIA_ADM`;
- códigos de `ID_TIPO_REDE`;
- o indicador `IN_PUBLICA`;
- demais categorias originais de rede.

A definição canônica `REDE = PUBLICA` é aplicada somente na Silver, seguindo `docs/definicao_rede_publica.md`.

A Bronze não transforma o agregado geral que inclui rede privada em rede pública e não calcula média simples entre redes Federal, Estadual e Municipal.

#### Proficiências, etapas e variáveis adicionais

A Bronze não seleciona exclusivamente Anos Iniciais, Anos Finais, Língua Portuguesa ou Matemática.

Quando a fonte possui 2º ano, Ensino Médio, Ciências Humanas, Ciências da Natureza, níveis de proficiência, participação, erros-padrão ou outras variáveis publicadas, essas informações permanecem preservadas na estrutura Bronze correspondente.

A seleção das medidas necessárias ao modelo analítico é responsabilidade da Silver.

#### CSV, delimitador e codificação

Os CSV do SAEB não têm sua codificação presumida silenciosamente.

Para `TS_RESULTADO_UF_2011.csv`, foi confirmado:

- codificação: `utf-8`;
- delimitador: `;`;
- 12 delimitadores na linha de cabeçalho;
- 13 campos na estrutura tabular.

Para `TS_ESCOLA_2023.csv`, foi confirmado:

- falha de leitura com `utf-8`;
- falha de leitura com `utf-8-sig`;
- leitura válida com `cp1252`;
- delimitador: `;`;
- 136 delimitadores na linha de cabeçalho;
- 137 campos na estrutura tabular.

A configuração da ingestão utiliza diretamente esses parâmetros. Se a estrutura esperada mudar, a execução deve falhar explicitamente.

#### Situação da ingestão

A Bronze do SAEB está concluída e validada.

A extensão oficial agregada de 2023 é reproduzida por:

`src/bronze/saeb/ingest_saeb_resultados_2023.py`

e validada independentemente por:

`src/bronze/saeb/validar_bronze_saeb_resultados_2023.py`

A nova tabela produzida é:

`data/bronze/saeb/saeb_2023_resultados_uf.parquet`

Ela coexiste com:

`data/bronze/saeb/saeb_2023.parquet`

que preserva os registros escolares.

---

### 7.3 Rendimento Escolar

Os arquivos de Taxas de Rendimento Escolar apresentam mudanças estruturais ao longo da série de 2007 a 2023.

Foram identificadas alterações relacionadas a:

- formato dos arquivos, entre XLS e XLSX;
- nomes das abas;
- posição do cabeçalho;
- quantidade de colunas;
- nomenclatura das redes de ensino;
- organização das dimensões geográficas;
- existência de espaços finais em nomes de determinadas abas.

Por esse motivo, a ingestão não utiliza uma rotina que tente descobrir automaticamente qual aba ou estrutura deve ser utilizada.

Cada edição possui configuração explícita, definida a partir da auditoria realizada anteriormente.

#### Decisão de ingestão

A Bronze preserva a estrutura completa da planilha correspondente à Unidade da Federação em cada edição.

Os arquivos são lidos com `header=None`, de forma que títulos, cabeçalhos, subcabeçalhos e registros publicados na planilha sejam mantidos.

Não ocorre promoção automática de uma linha para cabeçalho analítico na Bronze.

A linha identificada durante a auditoria como referência estrutural é registrada apenas no metadado `_indice_cabecalho_origem`.

A reconstrução do cabeçalho analítico será responsabilidade da Silver.

#### Preservação das células

As colunas provenientes da planilha recebem nomes técnicos neutros:

`col_001`, `col_002`, `col_003`, etc.

Essa nomenclatura não representa alteração semântica da fonte.

Ela é utilizada porque a planilha contém títulos, cabeçalhos e valores ocupando as mesmas posições físicas ao longo das linhas.

As células de origem são persistidas como texto para permitir armazenamento estável em Parquet.

Valores especiais publicados pela fonte, como `--`, são preservados.

A conversão para números, categorias ou outros tipos analíticos será realizada somente na Silver.

#### Linhas vazias

Durante a ingestão são removidas apenas linhas em que todas as células da planilha estão efetivamente vazias.

Nenhum registro é removido por pertencer a uma rede, localização, etapa ou categoria que não será utilizada posteriormente no dashboard.

#### Rede e localização

Nenhum filtro analítico de rede ou localização é aplicado na Bronze.

Permanecem preservadas categorias como:

- Federal;
- Estadual;
- Municipal;
- Particular ou Privada;
- `Publico` ou `Pública`;
- Total;
- Rural;
- Urbana.

A seleção do agregado oficial da rede pública combinado com `Localização = Total` será realizada somente na Silver, conforme a decisão registrada em `docs/definicao_rede_publica.md`.

A Bronze não reconstrói a rede pública a partir de médias das redes Federal, Estadual e Municipal.

#### Etapas e indicadores

A Bronze não seleciona apenas Anos Iniciais e Anos Finais.

Também não seleciona previamente apenas aprovação, reprovação ou abandono.

Toda a estrutura publicada na aba utilizada é preservada.

O recorte de etapa e a identificação das colunas correspondentes aos indicadores serão realizados na Silver.

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

#### Espaços finais em nomes de abas

Durante a implementação da Bronze foram identificados espaços finais existentes nos próprios nomes das abas dos arquivos de origem.

Foram confirmados:

- 2014: `UF `;
- 2015: `UF `;
- 2016: `UF `;
- 2017 a 2023: `BRASIL_REGIOES_UFS `.

Esses espaços fazem parte dos nomes efetivamente armazenados nos workbooks, embora sejam pouco perceptíveis visualmente no Excel.

A ingestão utiliza os nomes exatos encontrados na fonte.

Não foi utilizado `.strip()` para corrigir automaticamente esses nomes.

Essa escolha é deliberada: uma alteração inesperada na estrutura da fonte deve provocar falha explícita no pipeline, em vez de ser silenciosamente normalizada.

#### Rastreabilidade

Cada registro produzido na Bronze do Rendimento possui metadados que permitem retornar à sua origem:

- `_fonte`;
- `_sha256_arquivo`;
- `_arquivo_origem`;
- `_aba_origem`;
- `_ano_referencia`;
- `_indice_cabecalho_origem`;
- `_linha_origem`.

O campo `_sha256_arquivo` identifica a versão exata do arquivo RAW utilizada na geração do Parquet.

O campo `_linha_origem` registra a posição da linha na planilha original.

O campo `_indice_cabecalho_origem` registra a referência estrutural identificada durante a auditoria, sem transformar essa linha em cabeçalho analítico da Bronze.

#### Resultado metodológico

A Bronze do Rendimento Escolar representa uma cópia estruturada e rastreável das planilhas de origem.

Nenhuma decisão de seleção da população analítica é aplicada nessa camada.

O fluxo adotado é:

```text
RAW
planilha original
    ↓
BRONZE
estrutura integral e rastreável
    ↓
SILVER
seleção de UF + rede pública + localização total + AI/AF
e reconstrução dos indicadores
```

---

### 7.4 TDI

A Taxa de Distorção Idade-Série apresenta mudanças estruturais entre os períodos, incluindo variação entre formatos XLS e XLSX, nomes de abas e quantidade de colunas.

Assim como no Rendimento Escolar, a ingestão utiliza configuração explícita por edição e não tenta selecionar automaticamente uma aba semelhante.

#### Decisão de ingestão

A Bronze preserva a estrutura integral da aba de UF identificada na auditoria para cada edição.

Não são aplicados na Bronze:

- filtro de rede pública;
- filtro de `Localização = Total`;
- seleção apenas de AI/AF;
- normalização de rede;
- normalização de UF;
- reconstrução ou recálculo da TDI.

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
| 2017 | `BRASIL_REGIÕES_UFS` |
| 2018 | `BRASIL_REGIÕES_UFS` |
| 2019 | `BRASIL_REGIÕES_UFS` |
| 2020 | `BRASIL_REGIÕES_UFS` |
| 2021 | `BRASIL_REGIÕES_UFS` |
| 2022 | `BRASIL_REGIÕES_UFS` |
| 2023 | `BRASIL_REGIÕES_UFS` |

Durante a leitura dos arquivos XLSX de 2015 a 2023, o `openpyxl` emitiu o aviso:

`Cannot parse header or footer so it will be ignored`

O aviso se refere ao cabeçalho ou rodapé de impressão do workbook e não impediu a leitura das células utilizadas na ingestão.

A validação independente posterior confirmou os Parquets produzidos, inclusive quanto à rastreabilidade e à correspondência do SHA-256 com os arquivos RAW.

#### Rede e localização

Embora a auditoria tenha confirmado a existência do agregado `Pública + Localização Total`, essa seleção não é aplicada na Bronze.

Ela será aplicada somente na Silver, conforme `docs/definicao_rede_publica.md`.

---

### 7.5 PND 2025

A PND 2025 está representada no RAW por três arquivos:

- `Dicionário_arquivos_variáveis_PND_2025.xlsx`;
- `microdados2025_parametros_itens.xlsx`;
- `microdados2025_pnd_arq1.txt`.

#### Seleção da fonte principal

O arquivo `microdados2025_pnd_arq1.txt` é a tabela principal de registros individuais utilizada para a ingestão Bronze.

Os dois arquivos XLSX permanecem no RAW como fontes auxiliares de documentação e parâmetros:

- o dicionário apoia a interpretação das variáveis;
- a planilha de parâmetros de itens preserva informações técnicas de calibração e itens.

Eles não serão convertidos, nesta etapa, em tabelas factuais da Bronze porque a ingestão analítica principal da PND utiliza o arquivo individual. Permanecem preservados integralmente no RAW e poderão ser utilizados em etapas posteriores se alguma transformação exigir essas informações.

Essa decisão evita criar tabelas Bronze sem uso definido apenas por existirem no pacote de microdados, sem perder a rastreabilidade ou a disponibilidade dos arquivos originais.

#### Estrutura técnica confirmada do TXT

A verificação técnica do arquivo `microdados2025_pnd_arq1.txt` confirmou:

- tamanho: `371.539.465 bytes`;
- codificação: `utf-8`;
- delimitador: `;`;
- 26 colunas;
- 1.087.360 linhas físicas;
- 1.087.359 registros de dados, descontada a linha de cabeçalho;
- SHA-256: `b15968a19e309bca6b63c6f6d7af094efdc13d900645dc7385872a6a50dd7baf`.

O cabeçalho possui, na ordem original:

`NU_ANO;CO_GRUPO;CO_MUNICIPIO_PROVA;SG_UF_MUNICIPIO_PROVA;TP_INSCRICAO_PND;IN_REAPLICACAO;CO_CADERNO;DS_VT_GAB_OBJ;DS_VT_ESC_OBJ;DS_VT_ACE_OBJ;TP_PRES;TP_SIT_DISC;PROFICIENCIA;NT_OBJ;NT_DIS;NT_GER;QT_ACERTOS;CO_RS_I1;CO_RS_I2;CO_RS_I3;CO_RS_I4;CO_RS_I5;CO_RS_I6;CO_RS_I7;CO_RS_I8;CO_RS_I9`

#### Preservação do cabeçalho

Para manter a mesma lógica de rastreabilidade adotada nas demais fontes Bronze, o TXT será lido com `header=None`.

Assim, a linha física do cabeçalho será preservada como a primeira linha da Bronze:

- `_indice_cabecalho_origem = 0`;
- `_linha_origem = 1`.

Consequentemente:

- registros substantivos de dados: `1.087.359`;
- linhas Bronze esperadas, incluindo o cabeçalho preservado: `1.087.360`.

Essa diferença de uma linha não representa criação de um participante adicional. Ela decorre exclusivamente da preservação da linha física de cabeçalho como parte da rastreabilidade da fonte.

#### Tipagem e valores especiais

As 26 colunas da fonte serão armazenadas como texto técnico na Bronze, utilizando `col_001` a `col_026`.

O uso de texto evita interpretar semanticamente, nesta camada:

- números com vírgula decimal;
- códigos;
- vetores de respostas;
- indicadores de presença;
- notas;
- proficiência.

O literal `NA` será preservado como texto quando estiver presente na fonte.

Somente campos realmente vazios serão representados como valores ausentes.

A conversão de `PROFICIENCIA`, `NT_OBJ`, `NT_DIS`, `NT_GER`, `QT_ACERTOS` e demais variáveis para tipos analíticos ocorrerá na Silver.

#### Leitura em blocos

Como o TXT possui aproximadamente 371,5 MB e mais de um milhão de registros, a ingestão será realizada em blocos (`chunks`), e não por carregamento integral do arquivo em memória.

Essa é uma decisão de eficiência operacional e não altera a informação substantiva.

Cada bloco será convertido para o mesmo esquema Bronze e escrito sequencialmente em um único arquivo Parquet com compressão Snappy.

Como o `pandas.read_csv(..., chunksize=...)` preserva no índice interno de cada bloco a posição acumulada do arquivo, cada chunk será submetido a `reset_index(drop=True)` antes da criação dos metadados técnicos. Além disso, as `Series` utilizadas na inserção dos metadados serão criadas com o mesmo índice do chunk.

Essa regra evita o alinhamento automático por índice do pandas, que poderia produzir valores ausentes nos metadados a partir do segundo bloco mesmo quando os valores atribuídos estivessem corretos. Trata-se exclusivamente de uma correção técnica de escrita por blocos; não altera nenhuma variável substantiva da PND.

#### População preservada

Na Bronze serão preservados todos os registros do arquivo principal.

Não será aplicada nessa camada a população analítica de 759.140 participantes.

Também não serão removidos:

- registros `TP_PRES = 888`;
- registros `TP_PRES = 555` sem resultados completos;
- registros apenas por não integrarem posteriormente a população analítica.

A Bronze preservará a granularidade individual da prova.

A definição da população analítica será aplicada somente na Silver.

---

## 8. Granularidade

A Bronze deverá manter a granularidade disponível na fonte selecionada.

Não será utilizada uma granularidade única artificial para todas as bases.

Exemplos:

- SAEB pode possuir dados agregados por UF ou em nível escolar, conforme a edição;
- IDEB possui tabelas agregadas;
- Rendimento e TDI possuem agregados geográficos;
- PND possui registros individuais da prova.

A harmonização de granularidade será feita somente quando necessária para a análise.

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

Os arquivos Bronze serão preferencialmente armazenados como:

`.parquet`

---

## 10. Validações da Bronze

Cada processo de ingestão deverá verificar pelo menos:

- existência do arquivo de origem;
- existência de registros;
- quantidade de linhas lidas;
- quantidade de colunas;
- ano ou edição esperada, quando aplicável;
- arquivo e aba de origem registrados;
- presença das colunas técnicas obrigatórias;
- consistência de `_linha_origem`, quando aplicável;
- integridade do arquivo RAW por comparação do SHA-256;
- sucesso da gravação e releitura do Parquet.

A Bronze não deverá considerar uma ingestão válida apenas porque o arquivo foi criado.

Sempre que aplicável, a validação final deverá ser executada por script independente do script de ingestão.

Essa separação reduz o risco de a própria rotina que produziu o arquivo considerar automaticamente sua saída válida.

O pipeline deverá produzir mensagens de controle.

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

Nenhum arquivo da Bronze deverá depender de transformação manual em Excel ou Power BI.

A partir dos arquivos existentes em:

`data/raw/`

todo o conteúdo de:

`data/bronze/`

deverá poder ser reconstruído executando o pipeline.

Isso significa que a Bronze é descartável e reproduzível.

A camada Raw não é descartável.

---

## 12. Regra de falha

Se o pipeline não reconhecer corretamente:

- uma aba;
- um cabeçalho ou estrutura;
- um ano;
- uma codificação;
- um delimitador;
- uma estrutura esperada;

a execução deverá falhar de forma explícita.

Não deverá selecionar silenciosamente outra aba, codificação ou estrutura semelhante.

É preferível interromper o pipeline do que produzir dados aparentemente válidos a partir de uma interpretação incorreta da fonte.

---

## 13. Separação de responsabilidades

O projeto adotará a seguinte divisão:

### RAW

Arquivo original, imutável.

### BRONZE

Arquivo original estruturado e rastreável, com mínima transformação técnica.

### SILVER

Dados limpos, tipados, normalizados e semanticamente harmonizados.

### GOLD

Dados organizados para análise, indicadores, modelo dimensional e Power BI.

A regra pode ser resumida como:

```text
RAW
arquivo como publicado
       ↓
BRONZE
arquivo estruturado e rastreável
       ↓
SILVER
dado limpo e harmonizado
       ↓
GOLD
dado analítico
```

---

## 14. Resultado da ingestão — Rendimento Escolar

A ingestão Bronze do Rendimento Escolar foi executada para as 17 edições compreendidas entre 2007 e 2023.

Após a geração dos arquivos Parquet, foi realizada validação independente por meio de:

`src/bronze/validar_bronze_rendimento.py`

### Resultado

- arquivos RAW esperados: 17;
- arquivos Parquet encontrados: 17;
- período: 2007–2023;
- total de linhas armazenadas na Bronze: 9.012;
- arquivos vazios: nenhum;
- divergências de ano de referência: nenhuma;
- divergências no arquivo de origem: nenhuma;
- ausência de colunas técnicas obrigatórias: nenhuma;
- duplicidades em `_linha_origem`: nenhuma;
- divergências entre o SHA-256 armazenado na Bronze e o arquivo RAW: nenhuma.

Todos os arquivos foram aprovados na validação independente.

### Quantidade de linhas por edição

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

### Conclusão

A camada Bronze do Rendimento Escolar foi considerada válida.

Os arquivos originais foram convertidos para Parquet sem aplicação de filtros analíticos ou harmonizações semânticas.

A rastreabilidade foi preservada por arquivo, aba, ano, linha de origem e SHA-256.

Status:

`RENDIMENTO ESCOLAR — BRONZE ✅`

---

## 15. Resultado da ingestão — TDI

A ingestão Bronze da Taxa de Distorção Idade-Série foi executada para as 17 edições compreendidas entre 2007 e 2023 por meio de:

`src/bronze/ingest_tdi.py`

Após a geração dos arquivos Parquet, foi realizada validação independente por meio de:

`src/bronze/validar_bronze_tdi.py`

### Resultado

- arquivos RAW esperados: 17;
- arquivos Parquet encontrados: 17;
- período: 2007–2023;
- total de linhas armazenadas na Bronze: 8.989;
- arquivos vazios: nenhum;
- divergências de ano de referência: nenhuma;
- divergências no arquivo de origem: nenhuma;
- ausência de colunas técnicas obrigatórias: nenhuma;
- duplicidades em `_linha_origem`: nenhuma;
- divergências na sequência das colunas técnicas: nenhuma;
- divergências entre o SHA-256 armazenado na Bronze e o arquivo RAW: nenhuma.

Todos os arquivos foram aprovados na validação independente.

### Quantidade de linhas por edição

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

### Conclusão

A camada Bronze da TDI foi considerada válida.

Os arquivos originais foram convertidos para Parquet sem aplicação do filtro analítico de rede pública, seleção de localização, harmonização das etapas ou alteração dos valores publicados.

A rastreabilidade foi preservada por arquivo, aba, ano, linha de origem e SHA-256.

Status:

`TDI — BRONZE ✅`

---

## 16. Resultado da ingestão — IDEB

A ingestão Bronze do Índice de Desenvolvimento da Educação Básica foi realizada a partir do arquivo:

`divulgacao_regioes_ufs_ideb_2023.xlsx`

Foram preservadas integralmente as três abas existentes no arquivo:

- `UF e Regiões (AI)`;
- `UF e Regiões (AF)`;
- `UF e Regiões (EM)`.

Cada aba foi persistida separadamente em Parquet.

Após a ingestão, foi realizada validação independente por meio de:

`src/bronze/validar_bronze_ideb.py`

### Resultado

| Etapa de origem | Aba | Linhas Bronze | Colunas da fonte |
|---|---|---:|---:|
| AI | `UF e Regiões (AI)` | 150 | 120 |
| AF | `UF e Regiões (AF)` | 149 | 110 |
| EM | `UF e Regiões (EM)` | 117 | 110 |

Foram encontrados os três arquivos Parquet esperados:

- `ideb_ai.parquet`;
- `ideb_af.parquet`;
- `ideb_em.parquet`.

Nenhum dos arquivos estava vazio.

A validação confirmou:

- identificação correta da fonte;
- arquivo de origem correto;
- aba de origem correta;
- etapa de origem correta;
- presença dos metadados técnicos;
- consistência de `_linha_origem`;
- quantidade esperada de colunas da fonte;
- sequência das colunas técnicas `col_001`, `col_002`, etc.;
- presença dos marcadores técnicos esperados na linha de cabeçalho;
- correspondência entre o SHA-256 armazenado na Bronze e o arquivo RAW.

O SHA-256 confirmado para o arquivo de origem foi:

`e7cdb12afa3c0d2e4435aa914316d84e5ac1e31865fa56ad238ad48f778b1bd5`

### Preservação da estrutura histórica

O workbook contém informações anteriores ao período analítico definido para o projeto, incluindo dados de 2005.

Essas informações foram mantidas na Bronze.

Também foi preservada a aba correspondente ao Ensino Médio, embora o recorte analítico posterior utilize apenas Anos Iniciais e Anos Finais do Ensino Fundamental.

Não foram aplicados na Bronze:

- filtro de 2007–2023;
- exclusão de 2005;
- exclusão do Ensino Médio;
- filtro da rede pública;
- normalização de `Pública (4)` para `PUBLICA`;
- remoção de informações de aprovação, SAEB ou metas;
- transformação da estrutura histórica em formato analítico.

### Conclusão

A camada Bronze do IDEB foi considerada válida.

A estrutura original do workbook foi preservada em três arquivos Parquet rastreáveis até o arquivo, a aba e a linha de origem.

Status:

`IDEB — BRONZE ✅`

---

## 17. Resultado da ingestão — SAEB

A ingestão Bronze do Sistema de Avaliação da Educação Básica cobre 9 edições entre 2007 e 2023.

Após a extensão metodológica de 2023, essas 9 edições são representadas por **10 arquivos Parquet**, porque 2023 possui duas fontes oficiais preservadas separadamente.

A ingestão principal foi realizada por meio de:

`src/bronze/saeb/ingest_saeb.py`

e validada independentemente por:

`src/bronze/saeb/validar_bronze_saeb.py`

A fonte agregada adicional de 2023 é ingerida por:

`src/bronze/saeb/ingest_saeb_resultados_2023.py`

e validada independentemente por:

`src/bronze/saeb/validar_bronze_saeb_resultados_2023.py`

### Resultado

| Ano | Arquivo de origem | Aba | Granularidade | Linhas Bronze | Colunas da fonte |
|---:|---|---|---|---:|---:|
| 2007 | `MEDIA_UF_2007.xlsx` | `MEDIA_ESTADOS` | UF | 269 | 12 |
| 2009 | `MEDIA_UF_2009.xlsx` | `MEDIA_ESTADOS` | UF | 269 | 12 |
| 2011 | `TS_RESULTADO_UF_2011.csv` | não se aplica | UF | 4.375 | 13 |
| 2013 | `TS_UF_2013.xlsx` | `UF` | UF | 1.706 | 10 |
| 2015 | `TS_UF_2015.xlsx` | `UFs` | UF | 1.706 | 10 |
| 2017 | `TS_UF_2017.xlsx` | `TS_UF` | UF | 1.702 | 70 |
| 2019 | `TS_UF_2019.xlsx` | `Estados` | UF | 1.551 | 156 |
| 2021 | `TS_UF_2021.xlsx` | `Estados` | UF | 1.517 | 156 |
| 2023 | `TS_ESCOLA_2023.csv` | não se aplica | ESCOLA | 70.152 | 137 |
| 2023 | `Resultados_Saeb_2023_Brasil_Estados_Municipios.xlsb` | `Estados` | UF | 1.553 | 177 |

O conjunto original das nove Bronzes totalizava `83.247 linhas`.

A inclusão da Bronze agregada oficial de 2023 acrescentou 1.553 linhas.

O total atual das tabelas Bronze do SAEB é:

`84.800 linhas`

Esse total representa linhas físicas preservadas em 10 Parquets e não deve ser interpretado como quantidade de observações analíticas comparáveis entre si, pois as fontes possuem granularidades e estruturas distintas.

### Validação das nove Bronzes originais

A validação confirmou para as nove tabelas originais:

- presença dos Parquets esperados;
- ausência de arquivos vazios;
- quantidade esperada de linhas e colunas;
- identificação correta do arquivo e da aba;
- granularidade de origem;
- consistência de `_ano_referencia`, `_indice_cabecalho_origem` e `_linha_origem`;
- sequência das colunas técnicas;
- marcadores estruturais esperados;
- correspondência entre SHA-256 da Bronze e o RAW atual.

### Validação da Bronze agregada oficial de 2023

A Bronze adicional:

`data/bronze/saeb/saeb_2023_resultados_uf.parquet`

foi comparada diretamente com:

`data/raw/saeb/Resultados_Saeb_2023_Brasil_Estados_Municipios.xlsb`

na aba `Estados`.

A validação independente confirmou:

- SHA-256: `e593b547f608b2377ac3d90491d02097326d3b276d4539a93201922466207a01`;
- 1.553 linhas RAW/Bronze;
- 177 colunas de origem;
- 177 colunas de origem persistidas como texto;
- 274.881 células comparadas RAW ↔ Bronze;
- reprodução integral do conteúdo da aba após normalização textual;
- proveniência de arquivo, aba, linha, cabeçalho e granularidade;
- `_indice_cabecalho_origem = 0`;
- `_linha_origem` de 1 a 1.553;
- `_granularidade_origem = UF`.

Também foi validado o estrato oficial `Total - Federal, Estadual e Municipal`, com `LOCALIZACAO = Total` e `CAPITAL = Total`:

- 27 UFs;
- nenhuma duplicidade;
- nenhum valor ausente nas quatro proficiências utilizadas pela Silver.

Faixas observadas:

- `MEDIA_5_LP`: 185,22 a 225,51;
- `MEDIA_5_MT`: 193,75 a 239,52;
- `MEDIA_9_LP`: 230,61 a 265,44;
- `MEDIA_9_MT`: 230,17 a 264,71.

Resultado:

`BRONZE SAEB 2023 RESULTADOS OFICIAIS DE UF: OK`

### Justificativa da extensão de 2023

A Bronze escolar de 2023 foi mantida intacta.

Durante a auditoria da Silver, foi testada a hipótese de reproduzir os resultados estaduais utilizando as médias escolares ponderadas por `NU_PRESENTES`.

Foram comparados `27 UFs × 2 etapas × 2 disciplinas = 108 valores`.

A comparação apresentou:

- `0/108` coincidências após arredondamento para duas casas;
- diferença absoluta média: `1,389714`;
- diferença absoluta mediana: `1,092905`;
- maior diferença absoluta: `6,150034`.

Por isso, `NU_PRESENTES` foi rejeitado como regra de reconstrução do resultado estadual.

A solução adotada não foi agregar as escolas na Bronze, mas incorporar a publicação oficial agregada de UF como uma segunda fonte Bronze de 2023.

### Diferença estrutural entre 2013 e 2015

Em 2013:

- `_indice_cabecalho_origem = 3`;
- a primeira linha semântica do cabeçalho corresponde a `_linha_origem = 4`.

Em 2015:

- `_indice_cabecalho_origem = 2`;
- a primeira linha semântica do cabeçalho corresponde a `_linha_origem = 3`.

Essa diferença permanece explicitamente documentada e preservada.

### Codificação e delimitador dos CSV

Foram utilizados:

- 2011: `utf-8` com delimitador `;`;
- 2023 escolar: `cp1252` com delimitador `;`.

### Granularidade

A Bronze preserva as granularidades efetivamente publicadas:

- 2007 a 2021: UF;
- 2023 escolar: ESCOLA;
- 2023 agregado oficial: UF.

A tabela escolar de 2023 não é agregada pela Bronze.

A tabela agregada de 2023 é outra publicação oficial, ingerida diretamente e sem reconstrução.

### Conclusão

A camada Bronze do SAEB foi considerada válida após a extensão controlada de 2023.

A rastreabilidade foi preservada por arquivo, aba, ano, granularidade, linha de origem e SHA-256.

Status:

`SAEB — BRONZE ✅`

---

## 18. Resultado da ingestão — PND 2025

A ingestão Bronze da PND 2025 foi executada por meio de:

`src/bronze/ingest_pnd.py`

A validação independente foi executada por meio de:

`src/bronze/validar_bronze_pnd.py`

### Fonte principal

Foi utilizada como tabela factual da Bronze:

`microdados2025_pnd_arq1.txt`

Os arquivos auxiliares:

- `Dicionário_arquivos_variáveis_PND_2025.xlsx`;
- `microdados2025_parametros_itens.xlsx`;

permanecem preservados no RAW como documentação e parâmetros técnicos.

### Resultado da ingestão

A execução confirmou:

- codificação: `utf-8`;
- delimitador: `;`;
- 26 colunas na fonte;
- 1.087.359 registros de dados;
- 1.087.360 linhas Bronze, incluindo a linha física do cabeçalho preservada;
- granularidade: `REGISTRO_INDIVIDUAL`;
- SHA-256 do RAW: `b15968a19e309bca6b63c6f6d7af094efdc13d900645dc7385872a6a50dd7baf`.

A ingestão foi processada em 11 chunks:

- 10 chunks de 100.000 linhas;
- 1 chunk final de 87.360 linhas.

O arquivo produzido foi:

`data/bronze/pnd/pnd_2025.parquet`

### Validação independente

A validação confirmou:

- correspondência do SHA-256 com o arquivo RAW;
- presença das 26 colunas esperadas;
- preservação do cabeçalho físico;
- sequência contígua de `_linha_origem`;
- consistência dos metadados de rastreabilidade;
- granularidade `REGISTRO_INDIVIDUAL`;
- total de 1.087.360 linhas na Bronze.

O resultado final foi:

`BRONZE DA PND 2025: OK`

### Correção técnica durante a implementação

Na primeira execução da validação foi detectada inconsistência em `_fonte` a partir dos chunks posteriores ao primeiro.

A causa foi o alinhamento automático por índice do pandas durante a inserção das `Series` de metadados técnicos.

A correção aplicada foi:

- `reset_index(drop=True)` em cada chunk antes da criação dos metadados;
- criação das `Series` técnicas com `index=chunk.index`.

Após a correção, a ingestão foi refeita integralmente e a validação independente passou em todos os controles.

Essa correção não alterou nenhuma variável substantiva da PND; afetava exclusivamente o preenchimento técnico dos metadados da Bronze.

### Conclusão

A camada Bronze da PND 2025 foi considerada válida.

Todos os registros do arquivo principal foram preservados, sem aplicação da população analítica de 759.140 participantes e sem exclusão de registros por condição de presença ou completude dos resultados.

Status:

`PND 2025 — BRONZE ✅`

---

## 19. Situação atual da camada Bronze

Até esta atualização:

| Fonte | Ingestão | Validação independente |
|---|---|---|
| Rendimento Escolar | ✅ concluída | ✅ concluída |
| TDI | ✅ concluída | ✅ concluída |
| IDEB | ✅ concluída | ✅ concluída |
| SAEB | ✅ concluída | ✅ concluída |
| PND 2025 | ✅ concluída | ✅ concluída |

As decisões metodológicas documentadas nas auditorias e em `docs/definicao_rede_publica.md` são aplicadas na Silver. Na Bronze permanecem apenas transformações técnicas, preservação estrutural e metadados de rastreabilidade. A inclusão do resultado agregado oficial do SAEB 2023 não altera essa separação: trata-se de uma segunda fonte oficial, não de uma agregação calculada na Bronze.

---

## 20. Conclusão

A camada Bronze funciona como fronteira entre os arquivos heterogêneos publicados pelas fontes e o pipeline analítico.

Seu principal compromisso é com:

- fidelidade;
- rastreabilidade;
- reprodutibilidade;
- mínima transformação semântica.

A Bronze não é a camada em que as diferentes fontes se tornam semanticamente iguais.

Seu papel é produzir representações estruturadas, verificáveis e reconstruíveis a partir dos arquivos RAW.

Com a conclusão e validação independente de Rendimento Escolar, TDI, IDEB, SAEB e PND 2025, a camada Bronze do projeto encontra-se integralmente concluída.

A etapa subsequente do pipeline é a camada Silver, responsável pelas harmonizações semânticas, recortes analíticos, normalizações de rede, etapa, indicadores e granularidade. A camada Bronze permanece encerrada e reproduzível, salvo a incorporação futura de nova fonte oficial que exija extensão documentada.

---

## 21. Histórico de atualização

| Data | Alteração |
|---|---|
| 18/08/2026 | Definição inicial da arquitetura da camada Bronze |
| 18/08/2026 | Definidos limites entre Raw, Bronze, Silver e Gold |
| 18/08/2026 | Definida adoção de Parquet e metadados de rastreabilidade |
| 18/08/2026 | Documentada a tipagem técnica das células na Bronze |
| 18/08/2026 | Documentadas irregularidades nos nomes de abas do Rendimento Escolar |
| 18/08/2026 | Concluída e validada independentemente a ingestão Bronze do Rendimento Escolar (2007–2023) |
| 18/08/2026 | Concluída e validada independentemente a ingestão Bronze da TDI (2007–2023) |
| 18/08/2026 | Concluída e validada independentemente a ingestão Bronze do IDEB |
| 18/08/2026 | Reorganizada a documentação para separar decisões metodológicas, particularidades das fontes e resultados de execução |
| 18/08/2026 | Corrigida a seleção das fontes SAEB: agregados oficiais por UF confirmados de 2007 a 2021 e fonte escolar apenas para 2023 |
| 18/08/2026 | Confirmados delimitador e codificação dos CSV selecionados do SAEB: UTF-8/`;` em 2011 e CP1252/`;` em 2023 |
| 18/08/2026 | Corrigida a referência estrutural do cabeçalho SAEB 2015 para índice 2 (linha de origem 3), conforme diferença auditada em relação a 2013 |
| 18/08/2026 | Concluída e validada independentemente a ingestão Bronze do SAEB (2007–2023), com 9 edições e 83.247 linhas |
| 18/08/2026 | Confirmada a estrutura técnica da PND 2025 e definida a ingestão Bronze em blocos do TXT principal: UTF-8, `;`, 26 colunas, 1.087.359 registros e preservação da linha física de cabeçalho |
| 18/08/2026 | Corrigida a escrita em chunks da PND para resetar o índice de cada bloco e impedir alinhamento automático do pandas nos metadados técnicos |
| 18/08/2026 | Concluída e validada independentemente a ingestão Bronze da PND 2025, com 1.087.359 registros de dados e 1.087.360 linhas Bronze incluindo o cabeçalho preservado |
| 18/08/2026 | Camada Bronze concluída integralmente para Rendimento Escolar, TDI, IDEB, SAEB e PND 2025 |
| 19/08/2026 | Comparação da Bronze escolar do SAEB 2023 com os resultados estaduais oficiais mostrou 0/108 coincidências quando as médias escolares foram ponderadas por `NU_PRESENTES`; a regra de agregação foi rejeitada |
| 19/08/2026 | Incorporado ao RAW `Resultados_Saeb_2023_Brasil_Estados_Municipios.xlsb` e criada uma segunda Bronze de 2023 em granularidade UF, preservando separadamente a Bronze escolar existente |
| 19/08/2026 | Bronze agregada oficial do SAEB 2023 validada integralmente: 1.553 linhas, 177 colunas, 274.881 células RAW ↔ Bronze e SHA-256 `e593b547f608b2377ac3d90491d02097326d3b276d4539a93201922466207a01` |
| 19/08/2026 | Atualizado o total do SAEB Bronze para 10 Parquets e 84.800 linhas físicas, mantendo 9 edições e duas fontes oficiais distintas em 2023 |
