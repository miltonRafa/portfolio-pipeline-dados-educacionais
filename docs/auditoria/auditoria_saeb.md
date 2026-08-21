# Auditoria das Fontes — SAEB

## 1. Objetivo

Este documento registra a auditoria tecnica das fontes do **Sistema de Avaliacao da Educacao Basica (SAEB)** utilizadas no projeto.

A auditoria foi realizada antes da definicao final das regras de transformacao do pipeline, com o objetivo de identificar diferencas entre os arquivos disponibilizados ao longo dos anos e evitar a aplicacao de um tratamento uniforme sobre estruturas distintas.

Foram analisadas as edicoes de:

**2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021 e 2023.**

O projeto utiliza somente:

* Ensino Fundamental — Anos Iniciais;
* Ensino Fundamental — Anos Finais;
* Lingua Portuguesa;
* Matematica;
* resultados em nivel de Unidade Federativa (UF).

> **Status deste documento:** provisorio. Algumas decisoes sobre a fonte definitiva e o conceito de rede publica serao atualizadas apos a auditoria dos demais indicadores do projeto, especialmente IDEB, Rendimento Escolar e TDI.

---

## 2. Principios adotados na auditoria

A analise das fontes seguiu os seguintes principios:

1. preservar os arquivos originais na camada `raw`;
2. identificar o nivel original de cada fonte;
3. verificar se o resultado ja e disponibilizado por UF ou precisa ser calculado;
4. identificar as categorias de rede disponiveis em cada edicao;
5. verificar as variaveis utilizadas nas medias de Lingua Portuguesa e Matematica;
6. identificar a quantidade de participantes quando necessaria para agregacao;
7. nao interpretar valores ausentes como zero;
8. registrar diferencas estruturais entre as edicoes;
9. evitar reconstruir um indicador quando existir resultado oficial agregado adequado;
10. adiar decisoes que dependam da consistencia com outros indicadores.

---

# 3. SAEB 2007

## Arquivos disponiveis

```text
Dicionario_SAEB_2007.xlsx
TS_ESCOLA_2007.csv
MEDIA_UF_2007.xlsx
```

## `MEDIA_UF_2007.xlsx`

O arquivo apresenta resultados ja agregados por Unidade Federativa.

Principais campos identificados:

```text
ANO_SAEB
CO_UF
NO_UF
DEPENDENCIA_ADM
LOCALIZACAO
CAPITAL
MEDIA_4_LP
MEDIA_4_MT
MEDIA_8_LP
MEDIA_8_MT
MEDIA_11_LP
MEDIA_11_MT
```

Para o recorte deste projeto interessam:

```text
MEDIA_4_LP
MEDIA_4_MT
MEDIA_8_LP
MEDIA_8_MT
```

### Categorias de rede

Foram identificadas:

```text
Total - Federal, Estadual, Municipal e Privada
Estadual
Municipal
Privada
Total - Estadual e Municipal
```

Nao foi encontrada nesse arquivo uma categoria denominada:

```text
Total - Federal, Estadual e Municipal
```

Portanto, o agregado publico disponivel diretamente no arquivo de UF corresponde a **Estadual + Municipal**, enquanto o outro total inclui tambem a rede privada.

---

## `TS_ESCOLA_2007.csv`

O arquivo contem registros em nivel de escola.

Variaveis relevantes:

```text
ID_UF
IN_PUBLICA
ID_LOCALIZACAO

NU_PRESENTES_4EF
NU_PRESENTES_8EF

MEDIA_4EF_LP
MEDIA_4EF_MT
MEDIA_8EF_LP
MEDIA_8EF_MT
```

O dicionario identifica:

* `ID_UF`: codigo da Unidade Federativa;
* `IN_PUBLICA`: indicador de escola publica;
* `NU_PRESENTES_4EF`: alunos presentes na avaliacao da etapa correspondente;
* `NU_PRESENTES_8EF`: alunos presentes na avaliacao da etapa correspondente;
* `MEDIA_*`: proficiencia media dos participantes.

A inspecao do arquivo encontrou:

```text
IN_PUBLICA = 0      18 registros
IN_PUBLICA = 1   48.933 registros

Total: 48.951 registros
```

Foram encontradas as 27 UFs.

### Situacao

O ano de 2007 possui duas fontes tecnicamente possiveis:

1. resultado ja agregado em `MEDIA_UF_2007.xlsx`;
2. resultado construido a partir de `TS_ESCOLA_2007.csv`.

A fonte definitiva ainda nao foi escolhida porque a decisao depende do conceito de **rede publica** que sera adotado de forma consistente nos demais indicadores.

**Status:** auditado, decisao final pendente.

---

# 4. SAEB 2009

## Arquivos disponiveis

```text
Dicionario_SAEB_2009.xlsx
TS_ESCOLA_2009.csv
MEDIA_UF_2009.xlsx
```

A estrutura e semelhante a encontrada em 2007.

## `MEDIA_UF_2009.xlsx`

Principais campos:

```text
ANO_SAEB
CO_UF
NO_UF
DEPENDENCIA_ADM
LOCALIZACAO
CAPITAL
MEDIA_4_LP
MEDIA_4_MT
MEDIA_8_LP
MEDIA_8_MT
MEDIA_11_LP
MEDIA_11_MT
```

Categorias de rede:

```text
Total - Federal, Estadual, Municipal e Privada
Estadual
Municipal
Privada
Total - Estadual e Municipal
```

Assim como em 2007, nao existe diretamente a categoria:

```text
Total - Federal, Estadual e Municipal
```

---

## `TS_ESCOLA_2009.csv`

Variaveis relevantes:

```text
ID_UF
IN_PUBLICA
ID_LOCALIZACAO

NU_PRESENTES_4EF
NU_PRESENTES_8EF

MEDIA_4EF_LP
MEDIA_4EF_MT
MEDIA_8EF_LP
MEDIA_8EF_MT
```

Resultado da inspecao:

```text
IN_PUBLICA = 0    1.665 registros
IN_PUBLICA = 1   58.682 registros

Total: 60.347 registros
```

As 27 UFs estao presentes.

### Situacao

Assim como em 2007, existem duas possibilidades de fonte.

**Status:** auditado, decisao final pendente.

---

# 5. SAEB 2011

## Arquivos disponiveis

```text
Dicionario_SAEB_2011.xlsx
TS_RESULTADO_UF_2011.csv
```

O arquivo utilizado ja apresenta resultados agregados por Unidade Federativa.

Principais campos:

```text
ID_SAEB
ID_REGIAO
SIGLA_UF
ID_UF
ID_SERIE
ID_TIPO_REDE
ID_LOCALIZACAO
ID_CAPITAL
NU_PARTICIPANTES
MEDIA_LP
MEDIA_MT
ERRO_PADRAO_LP
ERRO_PADRAO_MT
```

## Codigos verificados no dicionario

### Serie

```text
5  = 4ª serie / 5º ano do Ensino Fundamental
9  = 8ª serie / 9º ano do Ensino Fundamental
12 = 3ª serie do Ensino Medio
```

### Tipo de rede

```text
0 = Todas
1 = Federal
2 = Estadual
3 = Municipal
4 = Privada
5 = Publica
```

### Localizacao

```text
0 = Todas
1 = Urbana
2 = Rural
```

### Area

```text
0 = Todas
1 = Capital
2 = Interior
```

## Recorte identificado para o projeto

Para obter o resultado publico total da UF:

```text
ID_TIPO_REDE = 5
ID_LOCALIZACAO = 0
ID_CAPITAL = 0
ID_SERIE = 5 ou 9
```

As proficiencias sao obtidas diretamente de:

```text
MEDIA_LP
MEDIA_MT
```

Como o arquivo ja contem o resultado agregado por UF, nao e necessario reconstruir a media a partir das escolas.

**Status:** auditado.

---

# 6. SAEB 2013

## Arquivo

```text
TS_UF_2013.xlsx
```

Aba utilizada:

```text
UF
```

## Estrutura

A planilha possui cabecalho multinivel.

Estrutura observada:

```text
linha 0 → titulo
linha 1 → observacao metodologica
linha 2 → vazia
linhas 3 a 5 → cabecalhos
linha 6 em diante → dados
```

As dez colunas principais correspondem a:

```text
UF
REDE
LOCALIZACAO
CAPITAL

Lingua Portuguesa - Anos Iniciais
Matematica - Anos Iniciais

Lingua Portuguesa - Anos Finais
Matematica - Anos Finais

Lingua Portuguesa - Ensino Medio
Matematica - Ensino Medio
```

## Observacao metodologica da propria fonte

A planilha informa que:

> celulas em branco significam que nao foi possivel calcular a media para aquele estrato.

Portanto, valores em branco devem continuar sendo tratados como ausentes.

## Categorias encontradas

### Rede

```text
Estadual
Federal
Municipal
Privada
Total - Estadual e Municipal
Total - Federal, Estadual e Municipal
Total - Federal, Estadual, Municipal e Privada
```

### Localizacao

```text
Rural
Total
Urbana
```

### Capital

```text
Capital
Interior
Total
```

Existe diretamente o agregado:

```text
Total - Federal, Estadual e Municipal
```

**Status:** auditado.

---

# 7. SAEB 2015

## Arquivo

```text
TS_UF_2015.xlsx
```

Aba:

```text
UFs
```

## Estrutura

A estrutura e semelhante a de 2013.

Os dados comecam apos cinco linhas de titulo e cabecalho.

Campos analiticos:

```text
UF
REDE
LOCALIZACAO
CAPITAL

LP - Anos Iniciais
MT - Anos Iniciais

LP - Anos Finais
MT - Anos Finais

LP - Ensino Medio
MT - Ensino Medio
```

## Particularidade importante

A fonte informa que:

> celulas com valor 0 significam que nao foi possivel calcular a media para aquele estrato.

Consequentemente:

```text
0 em coluna de proficiencia = proficiencia zero
```

Esses valores deverao ser tratados como ausentes durante a transformacao.

## Categorias encontradas

### Rede

```text
Estadual
Federal
Municipal
Privada
Total - Estadual e Municipal
Total - Federal, Estadual e Municipal
Total - Federal, Estadual, Municipal e Privada
```

### Localizacao

```text
Rural
Total
Urbana
```

### Capital

```text
Capital
Interior
Total
```

**Status:** auditado.

---

# 8. SAEB 2017

## Arquivo

```text
TS_UF_2017.xlsx
```

A estrutura ja esta organizada em formato tabular.

Principais variaveis do projeto:

```text
CO_UF
NO_UF
DEPENDENCIA_ADM
LOCALIZACAO
CAPITAL

MEDIA_5_LP
MEDIA_5_MT
MEDIA_9_LP
MEDIA_9_MT
```

Ha tambem variaveis referentes ao Ensino Medio e aos niveis de proficiencia, que nao fazem parte do recorte atual.

## Categorias de rede

```text
Estadual
Federal
Municipal
Privada
Total - Estadual e Municipal
Total - Federal, Estadual e Municipal
Total - Federal, Estadual, Municipal e Privada
```

### Localizacao

```text
Rural
Total
Urbana
```

### Capital

```text
Capital
Interior
Total
```

**Status:** auditado.

---

# 9. SAEB 2019

## Arquivo

```text
TS_UF_2019.xlsx
```

Aba:

```text
Estados
```

Principais campos:

```text
CO_UF
NO_UF
DEPENDENCIA_ADM
LOCALIZACAO
CAPITAL

MEDIA_5_LP
MEDIA_5_MT
MEDIA_9_LP
MEDIA_9_MT
```

A base tambem possui resultados para:

* 2º ano;
* Ciencias Humanas;
* Ciencias da Natureza;
* Ensino Medio;
* niveis de proficiencia.

Essas variaveis nao integram o recorte atual.

As categorias de rede, localizacao e capital sao compativeis com 2017.

Existe:

```text
Total - Federal, Estadual e Municipal
```

**Status:** auditado.

---

# 10. SAEB 2021

## Arquivo

```text
TS_UF_2021.xlsx
```

Aba:

```text
Estados
```

Estrutura semelhante a de 2019.

Campos relevantes:

```text
CO_UF
NO_UF
DEPENDENCIA_ADM
LOCALIZACAO
CAPITAL

MEDIA_5_LP
MEDIA_5_MT
MEDIA_9_LP
MEDIA_9_MT
```

Tambem esta disponivel:

```text
Total - Federal, Estadual e Municipal
```

**Status:** auditado.

---

# 11. SAEB 2023

## Arquivos

```text
Dicionario_Saeb_2023.xlsx
TS_ESCOLA_2023.csv
```

O arquivo utilizado esta em nivel de escola.

Principais variaveis:

```text
ID_UF
IN_PUBLICA
ID_LOCALIZACAO

NU_PRESENTES_5EF
NU_PRESENTES_9EF

MEDIA_5EF_LP
MEDIA_5EF_MT
MEDIA_9EF_LP
MEDIA_9EF_MT
```

O arquivo possui outras variaveis relativas ao Ensino Medio, que nao integram o recorte do projeto.

## Resultado da inspecao

```text
IN_PUBLICA = 1    70.151 registros
```

Nao foram encontrados registros com `IN_PUBLICA = 0`.

Assim, o arquivo escolar utilizado em 2023 contem somente escolas identificadas como publicas.

### Localizacao

```text
Urbana: 53.756 registros
Rural:  16.395 registros
```

Foram identificadas as 27 UFs.

**Status:** auditado.

---

# 12. Sintese da auditoria

| Ano  | Fonte(s) disponivel(is)                     | Nivel       | Situacao                       |
| ---- | ------------------------------------------- | ----------- | ------------------------------ |
| 2007 | `MEDIA_UF_2007.xlsx` / `TS_ESCOLA_2007.csv` | UF / Escola | Auditada; fonte final pendente |
| 2009 | `MEDIA_UF_2009.xlsx` / `TS_ESCOLA_2009.csv` | UF / Escola | Auditada; fonte final pendente |
| 2011 | `TS_RESULTADO_UF_2011.csv`                  | UF          | Auditada                       |
| 2013 | `TS_UF_2013.xlsx`                           | UF          | Auditada                       |
| 2015 | `TS_UF_2015.xlsx`                           | UF          | Auditada                       |
| 2017 | `TS_UF_2017.xlsx`                           | UF          | Auditada                       |
| 2019 | `TS_UF_2019.xlsx`                           | UF          | Auditada                       |
| 2021 | `TS_UF_2021.xlsx`                           | UF          | Auditada                       |
| 2023 | `TS_ESCOLA_2023.csv`                        | Escola      | Auditada                       |

---

# 13. Questoes metodologicas identificadas

## 13.1 Agregacao de resultados escolares

Quando for necessario construir um resultado estadual a partir de `TS_ESCOLA`, nao devera ser utilizada a media simples das medias das escolas.

Escolas possuem diferentes quantidades de participantes.

A agregacao devera considerar a quantidade de alunos presentes:

```text
media UF =
Σ (media da escola × participantes da escola)
------------------------------------------------
Σ participantes das escolas com media valida
```

Para 2007 e 2009:

```text
Anos Iniciais → NU_PRESENTES_4EF
Anos Finais   → NU_PRESENTES_8EF
```

Para 2023:

```text
Anos Iniciais → NU_PRESENTES_5EF
Anos Finais   → NU_PRESENTES_9EF
```

Registros sem proficiencia valida nao devem participar nem do numerador nem do denominador.

---

## 13.2 Ausencia de resultado

Ausencia de resultado nao deve ser transformada em zero.

Foram encontradas diferentes representacoes:

```text
2013 → celula em branco
2015 → valor 0
TS_ESCOLA → possiveis valores ausentes
```

Cada estrutura devera ser tratada conforme a documentacao correspondente.

---

## 13.3 Estruturas diferentes ao longo da serie

A serie historica nao pode ser tratada como uma unica estrutura de arquivo.

Foram identificados:

### Arquivos escolares

```text
2007
2009
2023
```

### Resultado agregado por UF com codigos

```text
2011
```

### Resultado por UF com cabecalho multinivel

```text
2013
2015
```

### Resultado por UF em estrutura tabular

```text
2017
2019
2021
```

Essas diferencas deverao ser normalizadas somente apos a leitura adequada de cada fonte.

---

# 14. Questao pendente: definicao de rede publica

A auditoria do SAEB identificou diferencas importantes na forma como a rede publica aparece nas fontes.

Em 2013, 2015, 2017, 2019 e 2021 existe diretamente:

```text
Total - Federal, Estadual e Municipal
```

Em 2011 existe:

```text
ID_TIPO_REDE = 5 → Publica
```

Em 2007 e 2009, os arquivos agregados por UF possuem:

```text
Total - Estadual e Municipal
```

mas nao apresentam diretamente:

```text
Total - Federal, Estadual e Municipal
```

Os arquivos `TS_ESCOLA` desses anos permitem, por outro lado, identificar escolas por meio de `IN_PUBLICA`.

A decisao final sobre qual fonte utilizar em 2007 e 2009 sera tomada **somente apos a auditoria de IDEB, Rendimento Escolar e TDI**, para evitar a adocao de conceitos diferentes de rede publica entre os indicadores historicos.

---

# 15. Estrutura padronizada pretendida

Apos a definicao metodologica final, todas as edicoes do SAEB deverao resultar em uma estrutura comum:

```text
ANO
UF
REDE
ETAPA_ENSINO
DISCIPLINA
VALOR
```

Exemplo:

```text
2007 | MG | PUBLICA | ANOS INICIAIS | PORTUGUES  | ...
2007 | MG | PUBLICA | ANOS INICIAIS | MATEMATICA | ...
2007 | MG | PUBLICA | ANOS FINAIS   | PORTUGUES  | ...
2007 | MG | PUBLICA | ANOS FINAIS   | MATEMATICA | ...
```

Essa tabela padronizada sera posteriormente utilizada no modelo analitico e no Power BI.

---

# 16. Conclusao

A auditoria confirmou que existem fontes adequadas para todas as edicoes do SAEB utilizadas no periodo de 2007 a 2023, mas as estruturas e os niveis de agregacao variam entre os anos.

As principais diferencas encontradas foram:

* utilizacao de dados escolares em alguns anos;
* disponibilidade de resultados oficiais por UF em outros;
* mudancas na nomenclatura das etapas;
* alteracoes nos formatos das planilhas;
* diferentes formas de representar a rede publica;
* valores ausentes representados de formas distintas;
* necessidade de ponderacao pela quantidade de participantes quando a agregacao partir de escolas.

A auditoria das fontes do SAEB esta concluida quanto a identificacao de arquivos, estruturas, variaveis e particularidades metodologicas.

Permanece pendente a **decisao final sobre o recorte comum de rede e a fonte definitiva de 2007 e 2009**. Essa decisao sera registrada neste documento apos a auditoria conjunta de IDEB, Rendimento Escolar e TDI.

---

## Historico de atualizacao

| Data       | Alteracao                                              |
| ---------- | ------------------------------------------------------ |
| 18/08/2026 | Primeira versao da auditoria das fontes do SAEB        |
| A definir  | Atualizacao apos definicao do conceito de rede publica |
| A definir  | Registro das fontes definitivas utilizadas no pipeline |
