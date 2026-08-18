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

A estrutura final será definida após a transformação da população analítica auditada.

A PND permanecerá separada das séries históricas de IDEB, SAEB, Rendimento e TDI.

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

## 14. Situação atual

| Fonte | Bronze | Silver |
|---|---|---|
| Rendimento Escolar | ✅ | ✅ concluída e validada |
| TDI | ✅ | ✅ concluída e validada |
| IDEB | ✅ | ⏳ |
| SAEB | ✅ | ⏳ |
| PND 2025 | ✅ | ⏳ |

---

## 15. Histórico de decisões

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
| 18/08/2026 | Concluída a auditoria Silver da TDI para 2007–2023 |
| 18/08/2026 | Verificação focada confirmou agregado público explícito em todos os anos: `Publico` em 2007–2014 e `Pública` em 2015–2023 |
| 18/08/2026 | Corrigida a interpretação inicial da auditoria da TDI: a ausência aparente de `Pública` decorreu de busca textual sem normalização de acentuação |
| 18/08/2026 | Definido o grão Silver da TDI como ANO + UF + ETAPA + REDE, com 918 registros esperados |
| 18/08/2026 | Executada com sucesso a transformação Silver da TDI, gerando 918 registros para 2007–2023 |
| 18/08/2026 | Validados os 918 registros Silver da TDI diretamente contra a Bronze por arquivo, linha e coluna de origem |
| 18/08/2026 | TDI marcada como concluída na camada Silver após validação final com status OK |
