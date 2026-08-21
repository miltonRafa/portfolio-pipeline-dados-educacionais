# Auditoria das Fontes — IDEB

## 1. Objetivo

Este documento registra a auditoria técnica da fonte do **Índice de Desenvolvimento da Educação Básica (IDEB)** utilizada no projeto.

A auditoria foi realizada antes da definição das regras finais de transformação do pipeline, com os seguintes objetivos:

* identificar a estrutura do arquivo oficial disponibilizado pelo Inep;
* verificar o nível geográfico dos dados;
* identificar as etapas de ensino disponíveis;
* analisar as categorias de rede;
* verificar a cobertura temporal da série histórica;
* identificar particularidades metodológicas registradas pelo próprio Inep;
* confirmar a presença das 27 Unidades da Federação;
* verificar a existência de resultados da rede pública para todos os anos do recorte do projeto.

O projeto utiliza o período:

```text
2007–2023
```

e contempla somente:

* Ensino Fundamental — Anos Iniciais;
* Ensino Fundamental — Anos Finais;
* resultados em nível de Unidade Federativa;
* rede pública.

> **Status deste documento:** auditoria estrutural concluída. A utilização definitiva da categoria de rede pública será consolidada após a auditoria conjunta de SAEB, Rendimento Escolar e TDI.

---

# 2. Fonte disponível

Arquivo original:

```text
data/raw/ideb/divulgacao_regioes_ufs_ideb.xlsx
```

O arquivo foi disponibilizado pelo **Ministério da Educação / Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira (Inep)**.

A planilha reúne resultados históricos do IDEB e seus componentes.

Foram identificadas três abas:

```text
UF e Regiões (AI)
UF e Regiões (AF)
UF e Regiões (EM)
```

Correspondentes a:

```text
AI → Ensino Fundamental Regular - Anos Iniciais
AF → Ensino Fundamental Regular - Anos Finais
EM → Ensino Médio Regular
```

A aba de Ensino Médio não integra o recorte deste projeto.

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

Embora 2005 esteja disponível na fonte original, a série histórica adotada pelo projeto começa em:

```text
2007
```

Portanto, os anos utilizados serão:

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

O arquivo possui cabeçalho multinível, seguido por uma linha com os nomes técnicos das variáveis.

Além do IDEB, a planilha disponibiliza seus componentes históricos.

Entre eles:

```text
Taxa de Aprovação
Indicador de Rendimento (P)
Nota SAEB - Matemática
Nota SAEB - Língua Portuguesa
Nota Média Padronizada (N)
IDEB observado
Metas do IDEB
```

Os nomes técnicos incluem padrões como:

```text
VL_APROVACAO_2007_*
VL_INDICADOR_REND_2007

VL_NOTA_MATEMATICA_2007
VL_NOTA_PORTUGUES_2007
VL_NOTA_MEDIA_2007

VL_OBSERVADO_2007
```

e equivalentes para os demais anos.

Para a tabela de IDEB propriamente dita, as variáveis centrais do projeto são:

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
UF e Regiões (AI)
```

corresponde a:

```text
Ensino Fundamental Regular - Anos Iniciais
```

A fonte apresenta taxas de aprovação do:

```text
1º ao 5º ano
```

além do Indicador de Rendimento, das notas SAEB e do IDEB.

---

## 5.2 Anos Finais

A aba:

```text
UF e Regiões (AF)
```

corresponde a:

```text
Ensino Fundamental Regular - Anos Finais
```

A fonte apresenta taxas de aprovação do:

```text
6º ao 9º ano
```

além do Indicador de Rendimento, das notas SAEB e do IDEB.

---

# 6. Nível geográfico

A primeira coluna da planilha combina:

* regiões geográficas;
* Unidades da Federação.

Foram encontradas as cinco regiões:

```text
Norte
Nordeste
Sudeste
Sul
Centro-Oeste
```

e as 27 Unidades da Federação.

Portanto, o pipeline deverá filtrar explicitamente as UFs, impedindo que resultados regionais sejam incorporados à tabela estadual.

---

# 7. Padronização dos nomes das UFs

Durante a auditoria foram encontradas três abreviações utilizadas no arquivo oficial:

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

Esses valores deverão ser padronizados na etapa de transformação.

Após essa equivalência, foram identificadas corretamente as **27 Unidades da Federação**:

```text
Acre
Alagoas
Amapá
Amazonas
Bahia
Ceará
Distrito Federal
Espírito Santo
Goiás
Maranhão
Mato Grosso
Mato Grosso do Sul
Minas Gerais
Paraná
Paraíba
Pará
Pernambuco
Piauí
Rio de Janeiro
Rio Grande do Norte
Rio Grande do Sul
Rondônia
Roraima
Santa Catarina
Sergipe
São Paulo
Tocantins
```

---

# 8. Categorias de rede

A inspeção inicial encontrou os seguintes rótulos nas abas de Anos Iniciais e Anos Finais:

```text
Total
Pública
Privada
Estadual

Total (3)(4)
Pública (4)
Privada (2)
Total (4)
```

Os rótulos entre parênteses não representam necessariamente redes distintas.

Eles remetem às **notas metodológicas registradas pelo Inep no final da planilha**.

Nas linhas referentes às Unidades da Federação, a categoria de interesse do projeto aparece como:

```text
Pública (4)
```

---

# 9. Notas metodológicas da fonte

A auditoria das notas de rodapé identificou particularidades relevantes.

## Nota (1)

A fonte informa que determinadas médias do SAEB e resultados do IDEB de 2009 foram calculados somente com escolas urbanas.

Essa observação aparece especialmente relacionada a determinados resultados da edição de 2009.

---

## Nota (2)

A fonte informa que determinadas médias do SAEB e resultados do IDEB de 2009 não foram calculados em razão de perda amostral.

Portanto, eventuais valores ausentes ou marcados com `-` não devem ser convertidos artificialmente em zero.

---

## Nota (3)

A fonte informa que determinadas médias do SAEB e resultados do IDEB de 2009 foram calculados sem as escolas privadas.

---

## Nota (4)

A nota apresenta uma particularidade especialmente importante para a definição de rede:

> Médias do SAEB 2011 e Ideb 2011 calculados sem as escolas federais.

Portanto, a categoria:

```text
Pública (4)
```

não deve ser interpretada como uma nova categoria de rede.

O `(4)` registra uma exceção metodológica referente à edição de **2011**, na qual o resultado não inclui escolas federais.

Essa característica deverá ser preservada e documentada no projeto, em vez de ser corrigida artificialmente.

---

# 10. Particularidade do IDEB 2021

A fonte também apresenta uma nota específica para a edição de 2021, remetendo à:

```text
Nota Informativa do Ideb de 2021
```

e ao:

```text
Relatório de Resultados do Saeb de 2021
```

para informações sobre os impactos da pandemia de COVID-19 nos indicadores.

Essa observação deverá ser mantida na documentação metodológica do projeto.

Não será realizada alteração artificial nos valores de 2021.

---

# 11. Verificação da rede pública

Após a padronização dos nomes das UFs e a exclusão das cinco regiões geográficas, foi realizada uma validação específica das linhas identificadas como rede pública.

O filtro considerou:

```text
REDE iniciando por "Pública"
```

incluindo:

```text
Pública (4)
```

Foram encontradas:

```text
27 UFs
```

tanto em Anos Iniciais quanto em Anos Finais.

---

# 12. Verificação da série histórica

Foi verificada a disponibilidade do `VL_OBSERVADO` da rede pública em cada edição.

## Anos Iniciais

|  Ano | UFs com IDEB válido | UFs sem valor |
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

|  Ano | UFs com IDEB válido | UFs sem valor |
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

Portanto, a série utilizada pelo projeto possui cobertura completa das 27 UFs para o IDEB da rede pública nas duas etapas analisadas.

---

# 13. Ausência de necessidade de agregação

Diferentemente de fontes em nível escolar, o arquivo do IDEB já disponibiliza o indicador no nível geográfico desejado pelo projeto.

Assim:

```text
não será necessário calcular média estadual;
não será necessário ponderar escolas;
não será necessário reconstruir o IDEB;
```

O projeto deverá utilizar diretamente os valores oficiais:

```text
VL_OBSERVADO_<ANO>
```

da linha correspondente à rede pública de cada UF.

Essa escolha evita reconstruir um indicador que já foi oficialmente calculado e divulgado pelo Inep.

---

# 14. Tratamento de valores ausentes

A fonte utiliza, em determinados pontos, o caractere:

```text
-
```

para indicar ausência de resultado.

Esse símbolo não deverá ser interpretado como:

```text
0
```

No processo de transformação, deverá ser convertido para valor ausente:

```text
null / NaN
```

Embora a auditoria tenha confirmado que o IDEB observado da rede pública possui valores válidos para todas as 27 UFs no recorte 2007–2023, essa regra será mantida como validação geral da fonte.

---

# 15. Relação entre IDEB, SAEB e Rendimento

O arquivo do IDEB também contém informações referentes a:

```text
Taxa de Aprovação
Indicador de Rendimento
Notas SAEB
```

Esses campos fazem parte da composição e documentação do IDEB.

Entretanto, o projeto possui fontes específicas para:

```text
SAEB
Rendimento Escolar
```

Portanto, a existência dessas variáveis dentro da planilha do IDEB não implica automaticamente que elas substituirão as fontes específicas dos respectivos indicadores.

A decisão sobre qual fonte alimentará cada tabela será realizada somente após a auditoria de todos os conjuntos de dados.

---

# 16. Questão da rede pública

A auditoria do IDEB trouxe uma informação relevante para a decisão metodológica geral do projeto.

A série oficial utiliza a categoria:

```text
Pública
```

mas registra uma exceção explícita em 2011:

```text
resultados calculados sem as escolas federais
```

Isso demonstra que o universo da série oficial não é necessariamente absolutamente idêntico entre todas as edições.

Por essa razão, neste momento não será imposta artificialmente a regra:

```text
REDE PÚBLICA = FEDERAL + ESTADUAL + MUNICIPAL
```

para todos os indicadores e todos os anos.

A definição final será realizada somente após a auditoria de:

```text
SAEB
IDEB
Rendimento Escolar
TDI
```

A decisão deverá priorizar comparabilidade, transparência e fidelidade às fontes oficiais.

---

# 17. Estrutura padronizada pretendida

A tabela final de IDEB deverá apresentar uma estrutura longa e padronizada:

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

Os nomes das UFs serão padronizados durante a transformação.

---

# 18. Regras preliminares identificadas para o futuro pipeline

A auditoria indica que o tratamento do IDEB deverá contemplar:

```text
1. Ler somente as abas AI e AF.

2. Ignorar a aba de Ensino Médio.

3. Utilizar a linha de nomes técnicos como cabeçalho.

4. Padronizar:
   R. G. do Norte → Rio Grande do Norte
   R. G. do Sul   → Rio Grande do Sul
   M. G. do Sul   → Mato Grosso do Sul

5. Excluir as cinco regiões geográficas.

6. Manter somente as 27 UFs.

7. Selecionar a rede pública.

8. Converter "-" para valor ausente.

9. Utilizar VL_OBSERVADO_<ANO> como valor do IDEB.

10. Transformar a estrutura horizontal histórica
    em estrutura longa.

11. Manter somente 2007–2023.

12. Registrar a exceção metodológica de 2011.

13. Documentar a particularidade de 2021.
```

Essas regras são preliminares e somente serão incorporadas definitivamente ao pipeline após a conclusão das demais auditorias.

---

# 19. Validações previstas

Quando o pipeline for implementado, a tabela de IDEB deverá passar por validações automáticas.

Entre elas:

```text
9 anos esperados
27 UFs por ano
2 etapas de ensino
1 registro por ANO + UF + ETAPA
ausência de duplicidades
UF pertencente à lista oficial das 27 UFs
IDEB dentro de intervalo plausível
ausências preservadas como null
```

Considerando o recorte completo:

```text
9 anos × 27 UFs × 2 etapas = 486 registros esperados
```

caso todos os valores permaneçam disponíveis após a transformação.

A auditoria da fonte já confirmou a existência dos valores necessários para esse conjunto.

---

# 20. Conclusão

A auditoria confirmou que o arquivo:

```text
divulgacao_regioes_ufs_ideb.xlsx
```

é adequado como fonte histórica do IDEB para o projeto.

A planilha reúne toda a série necessária em um único arquivo oficial, possui resultados diretamente em nível de Unidade da Federação e apresenta valores da rede pública para todas as 27 UFs em Anos Iniciais e Anos Finais entre 2007 e 2023.

Foram identificadas particularidades que deverão ser preservadas no pipeline e na documentação:

* presença simultânea de regiões e UFs;
* abreviações em três nomes de UFs;
* rótulos de rede acompanhados de notas metodológicas;
* exceções relativas aos resultados de 2009;
* exclusão das escolas federais no cálculo de 2011, conforme nota da própria fonte;
* observação metodológica específica para 2021;
* representação de alguns valores ausentes por `-`.

Não existe necessidade de reconstruir o IDEB a partir de suas componentes. O projeto poderá utilizar diretamente os valores oficiais observados publicados pelo Inep.

A auditoria estrutural do IDEB está, portanto, **concluída**.

Permanece pendente apenas a decisão metodológica transversal sobre o conceito de **rede pública**, que será tomada após a auditoria dos demais indicadores históricos.

---

## Histórico de atualização

| Data       | Alteração                                                        |
| ---------- | ---------------------------------------------------------------- |
| 18/08/2026 | Primeira versão da auditoria técnica do IDEB                     |
| 18/08/2026 | Confirmada cobertura das 27 UFs em AI e AF, 2007–2023            |
| A definir  | Atualização após definição metodológica conjunta da rede pública |
| A definir  | Registro das regras definitivas incorporadas ao pipeline         |
