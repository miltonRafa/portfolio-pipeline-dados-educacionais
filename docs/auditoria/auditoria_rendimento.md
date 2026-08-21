# Auditoria das Fontes — Rendimento Escolar

## 1. Objetivo

Este documento registra a auditoria tecnica das fontes de Taxas de Rendimento Escolar utilizadas no projeto.

A auditoria foi realizada antes da implementacao das regras definitivas do pipeline, com os objetivos de:

- identificar a estrutura dos arquivos oficiais;
- verificar a cobertura temporal;
- confirmar a presenca das 27 Unidades da Federacao;
- identificar as categorias de localizacao e dependencia administrativa;
- verificar a disponibilidade da rede publica agregada;
- confirmar a existencia das taxas de aprovacao, reprovacao e abandono;
- verificar a disponibilidade dos resultados para Anos Iniciais e Anos Finais;
- validar a consistencia matematica das taxas;
- identificar alteracoes estruturais ocorridas entre as diferentes edicoes.

O periodo utilizado pelo projeto e:

2007–2023

O recorte considera:

- Ensino Fundamental — Anos Iniciais;
- Ensino Fundamental — Anos Finais;
- nivel geografico de Unidade da Federacao;
- rede publica;
- localizacao total.

---

## 2. Organizacao dos arquivos

Foram identificados 17 arquivos, correspondentes aos anos de 2007 a 2023.

Os arquivos originais foram mantidos em:

data/raw/rendimento/

Para facilitar a identificacao no repositorio, o ano de referencia foi acrescentado localmente aos nomes dos arquivos quando necessario.

Essa nomenclatura local nao e utilizada como unica fonte para determinacao do periodo. Durante a auditoria, o ano indicado no nome de cada arquivo foi confrontado com o ano existente internamente nos dados.

Todos os 17 arquivos passaram nessa validacao.

---

## 3. Particularidade do arquivo de 2008

Foi identificada uma inconsistencia de metadado no arquivo correspondente a 2008.

O conteudo interno identifica corretamente:

Taxas de Rendimento por Unidades da Federacao - 2008

e os registros possuem:

Ano = 2008

Entretanto, o nome da aba e:

Rendimento por UF - 2009

Como o conteudo interno confirma inequivocamente o ano de 2008, o arquivo sera tratado como fonte de 2008.

O arquivo bruto nao sera alterado.

---

## 4. Cobertura temporal

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

Todos os arquivos apresentaram internamente exclusivamente o ano esperado segundo a organizacao local.

---

## 5. Mudancas estruturais

A auditoria identificou alteracoes na estrutura das planilhas ao longo da serie.

### 2007

O arquivo apresenta dimensoes como:

Ano
Regiao
UF
Localizacao
Rede

### 2008–2015

A estrutura passa a utilizar principalmente:

Ano
UF
Localizacao
Rede

### 2016

A fonte apresenta novamente a informacao regional e utiliza:

Ano
Regiao
UF
Localizacao
Dependencia Administrativa

### 2017–2023

Os arquivos passam a reunir:

Brasil
Regioes Geograficas
Unidades da Federacao

no mesmo conjunto de dados.

Consequentemente, o pipeline devera selecionar explicitamente apenas as 27 UFs.

---

## 6. Mudancas de nomenclatura

Foram identificadas variacoes textuais nas categorias de rede.

Nos anos mais antigos aparecem formas como:

Publico
Particular

Em outros periodos aparecem:

Publica
Privada

Tambem ocorre mudanca do nome da dimensao:

Rede

para:

Dependencia Administrativa

Essas diferencas serao padronizadas apenas na etapa de transformacao.

Os arquivos raw permanecerao inalterados.

---

## 7. Localizacao

Em todos os 17 anos foram encontradas as categorias:

Rural
Total
Urbana

Para o objetivo analitico do projeto sera utilizada:

Localizacao = Total

Dessa forma, o indicador representa o conjunto da UF sem restringir os resultados as areas urbana ou rural.

---

## 8. Dependencia administrativa

As fontes disponibilizam categorias como:

Federal
Estadual
Municipal
Publica / Publico
Privada / Particular
Total

A auditoria confirmou que a categoria agregada de rede publica esta disponivel diretamente na fonte durante toda a serie historica.

Assim, nao sera necessario reconstruir a rede publica por meio da combinacao de:

Federal + Estadual + Municipal

---

## 9. Cobertura das Unidades da Federacao

Foi verificada a presenca das 27 UFs em todos os anos.

Resultado:

2007–2023:
27 / 27 UFs

Nao foram identificadas UFs ausentes no recorte analisado.

---

## 10. Rede publica e localizacao total

Foi realizada uma verificacao especifica da combinacao:

Rede = Publica
Localizacao = Total

considerando variacoes textuais como:

Publico
Publica

Em todos os anos foram encontrados:

27 / 27 UFs

Nao foram identificadas duplicidades nessa combinacao.

Portanto, existe exatamente um agregado publico estadual pertinente ao projeto para cada UF e ano.

---

## 11. Indicadores utilizados

As fontes apresentam tres componentes de rendimento:

Aprovacao
Reprovacao
Abandono

Para cada um deles existem resultados consolidados para:

Anos Iniciais
Anos Finais

O projeto utilizara, portanto, seis medidas por UF e ano:

Aprovacao × Anos Iniciais
Aprovacao × Anos Finais
Reprovacao × Anos Iniciais
Reprovacao × Anos Finais
Abandono × Anos Iniciais
Abandono × Anos Finais

---

## 12. Cobertura das medidas

A auditoria confirmou que, para a combinacao:

27 UFs
Rede Publica
Localizacao Total

os seis indicadores possuem cobertura completa entre 2007 e 2023.

Em todos os anos:

Aprovacao — Anos Iniciais: 27 validos / 0 ausentes
Aprovacao — Anos Finais: 27 validos / 0 ausentes

Reprovacao — Anos Iniciais: 27 validos / 0 ausentes
Reprovacao — Anos Finais: 27 validos / 0 ausentes

Abandono — Anos Iniciais: 27 validos / 0 ausentes
Abandono — Anos Finais: 27 validos / 0 ausentes

---

## 13. Validacao matematica

Foi aplicada a seguinte verificacao para cada UF, ano e etapa:

Aprovacao + Reprovacao + Abandono ≈ 100

A tolerancia definida para a auditoria foi de:

0,2 ponto percentual

Resultado para todos os anos entre 2007 e 2023:

Anos Iniciais:
maior desvio = 0,00

Anos Finais:
maior desvio = 0,00

Registros fora da tolerancia:

0

A consistencia interna das tres taxas foi, portanto, confirmada em toda a serie auditada.

---

## 14. Ausencia de necessidade de reconstrucao

Como a propria fonte disponibiliza os resultados consolidados de:

UF
Rede Publica
Localizacao Total
Anos Iniciais
Anos Finais

nao sera necessario:

- agregar municipios;
- calcular medias entre UFs ou municipios;
- combinar Federal, Estadual e Municipal;
- reconstruir taxas a partir de series individuais.

O pipeline devera utilizar diretamente os agregados oficiais disponibilizados pelo Inep.

---

## 15. Valores ausentes

As fontes utilizam representacoes como:

--
-

para determinados valores indisponiveis em outras categorias e niveis de desagregacao.

Esses valores nao devem ser convertidos para zero.

Na transformacao deverao ser tratados como valores ausentes.

No recorte efetivamente utilizado pelo projeto — rede publica, localizacao total, Anos Iniciais e Anos Finais — nao foram encontrados valores ausentes nas seis medidas auditadas.

---

## 16. Estrutura padronizada pretendida

A tabela final de Rendimento Escolar podera adotar estrutura longa:

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

a tabela completa devera possuir:

2.754 registros

caso as regras definitivas mantenham esse recorte.

---

## 17. Regras preliminares para o pipeline

A auditoria indica as seguintes regras futuras:

1. Identificar o ano interno de cada arquivo.
2. Validar o ano contra a organizacao local.
3. Reconhecer as diferentes estruturas historicas.
4. Selecionar somente as 27 UFs.
5. Excluir Brasil e regioes quando presentes.
6. Selecionar Localizacao = Total.
7. Selecionar Rede = Publica, normalizando Publico/Publica.
8. Utilizar os agregados de Anos Iniciais e Anos Finais.
9. Selecionar Aprovacao, Reprovacao e Abandono.
10. Converter "-" e "--" em valores ausentes.
11. Transformar os dados para formato longo.
12. Validar ausencia de duplicidades.
13. Validar presenca das 27 UFs.
14. Validar Aprovacao + Reprovacao + Abandono = 100 dentro da tolerancia estabelecida.

Essas regras somente serao incorporadas ao pipeline produtivo apos a conclusao das demais auditorias.

---

## 18. Conclusao

A auditoria confirmou que as fontes de Rendimento Escolar sao adequadas para a serie historica proposta pelo projeto.

Entre 2007 e 2023 existe cobertura integral das 27 Unidades da Federacao para:

- rede publica;
- localizacao total;
- Anos Iniciais;
- Anos Finais;
- aprovacao;
- reprovacao;
- abandono.

Nao ha necessidade de reconstruir o agregado publico nem de calcular as taxas a partir de niveis geograficos inferiores.

A validacao matematica confirmou ainda que:

Aprovacao + Reprovacao + Abandono = 100

em todos os registros auditados do recorte.

A auditoria estrutural do Rendimento Escolar esta, portanto, concluida.

Permanece pendente apenas a decisao metodologica transversal sobre o conceito de rede publica, que sera consolidada apos a auditoria dos demais indicadores.

---

## Historico de atualizacao

| Data | Alteracao |
|---|---|
| 18/08/2026 | Primeira versao da auditoria tecnica |
| 18/08/2026 | Confirmada cobertura das 27 UFs entre 2007 e 2023 |
| 18/08/2026 | Confirmada cobertura integral das seis medidas |
| 18/08/2026 | Validada a soma Aprovacao + Reprovacao + Abandono |
| A definir | Atualizacao apos definicao metodologica conjunta da rede publica |