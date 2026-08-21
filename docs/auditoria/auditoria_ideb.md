# Auditoria das Fontes — IDEB

## 1. Objetivo

Este documento registra a auditoria tecnica da fonte do **Indice de Desenvolvimento da Educacao Basica (IDEB)** utilizada no projeto.

A auditoria foi realizada antes da definicao das regras finais de transformacao do pipeline, com os seguintes objetivos:

* identificar a estrutura do arquivo oficial disponibilizado pelo Inep;
* verificar o nivel geografico dos dados;
* identificar as etapas de ensino disponiveis;
* analisar as categorias de rede;
* verificar a cobertura temporal da serie historica;
* identificar particularidades metodologicas registradas pelo proprio Inep;
* confirmar a presenca das 27 Unidades da Federacao;
* verificar a existencia de resultados da rede publica para todos os anos do recorte do projeto.

O projeto utiliza o periodo:

```text
2007–2023
```

e contempla somente:

* Ensino Fundamental — Anos Iniciais;
* Ensino Fundamental — Anos Finais;
* resultados em nivel de Unidade Federativa;
* rede publica.

> **Status deste documento:** auditoria estrutural concluida. A utilizacao definitiva da categoria de rede publica sera consolidada apos a auditoria conjunta de SAEB, Rendimento Escolar e TDI.

---

# 2. Fonte disponivel

Arquivo original:

```text
data/raw/ideb/divulgacao_regioes_ufs_ideb.xlsx
```

O arquivo foi disponibilizado pelo **Ministerio da Educacao / Instituto Nacional de Estudos e Pesquisas Educacionais Anisio Teixeira (Inep)**.

A planilha reune resultados historicos do IDEB e seus componentes.

Foram identificadas tres abas:

```text
UF e Regioes (AI)
UF e Regioes (AF)
UF e Regioes (EM)
```

Correspondentes a:

```text
AI → Ensino Fundamental Regular - Anos Iniciais
AF → Ensino Fundamental Regular - Anos Finais
EM → Ensino Medio Regular
```

A aba de Ensino Medio nao integra o recorte deste projeto.

---

# 3. Cobertura temporal

O arquivo apresenta resultados para:

```text
2005
2007
2009
2011
2013
2015
2017
2019
2021
2023
```

Embora 2005 esteja disponivel na fonte original, a serie historica adotada pelo projeto comeca em:

```text
2007
```

Portanto, os anos utilizados serao:

```text
2007
2009
2011
2013
2015
2017
2019
2021
2023
```

---

# 4. Estrutura da fonte

O arquivo possui cabecalho multinivel, seguido por uma linha com os nomes tecnicos das variaveis.

Alem do IDEB, a planilha disponibiliza seus componentes historicos.

Entre eles:

```text
Taxa de Aprovacao
Indicador de Rendimento (P)
Nota SAEB - Matematica
Nota SAEB - Lingua Portuguesa
Nota Media Padronizada (N)
IDEB observado
Metas do IDEB
```

Os nomes tecnicos incluem padroes como:

```text
VL_APROVACAO_2007_*
VL_INDICADOR_REND_2007

VL_NOTA_MATEMATICA_2007
VL_NOTA_PORTUGUES_2007
VL_NOTA_MEDIA_2007

VL_OBSERVADO_2007
```

e equivalentes para os demais anos.

Para a tabela de IDEB propriamente dita, as variaveis centrais do projeto sao:

```text
VL_OBSERVADO_2007
VL_OBSERVADO_2009
VL_OBSERVADO_2011
VL_OBSERVADO_2013
VL_OBSERVADO_2015
VL_OBSERVADO_2017
VL_OBSERVADO_2019
VL_OBSERVADO_2021
VL_OBSERVADO_2023
```

---

# 5. Etapas de ensino

## 5.1 Anos Iniciais

A aba:

```text
UF e Regioes (AI)
```

corresponde a:

```text
Ensino Fundamental Regular - Anos Iniciais
```

A fonte apresenta taxas de aprovacao do:

```text
1º ao 5º ano
```

alem do Indicador de Rendimento, das notas SAEB e do IDEB.

---

## 5.2 Anos Finais

A aba:

```text
UF e Regioes (AF)
```

corresponde a:

```text
Ensino Fundamental Regular - Anos Finais
```

A fonte apresenta taxas de aprovacao do:

```text
6º ao 9º ano
```

alem do Indicador de Rendimento, das notas SAEB e do IDEB.

---

# 6. Nivel geografico

A primeira coluna da planilha combina:

* regioes geograficas;
* Unidades da Federacao.

Foram encontradas as cinco regioes:

```text
Norte
Nordeste
Sudeste
Sul
Centro-Oeste
```

e as 27 Unidades da Federacao.

Portanto, o pipeline devera filtrar explicitamente as UFs, impedindo que resultados regionais sejam incorporados a tabela estadual.

---

# 7. Padronizacao dos nomes das UFs

Durante a auditoria foram encontradas tres abreviacoes utilizadas no arquivo oficial:

```text
R. G. do Norte
R. G. do Sul
M. G. do Sul
```

Elas correspondem a:

```text
R. G. do Norte → Rio Grande do Norte
R. G. do Sul   → Rio Grande do Sul
M. G. do Sul   → Mato Grosso do Sul
```

Esses valores deverao ser padronizados na etapa de transformacao.

Apos essa equivalencia, foram identificadas corretamente as **27 Unidades da Federacao**:

```text
Acre
Alagoas
Amapa
Amazonas
Bahia
Ceara
Distrito Federal
Espirito Santo
Goias
Maranhao
Mato Grosso
Mato Grosso do Sul
Minas Gerais
Parana
Paraiba
Para
Pernambuco
Piaui
Rio de Janeiro
Rio Grande do Norte
Rio Grande do Sul
Rondonia
Roraima
Santa Catarina
Sergipe
Sao Paulo
Tocantins
```

---

# 8. Categorias de rede

A inspecao inicial encontrou os seguintes rotulos nas abas de Anos Iniciais e Anos Finais:

```text
Total
Publica
Privada
Estadual

Total (3)(4)
Publica (4)
Privada (2)
Total (4)
```

Os rotulos entre parenteses nao representam necessariamente redes distintas.

Eles remetem as **notas metodologicas registradas pelo Inep no final da planilha**.

Nas linhas referentes as Unidades da Federacao, a categoria de interesse do projeto aparece como:

```text
Publica (4)
```

---

# 9. Notas metodologicas da fonte

A auditoria das notas de rodape identificou particularidades relevantes.

## Nota (1)

A fonte informa que determinadas medias do SAEB e resultados do IDEB de 2009 foram calculados somente com escolas urbanas.

Essa observacao aparece especialmente relacionada a determinados resultados da edicao de 2009.

---

## Nota (2)

A fonte informa que determinadas medias do SAEB e resultados do IDEB de 2009 nao foram calculados em razao de perda amostral.

Portanto, eventuais valores ausentes ou marcados com `-` nao devem ser convertidos artificialmente em zero.

---

## Nota (3)

A fonte informa que determinadas medias do SAEB e resultados do IDEB de 2009 foram calculados sem as escolas privadas.

---

## Nota (4)

A nota apresenta uma particularidade especialmente importante para a definicao de rede:

> Medias do SAEB 2011 e Ideb 2011 calculados sem as escolas federais.

Portanto, a categoria:

```text
Publica (4)
```

nao deve ser interpretada como uma nova categoria de rede.

O `(4)` registra uma excecao metodologica referente a edicao de **2011**, na qual o resultado nao inclui escolas federais.

Essa caracteristica devera ser preservada e documentada no projeto, em vez de ser corrigida artificialmente.

---

# 10. Particularidade do IDEB 2021

A fonte tambem apresenta uma nota especifica para a edicao de 2021, remetendo a:

```text
Nota Informativa do Ideb de 2021
```

e ao:

```text
Relatorio de Resultados do Saeb de 2021
```

para informacoes sobre os impactos da pandemia de COVID-19 nos indicadores.

Essa observacao devera ser mantida na documentacao metodologica do projeto.

Nao sera realizada alteracao artificial nos valores de 2021.

---

# 11. Verificacao da rede publica

Apos a padronizacao dos nomes das UFs e a exclusao das cinco regioes geograficas, foi realizada uma validacao especifica das linhas identificadas como rede publica.

O filtro considerou:

```text
REDE iniciando por "Publica"
```

incluindo:

```text
Publica (4)
```

Foram encontradas:

```text
27 UFs
```

tanto em Anos Iniciais quanto em Anos Finais.

---

# 12. Verificacao da serie historica

Foi verificada a disponibilidade do `VL_OBSERVADO` da rede publica em cada edicao.

## Anos Iniciais

|  Ano | UFs com IDEB valido | UFs sem valor |
| ---: | ------------------: | ------------: |
| 2007 |                  27 |             0 |
| 2009 |                  27 |             0 |
| 2011 |                  27 |             0 |
| 2013 |                  27 |             0 |
| 2015 |                  27 |             0 |
| 2017 |                  27 |             0 |
| 2019 |                  27 |             0 |
| 2021 |                  27 |             0 |
| 2023 |                  27 |             0 |

## Anos Finais

|  Ano | UFs com IDEB valido | UFs sem valor |
| ---: | ------------------: | ------------: |
| 2007 |                  27 |             0 |
| 2009 |                  27 |             0 |
| 2011 |                  27 |             0 |
| 2013 |                  27 |             0 |
| 2015 |                  27 |             0 |
| 2017 |                  27 |             0 |
| 2019 |                  27 |             0 |
| 2021 |                  27 |             0 |
| 2023 |                  27 |             0 |

Portanto, a serie utilizada pelo projeto possui cobertura completa das 27 UFs para o IDEB da rede publica nas duas etapas analisadas.

---

# 13. Ausencia de necessidade de agregacao

Diferentemente de fontes em nivel escolar, o arquivo do IDEB ja disponibiliza o indicador no nivel geografico desejado pelo projeto.

Assim:

```text
nao sera necessario calcular media estadual;
nao sera necessario ponderar escolas;
nao sera necessario reconstruir o IDEB;
```

O projeto devera utilizar diretamente os valores oficiais:

```text
VL_OBSERVADO_<ANO>
```

da linha correspondente a rede publica de cada UF.

Essa escolha evita reconstruir um indicador que ja foi oficialmente calculado e divulgado pelo Inep.

---

# 14. Tratamento de valores ausentes

A fonte utiliza, em determinados pontos, o caractere:

```text
-
```

para indicar ausencia de resultado.

Esse simbolo nao devera ser interpretado como:

```text
0
```

No processo de transformacao, devera ser convertido para valor ausente:

```text
null / NaN
```

Embora a auditoria tenha confirmado que o IDEB observado da rede publica possui valores validos para todas as 27 UFs no recorte 2007–2023, essa regra sera mantida como validacao geral da fonte.

---

# 15. Relacao entre IDEB, SAEB e Rendimento

O arquivo do IDEB tambem contem informacoes referentes a:

```text
Taxa de Aprovacao
Indicador de Rendimento
Notas SAEB
```

Esses campos fazem parte da composicao e documentacao do IDEB.

Entretanto, o projeto possui fontes especificas para:

```text
SAEB
Rendimento Escolar
```

Portanto, a existencia dessas variaveis dentro da planilha do IDEB nao implica automaticamente que elas substituirao as fontes especificas dos respectivos indicadores.

A decisao sobre qual fonte alimentara cada tabela sera realizada somente apos a auditoria de todos os conjuntos de dados.

---

# 16. Questao da rede publica

A auditoria do IDEB trouxe uma informacao relevante para a decisao metodologica geral do projeto.

A serie oficial utiliza a categoria:

```text
Publica
```

mas registra uma excecao explicita em 2011:

```text
resultados calculados sem as escolas federais
```

Isso demonstra que o universo da serie oficial nao e necessariamente absolutamente identico entre todas as edicoes.

Por essa razao, neste momento nao sera imposta artificialmente a regra:

```text
REDE PUBLICA = FEDERAL + ESTADUAL + MUNICIPAL
```

para todos os indicadores e todos os anos.

A definicao final sera realizada somente apos a auditoria de:

```text
SAEB
IDEB
Rendimento Escolar
TDI
```

A decisao devera priorizar comparabilidade, transparencia e fidelidade as fontes oficiais.

---

# 17. Estrutura padronizada pretendida

A tabela final de IDEB devera apresentar uma estrutura longa e padronizada:

```text
ANO
UF
REDE
ETAPA_ENSINO
VALOR
```

Exemplo:

```text
2007 | MG | PUBLICA | ANOS INICIAIS | 4.6
2007 | MG | PUBLICA | ANOS FINAIS   | 3.8
2009 | MG | PUBLICA | ANOS INICIAIS | ...
2009 | MG | PUBLICA | ANOS FINAIS   | ...
```

Os nomes das UFs serao padronizados durante a transformacao.

---

# 18. Regras preliminares identificadas para o futuro pipeline

A auditoria indica que o tratamento do IDEB devera contemplar:

```text
1. Ler somente as abas AI e AF.

2. Ignorar a aba de Ensino Medio.

3. Utilizar a linha de nomes tecnicos como cabecalho.

4. Padronizar:
   R. G. do Norte → Rio Grande do Norte
   R. G. do Sul   → Rio Grande do Sul
   M. G. do Sul   → Mato Grosso do Sul

5. Excluir as cinco regioes geograficas.

6. Manter somente as 27 UFs.

7. Selecionar a rede publica.

8. Converter "-" para valor ausente.

9. Utilizar VL_OBSERVADO_<ANO> como valor do IDEB.

10. Transformar a estrutura horizontal historica
    em estrutura longa.

11. Manter somente 2007–2023.

12. Registrar a excecao metodologica de 2011.

13. Documentar a particularidade de 2021.
```

Essas regras sao preliminares e somente serao incorporadas definitivamente ao pipeline apos a conclusao das demais auditorias.

---

# 19. Validacoes previstas

Quando o pipeline for implementado, a tabela de IDEB devera passar por validacoes automaticas.

Entre elas:

```text
9 anos esperados
27 UFs por ano
2 etapas de ensino
1 registro por ANO + UF + ETAPA
ausencia de duplicidades
UF pertencente a lista oficial das 27 UFs
IDEB dentro de intervalo plausivel
ausencias preservadas como null
```

Considerando o recorte completo:

```text
9 anos × 27 UFs × 2 etapas = 486 registros esperados
```

caso todos os valores permanecam disponiveis apos a transformacao.

A auditoria da fonte ja confirmou a existencia dos valores necessarios para esse conjunto.

---

# 20. Conclusao

A auditoria confirmou que o arquivo:

```text
divulgacao_regioes_ufs_ideb.xlsx
```

e adequado como fonte historica do IDEB para o projeto.

A planilha reune toda a serie necessaria em um unico arquivo oficial, possui resultados diretamente em nivel de Unidade da Federacao e apresenta valores da rede publica para todas as 27 UFs em Anos Iniciais e Anos Finais entre 2007 e 2023.

Foram identificadas particularidades que deverao ser preservadas no pipeline e na documentacao:

* presenca simultanea de regioes e UFs;
* abreviacoes em tres nomes de UFs;
* rotulos de rede acompanhados de notas metodologicas;
* excecoes relativas aos resultados de 2009;
* exclusao das escolas federais no calculo de 2011, conforme nota da propria fonte;
* observacao metodologica especifica para 2021;
* representacao de alguns valores ausentes por `-`.

Nao existe necessidade de reconstruir o IDEB a partir de suas componentes. O projeto podera utilizar diretamente os valores oficiais observados publicados pelo Inep.

A auditoria estrutural do IDEB esta, portanto, **concluida**.

Permanece pendente apenas a decisao metodologica transversal sobre o conceito de **rede publica**, que sera tomada apos a auditoria dos demais indicadores historicos.

---

## Historico de atualizacao

| Data       | Alteracao                                                        |
| ---------- | ---------------------------------------------------------------- |
| 18/08/2026 | Primeira versao da auditoria tecnica do IDEB                     |
| 18/08/2026 | Confirmada cobertura das 27 UFs em AI e AF, 2007–2023            |
| A definir  | Atualizacao apos definicao metodologica conjunta da rede publica |
| A definir  | Registro das regras definitivas incorporadas ao pipeline         |
