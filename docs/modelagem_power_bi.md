# Modelagem no Power BI

## 1. Objetivo

Esta etapa documenta a conexão da camada Gold ao Power BI, os relacionamentos do
modelo dimensional e as medidas DAX atualmente implementadas.

O Power BI deve consumir exclusivamente os arquivos Parquet localizados em:

```text
data/gold/
```

Nenhuma consulta do dashboard deve ler diretamente as camadas Raw, Bronze ou
Silver.

Essa decisão preserva a separação arquitetural do pipeline:

```text
RAW
  ↓
BRONZE
  ↓
SILVER
  ↓
GOLD
  ↓
POWER BI
```

A Gold é a camada de consumo analítico do projeto.

---

## 2. Consultas carregadas

As consultas auxiliares utilizadas apenas para leitura dos arquivos devem
permanecer com carga desabilitada:

```text
gold
fnParquetGold
```

As tabelas carregadas no modelo são:

```text
DIM_UF
DIM_TEMPO
DIM_ETAPA
DIM_AREA_PND
DIM_MUNICIPIO

FATO_RENDIMENTO
FATO_TDI
FATO_IDEB
FATO_SAEB
FATO_PND
```

A função `fnParquetGold` permite selecionar cada Parquet a partir da pasta Gold
sem repetir o caminho completo em todas as consultas.

Essa solução reduz duplicação de código no Power Query e facilita a alteração
futura do diretório-base do projeto.

### 2.1 Configurar o PBIX em outro computador

O procedimento completo está em [Abrir e Configurar o Power BI](../README.md#6-abrir-e-configurar-o-power-bi).
Depois de gerar a Gold pelo pipeline, abra o PBIX no Power BI Desktop e acesse
**Transformar dados → gold → Fonte**. Na configuração mostrada nesta versão,
o caminho está diretamente na consulta `gold`, e não em um parâmetro separado
chamado `CaminhoBase`:

```powerquery
= Folder.Files("C:\portfolio-pipeline-dados-educacionais\data\gold")
```

Troque esse caminho absoluto pela pasta `data\gold` do clone local. A função
[Folder.Files](https://learn.microsoft.com/en-us/powerquery-m/folder-files)
lista também os arquivos das subpastas `dimensoes` e `fatos`. Não é preciso
mover os Parquets para a raiz da Gold. Preserve seus nomes e evite arquivos
duplicados com o mesmo nome em subpastas desse diretório.

As consultas analíticas reutilizam `fnParquetGold`, como no exemplo:

```powerquery
= fnParquetGold("dim_uf.parquet")
```

A tela de parâmetro exibida ao selecionar a função é esperada; a atualização
das tabelas não exige invocação manual. Confira as 27 linhas de `DIM_UF`,
use **Fechar e Aplicar** e salve o PBIX. Após regenerar a Gold, atualize o
relatório no Power BI. A atualização do relatório lê os Parquets; não executa
o download nem o pipeline Python.

---

## 3. Relacionamentos do modelo

Todos os relacionamentos do modelo seguem o padrão:

```text
cardinalidade: 1:*
direção de filtro: única
sentido: dimensão → fato
relacionamento ativo: sim
```

### 3.1 DIM_UF

```text
DIM_UF[UF]
    → FATO_RENDIMENTO[UF]
    → FATO_TDI[UF]
    → FATO_IDEB[UF]
    → FATO_SAEB[UF]
    → FATO_PND[UF_PROVA]
```

### 3.2 DIM_TEMPO

```text
DIM_TEMPO[ANO]
    → FATO_RENDIMENTO[ANO]
    → FATO_TDI[ANO]
    → FATO_IDEB[ANO]
    → FATO_SAEB[ANO]
    → FATO_PND[ANO]
```

### 3.3 DIM_ETAPA

```text
DIM_ETAPA[ETAPA]
    → FATO_RENDIMENTO[ETAPA]
    → FATO_TDI[ETAPA]
    → FATO_IDEB[ETAPA]
    → FATO_SAEB[ETAPA]
```

A PND não possui relação com `DIM_ETAPA`, pois sua estrutura analítica é
organizada por área da licenciatura, e não por etapa da Educação Básica.

### 3.4 DIM_AREA_PND

```text
DIM_AREA_PND[CO_GRUPO]
    → FATO_PND[CO_GRUPO]
```

### 3.5 DIM_MUNICIPIO

```text
DIM_MUNICIPIO[CO_MUNICIPIO]
    → FATO_PND[CO_MUNICIPIO_PROVA]
```

---

## 4. Decisão sobre DIM_UF e DIM_MUNICIPIO

Não é criada relação direta entre:

```text
DIM_UF
e
DIM_MUNICIPIO
```

A FATO_PND já possui:

```text
UF_PROVA
CO_MUNICIPIO_PROVA
```

e se relaciona diretamente com as duas dimensões.

Criar adicionalmente:

```text
DIM_UF → DIM_MUNICIPIO
```

introduziria um segundo caminho geográfico de filtragem até a FATO_PND.

Por isso, a relação é deliberadamente omitida para manter o modelo em estrela e
evitar caminhos ambíguos de filtro.

A coluna `UF` existente em `DIM_MUNICIPIO` permanece útil para validações de
consistência territorial, mas não cria relacionamento físico no modelo.

---

## 5. Tipos de dados esperados

### DIM_UF

```text
UF → Texto
```

### DIM_TEMPO

```text
ANO → Número inteiro
```

### DIM_ETAPA

```text
ETAPA → Texto
ORDEM_ETAPA → Número inteiro
```

### DIM_AREA_PND

```text
CO_GRUPO → Número inteiro
AREA_PROVA → Texto
```

### DIM_MUNICIPIO

```text
CO_MUNICIPIO → Número inteiro
UF → Texto
```

### FATO_RENDIMENTO

```text
ANO → Número inteiro
UF → Texto
ETAPA → Texto
REDE → Texto
INDICADOR → Texto
VALOR → Número decimal
```

### FATO_TDI

```text
ANO → Número inteiro
UF → Texto
ETAPA → Texto
REDE → Texto
TDI → Número decimal
```

### FATO_IDEB

```text
ANO → Número inteiro
UF → Texto
ETAPA → Texto
REDE → Texto
IDEB → Número decimal
```

### FATO_SAEB

```text
ANO → Número inteiro
UF → Texto
ETAPA → Texto
REDE → Texto
DISCIPLINA → Texto
PROFICIENCIA → Número decimal
```

### FATO_PND

```text
ANO → Número inteiro
UF_PROVA → Texto
CO_MUNICIPIO_PROVA → Número inteiro
CO_GRUPO → Número inteiro
PROFICIENCIA → Número decimal
NT_OBJ → Número decimal
NT_DIS → Número decimal
NT_GER → Número decimal
QT_ACERTOS → Número inteiro
PADRAO_DESEMPENHO → Texto
```

Não devem ser adicionadas etapas de conversão no Power Query quando o Parquet já
apresentar o tipo correto.

---

## 6. Medidas DAX implementadas

A fonte de verdade das medidas é
[powerbi/medidas_power_bi.dax](../powerbi/medidas_power_bi.dax).

O modelo possui 27 medidas. Os nomes, referências entre medidas e fórmulas
abaixo reproduzem a implementação atual.

### 6.1 Rendimento Escolar

```DAX
Taxa de Aprovação =
CALCULATE(
    AVERAGE(FATO_RENDIMENTO[VALOR]),
    FATO_RENDIMENTO[INDICADOR] = "APROVACAO"
)
```

```DAX
Taxa de Reprovação =
CALCULATE(
    AVERAGE(FATO_RENDIMENTO[VALOR]),
    FATO_RENDIMENTO[INDICADOR] = "REPROVACAO"
)
```

```DAX
Taxa de Abandono =
CALCULATE(
    AVERAGE(FATO_RENDIMENTO[VALOR]),
    FATO_RENDIMENTO[INDICADOR] = "ABANDONO"
)
```

Essas medidas utilizam média porque cada linha da fato representa um valor de
indicador por UF, ano, etapa e rede. O contexto de filtro do Power BI determina
quais registros entram no cálculo.

### 6.2 TDI

```DAX
TDI Média =
AVERAGE(FATO_TDI[TDI])
```

### 6.3 IDEB

```DAX
IDEB Médio =
AVERAGE(FATO_IDEB[IDEB])
```

### 6.4 SAEB

```DAX
Proficiência Média SAEB =
AVERAGE(FATO_SAEB[PROFICIENCIA])
```

```DAX
Proficiência Média LP =
CALCULATE(
    AVERAGE(FATO_SAEB[PROFICIENCIA]),
    FATO_SAEB[DISCIPLINA] = "LP"
)
```

```DAX
Proficiência Média MT =
CALCULATE(
    AVERAGE(FATO_SAEB[PROFICIENCIA]),
    FATO_SAEB[DISCIPLINA] = "MT"
)
```

### 6.5 PND 2025

AUD-04B (13/11/2026): `PADRAO_DESEMPENHO` agora classifica a nota geral publicada
`NT_GER`. A coluna e o esquema permanecem; seus valores passam a
`ABAIXO_DO_BASICO`, `BASICO` e `ADEQUADO`. `Registros analisados — PND` continua contando
registros analíticos por COUNTROWS, sem deduplicação ou prova de pessoas únicas.

### 6.6 Padrão oficial de desempenho

A Nota Técnica 44/2025, item 9.3/Tabela 2 (p. 6), define Abaixo do Básico
para `NT_GER < 50`, Básico para `50 <= NT_GER < 70` e Adequado para `NT_GER >= 70`.
A classificação usa a nota publicada, sem recalcular TRI ou nota geral. A Nota
4/2026, itens 4.2–4.4, complementa os descritores com a nomenclatura Não
Proficiente, Proficiente Básico e Proficiente Adequado; os rótulos do projeto
seguem a Tabela 2 da Nota 44. A soma Básico ou Adequado é descritiva, sem inferir
aprovação ou habilitação.

O PBIX e a captura registram os níveis por nota geral e os resultados dos
recortes gerais, de Minas Gerais e de Minas Gerais com Pedagogia. O PBIX
versionado na main é a referência definitiva do painel e contém as
alterações manuais mais recentes feitas no Power BI Desktop. O arquivo
[medidas_power_bi.dax](../powerbi/medidas_power_bi.dax) registra as expressões
revisadas dos quatro percentuais de composição. O
[projeto PBIP](../powerbi/pbip/analise_indicadores_PND_oficial.pbip) permanece
como artefato complementar e não foi utilizado nas últimas alterações manuais
realizadas no Desktop. A auditoria reproduziu os cálculos do DAX sobre os dados
importados.

```DAX
Registros analisados — PND =
COUNTROWS(FATO_PND)

Nota Objetiva Média =
AVERAGE(FATO_PND[NT_OBJ])

Nota Discursiva Média =
AVERAGE(FATO_PND[NT_DIS])

Nota Geral Média =
AVERAGE(FATO_PND[NT_GER])

Média de Acertos =
AVERAGE(FATO_PND[QT_ACERTOS])

Abaixo do Básico =
CALCULATE(
    COUNTROWS(FATO_PND),
    FATO_PND[PADRAO_DESEMPENHO] = "ABAIXO_DO_BASICO"
)

Básico =
CALCULATE(
    COUNTROWS(FATO_PND),
    FATO_PND[PADRAO_DESEMPENHO] = "BASICO"
)

Adequado =
CALCULATE(
    COUNTROWS(FATO_PND),
    FATO_PND[PADRAO_DESEMPENHO] = "ADEQUADO"
)

Básico ou Adequado =
[Básico] + [Adequado]

% Básico ou Adequado =
DIVIDE(
    [Básico ou Adequado],
    CALCULATE(
        [Registros analisados — PND],
        REMOVEFILTERS(FATO_PND[PADRAO_DESEMPENHO])
    )
)

% Abaixo do Básico =
DIVIDE(
    [Abaixo do Básico],
    CALCULATE(
        [Registros analisados — PND],
        REMOVEFILTERS(FATO_PND[PADRAO_DESEMPENHO])
    )
)

% Básico =
DIVIDE(
    [Básico],
    CALCULATE(
        [Registros analisados — PND],
        REMOVEFILTERS(FATO_PND[PADRAO_DESEMPENHO])
    )
)

% Adequado =
DIVIDE(
    [Adequado],
    CALCULATE(
        [Registros analisados — PND],
        REMOVEFILTERS(FATO_PND[PADRAO_DESEMPENHO])
    )
)
```

Os percentuais mostram a composição do recorte de ano, UF, município e área.
Cada numerador seleciona o próprio nível e o denominador inclui todos os níveis
ao remover exclusivamente o filtro de `FATO_PND[PADRAO_DESEMPENHO]`.
O cartão de registros mantém os filtros ativos na sua contagem. Na definição
TMDL do PBIP preservada na main, as quatro fórmulas percentuais acima diferem
das expressões do arquivo DAX; não foram identificadas outras divergências de
fórmula nessa comparação. A equivalência integral entre PBIX, PBIP e DAX não
foi comprovada nesta integração, pois o modelo interno do PBIX não foi
extraído. Isso não significa que o PBIP esteja desatualizado como um todo, e
nenhum artefato deve ser atualizado automaticamente para conciliar essas
diferenças. O PBIX da main permanece a referência definitiva do painel.

Os percentuais são exibidos com duas casas decimais. O cartão de total usa
“Registros analisados — PND”. A população analisada contém 265.915
Abaixo do Básico, 309.425 Básicos e 183.800 Adequados, total 759.140; Básico ou
Adequado soma 493.225 (64,9715467503%). A população é o recorte do projeto,
não a publicação oficial integral. Os critérios e testes estão documentados na
[camada Gold](camada_gold.md) e em
[`tests/test_pnd_classificacao.py`](../tests/test_pnd_classificacao.py).


### 6.7 Medida de apoio

A medida abaixo é usada em páginas que comparam IDEB e SAEB, restringindo a
visualização aos anos em que os dois indicadores possuem dado no contexto
selecionado:

```DAX
Ano de Avaliação Disponível =
VAR TemIDEB =
    NOT ISBLANK([IDEB Médio])
VAR TemSAEB =
    NOT ISBLANK([Proficiência Média SAEB])
RETURN
    IF(TemIDEB && TemSAEB, 1, 0)
```

### 6.8 Variações temporais

As medidas de variação temporal calculam a diferença absoluta entre o último e o
primeiro ano com dado dentro do intervalo selecionado. A lógica não assume que
todas as fatos possuem observação em todos os anos.

```DAX
Variação Aprovação =
VAR AnosComDados =
    FILTER(
        ALLSELECTED(DIM_TEMPO[ANO]),
        NOT ISBLANK(CALCULATE([Taxa de Aprovação]))
    )
VAR PrimeiroAno =
    MINX(AnosComDados, DIM_TEMPO[ANO])
VAR UltimoAno =
    MAXX(AnosComDados, DIM_TEMPO[ANO])
VAR ValorInicial =
    CALCULATE(
        [Taxa de Aprovação],
        REMOVEFILTERS(DIM_TEMPO[ANO]),
        DIM_TEMPO[ANO] = PrimeiroAno
    )
VAR ValorFinal =
    CALCULATE(
        [Taxa de Aprovação],
        REMOVEFILTERS(DIM_TEMPO[ANO]),
        DIM_TEMPO[ANO] = UltimoAno
    )
RETURN
    IF(
        ISBLANK(PrimeiroAno)
            || ISBLANK(UltimoAno)
            || PrimeiroAno = UltimoAno,
        BLANK(),
        ValorFinal - ValorInicial
    )
```

```DAX
Variação IDEB =
VAR AnosComDados =
    FILTER(
        ALLSELECTED(DIM_TEMPO[ANO]),
        NOT ISBLANK(CALCULATE([IDEB Médio]))
    )
VAR PrimeiroAno =
    MINX(AnosComDados, DIM_TEMPO[ANO])
VAR UltimoAno =
    MAXX(AnosComDados, DIM_TEMPO[ANO])
VAR ValorInicial =
    CALCULATE(
        [IDEB Médio],
        REMOVEFILTERS(DIM_TEMPO[ANO]),
        DIM_TEMPO[ANO] = PrimeiroAno
    )
VAR ValorFinal =
    CALCULATE(
        [IDEB Médio],
        REMOVEFILTERS(DIM_TEMPO[ANO]),
        DIM_TEMPO[ANO] = UltimoAno
    )
RETURN
    IF(
        ISBLANK(PrimeiroAno)
            || ISBLANK(UltimoAno)
            || PrimeiroAno = UltimoAno,
        BLANK(),
        ValorFinal - ValorInicial
    )
```

```DAX
Variação SAEB Matemática =
VAR AnosComDados =
    FILTER(
        ALLSELECTED(DIM_TEMPO[ANO]),
        NOT ISBLANK(CALCULATE([Proficiência Média MT]))
    )
VAR PrimeiroAno =
    MINX(AnosComDados, DIM_TEMPO[ANO])
VAR UltimoAno =
    MAXX(AnosComDados, DIM_TEMPO[ANO])
VAR ValorInicial =
    CALCULATE(
        [Proficiência Média MT],
        REMOVEFILTERS(DIM_TEMPO[ANO]),
        DIM_TEMPO[ANO] = PrimeiroAno
    )
VAR ValorFinal =
    CALCULATE(
        [Proficiência Média MT],
        REMOVEFILTERS(DIM_TEMPO[ANO]),
        DIM_TEMPO[ANO] = UltimoAno
    )
RETURN
    IF(
        ISBLANK(PrimeiroAno)
            || ISBLANK(UltimoAno)
            || PrimeiroAno = UltimoAno,
        BLANK(),
        ValorFinal - ValorInicial
    )
```

```DAX
Variação SAEB Português =
VAR AnosComDados =
    FILTER(
        ALLSELECTED(DIM_TEMPO[ANO]),
        NOT ISBLANK(CALCULATE([Proficiência Média LP]))
    )
VAR PrimeiroAno =
    MINX(AnosComDados, DIM_TEMPO[ANO])
VAR UltimoAno =
    MAXX(AnosComDados, DIM_TEMPO[ANO])
VAR ValorInicial =
    CALCULATE(
        [Proficiência Média LP],
        REMOVEFILTERS(DIM_TEMPO[ANO]),
        DIM_TEMPO[ANO] = PrimeiroAno
    )
VAR ValorFinal =
    CALCULATE(
        [Proficiência Média LP],
        REMOVEFILTERS(DIM_TEMPO[ANO]),
        DIM_TEMPO[ANO] = UltimoAno
    )
RETURN
    IF(
        ISBLANK(PrimeiroAno)
            || ISBLANK(UltimoAno)
            || PrimeiroAno = UltimoAno,
        BLANK(),
        ValorFinal - ValorInicial
    )
```

```DAX
Variação TDI =
VAR AnosComDados =
    FILTER(
        ALLSELECTED(DIM_TEMPO[ANO]),
        NOT ISBLANK(CALCULATE([TDI Média]))
    )
VAR PrimeiroAno =
    MINX(AnosComDados, DIM_TEMPO[ANO])
VAR UltimoAno =
    MAXX(AnosComDados, DIM_TEMPO[ANO])
VAR ValorInicial =
    CALCULATE(
        [TDI Média],
        REMOVEFILTERS(DIM_TEMPO[ANO]),
        DIM_TEMPO[ANO] = PrimeiroAno
    )
VAR ValorFinal =
    CALCULATE(
        [TDI Média],
        REMOVEFILTERS(DIM_TEMPO[ANO]),
        DIM_TEMPO[ANO] = UltimoAno
    )
RETURN
    IF(
        ISBLANK(PrimeiroAno)
            || ISBLANK(UltimoAno)
            || PrimeiroAno = UltimoAno,
        BLANK(),
        ValorFinal - ValorInicial
    )
```

---

## 7. Formatação recomendada

Medidas percentuais armazenadas na escala 0-100:

```text
Taxa de Aprovação
Taxa de Reprovação
Taxa de Abandono
TDI Média
```

devem ser exibidas como número decimal com uma ou duas casas, e não como
percentual do Power BI.

As medidas abaixo são razões entre 0 e 1 e devem ser formatadas no Power BI como
percentual:

```text
% Básico ou Adequado
% Abaixo do Básico
% Básico
% Adequado
```

IDEB e SAEB devem ser exibidos com uma ou duas casas decimais.

PND:

```text
NT_OBJ / NT_GER → 1 ou 2 casas
NT_DIS → 1 ou 2 casas
Média de Acertos → 1 ou 2 casas
Registros analisados — PND → número inteiro com separador de milhar
```

---

## 8. Ordem da DIM_ETAPA

A coluna:

```text
DIM_ETAPA[ETAPA]
```

deve ser classificada por:

```text
DIM_ETAPA[ORDEM_ETAPA]
```

Isso garante a ordem analítica:

```text
ANOS_INICIAIS
ANOS_FINAIS
```

em segmentações e gráficos.
