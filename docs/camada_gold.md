# Camada Gold

## 1. Objetivo

A camada Gold organiza os dados ja auditados e padronizados na Silver em um modelo dimensional voltado a analise e ao consumo no Power BI.

A Gold nao substituira a Silver como camada de rastreabilidade. Sua funcao e:

- reduzir redundancias analiticas;
- separar dimensoes e fatos;
- conformar chaves compartilhadas entre as fontes;
- preservar explicitamente o grao de cada conjunto;
- facilitar relacionamentos `1:*` no Power BI;
- evitar calculos ou agregacoes que alterem os valores oficiais ja definidos na Silver;
- fornecer uma base simples, estavel e reproduzivel para medidas DAX e visualizacoes.

A camada Gold sera construida somente a partir das tabelas Silver ja concluidas e validadas.

Nao havera leitura direta de arquivos RAW ou Bronze na transformacao Gold.

---

## 2. Situacao de entrada

A Gold parte das seguintes tabelas Silver concluidas:

| Fonte | Arquivo Silver | Situacao |
|---|---|---|
| Rendimento Escolar | `data/silver/rendimento/rendimento_2007_2023.parquet` | ✅ concluida e validada |
| TDI | `data/silver/tdi/tdi_2007_2023.parquet` | ✅ concluida e validada |
| IDEB | `data/silver/ideb/ideb_2007_2023.parquet` | ✅ concluida e validada |
| SAEB | `data/silver/saeb/saeb_2007_2023.parquet` | ✅ concluida e validada |
| PND 2025 | `data/silver/pnd/pnd_2025.parquet` | ✅ concluida e validada |

A Gold nao reabrira decisoes metodologicas ja resolvidas na Silver, salvo se uma nova evidencia material demonstrar necessidade de correcao.

---

## 3. Principios de modelagem

### 3.1 Modelo dimensional

O projeto adotara um modelo dimensional com:

- dimensoes conformadas compartilhadas pelas tabelas fato quando o dominio for efetivamente comum;
- fatos separados quando os graos forem diferentes;
- relacionamentos preferencialmente `1:*`;
- direcao de filtro da dimensao para a fato no Power BI.

Nao sera criada uma tabela fato unica para todos os indicadores.

A razao e estrutural: Rendimento, TDI, IDEB, SAEB e PND nao possuem o mesmo grao.

Forcar a uniao produziria:

- campos nulos artificiais;
- perda de clareza semantica;
- risco de agregacoes incorretas;
- dificuldade de manutencao;
- relacoes analiticas menos transparentes.

### 3.2 Chaves naturais

A Gold utilizara as chaves naturais ja presentes nas fontes sempre que elas forem estaveis e suficientes.

Exemplos:

- `UF`;
- `ANO`;
- `ETAPA`;
- `CO_GRUPO`;
- `CO_MUNICIPIO_PROVA`.

Nao serao criadas chaves substitutas apenas por convencao.

Essa decisao evita complexidade sem beneficio analitico no escopo atual.

### 3.3 Rede publica

A populacao historica da Silver ja esta restrita a rede canonica `PUBLICA`.

Nao sera criada `DIM_REDE`, porque nao existe variacao analitica de rede na Gold atual.

O campo `REDE` podera permanecer nas fatos historicas como informacao explicita de escopo e para facilitar auditoria visual, mas nao funcionara como dimensao de filtro.

### 3.4 Proveniencia

Metadados detalhados de arquivo, aba, linha e coluna de origem permanecem na Silver.

A Gold nao duplicara toda a proveniencia fisica das fontes.

Quando for necessario auditar um valor Gold, a validacao devera reconstruir sua origem a partir da Silver correspondente.

---

## 4. Arquitetura prevista

```text
data/
└── gold/
    ├── dimensoes/
    │   ├── dim_uf.parquet
    │   ├── dim_tempo.parquet
    │   ├── dim_etapa.parquet
    │   ├── dim_area_pnd.parquet
    │   └── dim_municipio.parquet
    │
    └── fatos/
        ├── fato_rendimento.parquet
        ├── fato_tdi.parquet
        ├── fato_ideb.parquet
        ├── fato_saeb.parquet
        └── fato_pnd.parquet
```

Codigo:

```text
src/
└── gold/
    ├── dimensoes/
    ├── rendimento/
    ├── tdi/
    ├── ideb/
    ├── saeb/
    └── pnd/
```

---

## 5. Dimensoes

## 5.1 `DIM_UF`

### Objetivo

Fornecer uma dimensao geografica comum para:

- Rendimento Escolar;
- TDI;
- IDEB;
- SAEB;
- PND.

### Grao

`uma linha por UF`

### Colunas

```text
UF
```

Sao esperadas 27 UFs.

A dimensao sera construida a partir da uniao dos valores de UF presentes nas Silvers.

Na PND, o relacionamento usara `UF_PROVA`.

Isso nao altera a semantica da PND: a UF continua representando a Unidade Federativa do municipio de aplicacao da prova, e nao residencia do participante.

### Decisao

Nao sera acrescentado nome completo da UF nesta primeira versao da Gold sem uma fonte de referencia ja integrada a Silver.

A sigla e suficiente para o relacionamento e preserva a origem dos dados.

---

## 5.2 `DIM_TEMPO`

### Objetivo

Conformar o eixo anual utilizado pelas cinco fatos.

### Grao

`uma linha por ano com observacao em pelo menos uma fato`

### Colunas

```text
ANO
```

A dimensao sera construida pela uniao dos anos existentes nas Silvers.

Espera-se:

- 2007 a 2023 nas series historicas;
- 2025 na PND.

O ano de 2024 nao sera criado artificialmente, porque nenhuma das fontes atuais possui observacao analitica para esse ano.

---

## 5.3 `DIM_ETAPA`

### Objetivo

Conformar as duas etapas do Ensino Fundamental utilizadas pelas series historicas.

### Grao

`uma linha por etapa`

### Colunas

```text
ETAPA
ORDEM_ETAPA
```

Valores:

| ETAPA | ORDEM_ETAPA |
|---|---:|
| `ANOS_INICIAIS` | 1 |
| `ANOS_FINAIS` | 2 |

`ORDEM_ETAPA` e um atributo tecnico de ordenacao para o Power BI.

A PND nao sera relacionada a `DIM_ETAPA`, porque sua estrutura analitica nao representa etapa escolar da Educacao Basica.

---

## 5.4 `DIM_AREA_PND`

### Objetivo

Separar da fato individual da PND o dominio repetitivo das areas da prova.

### Grao

`uma linha por CO_GRUPO`

### Colunas

```text
CO_GRUPO
AREA_PROVA
```

Sao esperadas 17 areas.

A dimensao sera derivada exclusivamente dos pares unicos `CO_GRUPO + AREA_PROVA` existentes na Silver da PND.

A validacao devera confirmar relacao `1:1` entre codigo e rotulo.

---

## 5.5 `DIM_MUNICIPIO`

### Objetivo

Separar da fato PND o dominio dos municipios efetivamente presentes na populacao analitica.

### Grao

`uma linha por CO_MUNICIPIO_PROVA`

### Colunas

```text
CO_MUNICIPIO
UF
```

Sao esperados 750 municipios na populacao Silver atualmente validada.

### Decisao sobre nome do municipio

A Silver atual da PND contem o codigo do municipio e a UF, mas nao contem o nome do municipio.

Por isso, a Gold nao fara leitura direta do dicionario RAW para acrescentar `NOME_MUNICIPIO`.

Essa decisao preserva a regra arquitetural:

`Gold ← Silver`

e evita um atalho:

`Gold ← Raw`

Se o nome do municipio se tornar necessario para a experiencia final no Power BI, sera criada uma etapa de enriquecimento explicitamente documentada antes de sua implementacao.

### Relacionamentos

`DIM_MUNICIPIO` sera relacionada diretamente a `FATO_PND`.

Ela nao sera relacionada a `DIM_UF`, evitando caminhos de filtro ambiguos no modelo.

---

## 6. Tabelas fato

## 6.1 `FATO_RENDIMENTO`

### Origem

`data/silver/rendimento/rendimento_2007_2023.parquet`

### Grao

`ANO + UF + ETAPA + REDE + INDICADOR`

### Cardinalidade esperada

`2.754 registros`

### Colunas analiticas

```text
ANO
UF
ETAPA
REDE
INDICADOR
VALOR
```

A Gold nao recalculara taxas.

`VALOR` devera reproduzir exatamente o valor analitico existente na Silver.

### Indicadores

Os indicadores permanecem na propria fato.

Nao sera criada `DIM_INDICADOR` nesta etapa porque:

- o dominio e pequeno;
- somente a fato de Rendimento utiliza esse atributo;
- uma dimensao separada nao acrescentaria vantagem analitica relevante no escopo atual.

---

## 6.2 `FATO_TDI`

### Origem

`data/silver/tdi/tdi_2007_2023.parquet`

### Grao

`ANO + UF + ETAPA + REDE`

### Cardinalidade esperada

`918 registros`

### Colunas analiticas

```text
ANO
UF
ETAPA
REDE
VALOR
```

Os valores deverao ser copiados da Silver sem nova agregacao.

---

## 6.3 `FATO_IDEB`

### Origem

`data/silver/ideb/ideb_2007_2023.parquet`

### Grao

`ANO + UF + ETAPA + REDE`

### Cardinalidade esperada

`486 registros`

### Colunas analiticas

```text
ANO
UF
ETAPA
REDE
VALOR
```

A Gold preservara somente as edicoes efetivamente existentes.

Nao sera criada interpolacao para anos sem IDEB.

---

## 6.4 `FATO_SAEB`

### Origem

`data/silver/saeb/saeb_2007_2023.parquet`

### Grao

`ANO + UF + ETAPA + REDE + DISCIPLINA`

### Cardinalidade esperada

`972 registros`

### Colunas analiticas

```text
ANO
UF
ETAPA
REDE
DISCIPLINA
VALOR
```

### Regra critica

A Gold utilizara diretamente os valores oficiais ja selecionados na Silver.

Nao serao criados:

```text
SOMA_PESO
SOMA_VALOR_PONDERADO
```

nem qualquer outra reconstrucao por media de escolas.

A comparacao metodologica realizada para o SAEB 2023 demonstrou que a media escolar ponderada por `NU_PRESENTES` nao reproduz o agregado oficial de UF.

Portanto, a Gold nao repetira uma regra ja rejeitada na Silver.

### Disciplina

`DISCIPLINA` permanecera na propria fato.

Nao sera criada `DIM_DISCIPLINA` nesta etapa porque:

- existem apenas `LP` e `MT`;
- somente o SAEB utiliza o atributo;
- separar duas categorias em uma dimensao nao oferece beneficio suficiente para justificar a complexidade adicional.

---

## 6.5 `FATO_PND`

### Origem

`data/silver/pnd/pnd_2025.parquet`

### Grao

`um registro individual valido da prova`

### Cardinalidade esperada

`759.140 registros`

### Colunas analiticas previstas

```text
ANO
UF_PROVA
CO_MUNICIPIO_PROVA
CO_GRUPO
PROFICIENCIA
NT_OBJ
NT_DIS
NT_GER
QT_ACERTOS
```

A fato nao transportara:

- `AREA_PROVA`, porque esse atributo ficara em `DIM_AREA_PND`;
- metadados fisicos de proveniencia;
- vetores de respostas;
- respostas do Questionario de Percepcao de Prova.

### Identificador individual

A fonte nao fornece identificador pessoal ou de participante.

A Gold nao inventara uma chave de participante.

A unicidade e rastreabilidade fisica continuam disponiveis na Silver por `LINHA_ORIGEM_BRONZE`.

---

## 7. Relacionamentos previstos no Power BI

### `DIM_UF`

```text
DIM_UF[UF] 1 ─── * FATO_RENDIMENTO[UF]
DIM_UF[UF] 1 ─── * FATO_TDI[UF]
DIM_UF[UF] 1 ─── * FATO_IDEB[UF]
DIM_UF[UF] 1 ─── * FATO_SAEB[UF]
DIM_UF[UF] 1 ─── * FATO_PND[UF_PROVA]
```

### `DIM_TEMPO`

```text
DIM_TEMPO[ANO] 1 ─── * FATO_RENDIMENTO[ANO]
DIM_TEMPO[ANO] 1 ─── * FATO_TDI[ANO]
DIM_TEMPO[ANO] 1 ─── * FATO_IDEB[ANO]
DIM_TEMPO[ANO] 1 ─── * FATO_SAEB[ANO]
DIM_TEMPO[ANO] 1 ─── * FATO_PND[ANO]
```

### `DIM_ETAPA`

```text
DIM_ETAPA[ETAPA] 1 ─── * FATO_RENDIMENTO[ETAPA]
DIM_ETAPA[ETAPA] 1 ─── * FATO_TDI[ETAPA]
DIM_ETAPA[ETAPA] 1 ─── * FATO_IDEB[ETAPA]
DIM_ETAPA[ETAPA] 1 ─── * FATO_SAEB[ETAPA]
```

### PND

```text
DIM_AREA_PND[CO_GRUPO] 1 ─── * FATO_PND[CO_GRUPO]

DIM_MUNICIPIO[CO_MUNICIPIO] 1 ─── * FATO_PND[CO_MUNICIPIO_PROVA]
```

### Direcao de filtro

A direcao padrao sera:

`dimensao → fato`

Nao serao criados filtros bidirecionais por padrao.

Qualquer excecao futura devera ser justificada pelo caso analitico especifico.

---

## 8. Limites entre Gold e Power BI

A Gold armazenara dados analiticos de base.

Calculos de apresentacao e indicadores derivados deverao permanecer, preferencialmente, na camada semantica do Power BI.

Exemplos de medidas que nao precisam ser materializadas como colunas Gold:

- media de IDEB;
- media SAEB por disciplina;
- media de aprovacao, reprovacao ou abandono;
- media da TDI;
- variacao entre primeiro e ultimo ano selecionado;
- media de `NT_OBJ`;
- media de `NT_DIS`;
- media de `NT_GER`;
- media de `QT_ACERTOS`;
- percentual de participantes PND abaixo de um limiar;
- contagem de participantes.

### Justificativa

Esses calculos dependem do contexto de filtro do relatorio.

Persisti-los na Gold como colunas ou agregados fixos poderia:

- duplicar logica;
- gerar inconsistencia entre Python e DAX;
- limitar a interatividade;
- criar dados derivados desnecessarios.

---

## 9. Tratamento dos valores PND

A Gold preservara os valores numericos da Silver sem modificar seu dominio.

Em particular:

- `PROFICIENCIA` pode assumir valores negativos;
- `NT_OBJ` permanece entre os valores publicados pela fonte;
- `NT_DIS` permanece entre os valores publicados pela fonte;
- `NT_GER` permanece entre os valores publicados pela fonte;
- `QT_ACERTOS` permanece uma contagem nao negativa.

Nao havera:

- truncamento;
- substituicao de valores negativos por zero;
- normalizacao adicional;
- arredondamento adicional.

A Silver e a referencia semantica para esses valores.

---

## 10. Validacoes da Gold

Toda transformacao Gold devera possuir validacao independente.

As validacoes deverao confirmar, conforme aplicavel:

- existencia dos arquivos Silver esperados;
- cardinalidade esperada das fatos;
- unicidade das chaves das dimensoes;
- inexistencia de chaves orfas nas fatos;
- dominio das 27 UFs;
- dominio das duas etapas;
- relacao `CO_GRUPO → AREA_PROVA` sem ambiguidade;
- 750 municipios na populacao atual da PND;
- igualdade dos valores analiticos entre Silver e Gold;
- ausencia de agregacoes nao documentadas;
- ausencia de duplicidades no grao de cada fato.

### Integridade referencial

Para cada chave estrangeira presente em uma fato, devera existir exatamente uma chave correspondente na dimensao.

Exemplo:

```text
FATO_SAEB[UF] ⊆ DIM_UF[UF]
```

A execucao devera falhar se uma chave orfa for encontrada.

---

## 11. Regra de transformacao

A Gold nao realizara nova interpretacao das fontes oficiais.

O fluxo sera:

```text
RAW
  ↓
BRONZE
  ↓
SILVER
  ↓
GOLD
  ↓
POWER BI
```

Responsabilidades:

```text
RAW     → preservacao da fonte original
BRONZE  → ingestao reproduzivel e rastreavel
SILVER  → padronizacao, selecao semantica e validacao
GOLD    → modelagem dimensional
POWER BI → medidas, contexto de filtro e visualizacao
```

---

## 12. Estrategia de implementacao

A implementacao seguira esta ordem:

1. documentar o modelo dimensional;
2. gerar e validar as dimensoes;
3. gerar e validar `FATO_RENDIMENTO`;
4. gerar e validar `FATO_TDI`;
5. gerar e validar `FATO_IDEB`;
6. gerar e validar `FATO_SAEB`;
7. gerar e validar `FATO_PND`;
8. validar integridade referencial global;
9. conectar a Gold ao Power BI;
10. recriar as medidas DAX sobre o novo modelo.

Essa ordem reduz o risco de criar relacionamentos antes de as chaves dimensionais estarem estaveis.

---

## 13. Politica de falha

A Gold devera falhar explicitamente se:

- uma Silver esperada nao existir;
- uma dimensao possuir chave duplicada;
- uma fato possuir chave orfa;
- a cardinalidade esperada mudar sem documentacao;
- o grao de uma fato deixar de ser unico;
- surgir UF fora do dominio esperado;
- surgir etapa fora do dominio esperado;
- surgir `CO_GRUPO` sem area correspondente;
- a Gold alterar valores da Silver sem regra documentada.

E preferivel interromper a execucao do que produzir um modelo dimensional aparentemente valido com perda semantica.

---

## 13.1 Implementacao das dimensoes

Arquivos implementados:

`src/gold/dimensoes/transformar_dimensoes.py`

`src/gold/dimensoes/validar_dimensoes.py`

Saidas:

```text
data/gold/dimensoes/dim_uf.parquet
data/gold/dimensoes/dim_tempo.parquet
data/gold/dimensoes/dim_etapa.parquet
data/gold/dimensoes/dim_area_pnd.parquet
data/gold/dimensoes/dim_municipio.parquet
```

O transformador le exclusivamente as Silvers concluidas.

Regras implementadas:

- `DIM_UF`: uniao das UFs das cinco Silvers, com exatamente 27 chaves unicas;
- `DIM_TEMPO`: uniao dos anos observados nas Silvers, preservando 2007–2023 e 2025, sem criar 2024 artificialmente;
- `DIM_ETAPA`: dominio `ANOS_INICIAIS` / `ANOS_FINAIS`, com `ORDEM_ETAPA` 1 e 2;
- `DIM_AREA_PND`: pares unicos `CO_GRUPO + AREA_PROVA`, com 17 areas e relacao 1:1;
- `DIM_MUNICIPIO`: pares unicos `CO_MUNICIPIO_PROVA + UF_PROVA`, com 750 municipios e uma unica UF por codigo.

O validador e independente do transformador e reconstroi cada dimensao diretamente das Silvers.

A execucao foi concluida com sucesso e a validacao independente retornou:

`DIMENSOES GOLD: OK`

Resultados confirmados:

- `DIM_UF`: 27 linhas, chave `UF` unica;
- `DIM_TEMPO`: 18 linhas, cobrindo 2007–2023 e 2025;
- `DIM_ETAPA`: 2 linhas, com chave `ETAPA` unica;
- `DIM_AREA_PND`: 17 linhas, com `CO_GRUPO` unico;
- `DIM_MUNICIPIO`: 750 linhas, com `CO_MUNICIPIO` unico;
- reproducao das Silvers: OK;
- dominios dimensionais: OK.

Status:

`DIMENSOES GOLD ✅ concluidas e validadas`

---

## 13.2 Implementacao da FATO_RENDIMENTO

Arquivos implementados:

`src/gold/rendimento/transformar_rendimento.py`

`src/gold/rendimento/validar_fato_rendimento.py`

Saida:

`data/gold/fatos/fato_rendimento.parquet`

A transformacao le exclusivamente:

`data/silver/rendimento/rendimento_2007_2023.parquet`

e mantem apenas as colunas analiticas:

```text
ANO
UF
ETAPA
REDE
INDICADOR
VALOR
```

Nenhuma taxa e recalculada.

A validacao implementada verifica:

- 2.754 registros;
- grao unico `ANO + UF + ETAPA + REDE + INDICADOR`;
- 17 anos;
- 27 UFs;
- duas etapas;
- rede unica `PUBLICA`;
- tres indicadores: `APROVACAO`, `REPROVACAO`, `ABANDONO`;
- ausencia de valores nulos;
- dominio de taxas entre 0 e 100;
- igualdade dos 2.754 valores Gold ↔ Silver;
- inexistencia de UFs orfas em `DIM_UF`;
- inexistencia de anos orfaos em `DIM_TEMPO`;
- inexistencia de etapas orfas em `DIM_ETAPA`.

A transformacao e a validacao independente foram executadas com sucesso.

Resultados confirmados:

- 2.754 registros;
- 17 anos;
- 27 UFs;
- 2 etapas;
- 3 indicadores;
- rede unica `PUBLICA`;
- zero valores ausentes;
- grao `ANO + UF + ETAPA + REDE + INDICADOR` unico;
- 2.754 registros comparados diretamente com a Silver;
- valores Gold = Silver;
- dominio das taxas 0–100;
- zero chaves orfas em `DIM_UF`, `DIM_TEMPO` e `DIM_ETAPA`.

Resultado final:

`FATO_RENDIMENTO GOLD: OK`

Status:

`FATO_RENDIMENTO ✅ concluida e validada`

---

## 13.3 Implementacao da FATO_TDI

Arquivos implementados:

`src/gold/tdi/transformar_tdi.py`

`src/gold/tdi/validar_fato_tdi.py`

Saida:

`data/gold/fatos/fato_tdi.parquet`

A transformacao le exclusivamente:

`data/silver/tdi/tdi_2007_2023.parquet`

e mantem as colunas analiticas:

```text
ANO
UF
ETAPA
REDE
TDI
```

Nenhuma taxa e recalculada.

A coluna `TDI` e preservada com o valor analitico definido na Silver.

A validacao implementada verifica:

- 918 registros;
- grao unico `ANO + UF + ETAPA + REDE`;
- 17 anos;
- 27 UFs;
- duas etapas;
- rede unica `PUBLICA`;
- ausencia de valores nulos;
- dominio da TDI entre 0 e 100;
- igualdade dos 918 valores Gold ↔ Silver;
- inexistencia de UFs orfas em `DIM_UF`;
- inexistencia de anos orfaos em `DIM_TEMPO`;
- inexistencia de etapas orfas em `DIM_ETAPA`.

A transformacao e a validacao independente foram executadas com sucesso.

Resultados confirmados:

- 918 registros;
- 17 anos;
- 27 UFs;
- 2 etapas;
- rede unica `PUBLICA`;
- zero valores ausentes;
- grao `ANO + UF + ETAPA + REDE` unico;
- 918 registros comparados diretamente com a Silver;
- valores Gold = Silver;
- dominio da TDI entre 0 e 100;
- zero chaves orfas em `DIM_UF`, `DIM_TEMPO` e `DIM_ETAPA`.

Resultado final:

`FATO_TDI GOLD: OK`

Status:

`FATO_TDI ✅ concluida e validada`

---

## 13.4 Implementacao da FATO_IDEB

Arquivos implementados:

`src/gold/ideb/transformar_ideb.py`

`src/gold/ideb/validar_fato_ideb.py`

Saida:

`data/gold/fatos/fato_ideb.parquet`

A transformacao le exclusivamente:

`data/silver/ideb/ideb_2007_2023.parquet`

e mantem as colunas analiticas:

```text
ANO
UF
ETAPA
REDE
IDEB
```

Nenhum valor do IDEB e recalculado.

A Gold preserva somente as nove edicoes efetivamente existentes no recorte:

```text
2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021, 2023
```

Nao sao criadas observacoes para os anos intermediarios.

A validacao implementada verifica:

- 486 registros;
- grao unico `ANO + UF + ETAPA + REDE`;
- nove edicoes;
- 27 UFs;
- duas etapas;
- rede unica `PUBLICA`;
- ausencia de valores nulos;
- dominio do IDEB entre 0 e 10;
- igualdade dos 486 valores Gold ↔ Silver;
- inexistencia de UFs orfas em `DIM_UF`;
- inexistencia de anos orfaos em `DIM_TEMPO`;
- inexistencia de etapas orfas em `DIM_ETAPA`.

A transformacao e a validacao independente foram executadas com sucesso.

Resultados confirmados:

- 486 registros;
- 9 edicoes;
- 27 UFs;
- 2 etapas;
- rede unica `PUBLICA`;
- zero valores ausentes;
- grao `ANO + UF + ETAPA + REDE` unico;
- 486 registros comparados diretamente com a Silver;
- valores Gold = Silver;
- dominio do IDEB entre 0 e 10;
- zero chaves orfas em `DIM_UF`, `DIM_TEMPO` e `DIM_ETAPA`.

Resultado final:

`FATO_IDEB GOLD: OK`

Status:

`FATO_IDEB ✅ concluida e validada`

---

## 13.5 Implementacao da FATO_SAEB

Arquivos implementados:

`src/gold/saeb/transformar_saeb.py`

`src/gold/saeb/validar_fato_saeb.py`

Saida:

`data/gold/fatos/fato_saeb.parquet`

A transformacao le exclusivamente:

`data/silver/saeb/saeb_2007_2023.parquet`

e mantem as colunas analiticas:

```text
ANO
UF
ETAPA
REDE
DISCIPLINA
PROFICIENCIA
```

Nenhuma proficiencia e recalculada ou recomposta.

A Gold preserva diretamente os valores oficiais ja selecionados e validados na Silver.

### Regra metodologica critica

Nao sao criadas colunas como:

```text
SOMA_PESO
SOMA_VALOR_PONDERADO
```

e nao e aplicada media ponderada a partir dos microdados escolares.

Essa decisao e deliberada. A auditoria do SAEB 2023 demonstrou que a recomposicao escolar ponderada por participantes nao reproduz o agregado oficial de UF. Por isso, a Gold utiliza a Silver como referencia semantica definitiva.

A politica historica de rede publica tambem e herdada da Silver. A Gold nao tenta recompor redes administrativas por conta propria.

A validacao implementada verifica:

- 972 registros;
- grao unico `ANO + UF + ETAPA + REDE + DISCIPLINA`;
- nove edicoes;
- 27 UFs;
- duas etapas;
- duas disciplinas: `LP` e `MT`;
- rede unica `PUBLICA`;
- ausencia de proficiencias nulas;
- dominio da proficiencia entre 0 e 500;
- igualdade das 972 proficiencias Gold ↔ Silver;
- inexistencia de UFs orfas em `DIM_UF`;
- inexistencia de anos orfaos em `DIM_TEMPO`;
- inexistencia de etapas orfas em `DIM_ETAPA`.

Nao sera criada `DIM_DISCIPLINA` nesta versao da Gold. O dominio possui somente duas categorias e e utilizado apenas pela FATO_SAEB.

A transformacao e a validacao independente foram executadas com sucesso.

Resultados confirmados:

- 972 registros;
- 9 edicoes;
- 27 UFs;
- 2 etapas;
- 2 disciplinas: `LP` e `MT`;
- rede unica `PUBLICA`;
- zero valores ausentes;
- grao `ANO + UF + ETAPA + REDE + DISCIPLINA` unico;
- 972 registros comparados diretamente com a Silver;
- proficiencias Gold = Silver;
- dominio da proficiencia entre 0 e 500;
- zero chaves orfas em `DIM_UF`, `DIM_TEMPO` e `DIM_ETAPA`.

Resultado final:

`FATO_SAEB GOLD: OK`

Status:

`FATO_SAEB ✅ concluida e validada`

---

## 13.6 Implementacao da FATO_PND

Arquivos implementados:

`src/gold/pnd/transformar_pnd.py`

`src/gold/pnd/validar_fato_pnd.py`

Saida:

`data/gold/fatos/fato_pnd.parquet`

A transformacao le exclusivamente:

`data/silver/pnd/pnd_2025.parquet`

e preserva o grao individual ja definido e validado na Silver:

`um registro individual valido da prova`

A fato mantem os campos necessarios ao modelo analitico e acrescenta a classificacao oficial de desempenho:

```text
ANO
UF_PROVA
CO_MUNICIPIO_PROVA
CO_GRUPO
PROFICIENCIA
NT_OBJ
NT_DIS
NT_GER
QT_ACERTOS
PADRAO_DESEMPENHO
```

Foram deliberadamente retirados da Gold:

- `AREA_PROVA`, porque o rotulo passa a ser fornecido por `DIM_AREA_PND`;
- `TP_INSCRICAO_PND`;
- `IN_REAPLICACAO`;
- `CO_CADERNO`;
- `TP_PRES`;
- `TP_SIT_DISC`;
- `ARQUIVO_ORIGEM`;
- `LINHA_ORIGEM_BRONZE`;
- `GRANULARIDADE_ORIGEM`.

Os campos tecnicos e variaveis que nao participam do escopo atual continuam preservados na Silver. Sua retirada da Gold reduz redundancia e mantem a fato orientada ao consumo analitico no Power BI.

A Gold nao cria identificador artificial de participante. A fonte nao disponibiliza um identificador pessoal, e registros distintos podem possuir os mesmos valores analiticos. Portanto, nao sera imposta uma falsa chave de unicidade baseada na combinacao de notas, area ou localizacao.

### Integridade dimensional da PND

A validacao verifica quatro relacionamentos:

```text
DIM_TEMPO[ANO] 1 ─── * FATO_PND[ANO]
DIM_UF[UF] 1 ─── * FATO_PND[UF_PROVA]
DIM_AREA_PND[CO_GRUPO] 1 ─── * FATO_PND[CO_GRUPO]
DIM_MUNICIPIO[CO_MUNICIPIO] 1 ─── * FATO_PND[CO_MUNICIPIO_PROVA]
```

Alem da ausencia de chaves orfas, e verificada a coerencia:

`CO_MUNICIPIO_PROVA → UF_PROVA`

contra o par correspondente em `DIM_MUNICIPIO`.

`DIM_MUNICIPIO` nao sera relacionada diretamente a `DIM_UF` no Power BI. Assim, evita-se criar um segundo caminho geografico de filtro entre UF e FATO_PND.

### Preservacao dos resultados

A transformacao nao recalcula:

- `PROFICIENCIA`;
- `NT_OBJ`;
- `NT_DIS`;
- `NT_GER`;
- `QT_ACERTOS`.

Os 759.140 registros da Gold deverao reproduzir diretamente os valores da Silver.

Valores negativos de `PROFICIENCIA` sao preservados.

Nao sera imposto na Gold limite inferior adicional a `PROFICIENCIA`, `NT_OBJ`, `NT_DIS` ou `NT_GER`, porque isso alteraria uma decisao metodologica ja resolvida e validada na Silver.

`QT_ACERTOS` permanece sujeito a regra semantica de contagem nao negativa.

### Padrao oficial de proficiencia da PND 2025

A classificacao de desempenho utilizada na Gold nao sera baseada em um ponto medio arbitrario da escala.

A referencia adotada e o padrao oficial estabelecido pelo Inep para a PND 2025.

A **Nota Tecnica nº 1/2026/GPP/GAB-INEP** documenta que os pontos de corte foram definidos por meio do **Metodo de Angoff Modificado** e posteriormente transpostos para a escala de proficiencia da Teoria de Resposta ao Item (TRI). Na secao 8.1, o Inep estabelece, para todas as areas da PND:

```text
Basico: 50 pontos
Adequado: 70 pontos
```

Fonte oficial:

INSTITUTO NACIONAL DE ESTUDOS E PESQUISAS EDUCACIONAIS ANISIO TEIXEIRA. **Nota Tecnica nº 1/2026/GPP/GAB-INEP**. Apresentacao dos procedimentos adotados para estabelecimento dos pontos de corte da Prova Nacional Docente – PND por meio da aplicacao do Metodo de Angoff Modificado, e subsequente transposicao dos resultados para a escala de proficiencia da Teoria de Resposta ao Item (TRI). Brasilia: Inep, 2026. Disponivel em: <https://download.inep.gov.br/pnd/notas_tecnicas/SEI_1873050_nota_tecnica_1.pdf>. Acesso em: 19 ago. 2026.

A **Nota Tecnica nº 44/2025/CEI/CGGI/DAES-INEP** demonstra que a proficiencia individual das questoes objetivas e estimada pela TRI e que a `NT_OBJ` e obtida pela transformacao dessa proficiencia para a escala de divulgacao de 0 a 100, com constantes especificas de cada area. Essas constantes sao ancoradas no ponto de corte definido pelo metodo de Angoff. A nota objetiva e, portanto, a variavel dos microdados compativel com os pontos de corte oficiais.

Fonte oficial:

INSTITUTO NACIONAL DE ESTUDOS E PESQUISAS EDUCACIONAIS ANISIO TEIXEIRA. **Nota Tecnica nº 44/2025/CEI/CGGI/DAES-INEP**. Metodologia de calculo da nota geral dos participantes do Enade das Licenciaturas e da Prova Nacional Docente (PND), edicoes de 2025. Brasilia: Inep, 2025. Disponivel em: <https://download.inep.gov.br/pnd/notas_tecnicas/SEI_1854638_nota_tecnica_44.pdf>. Acesso em: 19 ago. 2026.

A apresentacao oficial dos resultados da PND e do Enade das Licenciaturas 2025 confirma a interpretacao: sao considerados **proficientes** os participantes com desempenho igual ou superior a 50 pontos na escala de cada area e sao apresentados dois padroes de proficiencia.

Fonte oficial:

INSTITUTO NACIONAL DE ESTUDOS E PESQUISAS EDUCACIONAIS ANISIO TEIXEIRA. **PND e Enade das Licenciaturas: resultados de 2025**. Brasilia: Inep, 2026. p. 22. Disponivel em: <https://download.inep.gov.br/educacao_superior/enade/pnd_e_enade_2025_cursos.pdf>. Acesso em: 19 ago. 2026.

Com base nessas fontes, a Gold aplica a seguinte classificacao sobre `NT_OBJ`:

```text
NT_OBJ < 50              → NAO_PROFICIENTE
50 <= NT_OBJ < 70        → PADRAO_1
NT_OBJ >= 70             → PADRAO_2
```

Assim:

```text
PROFICIENTE = PADRAO_1 + PADRAO_2
NAO_PROFICIENTE = NT_OBJ < 50
```

O corte de 50 pontos **nao representa "50% de acertos" nem simplesmente a metade de uma escala escolhida pelo projeto**. Ele representa o ponto de corte oficial de proficiencia definido pelo Inep mediante procedimento de estabelecimento de padroes, com Metodo de Angoff Modificado e ancoragem na TRI.

O valor de 70 pontos corresponde ao segundo ponto de corte oficial, denominado `Adequado` na Nota Tecnica nº 1/2026. Na apresentacao dos resultados, os participantes proficientes sao organizados nos padroes 1 e 2; por isso, a Gold operacionaliza o primeiro intervalo proficiente como `PADRAO_1` e o segundo como `PADRAO_2`.

### Por que o corte nao e aplicado a NT_GER ou NT_DIS

A regra anterior do projeto, que considerava simultaneamente:

```text
NT_OBJ < 50
NT_GER < 50
NT_DIS < 5
```

foi **descartada antes da execucao da FATO_PND Gold**.

Apos consulta a documentacao tecnica oficial, nao foi encontrada base para interpretar `NT_GER < 50` ou `NT_DIS < 5` como pontos de corte oficiais de proficiencia.

A nota geral possui finalidade distinta. O Guia de Apoio Tecnico da PND informa que a Nota Geral resulta da ponderacao de 80% da nota objetiva e 20% da nota discursiva. Portanto, ela continuara disponivel para analises de media e distribuicao, mas nao sera utilizada para reproduzir o padrao oficial de proficiencia.

Referencia complementar:

INSTITUTO NACIONAL DE ESTUDOS E PESQUISAS EDUCACIONAIS ANISIO TEIXEIRA. **Guia de Apoio Tecnico – Prova Nacional Docente**. Brasilia: Inep, 2026. Disponivel em: <https://download.inep.gov.br/pnd/guia_apoio_tecnico_pnd_2026.pdf>. Acesso em: 19 ago. 2026.

`NT_DIS` tambem continuara como resultado descritivo. Nao sera criado um limite de 5 pontos como se representasse proficiencia oficial.

`PROFICIENCIA` permanece preservada na escala original da TRI encontrada nos microdados. Seus valores negativos continuam validos e nao sao truncados. A classificacao de desempenho nao e realizada diretamente sobre esse campo porque os proprios microdados ja disponibilizam `NT_OBJ`, que corresponde a transformacao da proficiencia objetiva para a escala oficial de divulgacao.

### Materializacao do padrao na Gold

Diferentemente de medias, percentuais e variacoes, `PADRAO_DESEMPENHO` nao depende do contexto de filtro do Power BI. E uma classificacao deterministica de cada registro a partir de um padrao oficial.

Por esse motivo, a Gold passa a materializar:

```text
PADRAO_DESEMPENHO
```

Essa coluna permite que o Power BI calcule, de forma simples e auditavel:

```text
total de nao proficientes
total de proficientes
% de proficientes
% de nao proficientes
distribuicao entre Padrao 1 e Padrao 2
```

Os percentuais e contagens continuam sendo medidas DAX, pois dependem do contexto de filtro por UF, municipio e area.

### Validacao prevista

A validacao independente verifica:

- 759.140 registros;
- ano unico 2025;
- 27 UFs de prova;
- 17 areas;
- 750 municipios de prova;
- zero ausencias nos dez campos Gold;
- igualdade dos nove campos de origem nos 759.140 registros Gold ↔ Silver;
- `NT_OBJ` dentro da escala oficial 0–100;
- classificacao independente de `PADRAO_DESEMPENHO` a partir dos cortes oficiais de 50 e 70 pontos;
- dominio exclusivo `NAO_PROFICIENTE`, `PADRAO_1` e `PADRAO_2`;
- ausencia de chaves orfas nas quatro dimensoes relacionadas;
- coerencia municipio → UF;
- `QT_ACERTOS` nao negativo;
- preservacao dos valores negativos de `PROFICIENCIA`;
- diagnostico dos valores minimos, maximos e negativos sem impor dominio artificial a `PROFICIENCIA`, `NT_DIS` ou `NT_GER`.

A transformacao e a validacao independente foram executadas com sucesso.

Resultados confirmados:

- 759.140 registros;
- ano unico 2025;
- 27 UFs de prova;
- 17 areas;
- 750 municipios de prova;
- zero resultados ausentes;
- 759.140 registros comparados diretamente com a Silver;
- resultados Gold = Silver;
- `NT_OBJ` integralmente na escala 0–100;
- zero chaves orfas em `DIM_UF`, `DIM_TEMPO`, `DIM_AREA_PND` e `DIM_MUNICIPIO`;
- coerencia `CO_MUNICIPIO_PROVA → UF_PROVA`: OK;
- valores negativos de `PROFICIENCIA` preservados.

A classificacao oficial derivada de `NT_OBJ` resultou em:

```text
NAO_PROFICIENTE (NT_OBJ < 50):        265.932
PADRAO_1 (50 <= NT_OBJ < 70):         304.638
PADRAO_2 (NT_OBJ >= 70):              188.570
PROFICIENTES (PADRAO_1 + PADRAO_2):   493.208
PERCENTUAL DE PROFICIENTES:           64,97%
```

O percentual de 64,97% reproduz, com arredondamento, o patamar de aproximadamente 65% divulgado oficialmente pelo Inep para a PND 2025, funcionando como evidencia externa adicional de coerencia da classificacao implementada. Essa comparacao nao substitui a validacao registro a registro com a Silver, mas reforca a plausibilidade do resultado agregado.

Diagnostico numerico observado:

```text
PROFICIENCIA: min=-3,976610 | max=2,688530 | negativos=389.188
NT_OBJ:       min=0        | max=100      | negativos=0
NT_DIS:       min=0        | max=10       | negativos=0
NT_GER:       min=0        | max=100      | negativos=0
QT_ACERTOS:   min=0        | max=77       | negativos=0
```

Resultado final:

`FATO_PND GOLD: OK`

Status:

`FATO_PND ✅ concluida e validada`

---

## 13.7 Validacao global da camada Gold

Apos a validacao individual das cinco dimensoes e das cinco tabelas fato, foi implementado um validador transversal do modelo dimensional:

`src/gold/validar_gold.py`

### Objetivo

A validacao global nao substitui os validadores especificos de cada fonte.

Os validadores individuais verificam a transformacao de cada tabela e, quando aplicavel, sua reproducao direta da Silver.

O validador global possui outro objetivo: confirmar que **o conjunto das tabelas Gold forma um modelo dimensional internamente coerente antes de ser consumido pelo Power BI**.

Essa separacao e deliberada:

```text
validacao individual
    ↓
confirma cada tabela isoladamente

validacao global
    ↓
confirma o funcionamento do conjunto dimensional
```

### Arquivos verificados

O script exige a existencia das cinco dimensoes:

```text
data/gold/dimensoes/dim_uf.parquet
data/gold/dimensoes/dim_tempo.parquet
data/gold/dimensoes/dim_etapa.parquet
data/gold/dimensoes/dim_area_pnd.parquet
data/gold/dimensoes/dim_municipio.parquet
```

e das cinco fatos:

```text
data/gold/fatos/fato_rendimento.parquet
data/gold/fatos/fato_tdi.parquet
data/gold/fatos/fato_ideb.parquet
data/gold/fatos/fato_saeb.parquet
data/gold/fatos/fato_pnd.parquet
```

A ausencia de qualquer arquivo provoca falha explicita.

### Validacao das dimensoes

Sao verificados:

- esquema e ordem das colunas;
- quantidade esperada de registros;
- ausencia de valores nulos;
- unicidade das chaves dimensionais;
- dominio completo das 27 UFs;
- 18 anos em `DIM_TEMPO`, correspondentes a 2007–2023 e 2025;
- duas etapas e sua ordem analitica;
- 17 codigos de area da PND;
- 750 municipios de prova;
- pertencimento das UFs de `DIM_MUNICIPIO` ao dominio de `DIM_UF`.

### Validacao das fatos

O script verifica os esquemas e as cardinalidades ja confirmadas pelas validacoes individuais:

```text
FATO_RENDIMENTO: 2.754
FATO_TDI:           918
FATO_IDEB:          486
FATO_SAEB:          972
FATO_PND:       759.140
```

Tambem sao reavaliados os graos das quatro fatos agregadas:

```text
FATO_RENDIMENTO
ANO + UF + ETAPA + REDE + INDICADOR

FATO_TDI
ANO + UF + ETAPA + REDE

FATO_IDEB
ANO + UF + ETAPA + REDE

FATO_SAEB
ANO + UF + ETAPA + REDE + DISCIPLINA
```

A `FATO_PND` e tratada de forma diferente. Como a fonte publica nao disponibiliza identificador individual do participante, o validador **nao inventa uma chave composta artificial nem exige unicidade de uma combinacao de notas e atributos**. Ele preserva a decisao metodologica de que cada linha corresponde a um registro individual valido da prova.

### Dominios analiticos

O validador global confirma:

- `PUBLICA` como unica rede das quatro fatos historicas;
- Rendimento entre 0 e 100;
- TDI entre 0 e 100;
- IDEB entre 0 e 10;
- proficiencia do SAEB entre 0 e 500;
- `LP` e `MT` como disciplinas do SAEB;
- as tres categorias de Rendimento: `APROVACAO`, `REPROVACAO` e `ABANDONO`;
- `NT_OBJ` da PND entre 0 e 100;
- `QT_ACERTOS` da PND nao negativo;
- `PADRAO_DESEMPENHO` restrito a `NAO_PROFICIENTE`, `PADRAO_1` e `PADRAO_2`;
- consistencia da classificacao da PND com os cortes oficiais de 50 e 70 pontos aplicados a `NT_OBJ`.

Os valores negativos de `PROFICIENCIA` da PND continuam preservados. O validador global nao cria dominio artificial para essa variavel.

### Integridade referencial

As quatro fatos historicas sao verificadas contra:

```text
DIM_UF
DIM_TEMPO
DIM_ETAPA
```

A PND e verificada contra:

```text
DIM_UF
DIM_TEMPO
DIM_AREA_PND
DIM_MUNICIPIO
```

Qualquer chave da fato sem correspondencia na respectiva dimensao provoca falha.

Tambem e validada a coerencia:

`CO_MUNICIPIO_PROVA → UF_PROVA`

contra `DIM_MUNICIPIO`.

### Reproducao dos dominios pelas dimensoes

Alem de verificar se nao existem chaves orfas, o script realiza a validacao inversa.

As dimensoes devem representar exatamente os dominios efetivamente utilizados pelas fatos:

- `DIM_UF` = conjunto de UFs das fatos;
- `DIM_TEMPO` = uniao dos anos das fatos;
- `DIM_ETAPA` = conjunto de etapas das fatos historicas;
- `DIM_AREA_PND` = conjunto de `CO_GRUPO` da `FATO_PND`;
- `DIM_MUNICIPIO` = conjunto de municipios da `FATO_PND`.

Essa regra evita dimensoes com categorias artificiais, registros sem uso ou anos criados apenas para preencher lacunas do calendario.

### Relacoes previstas no Power BI

A validacao global confirma os dados necessarios para as seguintes relacoes `1:*`:

```text
DIM_UF[UF]
    → FATO_RENDIMENTO[UF]
    → FATO_TDI[UF]
    → FATO_IDEB[UF]
    → FATO_SAEB[UF]
    → FATO_PND[UF_PROVA]

DIM_TEMPO[ANO]
    → todas as fatos

DIM_ETAPA[ETAPA]
    → FATO_RENDIMENTO[ETAPA]
    → FATO_TDI[ETAPA]
    → FATO_IDEB[ETAPA]
    → FATO_SAEB[ETAPA]

DIM_AREA_PND[CO_GRUPO]
    → FATO_PND[CO_GRUPO]

DIM_MUNICIPIO[CO_MUNICIPIO]
    → FATO_PND[CO_MUNICIPIO_PROVA]
```

A direcao de filtro recomendada permanece:

`dimensao → fato`

Nao sera criada relacao direta `DIM_MUNICIPIO → DIM_UF`, pois a FATO_PND ja possui relacionamento direto com ambas e a relacao adicional criaria um segundo caminho geografico de filtragem.

### Regra de fechamento

A validacao global foi executada com sucesso.

Resultados confirmados:

```text
DIM_UF: 27
DIM_TEMPO: 18
DIM_ETAPA: 2
DIM_AREA_PND: 17
DIM_MUNICIPIO: 750

FATO_RENDIMENTO: 2.754
FATO_TDI: 918
FATO_IDEB: 486
FATO_SAEB: 972
FATO_PND: 759.140
```

A integridade referencial foi confirmada entre:

```text
Fatos historicas
    → DIM_UF
    → DIM_TEMPO
    → DIM_ETAPA

FATO_PND
    → DIM_UF
    → DIM_TEMPO
    → DIM_AREA_PND
    → DIM_MUNICIPIO
```

Tambem foram confirmados:

- coerencia `CO_MUNICIPIO_PROVA → UF_PROVA`;
- dimensoes correspondendo exatamente aos dominios efetivamente utilizados pelas fatos;
- classificacao oficial da PND com 265.932 nao proficientes, 304.638 no Padrao 1 e 188.570 no Padrao 2;
- 493.208 participantes proficientes, equivalentes a 64,97%.

Resultado final:

`MODELO DIMENSIONAL GOLD: OK`

Status:

`CAMADA GOLD ✅ concluida e validada globalmente`

A camada Gold esta pronta para consumo no Power BI.

---

## 14. Situacao atual

Todas as cinco dimensoes e as cinco tabelas fato da camada Gold estao concluidas e validadas individualmente e em conjunto.
A validacao global retornou `MODELO DIMENSIONAL GOLD: OK`. A camada Gold esta pronta para ser consumida pelo Power BI.


| Componente | Situacao |
|---|---|
| Modelo dimensional | ✅ definido |
| Dimensoes | ✅ concluidas e validadas |
| FATO_RENDIMENTO | ✅ concluida e validada |
| FATO_TDI | ✅ concluida e validada |
| FATO_IDEB | ✅ concluida e validada |
| FATO_SAEB | ✅ concluida e validada |
| FATO_PND | ✅ concluida e validada |
| Validacao referencial global | ✅ implementada e validada |
| Power BI sobre Gold | ✅ migrado, modelado e validado |

---

## 15. Historico de decisoes

| Data | Decisao |
|---|---|
| 19/08/2026 | Iniciada a definicao da camada Gold apos conclusao integral da Silver |
| 19/08/2026 | Definido modelo dimensional com fatos separadas por fonte, preservando os diferentes graos |
| 19/08/2026 | Definidas dimensoes conformadas `DIM_UF`, `DIM_TEMPO` e `DIM_ETAPA` para as series historicas |
| 19/08/2026 | Definidas `DIM_AREA_PND` e `DIM_MUNICIPIO` para reduzir repeticao na fato individual da PND |
| 19/08/2026 | Definido uso de chaves naturais estaveis em vez de chaves substitutas artificiais |
| 19/08/2026 | Definido que a Gold sera construida somente a partir da Silver, sem leitura direta de RAW ou Bronze |
| 19/08/2026 | Definido que nao havera `DIM_REDE`, pois o escopo historico atual possui apenas a rede canonica `PUBLICA` |
| 19/08/2026 | Definido que `DISCIPLINA` e `INDICADOR` permanecerao em suas respectivas fatos, evitando dimensoes sem ganho analitico no escopo atual |
| 19/08/2026 | Definido que `FATO_SAEB` usara diretamente os valores oficiais da Silver, sem `SOMA_PESO`, `SOMA_VALOR_PONDERADO` ou recomposicao a partir de escolas |
| 19/08/2026 | Definido que medidas agregadas e percentuais dependentes de filtro serao calculados no Power BI, nao persistidos como colunas derivadas na Gold |
| 19/08/2026 | Definido que `DIM_MUNICIPIO` nao recebera nome do municipio por leitura direta do RAW; qualquer enriquecimento futuro sera documentado antes da implementacao |
| 19/08/2026 | Implementados transformador e validador independente das cinco dimensoes Gold; conclusao depende da execucao e validacao contra as Silvers |
| 19/08/2026 | Transformacao das dimensoes Gold executada com sucesso: 27 UFs, 18 anos, 2 etapas, 17 areas PND e 750 municipios |
| 19/08/2026 | Validacao independente das dimensoes concluida; chaves unicas, reproducao das Silvers e dominios dimensionais confirmados; resultado `DIMENSOES GOLD: OK` |
| 19/08/2026 | Implementados transformador e validador independente da `FATO_RENDIMENTO`, preservando os 2.754 valores da Silver sem recalculo e com validacao referencial contra `DIM_UF`, `DIM_TEMPO` e `DIM_ETAPA` |
| 19/08/2026 | `FATO_RENDIMENTO` executada e validada com 2.754 registros; igualdade Gold ↔ Silver e integridade referencial confirmadas; resultado `FATO_RENDIMENTO GOLD: OK` |
| 19/08/2026 | Implementados transformador e validador independente da `FATO_TDI`, preservando 918 valores da Silver sem recalculo e validando `DIM_UF`, `DIM_TEMPO` e `DIM_ETAPA` |
| 19/08/2026 | `FATO_TDI` executada e validada com 918 registros; igualdade Gold ↔ Silver e integridade referencial confirmadas; resultado `FATO_TDI GOLD: OK` |
| 19/08/2026 | Implementados transformador e validador independente da `FATO_IDEB`, preservando as nove edicoes 2007–2023, os 486 valores da Silver e a integridade referencial com as dimensoes |
| 19/08/2026 | `FATO_IDEB` executada e validada com 486 registros e 9 edicoes; igualdade Gold ↔ Silver e integridade referencial confirmadas; resultado `FATO_IDEB GOLD: OK` |
| 19/08/2026 | Implementados transformador e validador independente da `FATO_SAEB`, preservando as 972 proficiencias oficiais da Silver, sem ponderacao escolar ou recomposicao, e validando integridade com as dimensoes |
| 19/08/2026 | `FATO_SAEB` executada e validada com 972 registros e 9 edicoes; proficiencias Gold = Silver, dominio 0–500 e integridade referencial confirmados; resultado `FATO_SAEB GOLD: OK` |
| 19/08/2026 | Implementados transformador e validador independente da `FATO_PND`, preservando o grao individual de 759.140 registros e relacionamentos com tempo, UF, area e municipio |
| 19/08/2026 | Retificada a metodologia da PND antes da execucao da Gold: descartados os cortes arbitrarios em `NT_GER` e `NT_DIS`; adotados os pontos de corte oficiais do Inep aplicados a `NT_OBJ` |
| 19/08/2026 | Documentadas as referencias oficiais dos cortes: Nota Tecnica nº 1/2026/GPP/GAB-INEP (Angoff Modificado; Basico=50 e Adequado=70), Nota Tecnica nº 44/2025/CEI/CGGI/DAES-INEP (transformacao TRI → `NT_OBJ`) e apresentacao oficial dos resultados de 2025 |
| 19/08/2026 | `PADRAO_DESEMPENHO` passou a ser materializado na FATO_PND como classificacao deterministica: `NAO_PROFICIENTE`, `PADRAO_1` e `PADRAO_2`; percentuais permanecem medidas DAX |
| 19/08/2026 | `FATO_PND` executada e validada com 759.140 registros; resultados Gold = Silver e integridade referencial confirmados; resultado `FATO_PND GOLD: OK` |
| 19/08/2026 | Classificacao oficial da PND validada: 265.932 nao proficientes, 304.638 no Padrao 1, 188.570 no Padrao 2 e 493.208 proficientes (64,97%) |
| 19/08/2026 | Concluidas e validadas todas as cinco tabelas fato da camada Gold; proxima etapa definida como validacao referencial global do modelo dimensional |
| 19/08/2026 | Implementado `src/gold/validar_gold.py` para validacao transversal das cinco dimensoes e cinco fatos antes do consumo no Power BI |
| 19/08/2026 | Documentada a distincao entre validacao individual das tabelas e validacao global do modelo dimensional |
| 19/08/2026 | Definido que a Gold so sera considerada integralmente pronta para o Power BI apos o retorno `MODELO DIMENSIONAL GOLD: OK` |
| 19/08/2026 | Executada a validacao global da camada Gold; todas as dimensoes, fatos, dominios e relacionamentos foram aprovados |
| 19/08/2026 | Confirmado `MODELO DIMENSIONAL GOLD: OK`; camada Gold concluida e liberada para consumo no Power BI |
