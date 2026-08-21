# Auditoria das Fontes — Prova Nacional Docente (PND) 2025

## 1. Objetivo

Este documento registra a auditoria tecnica dos microdados da Prova Nacional Docente (PND) 2025 utilizados no projeto.

A auditoria foi realizada antes da implementacao definitiva do pipeline, com os objetivos de:

- identificar os arquivos disponiveis;
- compreender o layout dos microdados;
- interpretar as variaveis por meio do dicionario oficial;
- identificar a populacao analitica valida;
- verificar cobertura geografica e por area;
- validar valores ausentes;
- verificar limites das metricas;
- validar a formula da nota geral;
- reproduzir os principais resultados diretamente a partir dos microdados.

---

## 2. Arquivos disponiveis

Foram identificados tres arquivos principais no conjunto utilizado:

- Dicionario de arquivos e variaveis PND 2025;
- parametros dos itens da PND 2025;
- microdados principais da PND 2025.

O arquivo principal utilizado na analise e:

microdados2025_pnd_arq1.txt

O arquivo utiliza:

- separador `;`;
- decimal `,`;
- valores ausentes representados por `NA`.

Foram identificadas 26 variaveis no arquivo principal.

---

## 3. Estrutura do dicionario

O dicionario oficial contem quatro planilhas:

- DICIONARIO_DE_ARQUIVOS;
- DICIONARIO_DE_VARIAVEIS;
- MUNICIPIOS;
- Versoes.

O arquivo utiliza uma variante de OOXML que apresentou incompatibilidade com a leitura convencional pelo openpyxl e pelo python-calamine.

Para a auditoria, seu conteudo foi lido diretamente da estrutura OOXML interna, sem modificacao do arquivo original.

A versao examinada registra atualizacao em 25/05/2026.

---

## 4. Universo bruto

O arquivo principal contem:

1.087.359 registros

Todos os registros pertencem ao ano:

2025

Foram identificadas:

- 27 Unidades da Federacao;
- 17 areas/grupos de prova;
- 3 tipos de inscricao;
- aplicacao e reaplicacao;
- 5 codigos de caderno.

---

## 5. Areas da PND

Foram identificados os seguintes codigos de grupo:

702 — Matematica
904 — Letras - Portugues
905 — Letras - Portugues e Ingles
906 — Letras - Portugues e Espanhol
1402 — Fisica
1502 — Quimica
1602 — Ciencias Biologicas
2001 — Pedagogia
2402 — Historia
2501 — Artes Visuais
3002 — Geografia
3202 — Filosofia
3502 — Educacao Fisica
4005 — Ciencia da Computacao
4301 — Musica
5402 — Ciencias Sociais
6407 — Letras - Ingles

---

## 6. Tipo de inscricao

A variavel TP_INSCRICAO_PND representa o perfil do participante.

Categorias:

1 — Concluinte Enade

2 — Demais Participantes

3 — Concluinte Enade que optou por realizar a prova em outra area, diferente da inscricao no Enade

---

## 7. Aplicacao e reaplicacao

A variavel IN_REAPLICACAO identifica a prova valida para o participante.

Categorias:

0 — aplicacao realizada em 26/10/2025

1 — reaplicacao realizada em 30/11/2025

Os cadernos 1 a 4 correspondem a aplicacao.

O caderno 5 corresponde a reaplicacao.

---

## 8. Situacao de presenca

A variavel TP_PRES possui as seguintes categorias:

222 — Ausente

334 — Eliminado por participacao indevida

444 — Ausente devido a multiplas inscricoes

555 — Presente com resultado valido

888 — Presente na prova, com resultado desconsiderado pelo Inep

A auditoria identificou 12 registros com TP_PRES = 888 que apresentavam campos numericos de resultado preenchidos.

Esses registros nao foram incorporados a populacao analitica porque o proprio dicionario informa que seus resultados foram desconsiderados pelo Inep.

---

## 9. Situacao da questao discursiva

A variavel TP_SIT_DISC possui as seguintes categorias:

222 — Nao se aplica, estudante ausente

333 — Questao em branco, estudante presente, nota zero

335 — Questao zerada por resposta nula, nota zero

336 — Questao com resposta divergente da tematica, nota zero

555 — Questao com resultado valido

O dicionario informa que os codigos:

333
335
336
555

sao considerados para o calculo da nota do estudante.

Portanto, nao deve ser aplicado filtro exigindo TP_SIT_DISC = 555.

Os valores zero associados aos codigos 333, 335 e 336 sao resultados validos.

---

## 10. Metricas disponiveis

### PROFICIENCIA

Proficiencia da TRI na prova objetiva, expressa como theta.

Faixa indicada no dicionario:

-9,999 a 9,999

### NT_OBJ

Nota da prova objetiva.

Faixa:

0 a 100

### NT_DIS

Nota final da questao discursiva.

Faixa:

0 a 10

### NT_GER

Nota Geral da PND.

Faixa:

0 a 100

Formula oficial:

NT_GER = NT_OBJ × 0,8 + 2 × NT_DIS

### QT_ACERTOS

Quantidade de acertos na prova objetiva.

Faixa:

0 a 80

---

## 11. Disponibilidade dos resultados

No universo bruto foram encontrados:

759.152 registros com todos os cinco campos numericos de resultado preenchidos

328.207 registros com todos os cinco campos numericos ausentes

Nao foram encontrados registros parcialmente preenchidos.

Os cinco campos examinados foram:

PROFICIENCIA
NT_OBJ
NT_DIS
NT_GER
QT_ACERTOS

---

## 12. Inconsistencia identificada em TP_PRES

Foram encontrados:

760.106 registros com TP_PRES = 555

Entretanto:

759.140 possuem os resultados numericos completos

966 nao possuem:

- PROFICIENCIA;
- NT_OBJ;
- NT_DIS;
- NT_GER;
- QT_ACERTOS;
- DS_VT_ESC_OBJ;
- DS_VT_ACE_OBJ.

Apesar de estarem classificados como TP_PRES = 555, esses registros nao contem resultados disponiveis para analise.

A causa dessa inconsistencia nao foi identificada nos materiais examinados.

Nao sera realizada imputacao ou reconstrucao dessas informacoes.

---

## 13. Populacao analitica

A populacao analitica utilizada pelo projeto e definida por:

TP_PRES = 555

e disponibilidade completa dos campos:

PROFICIENCIA
NT_OBJ
NT_DIS
NT_GER
QT_ACERTOS

Resultado:

759.140 participantes

Esse conjunto exclui:

- ausentes;
- participantes eliminados;
- registros desconsiderados pelo Inep;
- registros classificados como presentes, mas sem resultados disponiveis.

---

## 14. Validacao das faixas

Na populacao analitica de 759.140 registros nao foram identificados valores fora das faixas estabelecidas no dicionario para:

PROFICIENCIA
NT_OBJ
NT_DIS
NT_GER
QT_ACERTOS

Resultado:

0 valores fora das faixas oficiais.

---

## 15. Validacao da nota geral

Foi recalculada a relacao:

NT_GER = NT_OBJ × 0,8 + 2 × NT_DIS

utilizando tolerancia de 0,11 para diferencas decorrentes de arredondamento.

Resultado:

0 divergencias

A variavel NT_GER publicada e consistente com a formula registrada no dicionario.

---

## 16. Cobertura geografica

A populacao analitica apresenta participantes nas 27 Unidades da Federacao.

A soma dos participantes agrupados por UF e:

759.140

Esse valor coincide exatamente com o total da populacao analitica.

A variavel geografica utilizada e:

SG_UF_MUNICIPIO_PROVA

Ela representa a UF do municipio do local de realizacao da prova.

Portanto, nao deve ser interpretada automaticamente como UF de residencia do participante.

---

## 17. Cobertura por area

As 17 areas possuem registros na populacao analitica.

A soma dos participantes agrupados por CO_GRUPO e:

759.140

Esse valor coincide exatamente com o total da populacao analitica.

---

## 18. Resultados nacionais reproduzidos

A populacao analitica apresentou os seguintes resultados:

### PROFICIENCIA

Media:
-0,0015

Mediana:
-0,0236

Minimo:
-3,9766

Maximo:
2,6885

### NT_OBJ

Media:
57,5282

Mediana:
56,7000

Minimo:
0

Maximo:
100

### NT_DIS

Media:
5,6569

Mediana:
6,2500

Minimo:
0

Maximo:
10

### NT_GER

Media:
57,3364

Mediana:
57,1400

Minimo:
0

Maximo:
100

### QT_ACERTOS

Media:
41,9756

Mediana:
42

Minimo:
0

Maximo:
77

---

## 19. Resultados por UF

Foram reproduzidos para as 27 UFs:

- numero de participantes;
- media de PROFICIENCIA;
- media de NT_OBJ;
- media de NT_DIS;
- media de NT_GER;
- media de QT_ACERTOS.

A soma dos participantes das 27 UFs corresponde exatamente a 759.140 registros.

---

## 20. Resultados por area

Foram reproduzidos para as 17 areas:

- numero de participantes;
- media de PROFICIENCIA;
- media de NT_OBJ;
- media de NT_DIS;
- media de NT_GER;
- media de QT_ACERTOS.

A soma dos participantes das 17 areas corresponde exatamente a 759.140 registros.

---

## 21. Consideracao sobre PROFICIENCIA

As medias de PROFICIENCIA observadas individualmente nas 17 areas permanecem muito proximas de zero.

Essa caracteristica deve ser considerada antes de utilizar a variavel para comparacao ou ordenacao direta das areas.

A auditoria comprova o comportamento dos dados, mas os materiais examinados ate esta etapa nao sao suficientes para justificar interpretacao substantiva de pequenas diferencas de theta entre areas.

Por isso, a variavel podera ser preservada no pipeline, mas comparacoes entre areas deverao ser condicionadas a documentacao metodologica da escala.

---

## 22. Regras para o pipeline

A transformacao da PND devera:

1. ler o arquivo utilizando separador `;`;
2. interpretar virgula como separador decimal;
3. converter `NA` em valor ausente;
4. preservar os arquivos raw sem alteracao;
5. selecionar TP_PRES = 555;
6. exigir disponibilidade das metricas utilizadas na analise;
7. excluir TP_PRES = 888;
8. nao restringir TP_SIT_DISC apenas a 555;
9. preservar os zeros validos dos codigos 333, 335 e 336;
10. validar as faixas das metricas;
11. validar a formula de NT_GER;
12. validar as 27 UFs;
13. validar as 17 areas;
14. impedir imputacao dos 966 registros sem resultado;
15. distinguir UF do local de prova de eventual UF de residencia;
16. manter rastreabilidade das regras de exclusao.

---

## 23. Estruturas analiticas previstas

A PND podera gerar tabelas agregadas especificas.

### Resultado nacional

ANO
PARTICIPANTES
MEDIA_NT_OBJ
MEDIA_NT_DIS
MEDIA_NT_GER
MEDIA_QT_ACERTOS

### Resultado por UF

ANO
UF
PARTICIPANTES
MEDIA_NT_OBJ
MEDIA_NT_DIS
MEDIA_NT_GER
MEDIA_QT_ACERTOS

### Resultado por area

ANO
CO_GRUPO
AREA
PARTICIPANTES
MEDIA_NT_OBJ
MEDIA_NT_DIS
MEDIA_NT_GER
MEDIA_QT_ACERTOS

A variavel PROFICIENCIA podera ser preservada em estruturas auxiliares, observadas suas limitacoes interpretativas.

---

## 24. Conclusao

A auditoria confirmou a integridade estrutural dos microdados utilizados da PND 2025 e permitiu estabelecer de forma reproduzivel a populacao analitica do projeto.

O universo bruto contem:

1.087.359 registros

A populacao analitica contem:

759.140 participantes

As validacoes confirmaram:

- cobertura das 27 UFs;
- cobertura das 17 areas;
- ausencia de valores faltantes nas metricas utilizadas;
- ausencia de valores fora das faixas oficiais;
- consistencia integral da formula da Nota Geral;
- correspondencia entre os totais nacionais e os agrupamentos por UF e area.

Tambem foi documentada a existencia de 966 registros classificados como TP_PRES = 555 sem resultados disponiveis e de 12 registros TP_PRES = 888 com resultados preenchidos, mas explicitamente desconsiderados pelo Inep.

Nenhum desses casos sera corrigido ou imputado pelo pipeline.

A auditoria estrutural e analitica da PND 2025 esta concluida.

---

## Historico de atualizacao

| Data | Alteracao |
|---|---|
| 18/08/2026 | Inspecao inicial dos arquivos |
| 18/08/2026 | Leitura do dicionario por OOXML |
| 18/08/2026 | Definicao da populacao analitica |
| 18/08/2026 | Diagnostico dos 966 registros sem resultados |
| 18/08/2026 | Validacao das faixas e da formula da NT_GER |
| 18/08/2026 | Reproducao dos resultados nacionais, por UF e por area |
| 18/08/2026 | Auditoria da PND 2025 concluida |