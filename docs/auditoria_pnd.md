# Auditoria das Fontes — Prova Nacional Docente (PND) 2025

## 1. Objetivo

Este documento registra a auditoria técnica dos microdados da Prova Nacional Docente (PND) 2025 utilizados no projeto.

A auditoria foi realizada antes da implementação definitiva do pipeline, com os objetivos de:

- identificar os arquivos disponíveis;
- compreender o layout dos microdados;
- interpretar as variáveis por meio do dicionário oficial;
- identificar a população analítica válida;
- verificar cobertura geográfica e por área;
- validar valores ausentes;
- verificar limites das métricas;
- validar a fórmula da nota geral;
- reproduzir os principais resultados diretamente a partir dos microdados.

---

## 2. Arquivos disponíveis

Foram identificados três arquivos principais no conjunto utilizado:

- Dicionário de arquivos e variáveis PND 2025;
- parâmetros dos itens da PND 2025;
- microdados principais da PND 2025.

O arquivo principal utilizado na análise é:

microdados2025_pnd_arq1.txt

O arquivo utiliza:

- separador `;`;
- decimal `,`;
- valores ausentes representados por `NA`.

Foram identificadas 26 variáveis no arquivo principal.

---

## 3. Estrutura do dicionário

O dicionário oficial contém quatro planilhas:

- DICIONÁRIO_DE_ARQUIVOS;
- DICIONÁRIO_DE_VARIAVÉIS;
- MUNICÍPIOS;
- Versões.

O arquivo utiliza uma variante de OOXML que apresentou incompatibilidade com a leitura convencional pelo openpyxl e pelo python-calamine.

Para a auditoria, seu conteúdo foi lido diretamente da estrutura OOXML interna, sem modificação do arquivo original.

A versão examinada registra atualização em 25/05/2026.

---

## 4. Universo bruto

O arquivo principal contém:

1.087.359 registros

Todos os registros pertencem ao ano:

2025

Foram identificadas:

- 27 Unidades da Federação;
- 17 áreas/grupos de prova;
- 3 tipos de inscrição;
- aplicação e reaplicação;
- 5 códigos de caderno.

---

## 5. Áreas da PND

Foram identificados os seguintes códigos de grupo:

702 — Matemática
904 — Letras - Português
905 — Letras - Português e Inglês
906 — Letras - Português e Espanhol
1402 — Física
1502 — Química
1602 — Ciências Biológicas
2001 — Pedagogia
2402 — História
2501 — Artes Visuais
3002 — Geografia
3202 — Filosofia
3502 — Educação Física
4005 — Ciência da Computação
4301 — Música
5402 — Ciências Sociais
6407 — Letras - Inglês

---

## 6. Tipo de inscrição

A variável TP_INSCRICAO_PND representa o perfil do participante.

Categorias:

1 — Concluinte Enade

2 — Demais Participantes

3 — Concluinte Enade que optou por realizar a prova em outra área, diferente da inscrição no Enade

---

## 7. Aplicação e reaplicação

A variável IN_REAPLICACAO identifica a prova válida para o participante.

Categorias:

0 — aplicação realizada em 26/10/2025

1 — reaplicação realizada em 30/11/2025

Os cadernos 1 a 4 correspondem à aplicação.

O caderno 5 corresponde à reaplicação.

---

## 8. Situação de presença

A variável TP_PRES possui as seguintes categorias:

222 — Ausente

334 — Eliminado por participação indevida

444 — Ausente devido a múltiplas inscrições

555 — Presente com resultado válido

888 — Presente na prova, com resultado desconsiderado pelo Inep

A auditoria identificou 12 registros com TP_PRES = 888 que apresentavam campos numéricos de resultado preenchidos.

Esses registros não foram incorporados à população analítica porque o próprio dicionário informa que seus resultados foram desconsiderados pelo Inep.

---

## 9. Situação da questão discursiva

A variável TP_SIT_DISC possui as seguintes categorias:

222 — Não se aplica, estudante ausente

333 — Questão em branco, estudante presente, nota zero

335 — Questão zerada por resposta nula, nota zero

336 — Questão com resposta divergente da temática, nota zero

555 — Questão com resultado válido

O dicionário informa que os códigos:

333
335
336
555

são considerados para o cálculo da nota do estudante.

Portanto, não deve ser aplicado filtro exigindo TP_SIT_DISC = 555.

Os valores zero associados aos códigos 333, 335 e 336 são resultados válidos.

---

## 10. Métricas disponíveis

### PROFICIENCIA

Proficiência da TRI na prova objetiva, expressa como theta.

Faixa indicada no dicionário:

-9,999 a 9,999

### NT_OBJ

Nota da prova objetiva.

Faixa:

0 a 100

### NT_DIS

Nota final da questão discursiva.

Faixa:

0 a 10

### NT_GER

Nota Geral da PND.

Faixa:

0 a 100

Fórmula oficial:

NT_GER = NT_OBJ × 0,8 + 2 × NT_DIS

### QT_ACERTOS

Quantidade de acertos na prova objetiva.

Faixa:

0 a 80

---

## 11. Disponibilidade dos resultados

No universo bruto foram encontrados:

759.152 registros com todos os cinco campos numéricos de resultado preenchidos

328.207 registros com todos os cinco campos numéricos ausentes

Não foram encontrados registros parcialmente preenchidos.

Os cinco campos examinados foram:

PROFICIENCIA
NT_OBJ
NT_DIS
NT_GER
QT_ACERTOS

---

## 12. Inconsistência identificada em TP_PRES

Foram encontrados:

760.106 registros com TP_PRES = 555

Entretanto:

759.140 possuem os resultados numéricos completos

966 não possuem:

- PROFICIENCIA;
- NT_OBJ;
- NT_DIS;
- NT_GER;
- QT_ACERTOS;
- DS_VT_ESC_OBJ;
- DS_VT_ACE_OBJ.

Apesar de estarem classificados como TP_PRES = 555, esses registros não contêm resultados disponíveis para análise.

A causa dessa inconsistência não foi identificada nos materiais examinados.

Não será realizada imputação ou reconstrução dessas informações.

---

## 13. População analítica

A população analítica utilizada pelo projeto é definida por:

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
- registros classificados como presentes, mas sem resultados disponíveis.

---

## 14. Validação das faixas

Na população analítica de 759.140 registros não foram identificados valores fora das faixas estabelecidas no dicionário para:

PROFICIENCIA
NT_OBJ
NT_DIS
NT_GER
QT_ACERTOS

Resultado:

0 valores fora das faixas oficiais.

---

## 15. Validação da nota geral

Foi recalculada a relação:

NT_GER = NT_OBJ × 0,8 + 2 × NT_DIS

utilizando tolerância de 0,11 para diferenças decorrentes de arredondamento.

Resultado:

0 divergências

A variável NT_GER publicada é consistente com a fórmula registrada no dicionário.

---

## 16. Cobertura geográfica

A população analítica apresenta participantes nas 27 Unidades da Federação.

A soma dos participantes agrupados por UF é:

759.140

Esse valor coincide exatamente com o total da população analítica.

A variável geográfica utilizada é:

SG_UF_MUNICIPIO_PROVA

Ela representa a UF do município do local de realização da prova.

Portanto, não deve ser interpretada automaticamente como UF de residência do participante.

---

## 17. Cobertura por área

As 17 áreas possuem registros na população analítica.

A soma dos participantes agrupados por CO_GRUPO é:

759.140

Esse valor coincide exatamente com o total da população analítica.

---

## 18. Resultados nacionais reproduzidos

A população analítica apresentou os seguintes resultados:

### PROFICIENCIA

Média:
-0,0015

Mediana:
-0,0236

Mínimo:
-3,9766

Máximo:
2,6885

### NT_OBJ

Média:
57,5282

Mediana:
56,7000

Mínimo:
0

Máximo:
100

### NT_DIS

Média:
5,6569

Mediana:
6,2500

Mínimo:
0

Máximo:
10

### NT_GER

Média:
57,3364

Mediana:
57,1400

Mínimo:
0

Máximo:
100

### QT_ACERTOS

Média:
41,9756

Mediana:
42

Mínimo:
0

Máximo:
77

---

## 19. Resultados por UF

Foram reproduzidos para as 27 UFs:

- número de participantes;
- média de PROFICIENCIA;
- média de NT_OBJ;
- média de NT_DIS;
- média de NT_GER;
- média de QT_ACERTOS.

A soma dos participantes das 27 UFs corresponde exatamente a 759.140 registros.

---

## 20. Resultados por área

Foram reproduzidos para as 17 áreas:

- número de participantes;
- média de PROFICIENCIA;
- média de NT_OBJ;
- média de NT_DIS;
- média de NT_GER;
- média de QT_ACERTOS.

A soma dos participantes das 17 áreas corresponde exatamente a 759.140 registros.

---

## 21. Consideração sobre PROFICIENCIA

As médias de PROFICIENCIA observadas individualmente nas 17 áreas permanecem muito próximas de zero.

Essa característica deve ser considerada antes de utilizar a variável para comparação ou ordenação direta das áreas.

A auditoria comprova o comportamento dos dados, mas os materiais examinados até esta etapa não são suficientes para justificar interpretação substantiva de pequenas diferenças de theta entre áreas.

Por isso, a variável poderá ser preservada no pipeline, mas comparações entre áreas deverão ser condicionadas à documentação metodológica da escala.

---

## 22. Regras para o pipeline

A transformação da PND deverá:

1. ler o arquivo utilizando separador `;`;
2. interpretar vírgula como separador decimal;
3. converter `NA` em valor ausente;
4. preservar os arquivos raw sem alteração;
5. selecionar TP_PRES = 555;
6. exigir disponibilidade das métricas utilizadas na análise;
7. excluir TP_PRES = 888;
8. não restringir TP_SIT_DISC apenas a 555;
9. preservar os zeros válidos dos códigos 333, 335 e 336;
10. validar as faixas das métricas;
11. validar a fórmula de NT_GER;
12. validar as 27 UFs;
13. validar as 17 áreas;
14. impedir imputação dos 966 registros sem resultado;
15. distinguir UF do local de prova de eventual UF de residência;
16. manter rastreabilidade das regras de exclusão.

---

## 23. Estruturas analíticas previstas

A PND poderá gerar tabelas agregadas específicas.

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

### Resultado por área

ANO
CO_GRUPO
AREA
PARTICIPANTES
MEDIA_NT_OBJ
MEDIA_NT_DIS
MEDIA_NT_GER
MEDIA_QT_ACERTOS

A variável PROFICIENCIA poderá ser preservada em estruturas auxiliares, observadas suas limitações interpretativas.

---

## 24. Conclusão

A auditoria confirmou a integridade estrutural dos microdados utilizados da PND 2025 e permitiu estabelecer de forma reproduzível a população analítica do projeto.

O universo bruto contém:

1.087.359 registros

A população analítica contém:

759.140 participantes

As validações confirmaram:

- cobertura das 27 UFs;
- cobertura das 17 áreas;
- ausência de valores faltantes nas métricas utilizadas;
- ausência de valores fora das faixas oficiais;
- consistência integral da fórmula da Nota Geral;
- correspondência entre os totais nacionais e os agrupamentos por UF e área.

Também foi documentada a existência de 966 registros classificados como TP_PRES = 555 sem resultados disponíveis e de 12 registros TP_PRES = 888 com resultados preenchidos, mas explicitamente desconsiderados pelo Inep.

Nenhum desses casos será corrigido ou imputado pelo pipeline.

A auditoria estrutural e analítica da PND 2025 está concluída.

---

## Histórico de atualização

| Data | Alteração |
|---|---|
| 18/08/2026 | Inspeção inicial dos arquivos |
| 18/08/2026 | Leitura do dicionário por OOXML |
| 18/08/2026 | Definição da população analítica |
| 18/08/2026 | Diagnóstico dos 966 registros sem resultados |
| 18/08/2026 | Validação das faixas e da fórmula da NT_GER |
| 18/08/2026 | Reprodução dos resultados nacionais, por UF e por área |
| 18/08/2026 | Auditoria da PND 2025 concluída |