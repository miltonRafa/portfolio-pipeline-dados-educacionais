# Auditoria das Fontes — SAEB

## 1. Objetivo

Este documento registra a auditoria técnica das fontes do **Sistema de Avaliação da Educação Básica (SAEB)** utilizadas no projeto.

A auditoria foi realizada antes da definição final das regras de transformação do pipeline, com o objetivo de identificar diferenças entre os arquivos disponibilizados ao longo dos anos e evitar a aplicação de um tratamento uniforme sobre estruturas distintas.

Foram analisadas as edições de:

**2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021 e 2023.**

O projeto utiliza somente:

* Ensino Fundamental — Anos Iniciais;
* Ensino Fundamental — Anos Finais;
* Língua Portuguesa;
* Matemática;
* resultados em nível de Unidade Federativa (UF).

> **Status deste documento:** provisório. Algumas decisões sobre a fonte definitiva e o conceito de rede pública serão atualizadas após a auditoria dos demais indicadores do projeto, especialmente IDEB, Rendimento Escolar e TDI.

---

## 2. Princípios adotados na auditoria

A análise das fontes seguiu os seguintes princípios:

1. preservar os arquivos originais na camada `raw`;
2. identificar o nível original de cada fonte;
3. verificar se o resultado já é disponibilizado por UF ou precisa ser calculado;
4. identificar as categorias de rede disponíveis em cada edição;
5. verificar as variáveis utilizadas nas médias de Língua Portuguesa e Matemática;
6. identificar a quantidade de participantes quando necessária para agregação;
7. não interpretar valores ausentes como zero;
8. registrar diferenças estruturais entre as edições;
9. evitar reconstruir um indicador quando existir resultado oficial agregado adequado;
10. adiar decisões que dependam da consistência com outros indicadores.

---

# 3. SAEB 2007

## Arquivos disponíveis

```text
Dicionario_SAEB_2007.xlsx
TS_ESCOLA_2007.csv
MEDIA_UF_2007.xlsx
```

## `MEDIA_UF_2007.xlsx`

O arquivo apresenta resultados já agregados por Unidade Federativa.

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

Não foi encontrada nesse arquivo uma categoria denominada:

```text
Total - Federal, Estadual e Municipal
```

Portanto, o agregado público disponível diretamente no arquivo de UF corresponde a **Estadual + Municipal**, enquanto o outro total inclui também a rede privada.

---

## `TS_ESCOLA_2007.csv`

O arquivo contém registros em nível de escola.

Variáveis relevantes:

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

O dicionário identifica:

* `ID_UF`: código da Unidade Federativa;
* `IN_PUBLICA`: indicador de escola pública;
* `NU_PRESENTES_4EF`: alunos presentes na avaliação da etapa correspondente;
* `NU_PRESENTES_8EF`: alunos presentes na avaliação da etapa correspondente;
* `MEDIA_*`: proficiência média dos participantes.

A inspeção do arquivo encontrou:

```text
IN_PUBLICA = 0      18 registros
IN_PUBLICA = 1   48.933 registros

Total: 48.951 registros
```

Foram encontradas as 27 UFs.

### Situação

O ano de 2007 possui duas fontes tecnicamente possíveis:

1. resultado já agregado em `MEDIA_UF_2007.xlsx`;
2. resultado construído a partir de `TS_ESCOLA_2007.csv`.

A fonte definitiva ainda não foi escolhida porque a decisão depende do conceito de **rede pública** que será adotado de forma consistente nos demais indicadores.

**Status:** auditado, decisão final pendente.

---

# 4. SAEB 2009

## Arquivos disponíveis

```text
Dicionario_SAEB_2009.xlsx
TS_ESCOLA_2009.csv
MEDIA_UF_2009.xlsx
```

A estrutura é semelhante à encontrada em 2007.

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

Assim como em 2007, não existe diretamente a categoria:

```text
Total - Federal, Estadual e Municipal
```

---

## `TS_ESCOLA_2009.csv`

Variáveis relevantes:

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

Resultado da inspeção:

```text
IN_PUBLICA = 0    1.665 registros
IN_PUBLICA = 1   58.682 registros

Total: 60.347 registros
```

As 27 UFs estão presentes.

### Situação

Assim como em 2007, existem duas possibilidades de fonte.

**Status:** auditado, decisão final pendente.

---

# 5. SAEB 2011

## Arquivos disponíveis

```text
Dicionario_SAEB_2011.xlsx
TS_RESULTADO_UF_2011.csv
```

O arquivo utilizado já apresenta resultados agregados por Unidade Federativa.

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

## Códigos verificados no dicionário

### Série

```text
5  = 4ª série / 5º ano do Ensino Fundamental
9  = 8ª série / 9º ano do Ensino Fundamental
12 = 3ª série do Ensino Médio
```

### Tipo de rede

```text
0 = Todas
1 = Federal
2 = Estadual
3 = Municipal
4 = Privada
5 = Pública
```

### Localização

```text
0 = Todas
1 = Urbana
2 = Rural
```

### Área

```text
0 = Todas
1 = Capital
2 = Interior
```

## Recorte identificado para o projeto

Para obter o resultado público total da UF:

```text
ID_TIPO_REDE = 5
ID_LOCALIZACAO = 0
ID_CAPITAL = 0
ID_SERIE = 5 ou 9
```

As proficiências são obtidas diretamente de:

```text
MEDIA_LP
MEDIA_MT
```

Como o arquivo já contém o resultado agregado por UF, não é necessário reconstruir a média a partir das escolas.

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

A planilha possui cabeçalho multinível.

Estrutura observada:

```text
linha 0 → título
linha 1 → observação metodológica
linha 2 → vazia
linhas 3 a 5 → cabeçalhos
linha 6 em diante → dados
```

As dez colunas principais correspondem a:

```text
UF
REDE
LOCALIZACAO
CAPITAL

Língua Portuguesa - Anos Iniciais
Matemática - Anos Iniciais

Língua Portuguesa - Anos Finais
Matemática - Anos Finais

Língua Portuguesa - Ensino Médio
Matemática - Ensino Médio
```

## Observação metodológica da própria fonte

A planilha informa que:

> células em branco significam que não foi possível calcular a média para aquele estrato.

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

### Localização

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

A estrutura é semelhante à de 2013.

Os dados começam após cinco linhas de título e cabeçalho.

Campos analíticos:

```text
UF
REDE
LOCALIZACAO
CAPITAL

LP - Anos Iniciais
MT - Anos Iniciais

LP - Anos Finais
MT - Anos Finais

LP - Ensino Médio
MT - Ensino Médio
```

## Particularidade importante

A fonte informa que:

> células com valor 0 significam que não foi possível calcular a média para aquele estrato.

Consequentemente:

```text
0 em coluna de proficiência ≠ proficiência zero
```

Esses valores deverão ser tratados como ausentes durante a transformação.

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

### Localização

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

A estrutura já está organizada em formato tabular.

Principais variáveis do projeto:

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

Há também variáveis referentes ao Ensino Médio e aos níveis de proficiência, que não fazem parte do recorte atual.

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

### Localização

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

A base também possui resultados para:

* 2º ano;
* Ciências Humanas;
* Ciências da Natureza;
* Ensino Médio;
* níveis de proficiência.

Essas variáveis não integram o recorte atual.

As categorias de rede, localização e capital são compatíveis com 2017.

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

Estrutura semelhante à de 2019.

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

Também está disponível:

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

O arquivo utilizado está em nível de escola.

Principais variáveis:

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

O arquivo possui outras variáveis relativas ao Ensino Médio, que não integram o recorte do projeto.

## Resultado da inspeção

```text
IN_PUBLICA = 1    70.151 registros
```

Não foram encontrados registros com `IN_PUBLICA = 0`.

Assim, o arquivo escolar utilizado em 2023 contém somente escolas identificadas como públicas.

### Localização

```text
Urbana: 53.756 registros
Rural:  16.395 registros
```

Foram identificadas as 27 UFs.

**Status:** auditado.

---

# 12. Síntese da auditoria

| Ano  | Fonte(s) disponível(is)                     | Nível       | Situação                       |
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

# 13. Questões metodológicas identificadas

## 13.1 Agregação de resultados escolares

Quando for necessário construir um resultado estadual a partir de `TS_ESCOLA`, não deverá ser utilizada a média simples das médias das escolas.

Escolas possuem diferentes quantidades de participantes.

A agregação deverá considerar a quantidade de alunos presentes:

```text
média UF =
Σ (média da escola × participantes da escola)
------------------------------------------------
Σ participantes das escolas com média válida
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

Registros sem proficiência válida não devem participar nem do numerador nem do denominador.

---

## 13.2 Ausência de resultado

Ausência de resultado não deve ser transformada em zero.

Foram encontradas diferentes representações:

```text
2013 → célula em branco
2015 → valor 0
TS_ESCOLA → possíveis valores ausentes
```

Cada estrutura deverá ser tratada conforme a documentação correspondente.

---

## 13.3 Estruturas diferentes ao longo da série

A série histórica não pode ser tratada como uma única estrutura de arquivo.

Foram identificados:

### Arquivos escolares

```text
2007
2009
2023
```

### Resultado agregado por UF com códigos

```text
2011
```

### Resultado por UF com cabeçalho multinível

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

Essas diferenças deverão ser normalizadas somente após a leitura adequada de cada fonte.

---

# 14. Questão pendente: definição de rede pública

A auditoria do SAEB identificou diferenças importantes na forma como a rede pública aparece nas fontes.

Em 2013, 2015, 2017, 2019 e 2021 existe diretamente:

```text
Total - Federal, Estadual e Municipal
```

Em 2011 existe:

```text
ID_TIPO_REDE = 5 → Pública
```

Em 2007 e 2009, os arquivos agregados por UF possuem:

```text
Total - Estadual e Municipal
```

mas não apresentam diretamente:

```text
Total - Federal, Estadual e Municipal
```

Os arquivos `TS_ESCOLA` desses anos permitem, por outro lado, identificar escolas por meio de `IN_PUBLICA`.

A decisão final sobre qual fonte utilizar em 2007 e 2009 será tomada **somente após a auditoria de IDEB, Rendimento Escolar e TDI**, para evitar a adoção de conceitos diferentes de rede pública entre os indicadores históricos.

---

# 15. Estrutura padronizada pretendida

Após a definição metodológica final, todas as edições do SAEB deverão resultar em uma estrutura comum:

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
2007 | MG | PUBLICA | ANOS INICIAIS | PORTUGUÊS  | ...
2007 | MG | PUBLICA | ANOS INICIAIS | MATEMÁTICA | ...
2007 | MG | PUBLICA | ANOS FINAIS   | PORTUGUÊS  | ...
2007 | MG | PUBLICA | ANOS FINAIS   | MATEMÁTICA | ...
```

Essa tabela padronizada será posteriormente utilizada no modelo analítico e no Power BI.

---

# 16. Conclusão

A auditoria confirmou que existem fontes adequadas para todas as edições do SAEB utilizadas no período de 2007 a 2023, mas as estruturas e os níveis de agregação variam entre os anos.

As principais diferenças encontradas foram:

* utilização de dados escolares em alguns anos;
* disponibilidade de resultados oficiais por UF em outros;
* mudanças na nomenclatura das etapas;
* alterações nos formatos das planilhas;
* diferentes formas de representar a rede pública;
* valores ausentes representados de formas distintas;
* necessidade de ponderação pela quantidade de participantes quando a agregação partir de escolas.

A auditoria das fontes do SAEB está concluída quanto à identificação de arquivos, estruturas, variáveis e particularidades metodológicas.

Permanece pendente a **decisão final sobre o recorte comum de rede e a fonte definitiva de 2007 e 2009**. Essa decisão será registrada neste documento após a auditoria conjunta de IDEB, Rendimento Escolar e TDI.

---

## Histórico de atualização

| Data       | Alteração                                              |
| ---------- | ------------------------------------------------------ |
| 18/08/2026 | Primeira versão da auditoria das fontes do SAEB        |
| A definir  | Atualização após definição do conceito de rede pública |
| A definir  | Registro das fontes definitivas utilizadas no pipeline |
