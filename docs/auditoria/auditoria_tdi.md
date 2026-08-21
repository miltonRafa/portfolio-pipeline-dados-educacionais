# Auditoria das Fontes — Taxa de Distorcao Idade-Serie (TDI)

## 1. Objetivo

Este documento registra a auditoria tecnica das fontes da Taxa de Distorcao Idade-Serie (TDI) utilizadas no projeto.

A auditoria foi realizada antes da implementacao definitiva do pipeline com os objetivos de:

- identificar a estrutura historica dos arquivos;
- verificar a cobertura temporal;
- confirmar a presenca das 27 Unidades da Federacao;
- identificar as categorias de localizacao e dependencia administrativa;
- verificar a disponibilidade do agregado oficial da rede publica;
- confirmar a existencia de resultados consolidados para Anos Iniciais e Anos Finais;
- identificar mudancas de nomenclatura e estrutura entre as diferentes edicoes;
- verificar duplicidades e valores ausentes no recorte pretendido.

O periodo considerado pelo projeto e:

2007–2023

O recorte analitico pretendido considera:

- Ensino Fundamental — Anos Iniciais;
- Ensino Fundamental — Anos Finais;
- nivel geografico de Unidade da Federacao;
- rede publica;
- localizacao total.

---

## 2. Cobertura temporal

Foram identificados 17 arquivos, correspondentes aos anos de 2007 a 2023.

Todos os arquivos apresentaram internamente o ano esperado.

A serie auditada compreende:

2007
2008
2009
2010
2011
2012
2013
2014
2015
2016
2017
2018
2019
2020
2021
2022
2023

---

## 3. Estrutura historica das fontes

A estrutura dos arquivos sofreu alteracoes ao longo da serie.

### 2007–2010

Os arquivos apresentam dimensoes como:

Ano
Regiao
UF
Localizacao
Rede

Nos anos iniciais, os agregados das etapas aparecem associados as denominacoes:

1ª a 4ª Serie / 1º ao 5º Ano
5ª a 8ª Serie / 6º ao 9º Ano

Esses campos correspondem, respectivamente, aos Anos Iniciais e aos Anos Finais do Ensino Fundamental.

### 2011–2014

Os arquivos passam a apresentar de forma mais direta os campos:

1º ao 5º Ano
6º ao 9º Ano

Alem dos resultados por ano escolar.

### 2015

O arquivo apresenta uma mudanca especifica na identificacao geografica, utilizando:

Codigo da UF
Sigla da UF

Para o projeto, a coluna de sigla da UF e a mais adequada para padronizacao geografica.

### 2016

A identificacao geografica passa a utilizar o nome completo da UF.

Tambem ocorre a substituicao da dimensao:

Rede

por:

Dependencia Administrativa

### 2017–2023

Os arquivos passam a reunir em uma mesma planilha:

Brasil
Regioes Geograficas
Unidades da Federacao

Consequentemente, o pipeline devera realizar filtro explicito das 27 UFs.

A partir de 2019, tambem ocorre mudanca nos nomes tecnicos das colunas.

Exemplos:

NU_ANO_CENSO
UNIDGEO
NO_CATEGORIA
NO_DEPENDENCIA
FUN_CAT_0
FUN_AI_CAT_0
FUN_AF_CAT_0

---

## 4. Localizacao

Em todos os anos foram encontradas as categorias:

Rural
Total
Urbana

Para o recorte analitico do projeto sera utilizada:

Localizacao = Total

Dessa forma, os resultados representam a totalidade da UF, sem restricao apenas as areas urbanas ou rurais.

---

## 5. Dependencia administrativa

As fontes apresentam categorias como:

Federal
Estadual
Municipal
Privada / Particular
Publica / Publico
Total

A auditoria confirmou a existencia de uma categoria agregada oficial de rede publica durante toda a serie de 2007 a 2023.

Nos anos mais antigos aparece:

Publico

Nos arquivos posteriores aparece:

Publica

Essa diferenca sera tratada apenas na etapa de padronizacao.

Os arquivos raw permanecerao inalterados.

---

## 6. Cobertura das Unidades da Federacao

Foi verificada a presenca das 27 Unidades da Federacao em todos os anos da serie.

Resultado:

2007–2023:
27 / 27 UFs

Nao foram identificadas UFs ausentes no recorte analisado.

---

## 7. Rede publica e localizacao total

Foi testada especificamente a combinacao:

Rede = Publica
Localizacao = Total

considerando as variacoes textuais:

Publico
Publica

Em todos os 17 anos foram encontrados:

27 / 27 UFs

Nao foram identificadas duplicidades.

Portanto, existe exatamente um registro pertinente ao recorte para cada UF e ano.

---

## 8. Etapas de ensino

A TDI disponibiliza resultados consolidados para:

Anos Iniciais
Anos Finais

Nos arquivos mais antigos, essas etapas aparecem vinculadas as nomenclaturas historicas:

1ª a 4ª Serie / 1º ao 5º Ano

e:

5ª a 8ª Serie / 6º ao 9º Ano

Nos arquivos posteriores, passam a ser apresentadas diretamente como:

Anos Iniciais
Anos Finais

O pipeline devera padronizar essas diferentes denominacoes em uma unica dimensao de etapa de ensino.

---

## 9. Cobertura dos indicadores

Para a combinacao:

27 UFs
Rede Publica
Localizacao Total

foram encontrados resultados validos para as duas etapas em todos os anos entre 2007 e 2023.

Em todos os anos:

Anos Iniciais:
27 valores validos
0 ausentes

Anos Finais:
27 valores validos
0 ausentes

Nao foram identificadas lacunas na serie utilizada pelo projeto.

---

## 10. Duplicidades

Foi verificada a existencia de registros duplicados para a chave logica:

Ano
UF
Rede Publica
Localizacao Total

Resultado:

Nenhuma duplicidade encontrada entre 2007 e 2023.

---

## 11. Valores ausentes

Algumas categorias secundarias das fontes utilizam representacoes como:

--
-

para indicar ausencia ou indisponibilidade de resultados.

Esses valores nao devem ser interpretados como zero.

Na transformacao deverao ser convertidos para valores ausentes.

No recorte efetivamente utilizado pelo projeto:

Rede Publica
Localizacao Total
Anos Iniciais
Anos Finais

nao foram encontrados valores ausentes.

---

## 12. Faixa dos valores

A auditoria tambem verificou os valores minimos e maximos encontrados em cada edicao.

Os resultados permaneceram dentro da escala esperada para uma taxa percentual.

Essa verificacao funcionara futuramente como uma validacao adicional do pipeline.

A regra de qualidade podera considerar:

0 <= TDI <= 100

---

## 13. Ausencia de necessidade de reconstrucao

A propria fonte disponibiliza diretamente os resultados consolidados para:

UF
Rede Publica
Localizacao Total
Anos Iniciais
Anos Finais

Portanto, nao sera necessario:

- agregar municipios;
- agregar escolas;
- calcular medias das series individuais;
- reconstruir a rede publica a partir de Federal, Estadual e Municipal.

O pipeline utilizara diretamente o agregado oficial disponibilizado pela fonte.

---

## 14. Estrutura padronizada pretendida

A tabela final da TDI podera adotar a seguinte estrutura:

ANO
UF
REDE
ETAPA_ENSINO
VALOR

Exemplo:

2007 | AC | PUBLICA | ANOS_INICIAIS | ...
2007 | AC | PUBLICA | ANOS_FINAIS   | ...
2007 | AL | PUBLICA | ANOS_INICIAIS | ...
2007 | AL | PUBLICA | ANOS_FINAIS   | ...

Considerando:

17 anos × 27 UFs × 2 etapas

a tabela completa devera possuir:

918 registros

caso o recorte definitivo permaneca inalterado.

---

## 15. Regras preliminares para o pipeline

A auditoria indica as seguintes regras futuras:

1. Identificar e validar o ano interno de cada arquivo.
2. Reconhecer as diferentes estruturas historicas.
3. Identificar corretamente a coluna geografica utilizada em cada edicao.
4. Padronizar siglas e nomes completos das UFs.
5. Selecionar somente as 27 Unidades da Federacao.
6. Excluir Brasil e regioes geograficas quando presentes.
7. Selecionar Localizacao = Total.
8. Selecionar Rede = Publica.
9. Normalizar Publico/Publica.
10. Utilizar diretamente os agregados de Anos Iniciais e Anos Finais.
11. Converter "-" e "--" em valores ausentes.
12. Transformar os dados para formato longo.
13. Validar presenca das 27 UFs.
14. Validar ausencia de duplicidades.
15. Validar ausencia de valores ausentes no recorte esperado.
16. Validar que os valores estejam entre 0 e 100.

Essas regras somente serao incorporadas ao pipeline produtivo apos a conclusao das auditorias restantes.

---

## 16. Avisos tecnicos de leitura

Alguns arquivos XLSX geraram o aviso do openpyxl:

Cannot parse header or footer so it will be ignored

O aviso esta relacionado aos metadados de impressao das planilhas e nao impediu a leitura das tabelas.

Os dados, dimensoes e valores utilizados pela auditoria foram carregados normalmente.

---

## 17. Conclusao

A auditoria confirmou que as fontes da Taxa de Distorcao Idade-Serie sao adequadas para a serie historica proposta pelo projeto.

Entre 2007 e 2023 existe cobertura completa das 27 Unidades da Federacao para:

- rede publica;
- localizacao total;
- Anos Iniciais;
- Anos Finais.

Nao foram identificadas duplicidades nem valores ausentes no recorte utilizado.

Tambem nao sera necessario reconstruir o agregado publico nem calcular resultados a partir de niveis geograficos ou series individuais.

A auditoria estrutural da TDI esta, portanto, concluida.

Permanece pendente apenas a definicao metodologica transversal do conceito de rede publica, que sera consolidada apos a auditoria dos demais indicadores.

---

## Historico de atualizacao

| Data | Alteracao |
|---|---|
| 18/08/2026 | Primeira versao da auditoria tecnica |
| 18/08/2026 | Confirmada cobertura das 27 UFs entre 2007 e 2023 |
| 18/08/2026 | Confirmado agregado oficial da rede publica |
| 18/08/2026 | Confirmada cobertura completa de Anos Iniciais e Anos Finais |
| 18/08/2026 | Confirmada ausencia de duplicidades e valores ausentes |
| A definir | Atualizacao apos definicao metodologica conjunta da rede publica |