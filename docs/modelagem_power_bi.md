# Modelagem no Power BI

## 1. Objetivo

Esta etapa documenta a conexão da camada Gold ao Power BI, os relacionamentos do modelo dimensional e as primeiras medidas DAX.

O Power BI deverá consumir exclusivamente os arquivos Parquet localizados em:

```text
data/gold/
```

Nenhuma consulta do dashboard deverá ler diretamente as camadas Raw, Bronze ou Silver.

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

As consultas auxiliares utilizadas apenas para leitura dos arquivos devem permanecer com carga desabilitada:

```text
CaminhoBase
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

A função `fnParquetGold` permite selecionar cada Parquet a partir da pasta Gold sem repetir o caminho completo em todas as consultas.

Essa solução reduz duplicação de código no Power Query e facilita a alteração futura do diretório-base do projeto.

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

A PND não possui relação com `DIM_ETAPA`, pois sua estrutura analítica é organizada por área da licenciatura, e não por etapa da Educação Básica.

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

Por isso, a relação é deliberadamente omitida para manter o modelo em estrela e evitar caminhos ambíguos de filtro.

A coluna `UF` existente em `DIM_MUNICIPIO` permanece útil para validações de consistência territorial, mas não cria relacionamento físico no modelo.

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

Não devem ser adicionadas etapas de conversão no Power Query quando o Parquet já apresentar o tipo correto.

---

## 6. Medidas DAX iniciais

As medidas abaixo formam a primeira camada semântica do dashboard.

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

Essas medidas utilizam média porque cada linha da fato representa um valor de indicador por UF, ano, etapa e rede. O contexto de filtro do Power BI determina quais registros entram no cálculo.

---

### 6.2 TDI

```DAX
TDI Média =
AVERAGE(FATO_TDI[TDI])
```

---

### 6.3 IDEB

```DAX
IDEB Médio =
AVERAGE(FATO_IDEB[IDEB])
```

---

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

---

### 6.5 PND 2025

Cada linha da `FATO_PND` representa um registro individual válido da prova.

Por isso, a quantidade de participantes no contexto selecionado é calculada por contagem de linhas:

```DAX
Participantes PND =
COUNTROWS(FATO_PND)
```

```DAX
Nota Objetiva Média =
AVERAGE(FATO_PND[NT_OBJ])
```

```DAX
Nota Discursiva Média =
AVERAGE(FATO_PND[NT_DIS])
```

```DAX
Nota Geral Média =
AVERAGE(FATO_PND[NT_GER])
```

```DAX
Média de Acertos =
AVERAGE(FATO_PND[QT_ACERTOS])
```

### Padrão oficial de desempenho

A Gold materializa `PADRAO_DESEMPENHO` com base nos pontos de corte oficiais do Inep aplicados a `NT_OBJ`:

```text
NT_OBJ < 50           → NAO_PROFICIENTE
50 <= NT_OBJ < 70     → PADRAO_1
NT_OBJ >= 70          → PADRAO_2
```

Assim:

```DAX
Não Proficientes =
CALCULATE(
    COUNTROWS(FATO_PND),
    FATO_PND[PADRAO_DESEMPENHO] = "NAO_PROFICIENTE"
)
```

```DAX
Padrão 1 =
CALCULATE(
    COUNTROWS(FATO_PND),
    FATO_PND[PADRAO_DESEMPENHO] = "PADRAO_1"
)
```

```DAX
Padrão 2 =
CALCULATE(
    COUNTROWS(FATO_PND),
    FATO_PND[PADRAO_DESEMPENHO] = "PADRAO_2"
)
```

```DAX
Proficientes =
[Padrão 1] + [Padrão 2]
```

```DAX
% Proficientes =
DIVIDE(
    [Proficientes],
    [Participantes PND]
)
```

```DAX
% Não Proficientes =
DIVIDE(
    [Não Proficientes],
    [Participantes PND]
)
```

Os percentuais não são materializados na Gold porque dependem do contexto de filtro aplicado no Power BI.

---

## 7. Formatação recomendada

Medidas percentuais:

```text
Taxa de Aprovação
Taxa de Reprovação
Taxa de Abandono
TDI Média
```

devem ser exibidas como número decimal com uma ou duas casas, e não como percentual do Power BI, porque os valores já estão armazenados na escala 0–100.

As medidas:

```text
% Proficientes
% Não Proficientes
```

são razões entre 0 e 1 e devem ser formatadas no Power BI como percentual.

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
Média de Acertos → 1 ou 2 casas
Participantes → número inteiro com separador de milhar
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

---

## 9. Próxima etapa

Após criar e validar as medidas-base, serão implementadas separadamente as medidas de:

```text
variação temporal
primeiro e último ano selecionado
diferença entre períodos
```

Essa etapa será documentada antes da implementação porque IDEB e SAEB possuem apenas anos bienais, enquanto Rendimento e TDI possuem séries anuais.

A lógica temporal não deve assumir que todas as fatos possuem observação em todos os anos.
