# Auditoria das Fontes — Taxa de Distorção Idade-Série (TDI)

## 1. Objetivo

Este documento registra a auditoria técnica das fontes da Taxa de Distorção Idade-Série (TDI) utilizadas no projeto.

A auditoria foi realizada antes da implementação definitiva do pipeline com os objetivos de:

- identificar a estrutura histórica dos arquivos;
- verificar a cobertura temporal;
- confirmar a presença das 27 Unidades da Federação;
- identificar as categorias de localização e dependência administrativa;
- verificar a disponibilidade do agregado oficial da rede pública;
- confirmar a existência de resultados consolidados para Anos Iniciais e Anos Finais;
- identificar mudanças de nomenclatura e estrutura entre as diferentes edições;
- verificar duplicidades e valores ausentes no recorte pretendido.

O período considerado pelo projeto é:

2007–2023

O recorte analítico pretendido considera:

- Ensino Fundamental — Anos Iniciais;
- Ensino Fundamental — Anos Finais;
- nível geográfico de Unidade da Federação;
- rede pública;
- localização total.

---

## 2. Cobertura temporal

Foram identificados 17 arquivos, correspondentes aos anos de 2007 a 2023.

Todos os arquivos apresentaram internamente o ano esperado.

A série auditada compreende:

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

## 3. Estrutura histórica das fontes

A estrutura dos arquivos sofreu alterações ao longo da série.

### 2007–2010

Os arquivos apresentam dimensões como:

Ano
Região
UF
Localização
Rede

Nos anos iniciais, os agregados das etapas aparecem associados às denominações:

1ª a 4ª Série / 1º ao 5º Ano
5ª a 8ª Série / 6º ao 9º Ano

Esses campos correspondem, respectivamente, aos Anos Iniciais e aos Anos Finais do Ensino Fundamental.

### 2011–2014

Os arquivos passam a apresentar de forma mais direta os campos:

1º ao 5º Ano
6º ao 9º Ano

Além dos resultados por ano escolar.

### 2015

O arquivo apresenta uma mudança específica na identificação geográfica, utilizando:

Código da UF
Sigla da UF

Para o projeto, a coluna de sigla da UF é a mais adequada para padronização geográfica.

### 2016

A identificação geográfica passa a utilizar o nome completo da UF.

Também ocorre a substituição da dimensão:

Rede

por:

Dependência Administrativa

### 2017–2023

Os arquivos passam a reunir em uma mesma planilha:

Brasil
Regiões Geográficas
Unidades da Federação

Consequentemente, o pipeline deverá realizar filtro explícito das 27 UFs.

A partir de 2019, também ocorre mudança nos nomes técnicos das colunas.

Exemplos:

NU_ANO_CENSO
UNIDGEO
NO_CATEGORIA
NO_DEPENDENCIA
FUN_CAT_0
FUN_AI_CAT_0
FUN_AF_CAT_0

---

## 4. Localização

Em todos os anos foram encontradas as categorias:

Rural
Total
Urbana

Para o recorte analítico do projeto será utilizada:

Localização = Total

Dessa forma, os resultados representam a totalidade da UF, sem restrição apenas às áreas urbanas ou rurais.

---

## 5. Dependência administrativa

As fontes apresentam categorias como:

Federal
Estadual
Municipal
Privada / Particular
Pública / Publico
Total

A auditoria confirmou a existência de uma categoria agregada oficial de rede pública durante toda a série de 2007 a 2023.

Nos anos mais antigos aparece:

Publico

Nos arquivos posteriores aparece:

Pública

Essa diferença será tratada apenas na etapa de padronização.

Os arquivos raw permanecerão inalterados.

---

## 6. Cobertura das Unidades da Federação

Foi verificada a presença das 27 Unidades da Federação em todos os anos da série.

Resultado:

2007–2023:
27 / 27 UFs

Não foram identificadas UFs ausentes no recorte analisado.

---

## 7. Rede pública e localização total

Foi testada especificamente a combinação:

Rede = Pública
Localização = Total

considerando as variações textuais:

Publico
Pública

Em todos os 17 anos foram encontrados:

27 / 27 UFs

Não foram identificadas duplicidades.

Portanto, existe exatamente um registro pertinente ao recorte para cada UF e ano.

---

## 8. Etapas de ensino

A TDI disponibiliza resultados consolidados para:

Anos Iniciais
Anos Finais

Nos arquivos mais antigos, essas etapas aparecem vinculadas às nomenclaturas históricas:

1ª a 4ª Série / 1º ao 5º Ano

e:

5ª a 8ª Série / 6º ao 9º Ano

Nos arquivos posteriores, passam a ser apresentadas diretamente como:

Anos Iniciais
Anos Finais

O pipeline deverá padronizar essas diferentes denominações em uma única dimensão de etapa de ensino.

---

## 9. Cobertura dos indicadores

Para a combinação:

27 UFs
Rede Pública
Localização Total

foram encontrados resultados válidos para as duas etapas em todos os anos entre 2007 e 2023.

Em todos os anos:

Anos Iniciais:
27 valores válidos
0 ausentes

Anos Finais:
27 valores válidos
0 ausentes

Não foram identificadas lacunas na série utilizada pelo projeto.

---

## 10. Duplicidades

Foi verificada a existência de registros duplicados para a chave lógica:

Ano
UF
Rede Pública
Localização Total

Resultado:

Nenhuma duplicidade encontrada entre 2007 e 2023.

---

## 11. Valores ausentes

Algumas categorias secundárias das fontes utilizam representações como:

--
-

para indicar ausência ou indisponibilidade de resultados.

Esses valores não devem ser interpretados como zero.

Na transformação deverão ser convertidos para valores ausentes.

No recorte efetivamente utilizado pelo projeto:

Rede Pública
Localização Total
Anos Iniciais
Anos Finais

não foram encontrados valores ausentes.

---

## 12. Faixa dos valores

A auditoria também verificou os valores mínimos e máximos encontrados em cada edição.

Os resultados permaneceram dentro da escala esperada para uma taxa percentual.

Essa verificação funcionará futuramente como uma validação adicional do pipeline.

A regra de qualidade poderá considerar:

0 <= TDI <= 100

---

## 13. Ausência de necessidade de reconstrução

A própria fonte disponibiliza diretamente os resultados consolidados para:

UF
Rede Pública
Localização Total
Anos Iniciais
Anos Finais

Portanto, não será necessário:

- agregar municípios;
- agregar escolas;
- calcular médias das séries individuais;
- reconstruir a rede pública a partir de Federal, Estadual e Municipal.

O pipeline utilizará diretamente o agregado oficial disponibilizado pela fonte.

---

## 14. Estrutura padronizada pretendida

A tabela final da TDI poderá adotar a seguinte estrutura:

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

a tabela completa deverá possuir:

918 registros

caso o recorte definitivo permaneça inalterado.

---

## 15. Regras preliminares para o pipeline

A auditoria indica as seguintes regras futuras:

1. Identificar e validar o ano interno de cada arquivo.
2. Reconhecer as diferentes estruturas históricas.
3. Identificar corretamente a coluna geográfica utilizada em cada edição.
4. Padronizar siglas e nomes completos das UFs.
5. Selecionar somente as 27 Unidades da Federação.
6. Excluir Brasil e regiões geográficas quando presentes.
7. Selecionar Localização = Total.
8. Selecionar Rede = Pública.
9. Normalizar Publico/Pública.
10. Utilizar diretamente os agregados de Anos Iniciais e Anos Finais.
11. Converter "-" e "--" em valores ausentes.
12. Transformar os dados para formato longo.
13. Validar presença das 27 UFs.
14. Validar ausência de duplicidades.
15. Validar ausência de valores ausentes no recorte esperado.
16. Validar que os valores estejam entre 0 e 100.

Essas regras somente serão incorporadas ao pipeline produtivo após a conclusão das auditorias restantes.

---

## 16. Avisos técnicos de leitura

Alguns arquivos XLSX geraram o aviso do openpyxl:

Cannot parse header or footer so it will be ignored

O aviso está relacionado aos metadados de impressão das planilhas e não impediu a leitura das tabelas.

Os dados, dimensões e valores utilizados pela auditoria foram carregados normalmente.

---

## 17. Conclusão

A auditoria confirmou que as fontes da Taxa de Distorção Idade-Série são adequadas para a série histórica proposta pelo projeto.

Entre 2007 e 2023 existe cobertura completa das 27 Unidades da Federação para:

- rede pública;
- localização total;
- Anos Iniciais;
- Anos Finais.

Não foram identificadas duplicidades nem valores ausentes no recorte utilizado.

Também não será necessário reconstruir o agregado público nem calcular resultados a partir de níveis geográficos ou séries individuais.

A auditoria estrutural da TDI está, portanto, concluída.

Permanece pendente apenas a definição metodológica transversal do conceito de rede pública, que será consolidada após a auditoria dos demais indicadores.

---

## Histórico de atualização

| Data | Alteração |
|---|---|
| 18/08/2026 | Primeira versão da auditoria técnica |
| 18/08/2026 | Confirmada cobertura das 27 UFs entre 2007 e 2023 |
| 18/08/2026 | Confirmado agregado oficial da rede pública |
| 18/08/2026 | Confirmada cobertura completa de Anos Iniciais e Anos Finais |
| 18/08/2026 | Confirmada ausência de duplicidades e valores ausentes |
| A definir | Atualização após definição metodológica conjunta da rede pública |