# Modelagem no Power BI

## 1. Objetivo

Esta etapa documenta a conexao da camada Gold ao Power BI, os relacionamentos do modelo dimensional e as primeiras medidas DAX.

O Power BI devera consumir exclusivamente os arquivos Parquet localizados em:

```text
data/gold/
```

Nenhuma consulta do dashboard devera ler diretamente as camadas Raw, Bronze ou Silver.

Essa decisao preserva a separacao arquitetural do pipeline:

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

A Gold e a camada de consumo analitico do projeto.

---

## 2. Consultas carregadas

As consultas auxiliares utilizadas apenas para leitura dos arquivos devem permanecer com carga desabilitada:

```text
CaminhoBase
gold
fnParquetGold
```

As tabelas carregadas no modelo sao:

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

A funcao `fnParquetGold` permite selecionar cada Parquet a partir da pasta Gold sem repetir o caminho completo em todas as consultas.

Essa solucao reduz duplicacao de codigo no Power Query e facilita a alteracao futura do diretorio-base do projeto.

---

## 3. Relacionamentos do modelo

Todos os relacionamentos do modelo seguem o padrao:

```text
cardinalidade: 1:*
direcao de filtro: unica
sentido: dimensao → fato
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

A PND nao possui relacao com `DIM_ETAPA`, pois sua estrutura analitica e organizada por area da licenciatura, e nao por etapa da Educacao Basica.

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

## 4. Decisao sobre DIM_UF e DIM_MUNICIPIO

Nao e criada relacao direta entre:

```text
DIM_UF
e
DIM_MUNICIPIO
```

A FATO_PND ja possui:

```text
UF_PROVA
CO_MUNICIPIO_PROVA
```

e se relaciona diretamente com as duas dimensoes.

Criar adicionalmente:

```text
DIM_UF → DIM_MUNICIPIO
```

introduziria um segundo caminho geografico de filtragem ate a FATO_PND.

Por isso, a relacao e deliberadamente omitida para manter o modelo em estrela e evitar caminhos ambiguos de filtro.

A coluna `UF` existente em `DIM_MUNICIPIO` permanece util para validacoes de consistencia territorial, mas nao cria relacionamento fisico no modelo.

---

## 5. Tipos de dados esperados

### DIM_UF

```text
UF → Texto
```

### DIM_TEMPO

```text
ANO → Numero inteiro
```

### DIM_ETAPA

```text
ETAPA → Texto
ORDEM_ETAPA → Numero inteiro
```

### DIM_AREA_PND

```text
CO_GRUPO → Numero inteiro
AREA_PROVA → Texto
```

### DIM_MUNICIPIO

```text
CO_MUNICIPIO → Numero inteiro
UF → Texto
```

### FATO_RENDIMENTO

```text
ANO → Numero inteiro
UF → Texto
ETAPA → Texto
REDE → Texto
INDICADOR → Texto
VALOR → Numero decimal
```

### FATO_TDI

```text
ANO → Numero inteiro
UF → Texto
ETAPA → Texto
REDE → Texto
TDI → Numero decimal
```

### FATO_IDEB

```text
ANO → Numero inteiro
UF → Texto
ETAPA → Texto
REDE → Texto
IDEB → Numero decimal
```

### FATO_SAEB

```text
ANO → Numero inteiro
UF → Texto
ETAPA → Texto
REDE → Texto
DISCIPLINA → Texto
PROFICIENCIA → Numero decimal
```

### FATO_PND

```text
ANO → Numero inteiro
UF_PROVA → Texto
CO_MUNICIPIO_PROVA → Numero inteiro
CO_GRUPO → Numero inteiro
PROFICIENCIA → Numero decimal
NT_OBJ → Numero decimal
NT_DIS → Numero decimal
NT_GER → Numero decimal
QT_ACERTOS → Numero inteiro
PADRAO_DESEMPENHO → Texto
```

Nao devem ser adicionadas etapas de conversao no Power Query quando o Parquet ja apresentar o tipo correto.

---

## 6. Medidas DAX iniciais

As medidas abaixo formam a primeira camada semantica do dashboard.

### 6.1 Rendimento Escolar

```DAX
Taxa de Aprovacao =
CALCULATE(
    AVERAGE(FATO_RENDIMENTO[VALOR]),
    FATO_RENDIMENTO[INDICADOR] = "APROVACAO"
)
```

```DAX
Taxa de Reprovacao =
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

Essas medidas utilizam media porque cada linha da fato representa um valor de indicador por UF, ano, etapa e rede. O contexto de filtro do Power BI determina quais registros entram no calculo.

---

### 6.2 TDI

```DAX
TDI Media =
AVERAGE(FATO_TDI[TDI])
```

---

### 6.3 IDEB

```DAX
IDEB Medio =
AVERAGE(FATO_IDEB[IDEB])
```

---

### 6.4 SAEB

```DAX
Proficiencia Media SAEB =
AVERAGE(FATO_SAEB[PROFICIENCIA])
```

```DAX
Proficiencia Media LP =
CALCULATE(
    AVERAGE(FATO_SAEB[PROFICIENCIA]),
    FATO_SAEB[DISCIPLINA] = "LP"
)
```

```DAX
Proficiencia Media MT =
CALCULATE(
    AVERAGE(FATO_SAEB[PROFICIENCIA]),
    FATO_SAEB[DISCIPLINA] = "MT"
)
```

---

### 6.5 PND 2025

Cada linha da `FATO_PND` representa um registro individual valido da prova.

Por isso, a quantidade de participantes no contexto selecionado e calculada por contagem de linhas:

```DAX
Participantes PND =
COUNTROWS(FATO_PND)
```

```DAX
Nota Objetiva Media =
AVERAGE(FATO_PND[NT_OBJ])
```

```DAX
Nota Discursiva Media =
AVERAGE(FATO_PND[NT_DIS])
```

```DAX
Nota Geral Media =
AVERAGE(FATO_PND[NT_GER])
```

```DAX
Media de Acertos =
AVERAGE(FATO_PND[QT_ACERTOS])
```

### Padrao oficial de desempenho

A Gold materializa `PADRAO_DESEMPENHO` com base nos pontos de corte oficiais do Inep aplicados a `NT_OBJ`:

```text
NT_OBJ < 50           → NAO_PROFICIENTE
50 <= NT_OBJ < 70     → PADRAO_1
NT_OBJ >= 70          → PADRAO_2
```

Assim:

```DAX
Nao Proficientes =
CALCULATE(
    COUNTROWS(FATO_PND),
    FATO_PND[PADRAO_DESEMPENHO] = "NAO_PROFICIENTE"
)
```

```DAX
Padrao 1 =
CALCULATE(
    COUNTROWS(FATO_PND),
    FATO_PND[PADRAO_DESEMPENHO] = "PADRAO_1"
)
```

```DAX
Padrao 2 =
CALCULATE(
    COUNTROWS(FATO_PND),
    FATO_PND[PADRAO_DESEMPENHO] = "PADRAO_2"
)
```

```DAX
Proficientes =
[Padrao 1] + [Padrao 2]
```

```DAX
% Proficientes =
DIVIDE(
    [Proficientes],
    [Participantes PND]
)
```

```DAX
% Nao Proficientes =
DIVIDE(
    [Nao Proficientes],
    [Participantes PND]
)
```

```DAX
% Padrao 1 =
DIVIDE(
    [Padrao 1],
    [Participantes PND]
)
```

```DAX
% Padrao 2 =
DIVIDE(
    [Padrao 2],
    [Participantes PND]
)
```

Os percentuais nao sao materializados na Gold porque dependem do contexto de filtro aplicado no Power BI.

---

## 7. Formatacao recomendada

Medidas percentuais:

```text
Taxa de Aprovacao
Taxa de Reprovacao
Taxa de Abandono
TDI Media
```

devem ser exibidas como numero decimal com uma ou duas casas, e nao como percentual do Power BI, porque os valores ja estao armazenados na escala 0–100.

As medidas:

```text
% Proficientes
% Nao Proficientes
% Padrao 1
% Padrao 2
```

sao razoes entre 0 e 1 e devem ser formatadas no Power BI como percentual.

IDEB:

```text
1 ou 2 casas decimais
```

SAEB:

```text
1 ou 2 casas decimais
```

PND:

```text
NT_OBJ / NT_GER → 1 ou 2 casas
NT_DIS → 1 ou 2 casas
Media de Acertos → 1 ou 2 casas
Participantes → numero inteiro com separador de milhar
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

Isso garante a ordem analitica:

```text
ANOS_INICIAIS
ANOS_FINAIS
```

em segmentacoes e graficos.

---

## 9. Medida de apoio

A medida abaixo e usada em paginas que comparam IDEB e SAEB, restringindo a visualizacao aos anos em que os dois indicadores possuem dado no contexto selecionado:

```DAX
Ano de Avaliacao Disponivel =
VAR TemIDEB =
    NOT ISBLANK([IDEB Medio])
VAR TemSAEB =
    NOT ISBLANK([Proficiencia Media SAEB])
RETURN
    IF(TemIDEB && TemSAEB, 1, 0)
```

## 10. Variacoes temporais

As medidas de variacao temporal calculam a diferenca absoluta entre o ultimo e o primeiro ano com dado dentro do intervalo selecionado. A logica nao assume que todas as fatos possuem observacao em todos os anos.

```DAX
Variacao Aprovacao =
VAR AnosComDados =
    FILTER(
        ALLSELECTED(DIM_TEMPO[ANO]),
        NOT ISBLANK(CALCULATE([Taxa de Aprovacao]))
    )
VAR PrimeiroAno =
    MINX(AnosComDados, DIM_TEMPO[ANO])
VAR UltimoAno =
    MAXX(AnosComDados, DIM_TEMPO[ANO])
VAR ValorInicial =
    CALCULATE(
        [Taxa de Aprovacao],
        REMOVEFILTERS(DIM_TEMPO[ANO]),
        DIM_TEMPO[ANO] = PrimeiroAno
    )
VAR ValorFinal =
    CALCULATE(
        [Taxa de Aprovacao],
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
Variacao IDEB =
VAR AnosComDados =
    FILTER(
        ALLSELECTED(DIM_TEMPO[ANO]),
        NOT ISBLANK(CALCULATE([IDEB Medio]))
    )
VAR PrimeiroAno =
    MINX(AnosComDados, DIM_TEMPO[ANO])
VAR UltimoAno =
    MAXX(AnosComDados, DIM_TEMPO[ANO])
VAR ValorInicial =
    CALCULATE(
        [IDEB Medio],
        REMOVEFILTERS(DIM_TEMPO[ANO]),
        DIM_TEMPO[ANO] = PrimeiroAno
    )
VAR ValorFinal =
    CALCULATE(
        [IDEB Medio],
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
Variacao SAEB Matematica =
VAR AnosComDados =
    FILTER(
        ALLSELECTED(DIM_TEMPO[ANO]),
        NOT ISBLANK(CALCULATE([Proficiencia Media MT]))
    )
VAR PrimeiroAno =
    MINX(AnosComDados, DIM_TEMPO[ANO])
VAR UltimoAno =
    MAXX(AnosComDados, DIM_TEMPO[ANO])
VAR ValorInicial =
    CALCULATE(
        [Proficiencia Media MT],
        REMOVEFILTERS(DIM_TEMPO[ANO]),
        DIM_TEMPO[ANO] = PrimeiroAno
    )
VAR ValorFinal =
    CALCULATE(
        [Proficiencia Media MT],
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
Variacao SAEB Portugues =
VAR AnosComDados =
    FILTER(
        ALLSELECTED(DIM_TEMPO[ANO]),
        NOT ISBLANK(CALCULATE([Proficiencia Media LP]))
    )
VAR PrimeiroAno =
    MINX(AnosComDados, DIM_TEMPO[ANO])
VAR UltimoAno =
    MAXX(AnosComDados, DIM_TEMPO[ANO])
VAR ValorInicial =
    CALCULATE(
        [Proficiencia Media LP],
        REMOVEFILTERS(DIM_TEMPO[ANO]),
        DIM_TEMPO[ANO] = PrimeiroAno
    )
VAR ValorFinal =
    CALCULATE(
        [Proficiencia Media LP],
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
Variacao TDI =
VAR AnosComDados =
    FILTER(
        ALLSELECTED(DIM_TEMPO[ANO]),
        NOT ISBLANK(CALCULATE([TDI Media]))
    )
VAR PrimeiroAno =
    MINX(AnosComDados, DIM_TEMPO[ANO])
VAR UltimoAno =
    MAXX(AnosComDados, DIM_TEMPO[ANO])
VAR ValorInicial =
    CALCULATE(
        [TDI Media],
        REMOVEFILTERS(DIM_TEMPO[ANO]),
        DIM_TEMPO[ANO] = PrimeiroAno
    )
VAR ValorFinal =
    CALCULATE(
        [TDI Media],
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
