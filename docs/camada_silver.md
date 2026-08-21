# Camada Silver — Pipeline de Dados Educacionais

## 1. Objetivo

A camada Silver é responsável por transformar as representações técnicas e rastreáveis da Bronze em tabelas analíticas semanticamente harmonizadas.

Enquanto a Bronze preserva a estrutura efetiva de cada arquivo de origem, a Silver passa a aplicar regras de interpretação necessárias ao uso comparável dos indicadores.

A Silver não substitui a Bronze.

Cada tabela Silver deverá ser integralmente reconstruível a partir dos arquivos Bronze e das regras documentadas neste arquivo.

---

## 2. Princípio de trabalho

A transformação de cada fonte seguirá a sequência:

1. auditar a estrutura efetivamente preservada na Bronze;
2. documentar as regras semânticas;
3. implementar a transformação;
4. executar validação independente;
5. somente então considerar a fonte concluída na Silver.

Não serão implementadas regras por suposição a partir do nome de uma coluna ou da aparência de uma planilha.

Mudanças estruturais entre anos deverão ser configuradas explicitamente.

---

## 3. Relação entre Bronze e Silver

A Bronze preserva:

- estrutura de origem;
- linhas físicas necessárias à rastreabilidade;
- cabeçalhos originais;
- categorias textuais;
- granularidade publicada;
- metadados técnicos;
- SHA-256 do arquivo RAW.

A Silver poderá:

- excluir linhas físicas de título, notas e cabeçalhos;
- selecionar a população analítica definida para o projeto;
- harmonizar nomes de redes;
- harmonizar etapas de ensino;
- harmonizar indicadores;
- converter valores numéricos;
- transformar tabelas largas em formato analítico longo;
- harmonizar granularidade quando metodologicamente necessário;
- criar campos canônicos utilizados pela Gold.

Toda transformação deverá ter justificativa documentada.

---

## 4. Escopo analítico do projeto

### Série histórica

Para os indicadores históricos:

- período principal: 2007–2023;
- geografia analítica: Unidade Federativa;
- rede: pública;
- etapas: Ensino Fundamental — Anos Iniciais e Anos Finais.

### PND

A PND 2025 é complementar à série histórica e será tratada separadamente.

Sua população analítica será definida na Silver, conforme a auditoria já realizada.

---

## 5. Definição canônica de rede pública

Para este projeto, `PUBLICA` representa o universo das redes públicas de ensino:

- Federal;
- Estadual;
- Municipal.

A implementação deverá preferir o agregado público oficial quando a própria fonte o disponibilizar.

Quando a estrutura da fonte não possuir esse agregado, será utilizada a regra específica previamente auditada para a edição.

Não será utilizada média aritmética simples de Federal, Estadual e Municipal para reconstruir um resultado público.

Também não será utilizado um agregado geral que inclua rede privada.

A coluna canônica será:

`REDE = PUBLICA`

A origem da classificação deverá continuar rastreável em campo específico quando necessário, como:

`REDE_ORIGEM`

---

## 6. Granularidade e tabelas previstas

### Rendimento Escolar

Grão previsto:

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

Grão previsto:

`ANO + UF + ETAPA + REDE`

Estrutura prevista:

- `ANO`;
- `UF`;
- `ETAPA`;
- `REDE`;
- `TDI`;
- `ARQUIVO_ORIGEM`.

### IDEB

Grão previsto:

`ANO + UF + ETAPA + REDE`

Estrutura prevista:

- `ANO`;
- `UF`;
- `ETAPA`;
- `REDE`;
- `IDEB`;
- `ARQUIVO_ORIGEM`.

### SAEB

Grão previsto:

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

- Língua Portuguesa;
- Matemática.

### PND 2025

A PND permanece separada das séries históricas de IDEB, SAEB, Rendimento e TDI.

Sua Silver mantém a granularidade de `REGISTRO_INDIVIDUAL`, aplicando apenas a população analítica auditada.

Grão:

`um registro válido da prova`

Como o arquivo principal não fornece um identificador individual do participante, não será criado um identificador artificial com significado substantivo. `LINHA_ORIGEM_BRONZE` será preservada apenas como chave técnica única de rastreabilidade.

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

Os vetores de gabarito/resposta e as nove respostas do Questionário de Percepção de Prova não integram esta Silver porque não são necessários ao escopo analítico atual, que utiliza notas, acertos, área e localização de aplicação. Eles continuam preservados integralmente na Bronze.

---

## 7. Valores ausentes e marcadores da fonte

Valores ausentes não serão imputados na Silver.

Marcadores textuais da fonte, como `--`, `NA`, células vazias ou códigos específicos, não serão automaticamente tratados como equivalentes.

Cada marcador deverá ser interpretado segundo a estrutura auditada da respectiva fonte.

Quando um marcador significar indisponibilidade de resultado, a Silver poderá convertê-lo para valor ausente, desde que essa regra esteja explicitamente documentada.

---

## 8. Conversão numérica

A Bronze preserva muitos valores como texto técnico.

Na Silver, os campos analíticos poderão ser convertidos para tipos numéricos.

A conversão deverá considerar explicitamente:

- vírgula decimal;
- ponto decimal;
- marcadores de ausência;
- valores zero substantivos;
- códigos que não representam medidas.

Não haverá conversão numérica genérica aplicada indistintamente a todas as colunas.

---

## 9. Rastreamento da origem

A Silver não precisa preservar todas as colunas técnicas da Bronze, mas deve manter rastreabilidade suficiente para identificar a fonte utilizada.

No mínimo, as tabelas analíticas deverão manter:

`ARQUIVO_ORIGEM`

Quando uma decisão depender de uma categoria original relevante, também deverá ser preservado um campo como:

`REDE_ORIGEM`

ou equivalente.

---

## 10. Validações mínimas

Cada transformação Silver deverá possuir validação independente.

As validações deverão verificar, conforme aplicável:

- existência dos arquivos Bronze esperados;
- anos esperados;
- UFs esperadas;
- etapas esperadas;
- rede pública corretamente selecionada;
- ausência de rede privada;
- indicadores esperados;
- unicidade do grão analítico;
- tipos numéricos;
- valores dentro de domínios plausíveis;
- ausência de duplicidades indevidas;
- rastreabilidade de arquivo de origem;
- quantidade de registros por ano;
- consistência entre transformação e regras documentadas.

A validação não deverá apenas conferir se o Parquet foi criado.

---

## 11. Regra de falha

A Silver deverá falhar explicitamente quando:

- uma estrutura anual não corresponder à configuração auditada;
- uma categoria necessária não existir;
- uma rede pública não puder ser identificada com segurança;
- uma etapa não puder ser mapeada;
- houver duplicidade no grão esperado;
- uma conversão numérica produzir perda não documentada;
- um novo padrão estrutural surgir sem regra definida.

É preferível interromper o pipeline a harmonizar silenciosamente uma estrutura desconhecida.

---

## 12. Ordem de implementação

A implementação será realizada fonte a fonte:

1. Rendimento Escolar;
2. TDI;
3. IDEB;
4. SAEB;
5. PND 2025.

Essa ordem permite iniciar pelas estruturas históricas mais diretamente comparáveis e deixar para o SAEB e a PND as transformações que exigem maior cuidado de granularidade e população.

---

## 13. Rendimento Escolar

A Bronze do Rendimento Escolar está concluída e validada para 2007–2023.

A auditoria para a Silver foi executada diretamente sobre os 17 Parquets Bronze por meio de:

`src/silver/rendimento/auditar_silver_rendimento.py`

A auditoria não alterou dados.

### 13.1 População analítica

A Silver utilizará, para cada Unidade Federativa e ano:

- `Localização = Total`;
- agregado oficial da rede pública;
- Ensino Fundamental — Anos Iniciais;
- Ensino Fundamental — Anos Finais;
- taxas de aprovação, reprovação e abandono.

Não serão calculadas médias entre Federal, Estadual e Municipal.

O agregado público já publicado pela fonte será utilizado diretamente.

A rede privada não será utilizada.

A categoria canônica será:

`REDE = PUBLICA`

A categoria textual efetivamente encontrada na fonte será mantida em:

`REDE_ORIGEM`

A localização original será mantida em:

`LOCALIZACAO_ORIGEM`

### 13.2 Mudanças estruturais da série

A auditoria confirmou cinco configurações relevantes.

#### 2007

O arquivo possui uma coluna adicional de região.

Campos de identificação:

- ano: `col_001`;
- região: `col_002`;
- UF: `col_003`;
- localização: `col_004`;
- rede: `col_005`.

Colunas analíticas:

| Indicador | Anos Iniciais | Anos Finais |
|---|---|---|
| Aprovação | `col_015` | `col_016` |
| Reprovação | `col_033` | `col_034` |
| Abandono | `col_051` | `col_052` |

O agregado público aparece como `Publico`.

#### 2008–2010

Campos de identificação:

- ano: `col_001`;
- UF: `col_002`;
- localização: `col_003`;
- rede: `col_004`.

Colunas analíticas:

| Indicador | Anos Iniciais | Anos Finais |
|---|---|---|
| Aprovação | `col_014` | `col_015` |
| Reprovação | `col_032` | `col_033` |
| Abandono | `col_050` | `col_051` |

O agregado público aparece como `Publico`.

#### 2011–2014

A estrutura passa a publicar diretamente colunas denominadas Anos Iniciais e Anos Finais.

Campos de identificação:

- ano: `col_001`;
- UF: `col_002`;
- localização: `col_003`;
- rede: `col_004`.

Colunas analíticas:

| Indicador | Anos Iniciais | Anos Finais |
|---|---|---|
| Aprovação | `col_006` | `col_007` |
| Reprovação | `col_024` | `col_025` |
| Abandono | `col_042` | `col_043` |

O agregado público aparece como `Publico`.

#### 2015

A disposição das métricas permanece equivalente a 2011–2014, mas a identificação da Unidade Federativa passa a aparecer pelo nome e a categoria pública aparece como `Pública`.

Colunas analíticas:

| Indicador | Anos Iniciais | Anos Finais |
|---|---|---|
| Aprovação | `col_006` | `col_007` |
| Reprovação | `col_024` | `col_025` |
| Abandono | `col_042` | `col_043` |

#### 2016

A estrutura volta a possuir coluna de região e desloca os campos analíticos em uma posição.

Campos de identificação:

- ano: `col_001`;
- região: `col_002`;
- UF: `col_003`;
- localização: `col_004`;
- dependência administrativa: `col_005`.

Colunas analíticas:

| Indicador | Anos Iniciais | Anos Finais |
|---|---|---|
| Aprovação | `col_007` | `col_008` |
| Reprovação | `col_025` | `col_026` |
| Abandono | `col_043` | `col_044` |

O agregado oficial utilizado é `Pública`.

#### 2017–2023

A fonte passa a incluir Brasil, regiões geográficas e Unidades da Federação na mesma coluna `Unidade Geográfica`.

Campos de identificação:

- ano: `col_001`;
- unidade geográfica: `col_002`;
- localização: `col_003`;
- dependência administrativa: `col_004`.

Colunas analíticas:

| Indicador | Anos Iniciais | Anos Finais |
|---|---|---|
| Aprovação | `col_006` | `col_007` |
| Reprovação | `col_024` | `col_025` |
| Abandono | `col_042` | `col_043` |

A transformação manterá apenas as 27 Unidades Federativas.

Brasil e regiões geográficas serão excluídos por não pertencerem ao grão analítico definido.

O agregado oficial utilizado é `Pública`.

### 13.3 Harmonização da UF

Nas edições que utilizam siglas, elas serão preservadas.

Nas edições que utilizam nomes completos das Unidades Federativas, será aplicado um mapeamento explícito para as 27 siglas oficiais.

Não haverá inferência aproximada de nomes.

O processo deverá falhar se alguma UF esperada não for reconhecida ou se houver duplicidade de uma UF na seleção pública-total.

### 13.4 Marcadores de ausência

O marcador `--` será convertido para valor ausente na Silver.

Essa conversão é semântica e ocorre somente agora porque, na Bronze, o marcador foi preservado como parte da fonte.

O valor `0` permanecerá como zero substantivo e nunca será interpretado como ausência.

Não haverá imputação de valores ausentes.

### 13.5 Conversão numérica e precisão

As taxas serão convertidas para tipo numérico.

Algumas planilhas antigas expõem resíduos de representação binária, por exemplo valores equivalentes a `84.39999999999999`.

Na Silver, as taxas serão normalizadas para uma casa decimal.

A normalização não cria nova medida: ela remove apenas resíduos técnicos de representação do número e mantém a precisão utilizada pelas taxas publicadas.

Os valores deverão permanecer no domínio de 0 a 100.

### 13.6 Formato Silver

Será produzido um único arquivo harmonizado:

`data/silver/rendimento/rendimento_2007_2023.parquet`

Grão:

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

As duas últimas colunas permitem validar cada valor da Silver diretamente contra a linha e a coluna da Bronze que o originaram.

### 13.7 Cardinalidade esperada

São esperados:

- 17 anos;
- 27 UFs;
- 2 etapas;
- 3 indicadores;
- 1 rede canônica.

Assim:

`17 × 27 × 2 × 3 = 2.754 registros`

A presença de valor ausente não remove o registro do grão. O registro permanece e `VALOR` fica ausente.

### 13.8 Validação independente

A validação deverá confirmar:

- 2.754 registros;
- 162 registros por ano;
- 27 UFs em cada ano;
- ausência de duplicidade no grão;
- somente `REDE = PUBLICA`;
- somente Anos Iniciais e Anos Finais;
- somente aprovação, reprovação e abandono;
- taxas numéricas entre 0 e 100;
- preservação de zeros;
- conversão de `--` para ausência;
- correspondência de cada registro Silver com a linha, coluna e arquivo da Bronze;
- coerência das combinações completas de aprovação, reprovação e abandono com total aproximado de 100%, considerando arredondamento de publicação.

Scripts:

`src/silver/rendimento/transformar_rendimento.py`

`src/silver/rendimento/validar_silver_rendimento.py`

### 13.9 Resultado da execução e validação

Em 18/08/2026, a transformação Silver do Rendimento Escolar foi executada com sucesso.

Resultado produzido:

`data/silver/rendimento/rendimento_2007_2023.parquet`

A execução confirmou:

- 2.754 registros;
- 17 anos completos, de 2007 a 2023;
- 27 UFs em cada ano;
- 162 registros por ano;
- 2 etapas: `ANOS_INICIAIS` e `ANOS_FINAIS`;
- 3 indicadores: `APROVACAO`, `REPROVACAO` e `ABANDONO`;
- rede canônica única: `PUBLICA`;
- nenhum valor ausente na população analítica selecionada.

A ausência de valores nulos no resultado não altera a regra metodológica definida para o marcador `--`. A conversão de `--` para ausência permanece implementada; porém, nas linhas selecionadas para o agregado público, localização Total e etapas Anos Iniciais/Anos Finais, não houve ocorrência desse marcador nos valores finais.

A validação independente confirmou:

- grão analítico único;
- domínio das taxas entre 0 e 100;
- 2.754 registros comparados diretamente com a Bronze;
- rastreabilidade por arquivo, linha e coluna de origem;
- 918 combinações completas de ano, UF e etapa com aprovação, reprovação e abandono submetidas ao teste de soma;
- coerência das somas dentro da tolerância definida para arredondamento de publicação.

Status final:

`SILVER DO RENDIMENTO ESCOLAR: OK`

Com isso, o Rendimento Escolar passa a ser considerado concluído na camada Silver.

---

---

## 14. TDI — Distorção Idade-Série

A auditoria da Bronze da TDI foi executada diretamente sobre os 17 Parquets de 2007–2023 por meio de:

`src/silver/tdi/auditar_silver_tdi.py`

Como a primeira inspeção textual não exibiu a categoria `Pública` nos anos mais recentes, foi executada uma verificação focada adicional:

`src/silver/tdi/verificar_rede_publica_tdi.py`

Essa segunda verificação normaliza acentuação antes de comparar categorias e confirmou que **todos os anos de 2007 a 2023 possuem agregado público explícito**.

A primeira ausência aparente foi, portanto, um efeito do mecanismo de busca textual da auditoria: o termo sem acento `public` não localizava corretamente `Pública`. Essa limitação da inspeção foi identificada e corrigida antes da transformação.

Nenhum arquivo Bronze ou Silver foi alterado por qualquer uma das duas auditorias.

### 14.1 População analítica

A Silver utilizará, para cada Unidade Federativa e ano:

- `Localização = Total`;
- agregado oficial `Publico` ou `Pública` publicado pela fonte;
- Ensino Fundamental — Anos Iniciais;
- Ensino Fundamental — Anos Finais.

Não será calculada média entre Federal, Estadual e Municipal.

A categoria `Total` da dependência administrativa não será usada como substituta da rede pública, porque inclui universo distinto do agregado público.

A rede privada não será utilizada.

A categoria canônica será:

`REDE = PUBLICA`

A categoria efetivamente encontrada na fonte será preservada em:

`REDE_ORIGEM`

### 14.2 Confirmação do agregado público

A verificação focada confirmou:

- 2007–2014: `Publico`;
- 2015–2023: `Pública`.

Para 2007–2016 existem 27 linhas `Público/Pública + Localização Total`, uma por UF.

Para 2017–2023 existem 33 linhas `Pública + Localização Total`, porque a fonte reúne Brasil, cinco regiões geográficas e 27 UFs.

Na Silver, Brasil e regiões serão excluídos e somente as 27 UFs serão mantidas.

### 14.3 Mudanças estruturais da série

#### 2007–2010

Campos de identificação:

- ano: `col_001`;
- região: `col_002`;
- UF: `col_003`;
- localização: `col_004`;
- rede: `col_005`.

TDI:

- Anos Iniciais: `col_015`;
- Anos Finais: `col_016`.

#### 2011–2014

Campos de identificação:

- ano: `col_001`;
- região: `col_002`;
- UF: `col_003`;
- localização: `col_004`;
- rede: `col_005`.

TDI:

- Anos Iniciais: `col_007`;
- Anos Finais: `col_008`.

#### 2015

A fonte inclui código e sigla da UF em colunas separadas.

Campos de identificação:

- ano: `col_001`;
- região: `col_002`;
- código da UF: `col_003`;
- sigla da UF: `col_004`;
- localização: `col_005`;
- rede: `col_006`.

TDI:

- Anos Iniciais: `col_008`;
- Anos Finais: `col_009`.

#### 2016

A UF passa a ser representada por nome completo.

Campos de identificação:

- ano: `col_001`;
- região: `col_002`;
- UF: `col_003`;
- localização: `col_004`;
- dependência administrativa: `col_005`.

TDI:

- Anos Iniciais: `col_007`;
- Anos Finais: `col_008`.

#### 2017–2023

A fonte passa a reunir Brasil, regiões geográficas e UFs em `Unidade Geográfica`.

Campos de identificação:

- ano: `col_001`;
- unidade geográfica: `col_002`;
- localização: `col_003`;
- dependência administrativa: `col_004`.

TDI:

- Anos Iniciais: `col_006`;
- Anos Finais: `col_007`.

### 14.4 Harmonização da UF

Siglas serão preservadas quando já existentes.

Nomes completos serão convertidos para siglas por mapeamento explícito das 27 UFs.

Em 2017–2023, Brasil e regiões geográficas não serão reconhecidos como UF e serão excluídos da população analítica.

A transformação falhará se alguma UF esperada estiver ausente ou duplicada.

### 14.5 Marcadores de ausência e precisão

O marcador `--` será convertido para ausência somente na Silver.

Zero permanecerá zero substantivo.

Não haverá imputação.

Resíduos binários de representação numérica, como `21.400000000000002`, serão normalizados para uma casa decimal, preservando a precisão publicada pela fonte.

A TDI deverá permanecer no intervalo de 0 a 100.

### 14.6 Formato Silver

Será produzido:

`data/silver/tdi/tdi_2007_2023.parquet`

Grão:

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

São esperados:

- 17 anos;
- 27 UFs;
- 2 etapas;
- 1 rede canônica.

Assim:

`17 × 27 × 2 = 918 registros`

A presença de valor ausente não remove o registro do grão.

### 14.8 Validação independente

A validação deverá confirmar:

- 918 registros;
- 54 registros por ano;
- 27 UFs em cada ano;
- ausência de duplicidade no grão;
- somente `REDE = PUBLICA`;
- somente Anos Iniciais e Anos Finais;
- TDI numérica entre 0 e 100;
- preservação de zeros;
- conversão de `--` para ausência;
- correspondência de cada registro Silver com arquivo, linha e coluna da Bronze.

Scripts:

`src/silver/tdi/transformar_tdi.py`

`src/silver/tdi/validar_silver_tdi.py`

### 14.9 Resultado da execução e validação

Em 18/08/2026, a transformação Silver da TDI foi executada com sucesso.

Resultado produzido:

`data/silver/tdi/tdi_2007_2023.parquet`

A execução confirmou:

- 918 registros;
- 17 anos completos, de 2007 a 2023;
- 27 UFs em cada ano;
- 54 registros por ano;
- 2 etapas: `ANOS_INICIAIS` e `ANOS_FINAIS`;
- rede canônica única: `PUBLICA`;
- nenhum valor ausente na população analítica selecionada.

A ausência de valores nulos no resultado não altera a regra metodológica definida para o marcador `--`. A conversão de `--` para ausência permanece implementada; porém, nas linhas selecionadas para o agregado público, localização Total e etapas Anos Iniciais/Anos Finais, não houve ocorrência desse marcador nos valores finais.

A validação independente confirmou:

- grão analítico único;
- domínio da TDI entre 0 e 100;
- 918 registros comparados diretamente com a Bronze;
- rastreabilidade por arquivo, linha e coluna de origem;
- correspondência integral entre os valores Silver e suas células de origem na Bronze.

Status final:

`SILVER DA TDI: OK`

Com isso, a TDI passa a ser considerada concluída na camada Silver.

---

## 15. IDEB — Índice de Desenvolvimento da Educação Básica

A auditoria da Bronze do IDEB foi executada sobre os Parquets:

- `data/bronze/ideb/ideb_ai.parquet`;
- `data/bronze/ideb/ideb_af.parquet`;
- `data/bronze/ideb/ideb_em.parquet`.

O Ensino Médio foi inspecionado apenas para documentar a estrutura da fonte. A Silver histórica do projeto permanece restrita aos Anos Iniciais e Anos Finais do Ensino Fundamental.

Scripts de auditoria e diagnóstico:

`src/silver/ideb/auditar_silver_ideb.py`

`src/silver/ideb/verificar_rede_publica_ideb.py`

`src/silver/ideb/diagnosticar_ufs_ausentes_ideb.py`

Nenhum desses scripts altera a Bronze ou a Silver.

### 15.1 Escopo temporal

O workbook de divulgação de 2023 contém resultados observados para:

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

O projeto histórico começa em 2007. Por isso, 2005 será preservado na Bronze, mas excluído da Silver.

A série Silver do IDEB conterá nove anos:

`2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021, 2023`

O IDEB é divulgado em anos de aplicação correspondentes à série histórica disponível na planilha; portanto, não serão criadas linhas artificiais para anos pares.

### 15.2 Identificação dos anos e erro visual `20215`

O cabeçalho visual da planilha contém a grafia `20215` em posições correspondentes a 2021.

A Bronze preserva essa característica da fonte e não a corrige.

Na Silver, a seleção do ano não será feita pelo texto visual do cabeçalho. Será usada a linha técnica identificada na Bronze por `_indice_cabecalho_origem`; como `_linha_origem` utiliza numeração iniciada em um, a linha de referência é calculada como `_linha_origem = _indice_cabecalho_origem + 1`. Essa linha contém os nomes oficiais das variáveis:

`VL_OBSERVADO_2007`

`VL_OBSERVADO_2009`

`VL_OBSERVADO_2011`

`VL_OBSERVADO_2013`

`VL_OBSERVADO_2015`

`VL_OBSERVADO_2017`

`VL_OBSERVADO_2019`

`VL_OBSERVADO_2021`

`VL_OBSERVADO_2023`

Essa decisão evita interpretar o erro gráfico como ano válido e mantém a transformação ancorada na variável técnica da própria fonte.

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

A implementação não dependerá somente dessas posições fixas. O script localizará cada coluna por `VL_OBSERVADO_YYYY` na linha técnica e falhará se a variável não for encontrada de forma única.

### 15.4 Rede pública

Nas linhas das Unidades Federativas, o agregado público é publicado como:

`Pública (4)`

A Silver utilizará diretamente esse agregado oficial.

Não será calculada média entre redes.

Não será utilizado `Total (4)` como substituto da rede pública.

A rede privada e a rede estadual isolada não serão utilizadas.

A categoria canônica será:

`REDE = PUBLICA`

O rótulo original será preservado em:

`REDE_ORIGEM = Pública (4)`

A nota metodológica `(4)` da própria planilha informa que as médias do SAEB 2011 e o IDEB 2011 foram calculados sem as escolas federais. A Silver não tentará recompor ou alterar esse valor: será preservado o resultado oficial publicado pelo Inep.

### 15.5 Harmonização das UFs

A auditoria inicialmente reconheceu 24 das 27 UFs porque três nomes aparecem abreviados na própria fonte.

Foram identificadas as seguintes correspondências:

- `R. G. do Norte` → `RN`;
- `R. G. do Sul` → `RS`;
- `M. G. do Sul` → `MS`.

Essas grafias aparecem tanto nos Anos Iniciais quanto nos Anos Finais e possuem linha `Pública (4)` com resultados para todos os nove anos da série.

A Silver harmonizará essas três formas para as siglas oficiais, sem modificar a Bronze.

Os demais nomes de UF também serão convertidos para as 27 siglas oficiais por mapeamento explícito.

A grafia de origem será preservada em:

`GEOGRAFIA_ORIGEM`

A transformação falhará caso, depois da harmonização:

- alguma das 27 UFs esteja ausente;
- exista UF adicional;
- uma UF possua mais de uma linha pública.

### 15.6 Anos Iniciais e Anos Finais

Os arquivos Bronze usados serão:

`data/bronze/ideb/ideb_ai.parquet`

`data/bronze/ideb/ideb_af.parquet`

As etapas canônicas serão:

`ANOS_INICIAIS`

`ANOS_FINAIS`

O Ensino Médio permanecerá fora da Silver histórica principal.

### 15.7 Marcadores de ausência e domínio

Serão tratados como ausência apenas:

- célula vazia;
- `-`;
- `--`.

Zero continuará sendo valor substantivo.

Não haverá imputação.

O IDEB será numérico e deverá permanecer no intervalo de 0 a 10.

Os valores serão normalizados para uma casa decimal, preservando a precisão publicada do IDEB observado.

### 15.8 Formato Silver

Será produzido:

`data/silver/ideb/ideb_2007_2023.parquet`

Grão:

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

São esperados:

- 9 anos;
- 27 UFs;
- 2 etapas;
- 1 rede canônica.

Assim:

`9 × 27 × 2 = 486 registros`

A existência de valor ausente não removerá o registro do grão.

### 15.10 Validação independente

A validação deverá confirmar:

- 486 registros;
- 54 registros por ano;
- 27 UFs por ano e etapa;
- ausência de duplicidade no grão;
- somente `REDE = PUBLICA`;
- somente Anos Iniciais e Anos Finais;
- somente os nove anos previstos;
- IDEB numérico entre 0 e 10;
- harmonização explícita de `R. G. do Norte`, `R. G. do Sul` e `M. G. do Sul`;
- seleção de 2021 por `VL_OBSERVADO_2021`, e não pelo cabeçalho visual `20215`;
- correspondência de cada registro Silver com arquivo, aba, linha e coluna da Bronze.

Scripts:

`src/silver/ideb/transformar_ideb.py`

`src/silver/ideb/validar_silver_ideb.py`

### 15.11 Resultado da execução e validação

Em 19/08/2026, a transformação Silver do IDEB foi executada com sucesso.

Resultado produzido:

`data/silver/ideb/ideb_2007_2023.parquet`

A execução confirmou:

- 486 registros;
- 9 anos da série histórica: 2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021 e 2023;
- 27 UFs em cada combinação de ano e etapa;
- 243 registros para `ANOS_INICIAIS`;
- 243 registros para `ANOS_FINAIS`;
- 54 registros por ano;
- rede canônica única: `PUBLICA`;
- nenhum valor ausente na população analítica selecionada.

A validação independente confirmou:

- grão analítico único `ANO + UF + ETAPA + REDE`;
- domínio do IDEB entre 0 e 10;
- harmonização dos aliases `R. G. do Norte` → `RN`, `R. G. do Sul` → `RS` e `M. G. do Sul` → `MS`, com preservação da grafia original na proveniência;
- identificação de 2021 por `VL_OBSERVADO_2021`, sem dependência do cabeçalho visual `20215`;
- 486 registros comparados diretamente com a Bronze;
- rastreabilidade por arquivo, aba, linha e coluna de origem;
- correspondência integral entre os valores Silver e suas células de origem na Bronze.

Status final:

`SILVER DO IDEB: OK`

Com isso, o IDEB passa a ser considerado concluído na camada Silver.

---

## 16. SAEB — auditoria preliminar da Silver

A construção da Silver do SAEB começou por auditoria estrutural dos nove Parquets Bronze correspondentes às edições de 2007 a 2023.

Script:

`src/silver/saeb/auditar_silver_saeb.py`

### 16.1 Correção da estratégia de identificação do cabeçalho

A primeira versão da auditoria tentou inferir automaticamente uma “linha técnica” com base na aparência textual das células. Essa heurística se mostrou inadequada nas edições mais recentes.

A própria saída demonstrou o problema: embora a primeira linha de 2017, 2019 e 2021 contenha os nomes das variáveis da fonte, a heurística classificou como supostas linhas técnicas registros de dados posteriores.

A decisão foi abandonar essa inferência.

A versão corrigida utiliza como referência autoritativa:

`_indice_cabecalho_origem`

Esse metadado foi gravado durante a ingestão Bronze justamente para registrar a posição real do cabeçalho na fonte. A linha física correspondente é obtida por:

`_linha_origem = _indice_cabecalho_origem + 1`

Justificativa: a camada Silver deve interpretar a estrutura a partir da proveniência preservada na Bronze, e não por uma tentativa probabilística de reconhecer cabeçalhos pelo conteúdo das células.

Impacto: a correção modifica apenas a auditoria. Nenhum dado Bronze foi alterado e nenhuma transformação Silver do SAEB foi executada antes da resolução do problema.

### 16.2 Evidências já confirmadas

A auditoria confirmou que 2007 e 2009 estão em granularidade UF e possuem a categoria:

`Total - Federal, Estadual, Municipal e Privada`

Esse total inclui a rede privada e, portanto, não poderá ser utilizado como representação da rede pública.

Em 2011, a Bronze contém explicitamente:

- `SIGLA_UF`;
- `ID_SERIE`;
- `ID_TIPO_REDE`;
- `ID_LOCALIZACAO`;
- `NU_PARTICIPANTES`;
- `MEDIA_LP`;
- `MEDIA_MT`.

Foram observadas as séries 5, 9 e 12 e seis códigos de rede, de 0 a 5. A regra de seleção do agregado público será confirmada pela auditoria focada antes da transformação.

Em 2013 e 2015, a fonte organiza diretamente as proficiências de Anos Iniciais e Anos Finais em colunas distintas de Língua Portuguesa e Matemática.

Em 2017, 2019 e 2021, as fontes continuam em granularidade UF, com dimensões de dependência administrativa, localização e capital, além das médias de proficiência por etapa.

A edição de 2023 permanece metodologicamente distinta porque sua Bronze está em granularidade escola. Nenhuma média simples entre escolas será produzida. A forma de agregação para UF somente será definida depois da confirmação das variáveis de participação/presença e das médias correspondentes.

### 16.3 Estado da decisão

A Silver do SAEB permanece em auditoria.

Ainda não está autorizada a transformação porque precisam ser fechadas, com evidência da própria Bronze:

- a categoria pública exata em cada edição de granularidade UF;
- a seleção de localização/capital usada para representar o total da UF;
- a regra específica de 2007 e 2009, que não possuem no total geral uma população exclusivamente pública;
- a estrutura completa de 2023;
- a variável de ponderação apropriada para a agregação escola → UF em 2023.

Nenhuma dessas regras será inferida por média aritmética simples.

---

### 16.4 Resultado da verificação focada de 2007 a 2021

A verificação focada confirmou que as edições de 2007 a 2021 permitem selecionar diretamente um único estrato de UF para os Anos Iniciais e Anos Finais, sem produzir média aritmética entre redes.

#### 2007 e 2009

A fonte disponibiliza a categoria:

`Total - Estadual e Municipal`

com:

`LOCALIZACAO = Total`

`CAPITAL = Total`

A seleção produz exatamente:

- 27 UFs;
- nenhuma UF faltante;
- nenhuma UF adicional;
- nenhuma duplicidade por UF;
- nenhum valor ausente;
- nenhum valor zero nas quatro médias de interesse.

A categoria:

`Total - Federal, Estadual, Municipal e Privada`

não será usada porque inclui a rede privada.

Também não existe categoria `Federal` isolada nas planilhas dessas duas edições.

Decisão metodológica: para 2007 e 2009 será preservado o agregado público disponível na própria fonte, `Total - Estadual e Municipal`. Ele será harmonizado para a categoria analítica `PUBLICA`, mas a origem exata será mantida em `REDE_ORIGEM`.

Limitação de comparabilidade: esse agregado não explicita a rede federal, ao contrário do agregado utilizado a partir de 2013. A série histórica deverá manter essa ressalva documental e não tentará estimar ou reconstruir a parcela federal.

#### 2011

A seleção validada é:

- `ID_SERIE = 5` para Anos Iniciais;
- `ID_SERIE = 9` para Anos Finais;
- `ID_TIPO_REDE = 5` para rede pública;
- `ID_LOCALIZACAO = 0`;
- `ID_CAPITAL = 0`.

Para cada etapa foram obtidas exatamente 27 UFs, sem duplicidades e sem valores ausentes em `MEDIA_LP`, `MEDIA_MT` e `NU_PARTICIPANTES`.

A Silver usará diretamente `MEDIA_LP` e `MEDIA_MT` publicadas nesse estrato. `NU_PARTICIPANTES` permanecerá como informação de origem/validação; não será usado para recalcular uma média já publicada para a UF.

#### 2013, 2015, 2017, 2019 e 2021

A seleção validada é:

`REDE = Total - Federal, Estadual e Municipal`

`LOCALIZACAO = Total`

`CAPITAL = Total`

Em todas as cinco edições foram confirmadas:

- 27 UFs;
- nenhuma UF faltante;
- nenhuma UF adicional;
- nenhuma duplicidade por UF;
- valores completos para Língua Portuguesa e Matemática nos Anos Iniciais e Anos Finais.

A Silver utilizará diretamente esse agregado oficial, sem média entre Federal, Estadual e Municipal.

Em 2015 a fonte informa que valor `0` representa impossibilidade de calcular a média para o estrato. No estrato público/Total/Total selecionado para a Silver não foi observado nenhum zero nas quatro médias de interesse.

### 16.5 Diagnóstico de 2023 e suspensão da regra por número de presentes

A Bronze de 2023 está em granularidade escola e contém 70.151 registros de escolas públicas, distribuídos pelas 27 UFs.

Foram identificadas as variáveis necessárias para um cálculo exploratório:

Anos Iniciais:

- `NU_PRESENTES_5EF`;
- `MEDIA_5EF_LP`;
- `MEDIA_5EF_MT`.

Anos Finais:

- `NU_PRESENTES_9EF`;
- `MEDIA_9EF_LP`;
- `MEDIA_9EF_MT`.

Foi testada, apenas como diagnóstico, a média das médias escolares ponderada pelo número de presentes da etapa. O teste produziu resultados para as 27 UFs e não gerou ausência de resultado estadual.

Esse resultado, entretanto, não autoriza a regra Silver.

A documentação oficial do Inep para o Saeb 2023 informa que a produção de resultados agregados utiliza pesos amostrais. Esses pesos incorporam o desenho da avaliação e procedimentos de expansão/calibração e permitem a formação de resultados para Brasil, regiões e UFs. Por isso, `NU_PRESENTES` não pode ser tratado automaticamente como equivalente ao peso estatístico oficial.

Decisão metodológica: a média escolar ponderada por `NU_PRESENTES` permanece apenas como teste diagnóstico e não será usada na Silver enquanto não for confrontada com os resultados agregados oficiais de 2023.

### 16.6 Validação externa necessária para 2023

O Inep disponibiliza, na página oficial de resultados do Saeb 2023:

- Planilhas de Resultados para Brasil, estados e municípios;
- Microdados Saeb 2023;
- Nota Técnica Saeb 2023;
- relatório de dados de proficiência.

A planilha oficial de resultados estaduais será usada como referência de validação do cálculo produzido a partir das escolas.

Procedimento definido:

1. obter e preservar a planilha oficial de resultados agregados de 2023;
2. identificar o estrato de UF, rede pública e localização total para 5º e 9º anos;
3. confrontar os 108 valores candidatos produzidos pela Bronze de escolas:
   `27 UFs × 2 etapas × 2 disciplinas`;
4. comparar com a precisão publicada pelo Inep;
5. somente depois decidir a fonte operacional da Silver 2023.

Se a agregação derivada das escolas reproduzir os resultados oficiais dentro da precisão publicada, poderá ser mantida, com documentação da validação.

Se não reproduzir, a Silver não usará a ponderação por `NU_PRESENTES`. Nesse caso, a planilha agregada oficial deverá ser incorporada ao pipeline como fonte canônica de 2023, com reabertura controlada da etapa Bronze do SAEB e nova validação.

Essa decisão evita produzir uma série aparentemente comparável por meio de uma ponderação que não reproduza o estimador oficial do Inep.

---

### 16.7 Fonte oficial agregada de 2023 incorporada à auditoria

Foi incorporado ao diretório RAW do SAEB o pacote oficial de resultados agregados de 2023, preservando sua estrutura original:

`data/raw/saeb/`

Arquivos identificados:

- `12EM_Erros_amostrais_e_intervalo_de_confiança.xlsx`;
- `2anoEF_Erros_amostrais_e_intervalo_de_confiança_Taxa_alfabetização.xlsx`;
- `5anoEF_Erros_amostrais_e_intervalo_de_confiança.xlsx`;
- `9anoEF_Erros_amostrais_e_intervalo_de_confiança.xlsx`;
- `Resultados_Saeb_2023_Brasil_Estados_Municipios.xlsb`.

Para a validação da Silver, o arquivo prioritário será:

`Resultados_Saeb_2023_Brasil_Estados_Municipios.xlsb`

Justificativa: ele reúne os resultados agregados oficiais para Brasil, estados e municípios e permitirá confrontar diretamente os valores estaduais publicados pelo Inep com os valores derivados da Bronze escolar.

Os arquivos de erros amostrais e intervalos de confiança serão mantidos no RAW como documentação complementar da fonte, mas não serão usados como substitutos da média de proficiência.

Antes da comparação numérica, será executada uma auditoria estrutural do arquivo `.xlsb` para identificar:

- nomes das abas;
- posição dos cabeçalhos;
- nível geográfico;
- dependência administrativa/rede;
- localização;
- etapa;
- disciplina;
- variáveis de proficiência.

Nenhuma regra de agregação de 2023 será finalizada antes dessa auditoria.

---

### 16.8 Veredito da comparação oficial × agregação escolar em 2023

A comparação entre os resultados oficiais estaduais do Saeb 2023 e a média das médias escolares ponderada por `NU_PRESENTES` foi concluída.

Foram confrontados:

`27 UFs × 2 etapas × 2 disciplinas = 108 valores`

Referência oficial:

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

- coincidências após arredondamento para duas casas: `0/108`;
- diferença absoluta média: `1,389714`;
- diferença absoluta mediana: `1,092905`;
- maior diferença absoluta: `6,150034`.

Por métrica:

- Anos Iniciais / Língua Portuguesa: 0/27 coincidências; diferença média 0,937030;
- Anos Iniciais / Matemática: 0/27 coincidências; diferença média 1,010801;
- Anos Finais / Língua Portuguesa: 0/27 coincidências; diferença média 1,820663;
- Anos Finais / Matemática: 0/27 coincidências; diferença média 1,790360.

A divergência não é residual de arredondamento. Em alguns casos supera quatro ou seis pontos de proficiência.

Decisão metodológica: `NU_PRESENTES` não será usado como peso canônico para reconstruir resultados estaduais de 2023.

Justificativa: a ponderação por presentes não reproduz nenhum dos 108 resultados oficiais publicados. A adoção dessa regra criaria uma série histórica metodologicamente incompatível com o resultado oficial do Saeb.

### 16.9 Reabertura controlada da Bronze do SAEB 2023

A Bronze escolar de 2023 permanece válida e será preservada:

`data/bronze/saeb/saeb_2023.parquet`

Ela representa corretamente a fonte `TS_ESCOLA_2023.csv` na granularidade escola e não será substituída nem sobrescrita.

Entretanto, ela não é suficiente para reproduzir o estimador estadual oficial utilizado no escopo histórico deste projeto.

Por isso, será adicionada uma segunda fonte Bronze de 2023, correspondente aos resultados oficiais agregados de UF:

RAW:

`data/raw/saeb/Resultados_Saeb_2023_Brasil_Estados_Municipios.xlsb`

Aba preservada:

`Estados`

Bronze adicional:

`data/bronze/saeb/saeb_2023_resultados_uf.parquet`

Scripts:

`src/bronze/saeb/ingest_saeb_resultados_2023.py`

`src/bronze/saeb/validar_bronze_saeb_resultados_2023.py`

A nova Bronze preservará integralmente a aba `Estados`, sem filtrar rede, localização ou indicadores durante a ingestão.

Metadados:

- `_fonte`;
- `_sha256_arquivo`;
- `_arquivo_origem`;
- `_aba_origem`;
- `_ano_referencia`;
- `_indice_cabecalho_origem`;
- `_linha_origem`;
- `_granularidade_origem`.

A existência de duas fontes Bronze em 2023 é intencional:

- `saeb_2023.parquet`: granularidade `ESCOLA`, preservando os microdados escolares;
- `saeb_2023_resultados_uf.parquet`: granularidade `UF`, preservando os resultados agregados oficiais.

A Silver histórica usará a segunda fonte para 2023 porque o seu grão analítico é UF e a tentativa de reconstruir o estimador estadual a partir das escolas não reproduziu os valores oficiais.

Essa decisão não invalida a Bronze escolar. Ela separa dois produtos oficiais com granularidades e finalidades metodológicas distintas.

### 16.10 Regra Silver consolidada do SAEB após a validação de 2023

Se a nova Bronze agregada de 2023 passar pela validação RAW → Bronze, a regra Silver ficará:

- 2007: `Total - Estadual e Municipal`, localização `Total`, capital `Total`;
- 2009: `Total - Estadual e Municipal`, localização `Total`, capital `Total`;
- 2011: `ID_TIPO_REDE = 5`, `ID_LOCALIZACAO = 0`, `ID_CAPITAL = 0`, séries 5 e 9;
- 2013: `Total - Federal, Estadual e Municipal`, localização `Total`, capital `Total`;
- 2015: mesma regra de 2013;
- 2017: mesma regra de 2013;
- 2019: mesma regra de 2013;
- 2021: mesma regra de 2013;
- 2023: resultados oficiais agregados da aba `Estados`, com `Total - Federal, Estadual e Municipal`, localização `Total` e capital `Total`.

Em todos os anos serão selecionadas apenas:

- Anos Iniciais;
- Anos Finais;
- Língua Portuguesa;
- Matemática.

A Silver não calculará médias entre redes e não reconstruirá o resultado estadual de 2023 a partir das médias escolares.

---

### 16.11 Política transversal de rede pública no projeto

A categoria analítica `PUBLICA` não significa exclusão da rede federal.

A regra geral do projeto é:

`PUBLICA = Federal + Estadual + Municipal`

sempre que a fonte oficial disponibiliza essa população de forma explícita ou por categoria pública consolidada.

A rede privada é excluída da população analítica histórica porque o escopo do projeto é a rede pública.

Aplicação por indicador:

- Rendimento Escolar: utiliza o agregado oficial `Pública`; não é calculada média entre Federal, Estadual e Municipal.
- TDI: utiliza o agregado oficial `Publico`/`Pública`; não é calculada média entre dependências.
- IDEB: utiliza a categoria oficial `Pública (4)`. Eventuais particularidades metodológicas da própria publicação, como a nota referente ao cálculo de 2011 sem escolas federais, são preservadas como característica da fonte e não como filtro criado pelo pipeline.
- SAEB 2013–2023: utiliza o agregado oficial `Total - Federal, Estadual e Municipal`.
- SAEB 2011: utiliza o código oficial de rede pública já identificado na fonte.
- SAEB 2007 e 2009: a fonte de resultados por UF disponibiliza `Total - Estadual e Municipal`, mas não apresenta categoria Federal isolada nem agregado Federal + Estadual + Municipal. Por isso, essas duas edições constituem exceção documental: a série usa o agregado público disponível na fonte e registra a ausência explícita da rede federal nessa categoria.
- PND: a lógica de rede pública não se aplica da mesma forma, pois o conjunto analítico da PND é definido pelos critérios próprios de presença e completude da avaliação, e não por uma série histórica de redes escolares equivalente aos demais indicadores.

Portanto, o projeto não adota a regra “retirar Federal e Particular”.

A regra correta é “retirar a rede privada e preservar a rede federal dentro da rede pública sempre que ela estiver contemplada no agregado oficial”. As exceções são documentadas quando a própria fonte histórica não oferece esse agregado.

---

### 16.12 Tipagem física da Bronze agregada do SAEB 2023

Durante a primeira execução da ingestão da aba `Estados`, o `pyarrow` interrompeu a gravação porque as colunas da planilha possuem conteúdo heterogêneo: a primeira linha contém os nomes técnicos das variáveis, enquanto as linhas seguintes contêm valores numéricos ou categorias.

Exemplo:

- `col_001`, linha 1: `ANO_SAEB`;
- `col_001`, linhas de dados: `2023`.

O Pandas leu essa coluna como `object`, mas o Arrow tentou inferir um único tipo físico para o Parquet e encontrou simultaneamente texto e inteiro.

Decisão técnica: todas as colunas de origem `col_001 ... col_NNN` da nova Bronze agregada de 2023 serão armazenadas como texto anulável.

Justificativa:

- a Bronze deve preservar a estrutura física da fonte, inclusive a linha de cabeçalho;
- não cabe à Bronze atribuir tipos analíticos a proficiências, códigos ou categorias;
- o Parquet exige um tipo lógico consistente por coluna;
- armazenar as células de origem como texto evita coerção indevida e perda da linha de cabeçalho;
- a conversão para número será feita somente na Silver, depois da identificação da variável pelo cabeçalho preservado.

Valores realmente ausentes continuam ausentes (`null`) e não são convertidos para as strings `"nan"` ou `"None"`.

A validação independente compara cada célula da fonte RAW com sua representação textual normalizada na Bronze, além de verificar SHA-256, arquivo, aba, linha física, cabeçalho e granularidade.

---

### 16.13 Otimização da validação RAW ↔ Bronze agregada de 2023

A primeira versão do validador independente percorria todas as células da aba `Estados` com acessos repetidos por `DataFrame.iloc`.

Embora o conjunto possua apenas 1.553 linhas e 177 colunas, esse padrão é ineficiente em Pandas porque cada acesso escalar cria sobrecarga de indexação e conversão. Na execução real, o processo permaneceu por tempo excessivo sem produzir nova saída no terminal.

Decisão técnica: a comparação foi substituída por uma validação vetorizada.

Procedimento:

1. a RAW é normalizada com a mesma regra textual usada na ingestão;
2. as colunas são harmonizadas para `col_001 ... col_177`;
3. RAW normalizada e Bronze são alinhadas na mesma ordem;
4. ausências são substituídas temporariamente por um marcador exclusivo apenas para comparação;
5. a igualdade é calculada de forma vetorizada com `DataFrame.eq`;
6. se houver divergência, somente as primeiras 20 células diferentes são materializadas para diagnóstico.

A regra metodológica da validação não mudou: continuam sendo confrontadas todas as células de origem. A alteração é exclusivamente de eficiência computacional.

O validador também passou a emitir etapas de progresso (`1/5` a `5/5`) para tornar evidente em qual operação uma eventual demora ocorre.

---

### 16.14 Bronze agregada oficial do Saeb 2023 validada

A nova Bronze de resultados oficiais agregados de UF foi executada e validada com sucesso.

Arquivo:

`data/bronze/saeb/saeb_2023_resultados_uf.parquet`

Resultado da validação:

- 1.553 linhas RAW/Bronze;
- 177 colunas de origem;
- 274.881 células de origem comparadas;
- SHA-256 da fonte validado;
- reprodução integral da aba `Estados` após normalização textual: OK;
- proveniência de arquivo, aba, linha, cabeçalho e granularidade: OK;
- estrato `Total - Federal, Estadual e Municipal` / localização `Total` / capital `Total`: 27 UFs, sem duplicidade.

Faixas observadas no estrato público estadual:

- `MEDIA_5_LP`: 185,22 a 225,51;
- `MEDIA_5_MT`: 193,75 a 239,52;
- `MEDIA_9_LP`: 230,61 a 265,44;
- `MEDIA_9_MT`: 230,17 a 264,71.

A extensão controlada da Bronze do Saeb 2023 está, portanto, concluída.

### 16.15 Implementação definida para a Silver do SAEB

A Silver do SAEB terá o grão:

`ANO + UF + ETAPA + REDE + DISCIPLINA`

Colunas analíticas principais:

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

Regras por edição:

- 2007 e 2009: `Total - Estadual e Municipal`, localização `Total`, capital `Total`; Anos Iniciais a partir de `MEDIA_4_LP`/`MEDIA_4_MT` e Anos Finais a partir de `MEDIA_8_LP`/`MEDIA_8_MT`;
- 2011: `ID_TIPO_REDE = 5`, `ID_LOCALIZACAO = 0`, `ID_CAPITAL = 0`; `ID_SERIE = 5` para Anos Iniciais e `ID_SERIE = 9` para Anos Finais; proficiências `MEDIA_LP` e `MEDIA_MT`;
- 2013 e 2015: cabeçalho hierárquico; `Total - Federal, Estadual e Municipal`, localização `Total`, capital `Total`; proficiências nas posições auditadas `col_005`/`col_006` (Anos Iniciais) e `col_007`/`col_008` (Anos Finais);
- 2017, 2019, 2021 e 2023: `Total - Federal, Estadual e Municipal`, localização `Total`, capital `Total`; uso dos campos técnicos próprios de cada fonte para 5º e 9º anos;
- em 2015, valor `0` nas médias continua sendo tratado como ausência apenas porque a própria fonte informa que zero representa impossibilidade de cálculo do estrato;
- em 2023, a Silver utiliza exclusivamente a Bronze oficial agregada de UF e não reconstrói resultados estaduais a partir das médias escolares.

Normalização:

- `REDE = PUBLICA`;
- `ETAPA = ANOS_INICIAIS | ANOS_FINAIS`;
- `DISCIPLINA = LP | MT`;
- UFs harmonizadas para siglas oficiais de duas letras;
- proficiências convertidas para número e arredondadas para duas casas decimais, acompanhando a precisão publicada pela fonte;
- marcadores `-`, `--` e vazios são tratados como ausência;
- não há imputação;
- não há média aritmética entre redes.

A quantidade estrutural esperada é:

`9 anos × 27 UFs × 2 etapas × 2 disciplinas = 972 registros`

Essa cardinalidade só será considerada concluída depois da execução da transformação e da validação independente.

### 16.16 Validação independente definida para a Silver do SAEB

O validador da Silver não importa nem reutiliza as funções do transformador.

Ele reconstrói de forma independente, diretamente das Bronzes, os registros esperados para cada edição e verifica:

- 9 anos esperados;
- 27 UFs por ano e etapa;
- duas etapas;
- duas disciplinas;
- rede canônica `PUBLICA`;
- unicidade do grão;
- ausência de proficiências nulas;
- domínio plausível de proficiência entre 0 e 500;
- regra específica de zero de 2015;
- seleção de rede/localização/capital por edição;
- valor publicado em cada célula de origem;
- arquivo, aba, linha, coluna e granularidade de origem;
- uso da Bronze oficial agregada de UF em 2023.

A Silver só será marcada como concluída depois de o validador retornar `SILVER DO SAEB: OK`.

---

### 16.17 Correção da leitura de 2013 e 2015 na transformação Silver

A primeira execução de `transformar_saeb.py` foi interrompida em 2013 porque o transformador procurava a variável técnica `DEPENDENCIA_ADM`.

Esse nome não existe nas Bronzes de 2013 e 2015.

A auditoria anterior já havia demonstrado que essas duas edições usam cabeçalho hierárquico em três linhas. Em 2013, o início do cabeçalho está em `_linha_origem = 4`; em 2015, em `_linha_origem = 3`.

Estrutura física confirmada para ambas:

- `col_001`: UF;
- `col_002`: REDE;
- `col_003`: LOCALIZAÇÃO;
- `col_004`: CAPITAL;
- `col_005`: Anos Iniciais / Língua Portuguesa;
- `col_006`: Anos Iniciais / Matemática;
- `col_007`: Anos Finais / Língua Portuguesa;
- `col_008`: Anos Finais / Matemática.

As linhas seguintes do cabeçalho identificam, separadamente, etapa e disciplina. Portanto, não é metodologicamente correto inventar nomes técnicos como `DEPENDENCIA_ADM`, `MEDIA_5_LP` ou `MEDIA_9_MT` para essas duas fontes.

Decisão de implementação:

- 2013 e 2015 passam a usar explicitamente as posições de coluna confirmadas pela auditoria;
- a seleção da rede continua sendo `Total - Federal, Estadual e Municipal`;
- localização e capital continuam `Total`;
- as UFs são harmonizadas a partir dos nomes presentes em `col_001`;
- a regra específica de 2015, em que valor `0` significa média não calculável para o estrato, permanece;
- 2017, 2019, 2021 e 2023 continuam usando os cabeçalhos técnicos de suas próprias fontes.

O validador independente foi corrigido pela mesma evidência estrutural, mas mantém implementação própria: ele reconstrói os registros esperados diretamente das Bronzes sem importar funções do transformador.

A falha não indica problema nos dados ou na Bronze. Ela revelou uma suposição incorreta da primeira versão da Silver sobre a uniformidade dos cabeçalhos entre edições.

---

### 16.18 Execução e validação final da Silver do SAEB

A transformação Silver do SAEB foi executada com sucesso em 19/08/2026.

Arquivo produzido:

`data/silver/saeb/saeb_2007_2023.parquet`

Resultado da transformação:

- 972 registros;
- anos: 2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021 e 2023;
- 27 UFs;
- etapas: `ANOS_INICIAIS` e `ANOS_FINAIS`;
- disciplinas: `LP` e `MT`;
- rede canônica: `PUBLICA`;
- valores ausentes: 0.

A cardinalidade observada corresponde exatamente ao grão planejado:

`9 anos × 27 UFs × 2 etapas × 2 disciplinas = 972 registros`

A validação independente também foi concluída com sucesso.

Foram confirmados:

- 9/9 anos esperados;
- 27 UFs por ano e etapa;
- unicidade do grão `ANO + UF + ETAPA + REDE + DISCIPLINA`;
- domínio plausível das proficiências entre 0 e 500;
- regra específica de zero do Saeb 2015;
- preservação, em 2007 e 2009, do agregado de origem `Total - Estadual e Municipal`;
- preservação, de 2013 a 2023, do agregado oficial `Total - Federal, Estadual e Municipal`;
- uso, em 2023, da Bronze oficial agregada de UF, e não da média das escolas ponderada por `NU_PRESENTES`;
- comparação direta dos 972 registros com as respectivas Bronzes;
- rastreabilidade de arquivo, aba, linha, coluna e granularidade.

Resultado final do validador:

`SILVER DO SAEB: OK`

A Silver do SAEB está concluída e não deve ser reaberta, salvo mudança das fontes ou descoberta de evidência metodológica nova que contradiga as decisões já documentadas.

---

## 17. PND 2025 — definição da Silver

### 17.1 Evidência da auditoria da população

A Bronze da PND preserva 1.087.359 registros substantivos do arquivo principal, além da linha física de cabeçalho.

A auditoria da população mostrou:

- 759.152 registros com os cinco resultados preenchidos;
- 328.207 registros com os cinco resultados ausentes;
- 0 registros parcialmente preenchidos.

Os cinco campos avaliados conjuntamente são:

- `PROFICIENCIA`;
- `NT_OBJ`;
- `NT_DIS`;
- `NT_GER`;
- `QT_ACERTOS`.

Entre os registros com `TP_PRES = 555`:

- 759.140 possuem os cinco resultados completos;
- 966 não possuem o conjunto completo de resultados.

Também existem 12 registros com `TP_PRES = 888` e resultados completos.

### 17.2 População analítica

A população Silver é definida por duas condições simultâneas:

`TP_PRES = 555`

e

`PROFICIENCIA + NT_OBJ + NT_DIS + NT_GER + QT_ACERTOS completos`

A cardinalidade esperada é:

`759.140 registros`

Os 12 registros `TP_PRES = 888` com resultados completos não são incluídos, porque a presença é parte explícita da definição da população analítica.

Os 966 registros `TP_PRES = 555` sem conjunto completo de resultados também não são incluídos.

Essa regra não imputa notas nem interpreta ausência como zero.

### 17.3 Localização geográfica

A PND utiliza a localização da aplicação da prova.

Na Silver:

- `CO_MUNICIPIO_PROVA` preserva o código do município do local de prova;
- `UF_PROVA` é derivada diretamente de `SG_UF_MUNICIPIO_PROVA`.

A UF não representa residência do participante.

O nome do município não será incorporado nesta etapa. O código IBGE permanece disponível para construção posterior de dimensão geográfica na Gold, utilizando a tabela oficial de municípios presente no dicionário da PND.

### 17.4 Área da prova

`CO_GRUPO` é definido pelo dicionário oficial como o código da área da prova de enquadramento do curso no Enade.

A Silver preserva o código e acrescenta `AREA_PROVA` com a categoria oficial correspondente.

São esperadas 17 categorias:

- 702 — Matemática;
- 904 — Letras - Português;
- 905 — Letras - Português e Inglês;
- 906 — Letras - Português e Espanhol;
- 1402 — Física;
- 1502 — Química;
- 1602 — Ciências Biológicas;
- 2001 — Pedagogia;
- 2402 — História;
- 2501 — Artes Visuais;
- 3002 — Geografia;
- 3202 — Filosofia;
- 3502 — Educação Física;
- 4005 — Ciência da Computação;
- 4301 — Música;
- 5402 — Ciências Sociais;
- 6407 — Letras - Inglês.

Os rótulos persistidos em `AREA_PROVA` mantêm a identificação oficial `(LICENCIATURA)` do dicionário.

Se surgir `CO_GRUPO` sem categoria documentada, a transformação deverá falhar explicitamente.

### 17.5 Tipagem

Na Bronze, as 26 colunas são preservadas como texto técnico.

Na Silver:

- ano, códigos, presença, situação, caderno e quantidade de acertos são convertidos para inteiros;
- `PROFICIENCIA`, `NT_OBJ`, `NT_DIS` e `NT_GER` são convertidos para números decimais;
- `UF_PROVA`, `AREA_PROVA` e metadados textuais permanecem texto.

A conversão numérica aceita vírgula ou ponto decimal.

O literal `NA`, célula vazia ou valor nulo é interpretado como ausência apenas para fins de tipagem e definição da população.

Não há arredondamento analítico na transformação da PND.

#### Domínio dos resultados numéricos

A primeira execução da transformação foi interrompida porque a versão inicial do script impunha, por precaução, a regra de que `PROFICIENCIA`, `NT_OBJ`, `NT_DIS` e `NT_GER` não poderiam assumir valores negativos.

Essa regra foi removida.

A evidência documental utilizada no projeto identifica os campos e sua função, mas não estabelece, no material auditado, um limite inferior obrigatório igual a zero para essas quatro medidas. Por isso, rejeitar registros negativos representaria introduzir uma restrição não documentada pela fonte.

Decisão:

- valores numéricos publicados em `PROFICIENCIA`, `NT_OBJ`, `NT_DIS` e `NT_GER` são preservados, inclusive se negativos;
- o transformador e o validador exibem mínimo, máximo e quantidade de valores negativos de cada medida para transparência;
- nenhum valor é recodificado, truncado ou substituído por zero;
- `QT_ACERTOS` continua obrigado a ser maior ou igual a zero, porque representa uma contagem de acertos.

Essa alteração corrige uma validação excessivamente restritiva do pipeline e não altera a definição da população analítica de 759.140 registros.

### 17.6 Colunas não levadas para a Silver

Não serão transportados para a Silver factual:

- `DS_VT_GAB_OBJ`;
- `DS_VT_ESC_OBJ`;
- `DS_VT_ACE_OBJ`;
- `CO_RS_I1` a `CO_RS_I9`.

Justificativa:

esses campos não são necessários às análises atualmente definidas para o dashboard, que utilizam médias de acertos e notas por UF e área, além de medidas de participantes abaixo de limiares analíticos.

A exclusão dessas colunas da Silver não representa perda da fonte: todos esses valores permanecem disponíveis na Bronze reproduzível.

### 17.7 Rastreabilidade e ausência de identificador individual

O arquivo principal não fornece um identificador individual do participante.

Por isso, a Silver não inventará um código de participante.

`LINHA_ORIGEM_BRONZE` é preservada como identificador técnico único do registro para:

- validação;
- diagnóstico;
- retorno ao registro de origem.

Ela não deve ser interpretada como identificador pessoal ou chave de negócio.

Também serão preservados:

- `ARQUIVO_ORIGEM`;
- `GRANULARIDADE_ORIGEM`.

### 17.8 Validação independente

O validador não reutiliza as funções do transformador.

Ele reconstrói diretamente da Bronze:

- a quantidade total de registros;
- a completude conjunta dos cinco resultados;
- as 759.140 linhas da população analítica;
- a exclusão dos 966 registros `TP_PRES = 555` sem resultados completos;
- a exclusão dos 12 registros `TP_PRES = 888` com resultados;
- a UF de prova;
- o código e o rótulo oficial da área;
- os cinco resultados numéricos;
- os códigos mantidos na Silver;
- a linha e o arquivo de origem.

Na validação independente, os 759.140 registros Silver foram comparados diretamente com a referência reconstruída da Bronze.

### 17.9 Situação de implementação

Arquivos implementados:

`src/silver/pnd/transformar_pnd.py`

`src/silver/pnd/validar_silver_pnd.py`

Saída gerada:

`data/silver/pnd/pnd_2025.parquet`

Os critérios definidos para conclusão foram atendidos:

1. a transformação produziu exatamente 759.140 registros;
2. a validação independente retornou `SILVER DA PND 2025: OK`.

Status:

`PND 2025 — SILVER ✅`

---

### 17.10 Execução e validação final da Silver da PND 2025

A transformação Silver da PND 2025 foi executada com sucesso em 19/08/2026.

Arquivo produzido:

`data/silver/pnd/pnd_2025.parquet`

Resultado da transformação:

- registros de dados na Bronze: 1.087.359;
- registros com os cinco resultados completos: 759.152;
- registros com resultados parcialmente preenchidos: 0;
- `TP_PRES = 555` com os cinco resultados completos: 759.140;
- `TP_PRES = 555` sem conjunto completo de resultados: 966;
- `TP_PRES = 888` com resultados completos e excluídos da população analítica: 12;
- linhas na Silver: 759.140;
- UFs: 27;
- áreas da prova: 17;
- municípios de prova: 750;
- valores ausentes nas cinco medidas analíticas: 0.

A validação independente reconstruiu a população diretamente da Bronze e comparou os 759.140 registros da Silver com a referência reconstruída.

Foram confirmados:

- `TP_PRES = 555` em todos os registros da Silver;
- ausência de valores ausentes em `PROFICIENCIA`, `NT_OBJ`, `NT_DIS`, `NT_GER` e `QT_ACERTOS`;
- 27 UFs;
- 17 áreas da prova;
- 750 municípios de prova;
- correspondência direta dos 759.140 registros Silver ↔ Bronze;
- rastreabilidade por linha de origem;
- mapeamento `CO_GRUPO` → área oficial.

Diagnóstico dos resultados numéricos:

| Campo | Mínimo | Máximo | Valores negativos |
|---|---:|---:|---:|
| `PROFICIENCIA` | -3,976610 | 2,688530 | 389.188 |
| `NT_OBJ` | 0,000000 | 100,000000 | 0 |
| `NT_DIS` | 0,000000 | 10,000000 | 0 |
| `NT_GER` | 0,000000 | 100,000000 | 0 |
| `QT_ACERTOS` | 0 | 77 | 0 |

Os valores negativos ocorrem exclusivamente em `PROFICIENCIA`.

Eles são preservados como publicados pela fonte. Nenhum valor foi truncado, recodificado, substituído por zero ou removido por ser negativo.

Resultado final do validador:

`SILVER DA PND 2025: OK`

Com esse resultado, a Silver da PND 2025 está concluída.

---

## 18. Situação atual

| Fonte | Bronze | Silver |
|---|---|---|
| Rendimento Escolar | ✅ concluída e validada | ✅ concluída e validada |
| TDI | ✅ concluída e validada | ✅ concluída e validada |
| IDEB | ✅ concluída e validada | ✅ concluída e validada |
| SAEB | ✅ concluída e validada | ✅ concluída e validada |
| PND 2025 | ✅ concluída e validada | ✅ concluída e validada |

Não existem fontes pendentes na camada Silver.

---

## 18.1 Conclusão da camada Silver

Com a validação independente da PND 2025, todas as fontes previstas para a camada Silver estão concluídas:

| Fonte | Silver |
|---|---|
| Rendimento Escolar | ✅ concluída |
| TDI | ✅ concluída |
| IDEB | ✅ concluída |
| SAEB | ✅ concluída |
| PND 2025 | ✅ concluída |

A camada Silver do projeto encontra-se integralmente concluída.

As próximas transformações deverão ocorrer na camada Gold, voltada à modelagem analítica, integração entre fatos e dimensões e preparação dos dados para o Power BI.

---

## 19. Histórico de decisões

| Data | Decisão |
|---|---|
| 18/08/2026 | Iniciada a camada Silver após conclusão integral da Bronze |
| 18/08/2026 | Definido que cada fonte será auditada diretamente a partir dos Parquets Bronze antes da implementação semântica |
| 18/08/2026 | Rendimento Escolar escolhido como primeira fonte da Silver |
| 18/08/2026 | Concluída a auditoria Silver do Rendimento Escolar e documentadas cinco configurações estruturais da série 2007–2023 |
| 18/08/2026 | Definido o grão Silver do Rendimento como ANO + UF + ETAPA + REDE + INDICADOR, com 2.754 registros esperados |
| 18/08/2026 | Definido o uso do agregado público oficial da fonte, localização Total, conversão de `--` para ausência e normalização das taxas para uma casa decimal |
| 18/08/2026 | Executada com sucesso a transformação Silver do Rendimento Escolar, gerando 2.754 registros para 2007–2023 |
| 18/08/2026 | Validados os 2.754 registros Silver diretamente contra a Bronze por arquivo, linha e coluna de origem |
| 18/08/2026 | Rendimento Escolar marcado como concluído na camada Silver após validação final com status OK |
| 18/08/2026 | Concluída a auditoria Silver da TDI para 2007–2023 |
| 18/08/2026 | Verificação focada confirmou agregado público explícito em todos os anos: `Publico` em 2007–2014 e `Pública` em 2015–2023 |
| 18/08/2026 | Corrigida a interpretação inicial da auditoria da TDI: a ausência aparente de `Pública` decorreu de busca textual sem normalização de acentuação |
| 18/08/2026 | Definido o grão Silver da TDI como ANO + UF + ETAPA + REDE, com 918 registros esperados |
| 18/08/2026 | Executada com sucesso a transformação Silver da TDI, gerando 918 registros para 2007–2023 |
| 18/08/2026 | Validados os 918 registros Silver da TDI diretamente contra a Bronze por arquivo, linha e coluna de origem |
| 18/08/2026 | TDI marcada como concluída na camada Silver após validação final com status OK |
| 19/08/2026 | Concluída a auditoria estrutural da Silver do IDEB |
| 19/08/2026 | Confirmado que as UFs usam o agregado oficial `Pública (4)` nas linhas de resultados do IDEB |
| 19/08/2026 | Identificadas grafias abreviadas na fonte: `R. G. do Norte`, `R. G. do Sul` e `M. G. do Sul`, harmonizadas respectivamente para RN, RS e MS |
| 19/08/2026 | Definida identificação dos anos do IDEB por `VL_OBSERVADO_YYYY`, evitando dependência do cabeçalho visual `20215` |
| 19/08/2026 | Definido o grão Silver do IDEB como ANO + UF + ETAPA + REDE, com 486 registros esperados |
| 19/08/2026 | Executada com sucesso a transformação Silver do IDEB, gerando 486 registros para nove anos, 27 UFs e duas etapas |
| 19/08/2026 | Validados os 486 registros Silver do IDEB diretamente contra a Bronze por arquivo, aba, linha e coluna de origem |
| 19/08/2026 | IDEB marcado como concluído na camada Silver após validação final com status OK |
| 19/08/2026 | Corrigida a auditoria Silver do SAEB: a identificação do cabeçalho passa a usar `_indice_cabecalho_origem` da Bronze, abandonando a heurística textual que classificou linhas de dados como cabeçalho em algumas edições |
| 19/08/2026 | Verificação focada do SAEB confirmou os agregados públicos de 2007–2021; para 2023, a ponderação por `NU_PRESENTES` foi mantida apenas como diagnóstico até confronto com a planilha oficial de resultados estaduais do Inep |
| 19/08/2026 | Incorporado ao RAW o pacote oficial de resultados agregados do Saeb 2023; `Resultados_Saeb_2023_Brasil_Estados_Municipios.xlsb` será usado para validar os resultados estaduais antes de definir a regra final de agregação escola → UF |
| 19/08/2026 | A comparação de 108 valores do Saeb 2023 confirmou 0/108 coincidências entre o resultado oficial estadual e a média escolar ponderada por `NU_PRESENTES`; essa ponderação foi rejeitada como regra canônica |
| 19/08/2026 | Definida reabertura controlada da Bronze do Saeb 2023 para incorporar a aba oficial `Estados` como fonte agregada de UF, preservando separadamente a Bronze escolar existente |
| 19/08/2026 | Esclarecida a política transversal de rede: `PUBLICA` inclui Federal + Estadual + Municipal sempre que o agregado oficial está disponível; a rede privada é excluída. SAEB 2007/2009 permanecem como exceção documental por disponibilizarem apenas `Total - Estadual e Municipal` |
| 19/08/2026 | Corrigida a tipagem física da Bronze agregada do Saeb 2023: colunas de origem heterogêneas passam a ser preservadas como texto anulável, com tipagem numérica adiada para a Silver |
| 19/08/2026 | Otimizada a validação da Bronze agregada do Saeb 2023: comparação célula a célula via `iloc` foi substituída por comparação vetorizada, mantendo a conferência integral de todas as células de origem |
| 19/08/2026 | Bronze oficial agregada do Saeb 2023 validada integralmente: 1.553 linhas, 177 colunas e 274.881 células RAW ↔ Bronze comparadas |
| 19/08/2026 | Definidos transformador e validador independente da Silver do Saeb 2007–2023, com grão `ANO + UF + ETAPA + REDE + DISCIPLINA` e 972 registros esperados |
| 19/08/2026 | Corrigida a Silver do Saeb para respeitar o cabeçalho hierárquico de 2013 e 2015; essas edições passam a usar as posições físicas auditadas `col_001`–`col_008`, sem inventar nomes técnicos inexistentes |
| 19/08/2026 | Silver do Saeb executada com 972 registros, 9 anos, 27 UFs, 2 etapas, 2 disciplinas e zero valores ausentes |
| 19/08/2026 | Validação independente da Silver do Saeb concluída com comparação direta dos 972 registros contra as Bronzes e rastreabilidade completa; resultado `SILVER DO SAEB: OK` |
| 19/08/2026 | Definida a população Silver da PND 2025 como `TP_PRES = 555` com `PROFICIENCIA`, `NT_OBJ`, `NT_DIS`, `NT_GER` e `QT_ACERTOS` completos, totalizando 759.140 registros esperados |
| 19/08/2026 | Definida a granularidade Silver da PND como registro individual da prova; `LINHA_ORIGEM_BRONZE` será usada apenas como chave técnica de rastreabilidade porque a fonte não fornece identificador individual |
| 19/08/2026 | Definidos `UF_PROVA`, `CO_MUNICIPIO_PROVA`, `CO_GRUPO` e `AREA_PROVA`; a área é mapeada pelas 17 categorias oficiais do dicionário da PND |
| 19/08/2026 | Vetores de resposta/gabarito e `CO_RS_I1`–`CO_RS_I9` permanecem na Bronze e não integram a Silver factual por não fazerem parte do escopo analítico atual |
| 19/08/2026 | Removida da transformação PND a restrição não documentada `resultado >= 0` para `PROFICIENCIA`, `NT_OBJ`, `NT_DIS` e `NT_GER`; os valores publicados passam a ser preservados integralmente e diagnosticados por mínimo, máximo e quantidade de negativos |
| 19/08/2026 | Mantida validação `QT_ACERTOS >= 0` por se tratar de contagem de acertos |
| 19/08/2026 | Silver da PND 2025 executada com 759.140 registros, 27 UFs, 17 áreas, 750 municípios e zero ausências nas cinco medidas analíticas |
| 19/08/2026 | Validação independente da PND comparou diretamente os 759.140 registros Silver com a Bronze e confirmou rastreabilidade e mapeamento de área; resultado `SILVER DA PND 2025: OK` |
| 19/08/2026 | Confirmado que valores negativos ocorrem apenas em `PROFICIENCIA` (389.188 registros; mínimo -3,976610) e são preservados conforme publicados pela fonte |
| 19/08/2026 | Camada Silver concluída integralmente para Rendimento Escolar, TDI, IDEB, SAEB e PND 2025 |
| 19/08/2026 | Revisada a situação final da camada Silver após a validação da PND: removido o status pendente residual e confirmadas todas as cinco fontes como concluídas e validadas |
