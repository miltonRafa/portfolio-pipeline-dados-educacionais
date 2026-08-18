# Auditoria das Fontes — Rendimento Escolar

## 1. Objetivo

Este documento registra a auditoria técnica das fontes de Taxas de Rendimento Escolar utilizadas no projeto.

A auditoria foi realizada antes da implementação das regras definitivas do pipeline, com os objetivos de:

- identificar a estrutura dos arquivos oficiais;
- verificar a cobertura temporal;
- confirmar a presença das 27 Unidades da Federação;
- identificar as categorias de localização e dependência administrativa;
- verificar a disponibilidade da rede pública agregada;
- confirmar a existência das taxas de aprovação, reprovação e abandono;
- verificar a disponibilidade dos resultados para Anos Iniciais e Anos Finais;
- validar a consistência matemática das taxas;
- identificar alterações estruturais ocorridas entre as diferentes edições.

O período utilizado pelo projeto é:

2007–2023

O recorte considera:

- Ensino Fundamental — Anos Iniciais;
- Ensino Fundamental — Anos Finais;
- nível geográfico de Unidade da Federação;
- rede pública;
- localização total.

---

## 2. Organização dos arquivos

Foram identificados 17 arquivos, correspondentes aos anos de 2007 a 2023.

Os arquivos originais foram mantidos em:

data/raw/rendimento/

Para facilitar a identificação no repositório, o ano de referência foi acrescentado localmente aos nomes dos arquivos quando necessário.

Essa nomenclatura local não é utilizada como única fonte para determinação do período. Durante a auditoria, o ano indicado no nome de cada arquivo foi confrontado com o ano existente internamente nos dados.

Todos os 17 arquivos passaram nessa validação.

---

## 3. Particularidade do arquivo de 2008

Foi identificada uma inconsistência de metadado no arquivo correspondente a 2008.

O conteúdo interno identifica corretamente:

Taxas de Rendimento por Unidades da Federação - 2008

e os registros possuem:

Ano = 2008

Entretanto, o nome da aba é:

Rendimento por UF - 2009

Como o conteúdo interno confirma inequivocamente o ano de 2008, o arquivo será tratado como fonte de 2008.

O arquivo bruto não será alterado.

---

## 4. Cobertura temporal

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

Todos os arquivos apresentaram internamente exclusivamente o ano esperado segundo a organização local.

---

## 5. Mudanças estruturais

A auditoria identificou alterações na estrutura das planilhas ao longo da série.

### 2007

O arquivo apresenta dimensões como:

Ano
Região
UF
Localização
Rede

### 2008–2015

A estrutura passa a utilizar principalmente:

Ano
UF
Localização
Rede

### 2016

A fonte apresenta novamente a informação regional e utiliza:

Ano
Região
UF
Localização
Dependência Administrativa

### 2017–2023

Os arquivos passam a reunir:

Brasil
Regiões Geográficas
Unidades da Federação

no mesmo conjunto de dados.

Consequentemente, o pipeline deverá selecionar explicitamente apenas as 27 UFs.

---

## 6. Mudanças de nomenclatura

Foram identificadas variações textuais nas categorias de rede.

Nos anos mais antigos aparecem formas como:

Publico
Particular

Em outros períodos aparecem:

Pública
Privada

Também ocorre mudança do nome da dimensão:

Rede

para:

Dependência Administrativa

Essas diferenças serão padronizadas apenas na etapa de transformação.

Os arquivos raw permanecerão inalterados.

---

## 7. Localização

Em todos os 17 anos foram encontradas as categorias:

Rural
Total
Urbana

Para o objetivo analítico do projeto será utilizada:

Localização = Total

Dessa forma, o indicador representa o conjunto da UF sem restringir os resultados às áreas urbana ou rural.

---

## 8. Dependência administrativa

As fontes disponibilizam categorias como:

Federal
Estadual
Municipal
Pública / Publico
Privada / Particular
Total

A auditoria confirmou que a categoria agregada de rede pública está disponível diretamente na fonte durante toda a série histórica.

Assim, não será necessário reconstruir a rede pública por meio da combinação de:

Federal + Estadual + Municipal

---

## 9. Cobertura das Unidades da Federação

Foi verificada a presença das 27 UFs em todos os anos.

Resultado:

2007–2023:
27 / 27 UFs

Não foram identificadas UFs ausentes no recorte analisado.

---

## 10. Rede pública e localização total

Foi realizada uma verificação específica da combinação:

Rede = Pública
Localização = Total

considerando variações textuais como:

Publico
Pública

Em todos os anos foram encontrados:

27 / 27 UFs

Não foram identificadas duplicidades nessa combinação.

Portanto, existe exatamente um agregado público estadual pertinente ao projeto para cada UF e ano.

---

## 11. Indicadores utilizados

As fontes apresentam três componentes de rendimento:

Aprovação
Reprovação
Abandono

Para cada um deles existem resultados consolidados para:

Anos Iniciais
Anos Finais

O projeto utilizará, portanto, seis medidas por UF e ano:

Aprovação × Anos Iniciais
Aprovação × Anos Finais
Reprovação × Anos Iniciais
Reprovação × Anos Finais
Abandono × Anos Iniciais
Abandono × Anos Finais

---

## 12. Cobertura das medidas

A auditoria confirmou que, para a combinação:

27 UFs
Rede Pública
Localização Total

os seis indicadores possuem cobertura completa entre 2007 e 2023.

Em todos os anos:

Aprovação — Anos Iniciais: 27 válidos / 0 ausentes
Aprovação — Anos Finais: 27 válidos / 0 ausentes

Reprovação — Anos Iniciais: 27 válidos / 0 ausentes
Reprovação — Anos Finais: 27 válidos / 0 ausentes

Abandono — Anos Iniciais: 27 válidos / 0 ausentes
Abandono — Anos Finais: 27 válidos / 0 ausentes

---

## 13. Validação matemática

Foi aplicada a seguinte verificação para cada UF, ano e etapa:

Aprovação + Reprovação + Abandono ≈ 100

A tolerância definida para a auditoria foi de:

0,2 ponto percentual

Resultado para todos os anos entre 2007 e 2023:

Anos Iniciais:
maior desvio = 0,00

Anos Finais:
maior desvio = 0,00

Registros fora da tolerância:

0

A consistência interna das três taxas foi, portanto, confirmada em toda a série auditada.

---

## 14. Ausência de necessidade de reconstrução

Como a própria fonte disponibiliza os resultados consolidados de:

UF
Rede Pública
Localização Total
Anos Iniciais
Anos Finais

não será necessário:

- agregar municípios;
- calcular médias entre UFs ou municípios;
- combinar Federal, Estadual e Municipal;
- reconstruir taxas a partir de séries individuais.

O pipeline deverá utilizar diretamente os agregados oficiais disponibilizados pelo Inep.

---

## 15. Valores ausentes

As fontes utilizam representações como:

--
-

para determinados valores indisponíveis em outras categorias e níveis de desagregação.

Esses valores não devem ser convertidos para zero.

Na transformação deverão ser tratados como valores ausentes.

No recorte efetivamente utilizado pelo projeto — rede pública, localização total, Anos Iniciais e Anos Finais — não foram encontrados valores ausentes nas seis medidas auditadas.

---

## 16. Estrutura padronizada pretendida

A tabela final de Rendimento Escolar poderá adotar estrutura longa:

ANO
UF
REDE
ETAPA_ENSINO
INDICADOR
VALOR

Exemplo:

2007 | AC | PUBLICA | ANOS_INICIAIS | APROVACAO  | ...
2007 | AC | PUBLICA | ANOS_INICIAIS | REPROVACAO | ...
2007 | AC | PUBLICA | ANOS_INICIAIS | ABANDONO   | ...
2007 | AC | PUBLICA | ANOS_FINAIS   | APROVACAO  | ...

Considerando:

17 anos × 27 UFs × 2 etapas × 3 indicadores

a tabela completa deverá possuir:

2.754 registros

caso as regras definitivas mantenham esse recorte.

---

## 17. Regras preliminares para o pipeline

A auditoria indica as seguintes regras futuras:

1. Identificar o ano interno de cada arquivo.
2. Validar o ano contra a organização local.
3. Reconhecer as diferentes estruturas históricas.
4. Selecionar somente as 27 UFs.
5. Excluir Brasil e regiões quando presentes.
6. Selecionar Localização = Total.
7. Selecionar Rede = Pública, normalizando Publico/Pública.
8. Utilizar os agregados de Anos Iniciais e Anos Finais.
9. Selecionar Aprovação, Reprovação e Abandono.
10. Converter "-" e "--" em valores ausentes.
11. Transformar os dados para formato longo.
12. Validar ausência de duplicidades.
13. Validar presença das 27 UFs.
14. Validar Aprovação + Reprovação + Abandono = 100 dentro da tolerância estabelecida.

Essas regras somente serão incorporadas ao pipeline produtivo após a conclusão das demais auditorias.

---

## 18. Conclusão

A auditoria confirmou que as fontes de Rendimento Escolar são adequadas para a série histórica proposta pelo projeto.

Entre 2007 e 2023 existe cobertura integral das 27 Unidades da Federação para:

- rede pública;
- localização total;
- Anos Iniciais;
- Anos Finais;
- aprovação;
- reprovação;
- abandono.

Não há necessidade de reconstruir o agregado público nem de calcular as taxas a partir de níveis geográficos inferiores.

A validação matemática confirmou ainda que:

Aprovação + Reprovação + Abandono = 100

em todos os registros auditados do recorte.

A auditoria estrutural do Rendimento Escolar está, portanto, concluída.

Permanece pendente apenas a decisão metodológica transversal sobre o conceito de rede pública, que será consolidada após a auditoria dos demais indicadores.

---

## Histórico de atualização

| Data | Alteração |
|---|---|
| 18/08/2026 | Primeira versão da auditoria técnica |
| 18/08/2026 | Confirmada cobertura das 27 UFs entre 2007 e 2023 |
| 18/08/2026 | Confirmada cobertura integral das seis medidas |
| 18/08/2026 | Validada a soma Aprovação + Reprovação + Abandono |
| A definir | Atualização após definição metodológica conjunta da rede pública |