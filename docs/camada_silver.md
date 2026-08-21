# Camada Silver — Pipeline de Dados Educacionais

## 1. Objetivo

A camada Silver e responsavel por transformar as representacoes tecnicas e rastreaveis da Bronze em tabelas analiticas semanticamente harmonizadas.

Enquanto a Bronze preserva a estrutura efetiva de cada arquivo de origem, a Silver passa a aplicar regras de interpretacao necessarias ao uso comparavel dos indicadores.

A Silver nao substitui a Bronze.

Cada tabela Silver devera ser integralmente reconstruivel a partir dos arquivos Bronze e das regras documentadas neste arquivo.

---

## 2. Principio de trabalho

A transformacao de cada fonte seguira a sequencia:

1. auditar a estrutura efetivamente preservada na Bronze;
2. documentar as regras semanticas;
3. implementar a transformacao;
4. executar validacao independente;
5. somente entao considerar a fonte concluida na Silver.

Nao serao implementadas regras por suposicao a partir do nome de uma coluna ou da aparencia de uma planilha.

Mudancas estruturais entre anos deverao ser configuradas explicitamente.

---

## 3. Relacao entre Bronze e Silver

A Bronze preserva:

- estrutura de origem;
- linhas fisicas necessarias a rastreabilidade;
- cabecalhos originais;
- categorias textuais;
- granularidade publicada;
- metadados tecnicos;
- SHA-256 do arquivo RAW.

A Silver podera:

- excluir linhas fisicas de titulo, notas e cabecalhos;
- selecionar a populacao analitica definida para o projeto;
- harmonizar nomes de redes;
- harmonizar etapas de ensino;
- harmonizar indicadores;
- converter valores numericos;
- transformar tabelas largas em formato analitico longo;
- harmonizar granularidade quando metodologicamente necessario;
- criar campos canonicos utilizados pela Gold.

Toda transformacao devera ter justificativa documentada.

---

## 4. Escopo analitico do projeto

### Serie historica

Para os indicadores historicos:

- periodo principal: 2007–2023;
- geografia analitica: Unidade Federativa;
- rede: publica;
- etapas: Ensino Fundamental — Anos Iniciais e Anos Finais.

### PND

A PND 2025 e complementar a serie historica e sera tratada separadamente.

Sua populacao analitica sera definida na Silver, conforme a auditoria ja realizada.

---

## 5. Definicao canonica de rede publica

Para este projeto, `PUBLICA` representa o universo das redes publicas de ensino:

- Federal;
- Estadual;
- Municipal.

A implementacao devera preferir o agregado publico oficial quando a propria fonte o disponibilizar.

Quando a estrutura da fonte nao possuir esse agregado, sera utilizada a regra especifica previamente auditada para a edicao.

Nao sera utilizada media aritmetica simples de Federal, Estadual e Municipal para reconstruir um resultado publico.

Tambem nao sera utilizado um agregado geral que inclua rede privada.

A coluna canonica sera:

`REDE = PUBLICA`

A origem da classificacao devera continuar rastreavel em campo especifico quando necessario, como:

`REDE_ORIGEM`

---

## 6. Granularidade e tabelas previstas

### Rendimento Escolar

Grao previsto:

`ANO + UF + ETAPA + REDE + INDICADOR`

Estrutura prevista:

- `ANO`;
- `UF`;
- `ETAPA`;
- `REDE`;
- `INDICADOR`;
- `VALOR`;
- `ARQUIVO_ORIGEM`.

Indicadores:

- `APROVACAO`;
- `REPROVACAO`;
- `ABANDONO`.

### TDI

Grao previsto:

`ANO + UF + ETAPA + REDE`

Estrutura prevista:

- `ANO`;
- `UF`;
- `ETAPA`;
- `REDE`;
- `TDI`;
- `ARQUIVO_ORIGEM`.

### IDEB

Grao previsto:

`ANO + UF + ETAPA + REDE`

Estrutura prevista:

- `ANO`;
- `UF`;
- `ETAPA`;
- `REDE`;
- `IDEB`;
- `ARQUIVO_ORIGEM`.

### SAEB

Grao previsto:

`ANO + UF + ETAPA + REDE + DISCIPLINA`

Estrutura prevista:

- `ANO`;
- `UF`;
- `ETAPA`;
- `REDE`;
- `DISCIPLINA`;
- `PROFICIENCIA_MEDIA`;
- `ARQUIVO_ORIGEM`.

Disciplinas principais do projeto:

- Lingua Portuguesa;
- Matematica.

### PND 2025

A PND permanece separada das series historicas de IDEB, SAEB, Rendimento e TDI.

Sua Silver mantem a granularidade de `REGISTRO_INDIVIDUAL`, aplicando apenas a populacao analitica auditada.

Grao:

`um registro valido da prova`

Como o arquivo principal nao fornece um identificador individual do participante, nao sera criado um identificador artificial com significado substantivo. `LINHA_ORIGEM_BRONZE` sera preservada apenas como chave tecnica unica de rastreabilidade.

Estrutura definida:

- `ANO`;
- `CO_GRUPO`;
- `AREA_PROVA`;
- `CO_MUNICIPIO_PROVA`;
- `UF_PROVA`;
- `TP_INSCRICAO_PND`;
- `IN_REAPLICACAO`;
- `CO_CADERNO`;
- `TP_PRES`;
- `TP_SIT_DISC`;
- `PROFICIENCIA`;
- `NT_OBJ`;
- `NT_DIS`;
- `NT_GER`;
- `QT_ACERTOS`;
- `ARQUIVO_ORIGEM`;
- `LINHA_ORIGEM_BRONZE`;
- `GRANULARIDADE_ORIGEM`.

Os vetores de gabarito/resposta e as nove respostas do Questionario de Percepcao de Prova nao integram esta Silver porque nao sao necessarios ao escopo analitico atual, que utiliza notas, acertos, area e localizacao de aplicacao. Eles continuam preservados integralmente na Bronze.

---

## 7. Valores ausentes e marcadores da fonte

Valores ausentes nao serao imputados na Silver.

Marcadores textuais da fonte, como `--`, `NA`, celulas vazias ou codigos especificos, nao serao automaticamente tratados como equivalentes.

Cada marcador devera ser interpretado segundo a estrutura auditada da respectiva fonte.

Quando um marcador significar indisponibilidade de resultado, a Silver podera converte-lo para valor ausente, desde que essa regra esteja explicitamente documentada.

---

## 8. Conversao numerica

A Bronze preserva muitos valores como texto tecnico.

Na Silver, os campos analiticos poderao ser convertidos para tipos numericos.

A conversao devera considerar explicitamente:

- virgula decimal;
- ponto decimal;
- marcadores de ausencia;
- valores zero substantivos;
- codigos que nao representam medidas.

Nao havera conversao numerica generica aplicada indistintamente a todas as colunas.

---

## 9. Rastreamento da origem

A Silver nao precisa preservar todas as colunas tecnicas da Bronze, mas deve manter rastreabilidade suficiente para identificar a fonte utilizada.

No minimo, as tabelas analiticas deverao manter:

`ARQUIVO_ORIGEM`

Quando uma decisao depender de uma categoria original relevante, tambem devera ser preservado um campo como:

`REDE_ORIGEM`

ou equivalente.

---

## 10. Validacoes minimas

Cada transformacao Silver devera possuir validacao independente.

As validacoes deverao verificar, conforme aplicavel:

- existencia dos arquivos Bronze esperados;
- anos esperados;
- UFs esperadas;
- etapas esperadas;
- rede publica corretamente selecionada;
- ausencia de rede privada;
- indicadores esperados;
- unicidade do grao analitico;
- tipos numericos;
- valores dentro de dominios plausiveis;
- ausencia de duplicidades indevidas;
- rastreabilidade de arquivo de origem;
- quantidade de registros por ano;
- consistencia entre transformacao e regras documentadas.

A validacao nao devera apenas conferir se o Parquet foi criado.

---

## 11. Regra de falha

A Silver devera falhar explicitamente quando:

- uma estrutura anual nao corresponder a configuracao auditada;
- uma categoria necessaria nao existir;
- uma rede publica nao puder ser identificada com seguranca;
- uma etapa nao puder ser mapeada;
- houver duplicidade no grao esperado;
- uma conversao numerica produzir perda nao documentada;
- um novo padrao estrutural surgir sem regra definida.

E preferivel interromper o pipeline a harmonizar silenciosamente uma estrutura desconhecida.

---

## 12. Ordem de implementacao

A implementacao sera realizada fonte a fonte:

1. Rendimento Escolar;
2. TDI;
3. IDEB;
4. SAEB;
5. PND 2025.

Essa ordem permite iniciar pelas estruturas historicas mais diretamente comparaveis e deixar para o SAEB e a PND as transformacoes que exigem maior cuidado de granularidade e populacao.

---

## 13. Rendimento Escolar

A Bronze do Rendimento Escolar esta concluida e validada para 2007–2023.

A auditoria para a Silver foi executada diretamente sobre os 17 Parquets Bronze por meio de:

`src/silver/rendimento/auditar_silver_rendimento.py`

A auditoria nao alterou dados.

### 13.1 Populacao analitica

A Silver utilizara, para cada Unidade Federativa e ano:

- `Localizacao = Total`;
- agregado oficial da rede publica;
- Ensino Fundamental — Anos Iniciais;
- Ensino Fundamental — Anos Finais;
- taxas de aprovacao, reprovacao e abandono.

Nao serao calculadas medias entre Federal, Estadual e Municipal.

O agregado publico ja publicado pela fonte sera utilizado diretamente.

A rede privada nao sera utilizada.

A categoria canonica sera:

`REDE = PUBLICA`

A categoria textual efetivamente encontrada na fonte sera mantida em:

`REDE_ORIGEM`

A localizacao original sera mantida em:

`LOCALIZACAO_ORIGEM`

### 13.2 Mudancas estruturais da serie

A auditoria confirmou cinco configuracoes relevantes.

#### 2007

O arquivo possui uma coluna adicional de regiao.

Campos de identificacao:

- ano: `col_001`;
- regiao: `col_002`;
- UF: `col_003`;
- localizacao: `col_004`;
- rede: `col_005`.

Colunas analiticas:

| Indicador | Anos Iniciais | Anos Finais |
|---|---|---|
| Aprovacao | `col_015` | `col_016` |
| Reprovacao | `col_033` | `col_034` |
| Abandono | `col_051` | `col_052` |

O agregado publico aparece como `Publico`.

#### 2008–2010

Campos de identificacao:

- ano: `col_001`;
- UF: `col_002`;
- localizacao: `col_003`;
- rede: `col_004`.

Colunas analiticas:

| Indicador | Anos Iniciais | Anos Finais |
|---|---|---|
| Aprovacao | `col_014` | `col_015` |
| Reprovacao | `col_032` | `col_033` |
| Abandono | `col_050` | `col_051` |

O agregado publico aparece como `Publico`.

#### 2011–2014

A estrutura passa a publicar diretamente colunas denominadas Anos Iniciais e Anos Finais.

Campos de identificacao:

- ano: `col_001`;
- UF: `col_002`;
- localizacao: `col_003`;
- rede: `col_004`.

Colunas analiticas:

| Indicador | Anos Iniciais | Anos Finais |
|---|---|---|
| Aprovacao | `col_006` | `col_007` |
| Reprovacao | `col_024` | `col_025` |
| Abandono | `col_042` | `col_043` |

O agregado publico aparece como `Publico`.

#### 2015

A disposicao das metricas permanece equivalente a 2011–2014, mas a identificacao da Unidade Federativa passa a aparecer pelo nome e a categoria publica aparece como `Publica`.

Colunas analiticas:

| Indicador | Anos Iniciais | Anos Finais |
|---|---|---|
| Aprovacao | `col_006` | `col_007` |
| Reprovacao | `col_024` | `col_025` |
| Abandono | `col_042` | `col_043` |

#### 2016

A estrutura volta a possuir coluna de regiao e desloca os campos analiticos em uma posicao.

Campos de identificacao:

- ano: `col_001`;
- regiao: `col_002`;
- UF: `col_003`;
- localizacao: `col_004`;
- dependencia administrativa: `col_005`.

Colunas analiticas:

| Indicador | Anos Iniciais | Anos Finais |
|---|---|---|
| Aprovacao | `col_007` | `col_008` |
| Reprovacao | `col_025` | `col_026` |
| Abandono | `col_043` | `col_044` |

O agregado oficial utilizado e `Publica`.

#### 2017–2023

A fonte passa a incluir Brasil, regioes geograficas e Unidades da Federacao na mesma coluna `Unidade Geografica`.

Campos de identificacao:

- ano: `col_001`;
- unidade geografica: `col_002`;
- localizacao: `col_003`;
- dependencia administrativa: `col_004`.

Colunas analiticas:

| Indicador | Anos Iniciais | Anos Finais |
|---|---|---|
| Aprovacao | `col_006` | `col_007` |
| Reprovacao | `col_024` | `col_025` |
| Abandono | `col_042` | `col_043` |

A transformacao mantera apenas as 27 Unidades Federativas.

Brasil e regioes geograficas serao excluidos por nao pertencerem ao grao analitico definido.

O agregado oficial utilizado e `Publica`.

### 13.3 Harmonizacao da UF

Nas edicoes que utilizam siglas, elas serao preservadas.

Nas edicoes que utilizam nomes completos das Unidades Federativas, sera aplicado um mapeamento explicito para as 27 siglas oficiais.

Nao havera inferencia aproximada de nomes.

O processo devera falhar se alguma UF esperada nao for reconhecida ou se houver duplicidade de uma UF na selecao publica-total.

### 13.4 Marcadores de ausencia

O marcador `--` sera convertido para valor ausente na Silver.

Essa conversao e semantica e ocorre somente agora porque, na Bronze, o marcador foi preservado como parte da fonte.

O valor `0` permanecera como zero substantivo e nunca sera interpretado como ausencia.

Nao havera imputacao de valores ausentes.

### 13.5 Conversao numerica e precisao

As taxas serao convertidas para tipo numerico.

Algumas planilhas antigas expoem residuos de representacao binaria, por exemplo valores equivalentes a `84.39999999999999`.

Na Silver, as taxas serao normalizadas para uma casa decimal.

A normalizacao nao cria nova medida: ela remove apenas residuos tecnicos de representacao do numero e mantem a precisao utilizada pelas taxas publicadas.

Os valores deverao permanecer no dominio de 0 a 100.

### 13.6 Formato Silver

Sera produzido um unico arquivo harmonizado:

`data/silver/rendimento/rendimento_2007_2023.parquet`

Grao:

`ANO + UF + ETAPA + REDE + INDICADOR`

Estrutura:

- `ANO`;
- `UF`;
- `ETAPA`;
- `REDE`;
- `INDICADOR`;
- `VALOR`;
- `REDE_ORIGEM`;
- `LOCALIZACAO_ORIGEM`;
- `ARQUIVO_ORIGEM`;
- `LINHA_ORIGEM_BRONZE`;
- `COLUNA_ORIGEM`.

As duas ultimas colunas permitem validar cada valor da Silver diretamente contra a linha e a coluna da Bronze que o originaram.

### 13.7 Cardinalidade esperada

Sao esperados:

- 17 anos;
- 27 UFs;
- 2 etapas;
- 3 indicadores;
- 1 rede canonica.

Assim:

`17 × 27 × 2 × 3 = 2.754 registros`

A presenca de valor ausente nao remove o registro do grao. O registro permanece e `VALOR` fica ausente.

### 13.8 Validacao independente

A validacao devera confirmar:

- 2.754 registros;
- 162 registros por ano;
- 27 UFs em cada ano;
- ausencia de duplicidade no grao;
- somente `REDE = PUBLICA`;
- somente Anos Iniciais e Anos Finais;
- somente aprovacao, reprovacao e abandono;
- taxas numericas entre 0 e 100;
- preservacao de zeros;
- conversao de `--` para ausencia;
- correspondencia de cada registro Silver com a linha, coluna e arquivo da Bronze;
- coerencia das combinacoes completas de aprovacao, reprovacao e abandono com total aproximado de 100%, considerando arredondamento de publicacao.

Scripts:

`src/silver/rendimento/transformar_rendimento.py`

`src/silver/rendimento/validar_silver_rendimento.py`

### 13.9 Resultado da execucao e validacao

Em 18/08/2026, a transformacao Silver do Rendimento Escolar foi executada com sucesso.

Resultado produzido:

`data/silver/rendimento/rendimento_2007_2023.parquet`

A execucao confirmou:

- 2.754 registros;
- 17 anos completos, de 2007 a 2023;
- 27 UFs em cada ano;
- 162 registros por ano;
- 2 etapas: `ANOS_INICIAIS` e `ANOS_FINAIS`;
- 3 indicadores: `APROVACAO`, `REPROVACAO` e `ABANDONO`;
- rede canonica unica: `PUBLICA`;
- nenhum valor ausente na populacao analitica selecionada.

A ausencia de valores nulos no resultado nao altera a regra metodologica definida para o marcador `--`. A conversao de `--` para ausencia permanece implementada; porem, nas linhas selecionadas para o agregado publico, localizacao Total e etapas Anos Iniciais/Anos Finais, nao houve ocorrencia desse marcador nos valores finais.

A validacao independente confirmou:

- grao analitico unico;
- dominio das taxas entre 0 e 100;
- 2.754 registros comparados diretamente com a Bronze;
- rastreabilidade por arquivo, linha e coluna de origem;
- 918 combinacoes completas de ano, UF e etapa com aprovacao, reprovacao e abandono submetidas ao teste de soma;
- coerencia das somas dentro da tolerancia definida para arredondamento de publicacao.

Status final:

`SILVER DO RENDIMENTO ESCOLAR: OK`

Com isso, o Rendimento Escolar passa a ser considerado concluido na camada Silver.

---

---

## 14. TDI — Distorcao Idade-Serie

A auditoria da Bronze da TDI foi executada diretamente sobre os 17 Parquets de 2007–2023 por meio de:

`src/silver/tdi/auditar_silver_tdi.py`

Como a primeira inspecao textual nao exibiu a categoria `Publica` nos anos mais recentes, foi executada uma verificacao focada adicional:

`src/silver/tdi/verificar_rede_publica_tdi.py`

Essa segunda verificacao normaliza acentuacao antes de comparar categorias e confirmou que **todos os anos de 2007 a 2023 possuem agregado publico explicito**.

A primeira ausencia aparente foi, portanto, um efeito do mecanismo de busca textual da auditoria: o termo sem acento `public` nao localizava corretamente `Publica`. Essa limitacao da inspecao foi identificada e corrigida antes da transformacao.

Nenhum arquivo Bronze ou Silver foi alterado por qualquer uma das duas auditorias.

### 14.1 Populacao analitica

A Silver utilizara, para cada Unidade Federativa e ano:

- `Localizacao = Total`;
- agregado oficial `Publico` ou `Publica` publicado pela fonte;
- Ensino Fundamental — Anos Iniciais;
- Ensino Fundamental — Anos Finais.

Nao sera calculada media entre Federal, Estadual e Municipal.

A categoria `Total` da dependencia administrativa nao sera usada como substituta da rede publica, porque inclui universo distinto do agregado publico.

A rede privada nao sera utilizada.

A categoria canonica sera:

`REDE = PUBLICA`

A categoria efetivamente encontrada na fonte sera preservada em:

`REDE_ORIGEM`

### 14.2 Confirmacao do agregado publico

A verificacao focada confirmou:

- 2007–2014: `Publico`;
- 2015–2023: `Publica`.

Para 2007–2016 existem 27 linhas `Publico/Publica + Localizacao Total`, uma por UF.

Para 2017–2023 existem 33 linhas `Publica + Localizacao Total`, porque a fonte reune Brasil, cinco regioes geograficas e 27 UFs.

Na Silver, Brasil e regioes serao excluidos e somente as 27 UFs serao mantidas.

### 14.3 Mudancas estruturais da serie

#### 2007–2010

Campos de identificacao:

- ano: `col_001`;
- regiao: `col_002`;
- UF: `col_003`;
- localizacao: `col_004`;
- rede: `col_005`.

TDI:

- Anos Iniciais: `col_015`;
- Anos Finais: `col_016`.

#### 2011–2014

Campos de identificacao:

- ano: `col_001`;
- regiao: `col_002`;
- UF: `col_003`;
- localizacao: `col_004`;
- rede: `col_005`.

TDI:

- Anos Iniciais: `col_007`;
- Anos Finais: `col_008`.

#### 2015

A fonte inclui codigo e sigla da UF em colunas separadas.

Campos de identificacao:

- ano: `col_001`;
- regiao: `col_002`;
- codigo da UF: `col_003`;
- sigla da UF: `col_004`;
- localizacao: `col_005`;
- rede: `col_006`.

TDI:

- Anos Iniciais: `col_008`;
- Anos Finais: `col_009`.

#### 2016

A UF passa a ser representada por nome completo.

Campos de identificacao:

- ano: `col_001`;
- regiao: `col_002`;
- UF: `col_003`;
- localizacao: `col_004`;
- dependencia administrativa: `col_005`.

TDI:

- Anos Iniciais: `col_007`;
- Anos Finais: `col_008`.

#### 2017–2023

A fonte passa a reunir Brasil, regioes geograficas e UFs em `Unidade Geografica`.

Campos de identificacao:

- ano: `col_001`;
- unidade geografica: `col_002`;
- localizacao: `col_003`;
- dependencia administrativa: `col_004`.

TDI:

- Anos Iniciais: `col_006`;
- Anos Finais: `col_007`.

### 14.4 Harmonizacao da UF

Siglas serao preservadas quando ja existentes.

Nomes completos serao convertidos para siglas por mapeamento explicito das 27 UFs.

Em 2017–2023, Brasil e regioes geograficas nao serao reconhecidos como UF e serao excluidos da populacao analitica.

A transformacao falhara se alguma UF esperada estiver ausente ou duplicada.

### 14.5 Marcadores de ausencia e precisao

O marcador `--` sera convertido para ausencia somente na Silver.

Zero permanecera zero substantivo.

Nao havera imputacao.

Residuos binarios de representacao numerica, como `21.400000000000002`, serao normalizados para uma casa decimal, preservando a precisao publicada pela fonte.

A TDI devera permanecer no intervalo de 0 a 100.

### 14.6 Formato Silver

Sera produzido:

`data/silver/tdi/tdi_2007_2023.parquet`

Grao:

`ANO + UF + ETAPA + REDE`

Estrutura:

- `ANO`;
- `UF`;
- `ETAPA`;
- `REDE`;
- `TDI`;
- `REDE_ORIGEM`;
- `LOCALIZACAO_ORIGEM`;
- `ARQUIVO_ORIGEM`;
- `LINHA_ORIGEM_BRONZE`;
- `COLUNA_ORIGEM`.

### 14.7 Cardinalidade esperada

Sao esperados:

- 17 anos;
- 27 UFs;
- 2 etapas;
- 1 rede canonica.

Assim:

`17 × 27 × 2 = 918 registros`

A presenca de valor ausente nao remove o registro do grao.

### 14.8 Validacao independente

A validacao devera confirmar:

- 918 registros;
- 54 registros por ano;
- 27 UFs em cada ano;
- ausencia de duplicidade no grao;
- somente `REDE = PUBLICA`;
- somente Anos Iniciais e Anos Finais;
- TDI numerica entre 0 e 100;
- preservacao de zeros;
- conversao de `--` para ausencia;
- correspondencia de cada registro Silver com arquivo, linha e coluna da Bronze.

Scripts:

`src/silver/tdi/transformar_tdi.py`

`src/silver/tdi/validar_silver_tdi.py`

### 14.9 Resultado da execucao e validacao

Em 18/08/2026, a transformacao Silver da TDI foi executada com sucesso.

Resultado produzido:

`data/silver/tdi/tdi_2007_2023.parquet`

A execucao confirmou:

- 918 registros;
- 17 anos completos, de 2007 a 2023;
- 27 UFs em cada ano;
- 54 registros por ano;
- 2 etapas: `ANOS_INICIAIS` e `ANOS_FINAIS`;
- rede canonica unica: `PUBLICA`;
- nenhum valor ausente na populacao analitica selecionada.

A ausencia de valores nulos no resultado nao altera a regra metodologica definida para o marcador `--`. A conversao de `--` para ausencia permanece implementada; porem, nas linhas selecionadas para o agregado publico, localizacao Total e etapas Anos Iniciais/Anos Finais, nao houve ocorrencia desse marcador nos valores finais.

A validacao independente confirmou:

- grao analitico unico;
- dominio da TDI entre 0 e 100;
- 918 registros comparados diretamente com a Bronze;
- rastreabilidade por arquivo, linha e coluna de origem;
- correspondencia integral entre os valores Silver e suas celulas de origem na Bronze.

Status final:

`SILVER DA TDI: OK`

Com isso, a TDI passa a ser considerada concluida na camada Silver.

---

## 15. IDEB — Indice de Desenvolvimento da Educacao Basica

A auditoria da Bronze do IDEB foi executada sobre os Parquets:

- `data/bronze/ideb/ideb_ai.parquet`;
- `data/bronze/ideb/ideb_af.parquet`;
- `data/bronze/ideb/ideb_em.parquet`.

O Ensino Medio foi inspecionado apenas para documentar a estrutura da fonte. A Silver historica do projeto permanece restrita aos Anos Iniciais e Anos Finais do Ensino Fundamental.

Scripts de auditoria e diagnostico:

`src/silver/ideb/auditar_silver_ideb.py`

`src/silver/ideb/verificar_rede_publica_ideb.py`

`src/silver/ideb/diagnosticar_ufs_ausentes_ideb.py`

Nenhum desses scripts altera a Bronze ou a Silver.

### 15.1 Escopo temporal

O workbook de divulgacao de 2023 contem resultados observados para:

- 2005;
- 2007;
- 2009;
- 2011;
- 2013;
- 2015;
- 2017;
- 2019;
- 2021;
- 2023.

O projeto historico comeca em 2007. Por isso, 2005 sera preservado na Bronze, mas excluido da Silver.

A serie Silver do IDEB contera nove anos:

`2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021, 2023`

O IDEB e divulgado em anos de aplicacao correspondentes a serie historica disponivel na planilha; portanto, nao serao criadas linhas artificiais para anos pares.

### 15.2 Identificacao dos anos e erro visual `20215`

O cabecalho visual da planilha contem a grafia `20215` em posicoes correspondentes a 2021.

A Bronze preserva essa caracteristica da fonte e nao a corrige.

Na Silver, a selecao do ano nao sera feita pelo texto visual do cabecalho. Sera usada a linha tecnica identificada na Bronze por `_indice_cabecalho_origem`; como `_linha_origem` utiliza numeracao iniciada em um, a linha de referencia e calculada como `_linha_origem = _indice_cabecalho_origem + 1`. Essa linha contem os nomes oficiais das variaveis:

`VL_OBSERVADO_2007`

`VL_OBSERVADO_2009`

`VL_OBSERVADO_2011`

`VL_OBSERVADO_2013`

`VL_OBSERVADO_2015`

`VL_OBSERVADO_2017`

`VL_OBSERVADO_2019`

`VL_OBSERVADO_2021`

`VL_OBSERVADO_2023`

Essa decisao evita interpretar o erro grafico como ano valido e mantem a transformacao ancorada na variavel tecnica da propria fonte.

### 15.3 Colunas do IDEB observado

Nos Anos Iniciais:

- 2007: `col_104`;
- 2009: `col_105`;
- 2011: `col_106`;
- 2013: `col_107`;
- 2015: `col_108`;
- 2017: `col_109`;
- 2019: `col_110`;
- 2021: `col_111`;
- 2023: `col_112`.

Nos Anos Finais:

- 2007: `col_094`;
- 2009: `col_095`;
- 2011: `col_096`;
- 2013: `col_097`;
- 2015: `col_098`;
- 2017: `col_099`;
- 2019: `col_100`;
- 2021: `col_101`;
- 2023: `col_102`.

A implementacao nao dependera somente dessas posicoes fixas. O script localizara cada coluna por `VL_OBSERVADO_YYYY` na linha tecnica e falhara se a variavel nao for encontrada de forma unica.

### 15.4 Rede publica

Nas linhas das Unidades Federativas, o agregado publico e publicado como:

`Publica (4)`

A Silver utilizara diretamente esse agregado oficial.

Nao sera calculada media entre redes.

Nao sera utilizado `Total (4)` como substituto da rede publica.

A rede privada e a rede estadual isolada nao serao utilizadas.

A categoria canonica sera:

`REDE = PUBLICA`

O rotulo original sera preservado em:

`REDE_ORIGEM = Publica (4)`

A nota metodologica `(4)` da propria planilha informa que as medias do SAEB 2011 e o IDEB 2011 foram calculados sem as escolas federais. A Silver nao tentara recompor ou alterar esse valor: sera preservado o resultado oficial publicado pelo Inep.

### 15.5 Harmonizacao das UFs

A auditoria inicialmente reconheceu 24 das 27 UFs porque tres nomes aparecem abreviados na propria fonte.

Foram identificadas as seguintes correspondencias:

- `R. G. do Norte` → `RN`;
- `R. G. do Sul` → `RS`;
- `M. G. do Sul` → `MS`.

Essas grafias aparecem tanto nos Anos Iniciais quanto nos Anos Finais e possuem linha `Publica (4)` com resultados para todos os nove anos da serie.

A Silver harmonizara essas tres formas para as siglas oficiais, sem modificar a Bronze.

Os demais nomes de UF tambem serao convertidos para as 27 siglas oficiais por mapeamento explicito.

A grafia de origem sera preservada em:

`GEOGRAFIA_ORIGEM`

A transformacao falhara caso, depois da harmonizacao:

- alguma das 27 UFs esteja ausente;
- exista UF adicional;
- uma UF possua mais de uma linha publica.

### 15.6 Anos Iniciais e Anos Finais

Os arquivos Bronze usados serao:

`data/bronze/ideb/ideb_ai.parquet`

`data/bronze/ideb/ideb_af.parquet`

As etapas canonicas serao:

`ANOS_INICIAIS`

`ANOS_FINAIS`

O Ensino Medio permanecera fora da Silver historica principal.

### 15.7 Marcadores de ausencia e dominio

Serao tratados como ausencia apenas:

- celula vazia;
- `-`;
- `--`.

Zero continuara sendo valor substantivo.

Nao havera imputacao.

O IDEB sera numerico e devera permanecer no intervalo de 0 a 10.

Os valores serao normalizados para uma casa decimal, preservando a precisao publicada do IDEB observado.

### 15.8 Formato Silver

Sera produzido:

`data/silver/ideb/ideb_2007_2023.parquet`

Grao:

`ANO + UF + ETAPA + REDE`

Estrutura:

- `ANO`;
- `UF`;
- `ETAPA`;
- `REDE`;
- `IDEB`;
- `GEOGRAFIA_ORIGEM`;
- `REDE_ORIGEM`;
- `ARQUIVO_ORIGEM`;
- `ABA_ORIGEM`;
- `LINHA_ORIGEM_BRONZE`;
- `COLUNA_ORIGEM`.

### 15.9 Cardinalidade esperada

Sao esperados:

- 9 anos;
- 27 UFs;
- 2 etapas;
- 1 rede canonica.

Assim:

`9 × 27 × 2 = 486 registros`

A existencia de valor ausente nao removera o registro do grao.

### 15.10 Validacao independente

A validacao devera confirmar:

- 486 registros;
- 54 registros por ano;
- 27 UFs por ano e etapa;
- ausencia de duplicidade no grao;
- somente `REDE = PUBLICA`;
- somente Anos Iniciais e Anos Finais;
- somente os nove anos previstos;
- IDEB numerico entre 0 e 10;
- harmonizacao explicita de `R. G. do Norte`, `R. G. do Sul` e `M. G. do Sul`;
- selecao de 2021 por `VL_OBSERVADO_2021`, e nao pelo cabecalho visual `20215`;
- correspondencia de cada registro Silver com arquivo, aba, linha e coluna da Bronze.

Scripts:

`src/silver/ideb/transformar_ideb.py`

`src/silver/ideb/validar_silver_ideb.py`

### 15.11 Resultado da execucao e validacao

Em 19/08/2026, a transformacao Silver do IDEB foi executada com sucesso.

Resultado produzido:

`data/silver/ideb/ideb_2007_2023.parquet`

A execucao confirmou:

- 486 registros;
- 9 anos da serie historica: 2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021 e 2023;
- 27 UFs em cada combinacao de ano e etapa;
- 243 registros para `ANOS_INICIAIS`;
- 243 registros para `ANOS_FINAIS`;
- 54 registros por ano;
- rede canonica unica: `PUBLICA`;
- nenhum valor ausente na populacao analitica selecionada.

A validacao independente confirmou:

- grao analitico unico `ANO + UF + ETAPA + REDE`;
- dominio do IDEB entre 0 e 10;
- harmonizacao dos aliases `R. G. do Norte` → `RN`, `R. G. do Sul` → `RS` e `M. G. do Sul` → `MS`, com preservacao da grafia original na proveniencia;
- identificacao de 2021 por `VL_OBSERVADO_2021`, sem dependencia do cabecalho visual `20215`;
- 486 registros comparados diretamente com a Bronze;
- rastreabilidade por arquivo, aba, linha e coluna de origem;
- correspondencia integral entre os valores Silver e suas celulas de origem na Bronze.

Status final:

`SILVER DO IDEB: OK`

Com isso, o IDEB passa a ser considerado concluido na camada Silver.

---

## 16. SAEB — auditoria preliminar da Silver

A construcao da Silver do SAEB comecou por auditoria estrutural dos nove Parquets Bronze correspondentes as edicoes de 2007 a 2023.

Script:

`src/silver/saeb/auditar_silver_saeb.py`

### 16.1 Correcao da estrategia de identificacao do cabecalho

A primeira versao da auditoria tentou inferir automaticamente uma “linha tecnica” com base na aparencia textual das celulas. Essa heuristica se mostrou inadequada nas edicoes mais recentes.

A propria saida demonstrou o problema: embora a primeira linha de 2017, 2019 e 2021 contenha os nomes das variaveis da fonte, a heuristica classificou como supostas linhas tecnicas registros de dados posteriores.

A decisao foi abandonar essa inferencia.

A versao corrigida utiliza como referencia autoritativa:

`_indice_cabecalho_origem`

Esse metadado foi gravado durante a ingestao Bronze justamente para registrar a posicao real do cabecalho na fonte. A linha fisica correspondente e obtida por:

`_linha_origem = _indice_cabecalho_origem + 1`

Justificativa: a camada Silver deve interpretar a estrutura a partir da proveniencia preservada na Bronze, e nao por uma tentativa probabilistica de reconhecer cabecalhos pelo conteudo das celulas.

Impacto: a correcao modifica apenas a auditoria. Nenhum dado Bronze foi alterado e nenhuma transformacao Silver do SAEB foi executada antes da resolucao do problema.

### 16.2 Evidencias ja confirmadas

A auditoria confirmou que 2007 e 2009 estao em granularidade UF e possuem a categoria:

`Total - Federal, Estadual, Municipal e Privada`

Esse total inclui a rede privada e, portanto, nao podera ser utilizado como representacao da rede publica.

Em 2011, a Bronze contem explicitamente:

- `SIGLA_UF`;
- `ID_SERIE`;
- `ID_TIPO_REDE`;
- `ID_LOCALIZACAO`;
- `NU_PARTICIPANTES`;
- `MEDIA_LP`;
- `MEDIA_MT`.

Foram observadas as series 5, 9 e 12 e seis codigos de rede, de 0 a 5. A regra de selecao do agregado publico sera confirmada pela auditoria focada antes da transformacao.

Em 2013 e 2015, a fonte organiza diretamente as proficiencias de Anos Iniciais e Anos Finais em colunas distintas de Lingua Portuguesa e Matematica.

Em 2017, 2019 e 2021, as fontes continuam em granularidade UF, com dimensoes de dependencia administrativa, localizacao e capital, alem das medias de proficiencia por etapa.

A edicao de 2023 permanece metodologicamente distinta porque sua Bronze esta em granularidade escola. Nenhuma media simples entre escolas sera produzida. A forma de agregacao para UF somente sera definida depois da confirmacao das variaveis de participacao/presenca e das medias correspondentes.

### 16.3 Estado da decisao

A Silver do SAEB permanece em auditoria.

Ainda nao esta autorizada a transformacao porque precisam ser fechadas, com evidencia da propria Bronze:

- a categoria publica exata em cada edicao de granularidade UF;
- a selecao de localizacao/capital usada para representar o total da UF;
- a regra especifica de 2007 e 2009, que nao possuem no total geral uma populacao exclusivamente publica;
- a estrutura completa de 2023;
- a variavel de ponderacao apropriada para a agregacao escola → UF em 2023.

Nenhuma dessas regras sera inferida por media aritmetica simples.

---

### 16.4 Resultado da verificacao focada de 2007 a 2021

A verificacao focada confirmou que as edicoes de 2007 a 2021 permitem selecionar diretamente um unico estrato de UF para os Anos Iniciais e Anos Finais, sem produzir media aritmetica entre redes.

#### 2007 e 2009

A fonte disponibiliza a categoria:

`Total - Estadual e Municipal`

com:

`LOCALIZACAO = Total`

`CAPITAL = Total`

A selecao produz exatamente:

- 27 UFs;
- nenhuma UF faltante;
- nenhuma UF adicional;
- nenhuma duplicidade por UF;
- nenhum valor ausente;
- nenhum valor zero nas quatro medias de interesse.

A categoria:

`Total - Federal, Estadual, Municipal e Privada`

nao sera usada porque inclui a rede privada.

Tambem nao existe categoria `Federal` isolada nas planilhas dessas duas edicoes.

Decisao metodologica: para 2007 e 2009 sera preservado o agregado publico disponivel na propria fonte, `Total - Estadual e Municipal`. Ele sera harmonizado para a categoria analitica `PUBLICA`, mas a origem exata sera mantida em `REDE_ORIGEM`.

Limitacao de comparabilidade: esse agregado nao explicita a rede federal, ao contrario do agregado utilizado a partir de 2013. A serie historica devera manter essa ressalva documental e nao tentara estimar ou reconstruir a parcela federal.

#### 2011

A selecao validada e:

- `ID_SERIE = 5` para Anos Iniciais;
- `ID_SERIE = 9` para Anos Finais;
- `ID_TIPO_REDE = 5` para rede publica;
- `ID_LOCALIZACAO = 0`;
- `ID_CAPITAL = 0`.

Para cada etapa foram obtidas exatamente 27 UFs, sem duplicidades e sem valores ausentes em `MEDIA_LP`, `MEDIA_MT` e `NU_PARTICIPANTES`.

A Silver usara diretamente `MEDIA_LP` e `MEDIA_MT` publicadas nesse estrato. `NU_PARTICIPANTES` permanecera como informacao de origem/validacao; nao sera usado para recalcular uma media ja publicada para a UF.

#### 2013, 2015, 2017, 2019 e 2021

A selecao validada e:

`REDE = Total - Federal, Estadual e Municipal`

`LOCALIZACAO = Total`

`CAPITAL = Total`

Em todas as cinco edicoes foram confirmadas:

- 27 UFs;
- nenhuma UF faltante;
- nenhuma UF adicional;
- nenhuma duplicidade por UF;
- valores completos para Lingua Portuguesa e Matematica nos Anos Iniciais e Anos Finais.

A Silver utilizara diretamente esse agregado oficial, sem media entre Federal, Estadual e Municipal.

Em 2015 a fonte informa que valor `0` representa impossibilidade de calcular a media para o estrato. No estrato publico/Total/Total selecionado para a Silver nao foi observado nenhum zero nas quatro medias de interesse.

### 16.5 Diagnostico de 2023 e suspensao da regra por numero de presentes

A Bronze de 2023 esta em granularidade escola e contem 70.151 registros de escolas publicas, distribuidos pelas 27 UFs.

Foram identificadas as variaveis necessarias para um calculo exploratorio:

Anos Iniciais:

- `NU_PRESENTES_5EF`;
- `MEDIA_5EF_LP`;
- `MEDIA_5EF_MT`.

Anos Finais:

- `NU_PRESENTES_9EF`;
- `MEDIA_9EF_LP`;
- `MEDIA_9EF_MT`.

Foi testada, apenas como diagnostico, a media das medias escolares ponderada pelo numero de presentes da etapa. O teste produziu resultados para as 27 UFs e nao gerou ausencia de resultado estadual.

Esse resultado, entretanto, nao autoriza a regra Silver.

A documentacao oficial do Inep para o Saeb 2023 informa que a producao de resultados agregados utiliza pesos amostrais. Esses pesos incorporam o desenho da avaliacao e procedimentos de expansao/calibracao e permitem a formacao de resultados para Brasil, regioes e UFs. Por isso, `NU_PRESENTES` nao pode ser tratado automaticamente como equivalente ao peso estatistico oficial.

Decisao metodologica: a media escolar ponderada por `NU_PRESENTES` permanece apenas como teste diagnostico e nao sera usada na Silver enquanto nao for confrontada com os resultados agregados oficiais de 2023.

### 16.6 Validacao externa necessaria para 2023

O Inep disponibiliza, na pagina oficial de resultados do Saeb 2023:

- Planilhas de Resultados para Brasil, estados e municipios;
- Microdados Saeb 2023;
- Nota Tecnica Saeb 2023;
- relatorio de dados de proficiencia.

A planilha oficial de resultados estaduais sera usada como referencia de validacao do calculo produzido a partir das escolas.

Procedimento definido:

1. obter e preservar a planilha oficial de resultados agregados de 2023;
2. identificar o estrato de UF, rede publica e localizacao total para 5º e 9º anos;
3. confrontar os 108 valores candidatos produzidos pela Bronze de escolas:
   `27 UFs × 2 etapas × 2 disciplinas`;
4. comparar com a precisao publicada pelo Inep;
5. somente depois decidir a fonte operacional da Silver 2023.

Se a agregacao derivada das escolas reproduzir os resultados oficiais dentro da precisao publicada, podera ser mantida, com documentacao da validacao.

Se nao reproduzir, a Silver nao usara a ponderacao por `NU_PRESENTES`. Nesse caso, a planilha agregada oficial devera ser incorporada ao pipeline como fonte canonica de 2023, com reabertura controlada da etapa Bronze do SAEB e nova validacao.

Essa decisao evita produzir uma serie aparentemente comparavel por meio de uma ponderacao que nao reproduza o estimador oficial do Inep.

---

### 16.7 Fonte oficial agregada de 2023 incorporada a auditoria

Foi incorporado ao diretorio RAW do SAEB o pacote oficial de resultados agregados de 2023, preservando sua estrutura original:

`data/raw/saeb/`

Arquivos identificados:

- `12EM_Erros_amostrais_e_intervalo_de_confianca.xlsx`;
- `2anoEF_Erros_amostrais_e_intervalo_de_confianca_Taxa_alfabetizacao.xlsx`;
- `5anoEF_Erros_amostrais_e_intervalo_de_confianca.xlsx`;
- `9anoEF_Erros_amostrais_e_intervalo_de_confianca.xlsx`;
- `Resultados_Saeb_2023_Brasil_Estados_Municipios.xlsb`.

Para a validacao da Silver, o arquivo prioritario sera:

`Resultados_Saeb_2023_Brasil_Estados_Municipios.xlsb`

Justificativa: ele reune os resultados agregados oficiais para Brasil, estados e municipios e permitira confrontar diretamente os valores estaduais publicados pelo Inep com os valores derivados da Bronze escolar.

Os arquivos de erros amostrais e intervalos de confianca serao mantidos no RAW como documentacao complementar da fonte, mas nao serao usados como substitutos da media de proficiencia.

Antes da comparacao numerica, sera executada uma auditoria estrutural do arquivo `.xlsb` para identificar:

- nomes das abas;
- posicao dos cabecalhos;
- nivel geografico;
- dependencia administrativa/rede;
- localizacao;
- etapa;
- disciplina;
- variaveis de proficiencia.

Nenhuma regra de agregacao de 2023 sera finalizada antes dessa auditoria.

---

### 16.8 Veredito da comparacao oficial × agregacao escolar em 2023

A comparacao entre os resultados oficiais estaduais do Saeb 2023 e a media das medias escolares ponderada por `NU_PRESENTES` foi concluida.

Foram confrontados:

`27 UFs × 2 etapas × 2 disciplinas = 108 valores`

Referencia oficial:

- aba `Estados`;
- `DEPENDENCIA_ADM = Total - Federal, Estadual e Municipal`;
- `LOCALIZACAO = Total`;
- `CAPITAL = Total`;
- `MEDIA_5_LP`;
- `MEDIA_5_MT`;
- `MEDIA_9_LP`;
- `MEDIA_9_MT`.

Candidato derivado da Bronze escolar:

- `IN_PUBLICA = 1`;
- `MEDIA_5EF_LP` e `MEDIA_5EF_MT` ponderadas por `NU_PRESENTES_5EF`;
- `MEDIA_9EF_LP` e `MEDIA_9EF_MT` ponderadas por `NU_PRESENTES_9EF`.

Resultado:

- coincidencias apos arredondamento para duas casas: `0/108`;
- diferenca absoluta media: `1,389714`;
- diferenca absoluta mediana: `1,092905`;
- maior diferenca absoluta: `6,150034`.

Por metrica:

- Anos Iniciais / Lingua Portuguesa: 0/27 coincidencias; diferenca media 0,937030;
- Anos Iniciais / Matematica: 0/27 coincidencias; diferenca media 1,010801;
- Anos Finais / Lingua Portuguesa: 0/27 coincidencias; diferenca media 1,820663;
- Anos Finais / Matematica: 0/27 coincidencias; diferenca media 1,790360.

A divergencia nao e residual de arredondamento. Em alguns casos supera quatro ou seis pontos de proficiencia.

Decisao metodologica: `NU_PRESENTES` nao sera usado como peso canonico para reconstruir resultados estaduais de 2023.

Justificativa: a ponderacao por presentes nao reproduz nenhum dos 108 resultados oficiais publicados. A adocao dessa regra criaria uma serie historica metodologicamente incompativel com o resultado oficial do Saeb.

### 16.9 Reabertura controlada da Bronze do SAEB 2023

A Bronze escolar de 2023 permanece valida e sera preservada:

`data/bronze/saeb/saeb_2023.parquet`

Ela representa corretamente a fonte `TS_ESCOLA_2023.csv` na granularidade escola e nao sera substituida nem sobrescrita.

Entretanto, ela nao e suficiente para reproduzir o estimador estadual oficial utilizado no escopo historico deste projeto.

Por isso, sera adicionada uma segunda fonte Bronze de 2023, correspondente aos resultados oficiais agregados de UF:

RAW:

`data/raw/saeb/Resultados_Saeb_2023_Brasil_Estados_Municipios.xlsb`

Aba preservada:

`Estados`

Bronze adicional:

`data/bronze/saeb/saeb_2023_resultados_uf.parquet`

Scripts:

`src/bronze/saeb/ingest_saeb_resultados_2023.py`

`src/bronze/saeb/validar_bronze_saeb_resultados_2023.py`

A nova Bronze preservara integralmente a aba `Estados`, sem filtrar rede, localizacao ou indicadores durante a ingestao.

Metadados:

- `_fonte`;
- `_sha256_arquivo`;
- `_arquivo_origem`;
- `_aba_origem`;
- `_ano_referencia`;
- `_indice_cabecalho_origem`;
- `_linha_origem`;
- `_granularidade_origem`.

A existencia de duas fontes Bronze em 2023 e intencional:

- `saeb_2023.parquet`: granularidade `ESCOLA`, preservando os microdados escolares;
- `saeb_2023_resultados_uf.parquet`: granularidade `UF`, preservando os resultados agregados oficiais.

A Silver historica usara a segunda fonte para 2023 porque o seu grao analitico e UF e a tentativa de reconstruir o estimador estadual a partir das escolas nao reproduziu os valores oficiais.

Essa decisao nao invalida a Bronze escolar. Ela separa dois produtos oficiais com granularidades e finalidades metodologicas distintas.

### 16.10 Regra Silver consolidada do SAEB apos a validacao de 2023

Se a nova Bronze agregada de 2023 passar pela validacao RAW → Bronze, a regra Silver ficara:

- 2007: `Total - Estadual e Municipal`, localizacao `Total`, capital `Total`;
- 2009: `Total - Estadual e Municipal`, localizacao `Total`, capital `Total`;
- 2011: `ID_TIPO_REDE = 5`, `ID_LOCALIZACAO = 0`, `ID_CAPITAL = 0`, series 5 e 9;
- 2013: `Total - Federal, Estadual e Municipal`, localizacao `Total`, capital `Total`;
- 2015: mesma regra de 2013;
- 2017: mesma regra de 2013;
- 2019: mesma regra de 2013;
- 2021: mesma regra de 2013;
- 2023: resultados oficiais agregados da aba `Estados`, com `Total - Federal, Estadual e Municipal`, localizacao `Total` e capital `Total`.

Em todos os anos serao selecionadas apenas:

- Anos Iniciais;
- Anos Finais;
- Lingua Portuguesa;
- Matematica.

A Silver nao calculara medias entre redes e nao reconstruira o resultado estadual de 2023 a partir das medias escolares.

---

### 16.11 Politica transversal de rede publica no projeto

A categoria analitica `PUBLICA` nao significa exclusao da rede federal.

A regra geral do projeto e:

`PUBLICA = Federal + Estadual + Municipal`

sempre que a fonte oficial disponibiliza essa populacao de forma explicita ou por categoria publica consolidada.

A rede privada e excluida da populacao analitica historica porque o escopo do projeto e a rede publica.

Aplicacao por indicador:

- Rendimento Escolar: utiliza o agregado oficial `Publica`; nao e calculada media entre Federal, Estadual e Municipal.
- TDI: utiliza o agregado oficial `Publico`/`Publica`; nao e calculada media entre dependencias.
- IDEB: utiliza a categoria oficial `Publica (4)`. Eventuais particularidades metodologicas da propria publicacao, como a nota referente ao calculo de 2011 sem escolas federais, sao preservadas como caracteristica da fonte e nao como filtro criado pelo pipeline.
- SAEB 2013–2023: utiliza o agregado oficial `Total - Federal, Estadual e Municipal`.
- SAEB 2011: utiliza o codigo oficial de rede publica ja identificado na fonte.
- SAEB 2007 e 2009: a fonte de resultados por UF disponibiliza `Total - Estadual e Municipal`, mas nao apresenta categoria Federal isolada nem agregado Federal + Estadual + Municipal. Por isso, essas duas edicoes constituem excecao documental: a serie usa o agregado publico disponivel na fonte e registra a ausencia explicita da rede federal nessa categoria.
- PND: a logica de rede publica nao se aplica da mesma forma, pois o conjunto analitico da PND e definido pelos criterios proprios de presenca e completude da avaliacao, e nao por uma serie historica de redes escolares equivalente aos demais indicadores.

Portanto, o projeto nao adota a regra “retirar Federal e Particular”.

A regra correta e “retirar a rede privada e preservar a rede federal dentro da rede publica sempre que ela estiver contemplada no agregado oficial”. As excecoes sao documentadas quando a propria fonte historica nao oferece esse agregado.

---

### 16.12 Tipagem fisica da Bronze agregada do SAEB 2023

Durante a primeira execucao da ingestao da aba `Estados`, o `pyarrow` interrompeu a gravacao porque as colunas da planilha possuem conteudo heterogeneo: a primeira linha contem os nomes tecnicos das variaveis, enquanto as linhas seguintes contem valores numericos ou categorias.

Exemplo:

- `col_001`, linha 1: `ANO_SAEB`;
- `col_001`, linhas de dados: `2023`.

O Pandas leu essa coluna como `object`, mas o Arrow tentou inferir um unico tipo fisico para o Parquet e encontrou simultaneamente texto e inteiro.

Decisao tecnica: todas as colunas de origem `col_001 ... col_NNN` da nova Bronze agregada de 2023 serao armazenadas como texto anulavel.

Justificativa:

- a Bronze deve preservar a estrutura fisica da fonte, inclusive a linha de cabecalho;
- nao cabe a Bronze atribuir tipos analiticos a proficiencias, codigos ou categorias;
- o Parquet exige um tipo logico consistente por coluna;
- armazenar as celulas de origem como texto evita coercao indevida e perda da linha de cabecalho;
- a conversao para numero sera feita somente na Silver, depois da identificacao da variavel pelo cabecalho preservado.

Valores realmente ausentes continuam ausentes (`null`) e nao sao convertidos para as strings `"nan"` ou `"None"`.

A validacao independente compara cada celula da fonte RAW com sua representacao textual normalizada na Bronze, alem de verificar SHA-256, arquivo, aba, linha fisica, cabecalho e granularidade.

---

### 16.13 Otimizacao da validacao RAW ↔ Bronze agregada de 2023

A primeira versao do validador independente percorria todas as celulas da aba `Estados` com acessos repetidos por `DataFrame.iloc`.

Embora o conjunto possua apenas 1.553 linhas e 177 colunas, esse padrao e ineficiente em Pandas porque cada acesso escalar cria sobrecarga de indexacao e conversao. Na execucao real, o processo permaneceu por tempo excessivo sem produzir nova saida no terminal.

Decisao tecnica: a comparacao foi substituida por uma validacao vetorizada.

Procedimento:

1. a RAW e normalizada com a mesma regra textual usada na ingestao;
2. as colunas sao harmonizadas para `col_001 ... col_177`;
3. RAW normalizada e Bronze sao alinhadas na mesma ordem;
4. ausencias sao substituidas temporariamente por um marcador exclusivo apenas para comparacao;
5. a igualdade e calculada de forma vetorizada com `DataFrame.eq`;
6. se houver divergencia, somente as primeiras 20 celulas diferentes sao materializadas para diagnostico.

A regra metodologica da validacao nao mudou: continuam sendo confrontadas todas as celulas de origem. A alteracao e exclusivamente de eficiencia computacional.

O validador tambem passou a emitir etapas de progresso (`1/5` a `5/5`) para tornar evidente em qual operacao uma eventual demora ocorre.

---

### 16.14 Bronze agregada oficial do Saeb 2023 validada

A nova Bronze de resultados oficiais agregados de UF foi executada e validada com sucesso.

Arquivo:

`data/bronze/saeb/saeb_2023_resultados_uf.parquet`

Resultado da validacao:

- 1.553 linhas RAW/Bronze;
- 177 colunas de origem;
- 274.881 celulas de origem comparadas;
- SHA-256 da fonte validado;
- reproducao integral da aba `Estados` apos normalizacao textual: OK;
- proveniencia de arquivo, aba, linha, cabecalho e granularidade: OK;
- estrato `Total - Federal, Estadual e Municipal` / localizacao `Total` / capital `Total`: 27 UFs, sem duplicidade.

Faixas observadas no estrato publico estadual:

- `MEDIA_5_LP`: 185,22 a 225,51;
- `MEDIA_5_MT`: 193,75 a 239,52;
- `MEDIA_9_LP`: 230,61 a 265,44;
- `MEDIA_9_MT`: 230,17 a 264,71.

A extensao controlada da Bronze do Saeb 2023 esta, portanto, concluida.

### 16.15 Implementacao definida para a Silver do SAEB

A Silver do SAEB tera o grao:

`ANO + UF + ETAPA + REDE + DISCIPLINA`

Colunas analiticas principais:

- `ANO`;
- `UF`;
- `ETAPA`;
- `REDE`;
- `DISCIPLINA`;
- `PROFICIENCIA`.

Colunas de rastreabilidade:

- `REDE_ORIGEM`;
- `LOCALIZACAO_ORIGEM`;
- `CAPITAL_ORIGEM`;
- `ARQUIVO_ORIGEM`;
- `ABA_ORIGEM`;
- `LINHA_ORIGEM_BRONZE`;
- `COLUNA_ORIGEM`;
- `GRANULARIDADE_ORIGEM`.

Regras por edicao:

- 2007 e 2009: `Total - Estadual e Municipal`, localizacao `Total`, capital `Total`; Anos Iniciais a partir de `MEDIA_4_LP`/`MEDIA_4_MT` e Anos Finais a partir de `MEDIA_8_LP`/`MEDIA_8_MT`;
- 2011: `ID_TIPO_REDE = 5`, `ID_LOCALIZACAO = 0`, `ID_CAPITAL = 0`; `ID_SERIE = 5` para Anos Iniciais e `ID_SERIE = 9` para Anos Finais; proficiencias `MEDIA_LP` e `MEDIA_MT`;
- 2013 e 2015: cabecalho hierarquico; `Total - Federal, Estadual e Municipal`, localizacao `Total`, capital `Total`; proficiencias nas posicoes auditadas `col_005`/`col_006` (Anos Iniciais) e `col_007`/`col_008` (Anos Finais);
- 2017, 2019, 2021 e 2023: `Total - Federal, Estadual e Municipal`, localizacao `Total`, capital `Total`; uso dos campos tecnicos proprios de cada fonte para 5º e 9º anos;
- em 2015, valor `0` nas medias continua sendo tratado como ausencia apenas porque a propria fonte informa que zero representa impossibilidade de calculo do estrato;
- em 2023, a Silver utiliza exclusivamente a Bronze oficial agregada de UF e nao reconstroi resultados estaduais a partir das medias escolares.

Normalizacao:

- `REDE = PUBLICA`;
- `ETAPA = ANOS_INICIAIS | ANOS_FINAIS`;
- `DISCIPLINA = LP | MT`;
- UFs harmonizadas para siglas oficiais de duas letras;
- proficiencias convertidas para numero e arredondadas para duas casas decimais, acompanhando a precisao publicada pela fonte;
- marcadores `-`, `--` e vazios sao tratados como ausencia;
- nao ha imputacao;
- nao ha media aritmetica entre redes.

A quantidade estrutural esperada e:

`9 anos × 27 UFs × 2 etapas × 2 disciplinas = 972 registros`

Essa cardinalidade so sera considerada concluida depois da execucao da transformacao e da validacao independente.

### 16.16 Validacao independente definida para a Silver do SAEB

O validador da Silver nao importa nem reutiliza as funcoes do transformador.

Ele reconstroi de forma independente, diretamente das Bronzes, os registros esperados para cada edicao e verifica:

- 9 anos esperados;
- 27 UFs por ano e etapa;
- duas etapas;
- duas disciplinas;
- rede canonica `PUBLICA`;
- unicidade do grao;
- ausencia de proficiencias nulas;
- dominio plausivel de proficiencia entre 0 e 500;
- regra especifica de zero de 2015;
- selecao de rede/localizacao/capital por edicao;
- valor publicado em cada celula de origem;
- arquivo, aba, linha, coluna e granularidade de origem;
- uso da Bronze oficial agregada de UF em 2023.

A Silver so sera marcada como concluida depois de o validador retornar `SILVER DO SAEB: OK`.

---

### 16.17 Correcao da leitura de 2013 e 2015 na transformacao Silver

A primeira execucao de `transformar_saeb.py` foi interrompida em 2013 porque o transformador procurava a variavel tecnica `DEPENDENCIA_ADM`.

Esse nome nao existe nas Bronzes de 2013 e 2015.

A auditoria anterior ja havia demonstrado que essas duas edicoes usam cabecalho hierarquico em tres linhas. Em 2013, o inicio do cabecalho esta em `_linha_origem = 4`; em 2015, em `_linha_origem = 3`.

Estrutura fisica confirmada para ambas:

- `col_001`: UF;
- `col_002`: REDE;
- `col_003`: LOCALIZACAO;
- `col_004`: CAPITAL;
- `col_005`: Anos Iniciais / Lingua Portuguesa;
- `col_006`: Anos Iniciais / Matematica;
- `col_007`: Anos Finais / Lingua Portuguesa;
- `col_008`: Anos Finais / Matematica.

As linhas seguintes do cabecalho identificam, separadamente, etapa e disciplina. Portanto, nao e metodologicamente correto inventar nomes tecnicos como `DEPENDENCIA_ADM`, `MEDIA_5_LP` ou `MEDIA_9_MT` para essas duas fontes.

Decisao de implementacao:

- 2013 e 2015 passam a usar explicitamente as posicoes de coluna confirmadas pela auditoria;
- a selecao da rede continua sendo `Total - Federal, Estadual e Municipal`;
- localizacao e capital continuam `Total`;
- as UFs sao harmonizadas a partir dos nomes presentes em `col_001`;
- a regra especifica de 2015, em que valor `0` significa media nao calculavel para o estrato, permanece;
- 2017, 2019, 2021 e 2023 continuam usando os cabecalhos tecnicos de suas proprias fontes.

O validador independente foi corrigido pela mesma evidencia estrutural, mas mantem implementacao propria: ele reconstroi os registros esperados diretamente das Bronzes sem importar funcoes do transformador.

A falha nao indica problema nos dados ou na Bronze. Ela revelou uma suposicao incorreta da primeira versao da Silver sobre a uniformidade dos cabecalhos entre edicoes.

---

### 16.18 Execucao e validacao final da Silver do SAEB

A transformacao Silver do SAEB foi executada com sucesso em 19/08/2026.

Arquivo produzido:

`data/silver/saeb/saeb_2007_2023.parquet`

Resultado da transformacao:

- 972 registros;
- anos: 2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021 e 2023;
- 27 UFs;
- etapas: `ANOS_INICIAIS` e `ANOS_FINAIS`;
- disciplinas: `LP` e `MT`;
- rede canonica: `PUBLICA`;
- valores ausentes: 0.

A cardinalidade observada corresponde exatamente ao grao planejado:

`9 anos × 27 UFs × 2 etapas × 2 disciplinas = 972 registros`

A validacao independente tambem foi concluida com sucesso.

Foram confirmados:

- 9/9 anos esperados;
- 27 UFs por ano e etapa;
- unicidade do grao `ANO + UF + ETAPA + REDE + DISCIPLINA`;
- dominio plausivel das proficiencias entre 0 e 500;
- regra especifica de zero do Saeb 2015;
- preservacao, em 2007 e 2009, do agregado de origem `Total - Estadual e Municipal`;
- preservacao, de 2013 a 2023, do agregado oficial `Total - Federal, Estadual e Municipal`;
- uso, em 2023, da Bronze oficial agregada de UF, e nao da media das escolas ponderada por `NU_PRESENTES`;
- comparacao direta dos 972 registros com as respectivas Bronzes;
- rastreabilidade de arquivo, aba, linha, coluna e granularidade.

Resultado final do validador:

`SILVER DO SAEB: OK`

A Silver do SAEB esta concluida e nao deve ser reaberta, salvo mudanca das fontes ou descoberta de evidencia metodologica nova que contradiga as decisoes ja documentadas.

---

## 17. PND 2025 — definicao da Silver

### 17.1 Evidencia da auditoria da populacao

A Bronze da PND preserva 1.087.359 registros substantivos do arquivo principal, alem da linha fisica de cabecalho.

A auditoria da populacao mostrou:

- 759.152 registros com os cinco resultados preenchidos;
- 328.207 registros com os cinco resultados ausentes;
- 0 registros parcialmente preenchidos.

Os cinco campos avaliados conjuntamente sao:

- `PROFICIENCIA`;
- `NT_OBJ`;
- `NT_DIS`;
- `NT_GER`;
- `QT_ACERTOS`.

Entre os registros com `TP_PRES = 555`:

- 759.140 possuem os cinco resultados completos;
- 966 nao possuem o conjunto completo de resultados.

Tambem existem 12 registros com `TP_PRES = 888` e resultados completos.

### 17.2 Populacao analitica

A populacao Silver e definida por duas condicoes simultaneas:

`TP_PRES = 555`

e

`PROFICIENCIA + NT_OBJ + NT_DIS + NT_GER + QT_ACERTOS completos`

A cardinalidade esperada e:

`759.140 registros`

Os 12 registros `TP_PRES = 888` com resultados completos nao sao incluidos, porque a presenca e parte explicita da definicao da populacao analitica.

Os 966 registros `TP_PRES = 555` sem conjunto completo de resultados tambem nao sao incluidos.

Essa regra nao imputa notas nem interpreta ausencia como zero.

### 17.3 Localizacao geografica

A PND utiliza a localizacao da aplicacao da prova.

Na Silver:

- `CO_MUNICIPIO_PROVA` preserva o codigo do municipio do local de prova;
- `UF_PROVA` e derivada diretamente de `SG_UF_MUNICIPIO_PROVA`.

A UF nao representa residencia do participante.

O nome do municipio nao sera incorporado nesta etapa. O codigo IBGE permanece disponivel para construcao posterior de dimensao geografica na Gold, utilizando a tabela oficial de municipios presente no dicionario da PND.

### 17.4 Area da prova

`CO_GRUPO` e definido pelo dicionario oficial como o codigo da area da prova de enquadramento do curso no Enade.

A Silver preserva o codigo e acrescenta `AREA_PROVA` com a categoria oficial correspondente.

Sao esperadas 17 categorias:

- 702 — Matematica;
- 904 — Letras - Portugues;
- 905 — Letras - Portugues e Ingles;
- 906 — Letras - Portugues e Espanhol;
- 1402 — Fisica;
- 1502 — Quimica;
- 1602 — Ciencias Biologicas;
- 2001 — Pedagogia;
- 2402 — Historia;
- 2501 — Artes Visuais;
- 3002 — Geografia;
- 3202 — Filosofia;
- 3502 — Educacao Fisica;
- 4005 — Ciencia da Computacao;
- 4301 — Musica;
- 5402 — Ciencias Sociais;
- 6407 — Letras - Ingles.

Os rotulos persistidos em `AREA_PROVA` mantem a identificacao oficial `(LICENCIATURA)` do dicionario.

Se surgir `CO_GRUPO` sem categoria documentada, a transformacao devera falhar explicitamente.

### 17.5 Tipagem

Na Bronze, as 26 colunas sao preservadas como texto tecnico.

Na Silver:

- ano, codigos, presenca, situacao, caderno e quantidade de acertos sao convertidos para inteiros;
- `PROFICIENCIA`, `NT_OBJ`, `NT_DIS` e `NT_GER` sao convertidos para numeros decimais;
- `UF_PROVA`, `AREA_PROVA` e metadados textuais permanecem texto.

A conversao numerica aceita virgula ou ponto decimal.

O literal `NA`, celula vazia ou valor nulo e interpretado como ausencia apenas para fins de tipagem e definicao da populacao.

Nao ha arredondamento analitico na transformacao da PND.

#### Dominio dos resultados numericos

A primeira execucao da transformacao foi interrompida porque a versao inicial do script impunha, por precaucao, a regra de que `PROFICIENCIA`, `NT_OBJ`, `NT_DIS` e `NT_GER` nao poderiam assumir valores negativos.

Essa regra foi removida.

A evidencia documental utilizada no projeto identifica os campos e sua funcao, mas nao estabelece, no material auditado, um limite inferior obrigatorio igual a zero para essas quatro medidas. Por isso, rejeitar registros negativos representaria introduzir uma restricao nao documentada pela fonte.

Decisao:

- valores numericos publicados em `PROFICIENCIA`, `NT_OBJ`, `NT_DIS` e `NT_GER` sao preservados, inclusive se negativos;
- o transformador e o validador exibem minimo, maximo e quantidade de valores negativos de cada medida para transparencia;
- nenhum valor e recodificado, truncado ou substituido por zero;
- `QT_ACERTOS` continua obrigado a ser maior ou igual a zero, porque representa uma contagem de acertos.

Essa alteracao corrige uma validacao excessivamente restritiva do pipeline e nao altera a definicao da populacao analitica de 759.140 registros.

### 17.6 Colunas nao levadas para a Silver

Nao serao transportados para a Silver factual:

- `DS_VT_GAB_OBJ`;
- `DS_VT_ESC_OBJ`;
- `DS_VT_ACE_OBJ`;
- `CO_RS_I1` a `CO_RS_I9`.

Justificativa:

esses campos nao sao necessarios as analises atualmente definidas para o dashboard, que utilizam medias de acertos e notas por UF e area, alem de medidas de participantes abaixo de limiares analiticos.

A exclusao dessas colunas da Silver nao representa perda da fonte: todos esses valores permanecem disponiveis na Bronze reproduzivel.

### 17.7 Rastreabilidade e ausencia de identificador individual

O arquivo principal nao fornece um identificador individual do participante.

Por isso, a Silver nao inventara um codigo de participante.

`LINHA_ORIGEM_BRONZE` e preservada como identificador tecnico unico do registro para:

- validacao;
- diagnostico;
- retorno ao registro de origem.

Ela nao deve ser interpretada como identificador pessoal ou chave de negocio.

Tambem serao preservados:

- `ARQUIVO_ORIGEM`;
- `GRANULARIDADE_ORIGEM`.

### 17.8 Validacao independente

O validador nao reutiliza as funcoes do transformador.

Ele reconstroi diretamente da Bronze:

- a quantidade total de registros;
- a completude conjunta dos cinco resultados;
- as 759.140 linhas da populacao analitica;
- a exclusao dos 966 registros `TP_PRES = 555` sem resultados completos;
- a exclusao dos 12 registros `TP_PRES = 888` com resultados;
- a UF de prova;
- o codigo e o rotulo oficial da area;
- os cinco resultados numericos;
- os codigos mantidos na Silver;
- a linha e o arquivo de origem.

Na validacao independente, os 759.140 registros Silver foram comparados diretamente com a referencia reconstruida da Bronze.

### 17.9 Situacao de implementacao

Arquivos implementados:

`src/silver/pnd/transformar_pnd.py`

`src/silver/pnd/validar_silver_pnd.py`

Saida gerada:

`data/silver/pnd/pnd_2025.parquet`

Os criterios definidos para conclusao foram atendidos:

1. a transformacao produziu exatamente 759.140 registros;
2. a validacao independente retornou `SILVER DA PND 2025: OK`.

Status:

`PND 2025 — SILVER ✅`

---

### 17.10 Execucao e validacao final da Silver da PND 2025

A transformacao Silver da PND 2025 foi executada com sucesso em 19/08/2026.

Arquivo produzido:

`data/silver/pnd/pnd_2025.parquet`

Resultado da transformacao:

- registros de dados na Bronze: 1.087.359;
- registros com os cinco resultados completos: 759.152;
- registros com resultados parcialmente preenchidos: 0;
- `TP_PRES = 555` com os cinco resultados completos: 759.140;
- `TP_PRES = 555` sem conjunto completo de resultados: 966;
- `TP_PRES = 888` com resultados completos e excluidos da populacao analitica: 12;
- linhas na Silver: 759.140;
- UFs: 27;
- areas da prova: 17;
- municipios de prova: 750;
- valores ausentes nas cinco medidas analiticas: 0.

A validacao independente reconstruiu a populacao diretamente da Bronze e comparou os 759.140 registros da Silver com a referencia reconstruida.

Foram confirmados:

- `TP_PRES = 555` em todos os registros da Silver;
- ausencia de valores ausentes em `PROFICIENCIA`, `NT_OBJ`, `NT_DIS`, `NT_GER` e `QT_ACERTOS`;
- 27 UFs;
- 17 areas da prova;
- 750 municipios de prova;
- correspondencia direta dos 759.140 registros Silver ↔ Bronze;
- rastreabilidade por linha de origem;
- mapeamento `CO_GRUPO` → area oficial.

Diagnostico dos resultados numericos:

| Campo | Minimo | Maximo | Valores negativos |
|---|---:|---:|---:|
| `PROFICIENCIA` | -3,976610 | 2,688530 | 389.188 |
| `NT_OBJ` | 0,000000 | 100,000000 | 0 |
| `NT_DIS` | 0,000000 | 10,000000 | 0 |
| `NT_GER` | 0,000000 | 100,000000 | 0 |
| `QT_ACERTOS` | 0 | 77 | 0 |

Os valores negativos ocorrem exclusivamente em `PROFICIENCIA`.

Eles sao preservados como publicados pela fonte. Nenhum valor foi truncado, recodificado, substituido por zero ou removido por ser negativo.

Resultado final do validador:

`SILVER DA PND 2025: OK`

Com esse resultado, a Silver da PND 2025 esta concluida.

---

## 18. Situacao atual

| Fonte | Bronze | Silver |
|---|---|---|
| Rendimento Escolar | ✅ concluida e validada | ✅ concluida e validada |
| TDI | ✅ concluida e validada | ✅ concluida e validada |
| IDEB | ✅ concluida e validada | ✅ concluida e validada |
| SAEB | ✅ concluida e validada | ✅ concluida e validada |
| PND 2025 | ✅ concluida e validada | ✅ concluida e validada |

Nao existem fontes pendentes na camada Silver.

---

## 18.1 Conclusao da camada Silver

Com a validacao independente da PND 2025, todas as fontes previstas para a camada Silver estao concluidas:

| Fonte | Silver |
|---|---|
| Rendimento Escolar | ✅ concluida |
| TDI | ✅ concluida |
| IDEB | ✅ concluida |
| SAEB | ✅ concluida |
| PND 2025 | ✅ concluida |

A camada Silver do projeto encontra-se integralmente concluida.

As proximas transformacoes deverao ocorrer na camada Gold, voltada a modelagem analitica, integracao entre fatos e dimensoes e preparacao dos dados para o Power BI.

---

## 19. Historico de decisoes

| Data | Decisao |
|---|---|
| 18/08/2026 | Iniciada a camada Silver apos conclusao integral da Bronze |
| 18/08/2026 | Definido que cada fonte sera auditada diretamente a partir dos Parquets Bronze antes da implementacao semantica |
| 18/08/2026 | Rendimento Escolar escolhido como primeira fonte da Silver |
| 18/08/2026 | Concluida a auditoria Silver do Rendimento Escolar e documentadas cinco configuracoes estruturais da serie 2007–2023 |
| 18/08/2026 | Definido o grao Silver do Rendimento como ANO + UF + ETAPA + REDE + INDICADOR, com 2.754 registros esperados |
| 18/08/2026 | Definido o uso do agregado publico oficial da fonte, localizacao Total, conversao de `--` para ausencia e normalizacao das taxas para uma casa decimal |
| 18/08/2026 | Executada com sucesso a transformacao Silver do Rendimento Escolar, gerando 2.754 registros para 2007–2023 |
| 18/08/2026 | Validados os 2.754 registros Silver diretamente contra a Bronze por arquivo, linha e coluna de origem |
| 18/08/2026 | Rendimento Escolar marcado como concluido na camada Silver apos validacao final com status OK |
| 18/08/2026 | Concluida a auditoria Silver da TDI para 2007–2023 |
| 18/08/2026 | Verificacao focada confirmou agregado publico explicito em todos os anos: `Publico` em 2007–2014 e `Publica` em 2015–2023 |
| 18/08/2026 | Corrigida a interpretacao inicial da auditoria da TDI: a ausencia aparente de `Publica` decorreu de busca textual sem normalizacao de acentuacao |
| 18/08/2026 | Definido o grao Silver da TDI como ANO + UF + ETAPA + REDE, com 918 registros esperados |
| 18/08/2026 | Executada com sucesso a transformacao Silver da TDI, gerando 918 registros para 2007–2023 |
| 18/08/2026 | Validados os 918 registros Silver da TDI diretamente contra a Bronze por arquivo, linha e coluna de origem |
| 18/08/2026 | TDI marcada como concluida na camada Silver apos validacao final com status OK |
| 19/08/2026 | Concluida a auditoria estrutural da Silver do IDEB |
| 19/08/2026 | Confirmado que as UFs usam o agregado oficial `Publica (4)` nas linhas de resultados do IDEB |
| 19/08/2026 | Identificadas grafias abreviadas na fonte: `R. G. do Norte`, `R. G. do Sul` e `M. G. do Sul`, harmonizadas respectivamente para RN, RS e MS |
| 19/08/2026 | Definida identificacao dos anos do IDEB por `VL_OBSERVADO_YYYY`, evitando dependencia do cabecalho visual `20215` |
| 19/08/2026 | Definido o grao Silver do IDEB como ANO + UF + ETAPA + REDE, com 486 registros esperados |
| 19/08/2026 | Executada com sucesso a transformacao Silver do IDEB, gerando 486 registros para nove anos, 27 UFs e duas etapas |
| 19/08/2026 | Validados os 486 registros Silver do IDEB diretamente contra a Bronze por arquivo, aba, linha e coluna de origem |
| 19/08/2026 | IDEB marcado como concluido na camada Silver apos validacao final com status OK |
| 19/08/2026 | Corrigida a auditoria Silver do SAEB: a identificacao do cabecalho passa a usar `_indice_cabecalho_origem` da Bronze, abandonando a heuristica textual que classificou linhas de dados como cabecalho em algumas edicoes |
| 19/08/2026 | Verificacao focada do SAEB confirmou os agregados publicos de 2007–2021; para 2023, a ponderacao por `NU_PRESENTES` foi mantida apenas como diagnostico ate confronto com a planilha oficial de resultados estaduais do Inep |
| 19/08/2026 | Incorporado ao RAW o pacote oficial de resultados agregados do Saeb 2023; `Resultados_Saeb_2023_Brasil_Estados_Municipios.xlsb` sera usado para validar os resultados estaduais antes de definir a regra final de agregacao escola → UF |
| 19/08/2026 | A comparacao de 108 valores do Saeb 2023 confirmou 0/108 coincidencias entre o resultado oficial estadual e a media escolar ponderada por `NU_PRESENTES`; essa ponderacao foi rejeitada como regra canonica |
| 19/08/2026 | Definida reabertura controlada da Bronze do Saeb 2023 para incorporar a aba oficial `Estados` como fonte agregada de UF, preservando separadamente a Bronze escolar existente |
| 19/08/2026 | Esclarecida a politica transversal de rede: `PUBLICA` inclui Federal + Estadual + Municipal sempre que o agregado oficial esta disponivel; a rede privada e excluida. SAEB 2007/2009 permanecem como excecao documental por disponibilizarem apenas `Total - Estadual e Municipal` |
| 19/08/2026 | Corrigida a tipagem fisica da Bronze agregada do Saeb 2023: colunas de origem heterogeneas passam a ser preservadas como texto anulavel, com tipagem numerica adiada para a Silver |
| 19/08/2026 | Otimizada a validacao da Bronze agregada do Saeb 2023: comparacao celula a celula via `iloc` foi substituida por comparacao vetorizada, mantendo a conferencia integral de todas as celulas de origem |
| 19/08/2026 | Bronze oficial agregada do Saeb 2023 validada integralmente: 1.553 linhas, 177 colunas e 274.881 celulas RAW ↔ Bronze comparadas |
| 19/08/2026 | Definidos transformador e validador independente da Silver do Saeb 2007–2023, com grao `ANO + UF + ETAPA + REDE + DISCIPLINA` e 972 registros esperados |
| 19/08/2026 | Corrigida a Silver do Saeb para respeitar o cabecalho hierarquico de 2013 e 2015; essas edicoes passam a usar as posicoes fisicas auditadas `col_001`–`col_008`, sem inventar nomes tecnicos inexistentes |
| 19/08/2026 | Silver do Saeb executada com 972 registros, 9 anos, 27 UFs, 2 etapas, 2 disciplinas e zero valores ausentes |
| 19/08/2026 | Validacao independente da Silver do Saeb concluida com comparacao direta dos 972 registros contra as Bronzes e rastreabilidade completa; resultado `SILVER DO SAEB: OK` |
| 19/08/2026 | Definida a populacao Silver da PND 2025 como `TP_PRES = 555` com `PROFICIENCIA`, `NT_OBJ`, `NT_DIS`, `NT_GER` e `QT_ACERTOS` completos, totalizando 759.140 registros esperados |
| 19/08/2026 | Definida a granularidade Silver da PND como registro individual da prova; `LINHA_ORIGEM_BRONZE` sera usada apenas como chave tecnica de rastreabilidade porque a fonte nao fornece identificador individual |
| 19/08/2026 | Definidos `UF_PROVA`, `CO_MUNICIPIO_PROVA`, `CO_GRUPO` e `AREA_PROVA`; a area e mapeada pelas 17 categorias oficiais do dicionario da PND |
| 19/08/2026 | Vetores de resposta/gabarito e `CO_RS_I1`–`CO_RS_I9` permanecem na Bronze e nao integram a Silver factual por nao fazerem parte do escopo analitico atual |
| 19/08/2026 | Removida da transformacao PND a restricao nao documentada `resultado >= 0` para `PROFICIENCIA`, `NT_OBJ`, `NT_DIS` e `NT_GER`; os valores publicados passam a ser preservados integralmente e diagnosticados por minimo, maximo e quantidade de negativos |
| 19/08/2026 | Mantida validacao `QT_ACERTOS >= 0` por se tratar de contagem de acertos |
| 19/08/2026 | Silver da PND 2025 executada com 759.140 registros, 27 UFs, 17 areas, 750 municipios e zero ausencias nas cinco medidas analiticas |
| 19/08/2026 | Validacao independente da PND comparou diretamente os 759.140 registros Silver com a Bronze e confirmou rastreabilidade e mapeamento de area; resultado `SILVER DA PND 2025: OK` |
| 19/08/2026 | Confirmado que valores negativos ocorrem apenas em `PROFICIENCIA` (389.188 registros; minimo -3,976610) e sao preservados conforme publicados pela fonte |
| 19/08/2026 | Camada Silver concluida integralmente para Rendimento Escolar, TDI, IDEB, SAEB e PND 2025 |
| 19/08/2026 | Revisada a situacao final da camada Silver apos a validacao da PND: removido o status pendente residual e confirmadas todas as cinco fontes como concluidas e validadas |
