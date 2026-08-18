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

No SAEB, esse campo registra se o arquivo selecionado para a edição foi publicado no nível de `UF` ou `ESCOLA`.

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
- dicionários de dados auxiliares.

A Bronze deverá respeitar a estrutura e a granularidade da fonte selecionada para cada edição, sem harmonização forçada.

#### Decisão de seleção da fonte

Quando houver resultado oficial agregado por Unidade da Federação entre os arquivos disponíveis e auditados, essa tabela será utilizada como fonte principal da respectiva edição.

A estrutura RAW atualmente disponível permite utilizar fonte agregada por UF em todas as edições de 2007 a 2021:

| Ano | Arquivo selecionado | Granularidade |
|---:|---|---|
| 2007 | `MEDIA_UF_2007.xlsx` | UF |
| 2009 | `MEDIA_UF_2009.xlsx` | UF |
| 2011 | `TS_RESULTADO_UF_2011.csv` | UF |
| 2013 | `TS_UF_2013.xlsx` | UF |
| 2015 | `TS_UF_2015.xlsx` | UF |
| 2017 | `TS_UF_2017.xlsx` | UF |
| 2019 | `TS_UF_2019.xlsx` | UF |
| 2021 | `TS_UF_2021.xlsx` | UF |
| 2023 | `TS_ESCOLA_2023.csv` | escola |

A edição de 2023 é a única, entre as fontes atualmente selecionadas para a série do projeto, cuja tabela disponível para ingestão permanece em nível escolar.

Essa escolha reduz transformações desnecessárias: quando o Inep já fornece uma tabela agregada por UF, a Bronze preserva esse agregado oficial em vez de reconstruí-lo a partir de escolas.

A decisão não representa uma agregação realizada na Bronze. Ela define explicitamente qual arquivo de origem será ingerido.

#### Arquivos escolares de 2007 e 2009

Também existem no RAW:

- `TS_ESCOLA_2007.csv`;
- `TS_ESCOLA_2009.csv`.

Esses arquivos não serão utilizados como fonte principal da série analítica porque os respectivos anos já possuem os arquivos oficiais agregados:

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

Não constituem tabelas de resultados do indicador e, por isso, não serão tratados como fatos da Bronze do SAEB.

Seu conteúdo poderá ser consultado pelo pipeline ou pela documentação sempre que necessário para interpretar códigos, campos e categorias.

#### Estruturas confirmadas nas fontes agregadas

Para 2007 e 2009, os arquivos `MEDIA_UF_*.xlsx` utilizam a aba:

`MEDIA_ESTADOS`

e apresentam diretamente variáveis como:

- `ANO_SAEB`;
- `CO_UF`;
- `NO_UF`;
- `DEPENDENCIA_ADM`;
- `LOCALIZACAO`;
- `CAPITAL`;
- médias de Língua Portuguesa;
- médias de Matemática.

Em 2011, `TS_RESULTADO_UF_2011.csv` possui estrutura tabular em CSV e utiliza códigos como:

- `ID_UF`;
- `ID_SERIE`;
- `ID_TIPO_REDE`;
- `ID_LOCALIZACAO`;
- `ID_CAPITAL`;
- `NU_PARTICIPANTES`;
- `MEDIA_LP`;
- `MEDIA_MT`.

Para 2013, 2015 e 2017, os arquivos de UF apresentam mudanças de layout e nomes de abas entre as edições.

Nos arquivos de 2013 e 2015, o cabeçalho é hierárquico e ocupa múltiplas linhas. A auditoria confirmou uma diferença adicional entre as duas edições:

- em 2013, a primeira linha semântica do cabeçalho está no índice `3`, correspondente à linha de origem `4`;
- em 2015, a primeira linha semântica do cabeçalho está no índice `2`, correspondente à linha de origem `3`.

A diferença ocorre porque a planilha de 2013 contém uma linha completamente vazia entre a observação inicial e o início do cabeçalho, enquanto a planilha de 2015 inicia o cabeçalho imediatamente após a observação inicial.

Essa diferença é preservada explicitamente em `_indice_cabecalho_origem`. Não será aplicada uma posição única de cabeçalho às duas edições.

Para 2019 e 2021, os arquivos:

- `TS_UF_2019.xlsx`;
- `TS_UF_2021.xlsx`;

utilizam a aba:

`Estados`

e contêm, além das médias de proficiência, variáveis adicionais de níveis de proficiência e diferentes etapas avaliadas.

Essas diferenças serão preservadas na Bronze e interpretadas semanticamente somente na Silver.

#### Preservação da granularidade

A Bronze manterá a granularidade da fonte selecionada em cada edição.

Assim:

- 2007 a 2021 permanecerão em nível de UF;
- 2023 permanecerá em nível escolar.

Os registros escolares de 2023 não serão agregados por UF na Bronze.

A agregação necessária para harmonizar 2023 com a série histórica será realizada somente na Silver e deverá seguir a metodologia definida na auditoria do SAEB.

#### Rede pública

Nenhum filtro de rede será aplicado na Bronze.

Serão preservados, conforme a estrutura de cada edição:

- categorias de `DEPENDENCIA_ADM`;
- códigos de `ID_TIPO_REDE`;
- o indicador `IN_PUBLICA`;
- demais categorias originais de rede.

A definição canônica:

`REDE = PUBLICA`

será aplicada somente na Silver, seguindo `docs/definicao_rede_publica.md`.

A Bronze não deverá transformar o agregado geral que inclui rede privada em rede pública, nem calcular média simples entre redes Federal, Estadual e Municipal.

#### Proficiências, etapas e variáveis adicionais

A Bronze não selecionará exclusivamente:

- Anos Iniciais;
- Anos Finais;
- Língua Portuguesa;
- Matemática.

Quando a fonte possuir:

- 2º ano;
- Ensino Médio;
- Ciências Humanas;
- Ciências da Natureza;
- níveis de proficiência;
- participação;
- erros-padrão;
- outras variáveis publicadas;

essas informações serão preservadas na estrutura Bronze correspondente.

A seleção das medidas necessárias ao modelo analítico será realizada somente na Silver.

#### CSV, delimitador e codificação

Os CSV do SAEB não terão sua codificação presumida silenciosamente.

Foi realizada verificação técnica específica dos dois arquivos CSV selecionados para a Bronze.

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

A configuração da ingestão utilizará diretamente esses parâmetros.

Não será implementada tentativa automática de múltiplas codificações durante a execução normal do pipeline.

Se um arquivo deixar de corresponder à codificação, ao delimitador ou aos marcadores estruturais documentados, a execução deverá falhar explicitamente.

Essa decisão torna a leitura reprodutível e evita que uma codificação alternativa seja aceita silenciosamente em uma futura versão da fonte.

#### Situação da ingestão

A ingestão Bronze do SAEB ainda não foi concluída nesta versão do documento.

A implementação deverá produzir um Parquet por edição selecionada, preservando a granularidade e a estrutura da fonte correspondente e adicionando os metadados técnicos de rastreabilidade definidos nesta documentação.

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

A ingestão Bronze do Sistema de Avaliação da Educação Básica foi executada para as 9 edições compreendidas entre 2007 e 2023:

- 2007;
- 2009;
- 2011;
- 2013;
- 2015;
- 2017;
- 2019;
- 2021;
- 2023.

A ingestão foi realizada por meio de:

`src/bronze/ingest_saeb.py`

Após a geração dos arquivos Parquet, foi executada validação independente por meio de:

`src/bronze/validar_bronze_saeb.py`

### Resultado

Foram encontrados e validados os 9 arquivos Parquet esperados.

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

O total armazenado na Bronze do SAEB foi de:

`83.247 linhas`

### Validações independentes

A validação confirmou, para todas as 9 edições:

- presença dos Parquets esperados;
- ausência de arquivos vazios;
- quantidade esperada de linhas;
- quantidade esperada de colunas da fonte;
- identificação correta do arquivo de origem;
- identificação correta da aba, quando aplicável;
- identificação correta da granularidade de origem;
- consistência de `_ano_referencia`;
- consistência de `_indice_cabecalho_origem`;
- consistência e unicidade de `_linha_origem`;
- sequência das colunas técnicas `col_001`, `col_002`, etc.;
- presença dos marcadores estruturais esperados;
- correspondência entre o SHA-256 armazenado na Bronze e o arquivo RAW atual.

Todos os arquivos apresentaram:

`SHA-256: OK`

e:

`Status: OK`

### Diferença estrutural entre 2013 e 2015

A validação confirmou uma diferença relevante entre os cabeçalhos hierárquicos das edições de 2013 e 2015.

Em 2013:

- `_indice_cabecalho_origem = 3`;
- a primeira linha semântica do cabeçalho corresponde a `_linha_origem = 4`;
- `_linha_origem = 3` é uma linha completamente vazia e, por isso, não é persistida na Bronze.

Em 2015:

- `_indice_cabecalho_origem = 2`;
- a primeira linha semântica do cabeçalho corresponde a `_linha_origem = 3`;
- não existe a linha vazia intermediária presente em 2013.

Essa diferença foi mantida explicitamente na configuração da ingestão e da validação.

### Codificação e delimitador dos CSV

Foram utilizados os parâmetros técnicos previamente verificados:

- 2011: `utf-8` com delimitador `;`;
- 2023: `cp1252` com delimitador `;`.

A ingestão não utiliza detecção automática ou tentativa silenciosa de codificações alternativas.

### Granularidade

A Bronze preserva a granularidade da fonte selecionada:

- 2007 a 2021: UF;
- 2023: ESCOLA.

A edição de 2023 não foi agregada por UF na Bronze.

Essa harmonização ocorrerá somente na Silver, conforme a metodologia já definida para o SAEB.

### Conclusão

A camada Bronze do SAEB foi considerada válida.

Os arquivos foram estruturados em Parquet sem aplicação de filtros analíticos de rede, etapa, disciplina ou população.

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

As decisões metodológicas documentadas nas auditorias e em `docs/definicao_rede_publica.md` serão aplicadas posteriormente na Silver. Na Bronze permanecem apenas as transformações técnicas e os metadados de rastreabilidade.

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

A próxima etapa do pipeline é a camada Silver, na qual serão realizadas as harmonizações semânticas, recortes analíticos, normalizações de rede, etapa, indicadores e granularidade já definidas metodologicamente.

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
