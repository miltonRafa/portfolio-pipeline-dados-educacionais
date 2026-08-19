# Camada Gold

## 1. Objetivo

A camada Gold organiza os dados já auditados e padronizados na Silver em um modelo dimensional voltado à análise e ao consumo no Power BI.

A Gold não substituirá a Silver como camada de rastreabilidade. Sua função é:

- reduzir redundâncias analíticas;
- separar dimensões e fatos;
- conformar chaves compartilhadas entre as fontes;
- preservar explicitamente o grão de cada conjunto;
- facilitar relacionamentos `1:*` no Power BI;
- evitar cálculos ou agregações que alterem os valores oficiais já definidos na Silver;
- fornecer uma base simples, estável e reproduzível para medidas DAX e visualizações.

A camada Gold será construída somente a partir das tabelas Silver já concluídas e validadas.

Não haverá leitura direta de arquivos RAW ou Bronze na transformação Gold.

---

## 2. Situação de entrada

A Gold parte das seguintes tabelas Silver concluídas:

| Fonte | Arquivo Silver | Situação |
|---|---|---|
| Rendimento Escolar | `data/silver/rendimento/rendimento_2007_2023.parquet` | ✅ concluída e validada |
| TDI | `data/silver/tdi/tdi_2007_2023.parquet` | ✅ concluída e validada |
| IDEB | `data/silver/ideb/ideb_2007_2023.parquet` | ✅ concluída e validada |
| SAEB | `data/silver/saeb/saeb_2007_2023.parquet` | ✅ concluída e validada |
| PND 2025 | `data/silver/pnd/pnd_2025.parquet` | ✅ concluída e validada |

A Gold não reabrirá decisões metodológicas já resolvidas na Silver, salvo se uma nova evidência material demonstrar necessidade de correção.

---

## 3. Princípios de modelagem

### 3.1 Modelo dimensional

O projeto adotará um modelo dimensional com:

- dimensões conformadas compartilhadas pelas tabelas fato quando o domínio for efetivamente comum;
- fatos separados quando os grãos forem diferentes;
- relacionamentos preferencialmente `1:*`;
- direção de filtro da dimensão para a fato no Power BI.

Não será criada uma tabela fato única para todos os indicadores.

A razão é estrutural: Rendimento, TDI, IDEB, SAEB e PND não possuem o mesmo grão.

Forçar a união produziria:

- campos nulos artificiais;
- perda de clareza semântica;
- risco de agregações incorretas;
- dificuldade de manutenção;
- relações analíticas menos transparentes.

### 3.2 Chaves naturais

A Gold utilizará as chaves naturais já presentes nas fontes sempre que elas forem estáveis e suficientes.

Exemplos:

- `UF`;
- `ANO`;
- `ETAPA`;
- `CO_GRUPO`;
- `CO_MUNICIPIO_PROVA`.

Não serão criadas chaves substitutas apenas por convenção.

Essa decisão evita complexidade sem benefício analítico no escopo atual.

### 3.3 Rede pública

A população histórica da Silver já está restrita à rede canônica `PUBLICA`.

Não será criada `DIM_REDE`, porque não existe variação analítica de rede na Gold atual.

O campo `REDE` poderá permanecer nas fatos históricas como informação explícita de escopo e para facilitar auditoria visual, mas não funcionará como dimensão de filtro.

### 3.4 Proveniência

Metadados detalhados de arquivo, aba, linha e coluna de origem permanecem na Silver.

A Gold não duplicará toda a proveniência física das fontes.

Quando for necessário auditar um valor Gold, a validação deverá reconstruir sua origem a partir da Silver correspondente.

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

Código:

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

## 5. Dimensões

## 5.1 `DIM_UF`

### Objetivo

Fornecer uma dimensão geográfica comum para:

- Rendimento Escolar;
- TDI;
- IDEB;
- SAEB;
- PND.

### Grão

`uma linha por UF`

### Colunas

```text
UF
```

São esperadas 27 UFs.

A dimensão será construída a partir da união dos valores de UF presentes nas Silvers.

Na PND, o relacionamento usará `UF_PROVA`.

Isso não altera a semântica da PND: a UF continua representando a Unidade Federativa do município de aplicação da prova, e não residência do participante.

### Decisão

Não será acrescentado nome completo da UF nesta primeira versão da Gold sem uma fonte de referência já integrada à Silver.

A sigla é suficiente para o relacionamento e preserva a origem dos dados.

---

## 5.2 `DIM_TEMPO`

### Objetivo

Conformar o eixo anual utilizado pelas cinco fatos.

### Grão

`uma linha por ano com observação em pelo menos uma fato`

### Colunas

```text
ANO
```

A dimensão será construída pela união dos anos existentes nas Silvers.

Espera-se:

- 2007 a 2023 nas séries históricas;
- 2025 na PND.

O ano de 2024 não será criado artificialmente, porque nenhuma das fontes atuais possui observação analítica para esse ano.

---

## 5.3 `DIM_ETAPA`

### Objetivo

Conformar as duas etapas do Ensino Fundamental utilizadas pelas séries históricas.

### Grão

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

`ORDEM_ETAPA` é um atributo técnico de ordenação para o Power BI.

A PND não será relacionada à `DIM_ETAPA`, porque sua estrutura analítica não representa etapa escolar da Educação Básica.

---

## 5.4 `DIM_AREA_PND`

### Objetivo

Separar da fato individual da PND o domínio repetitivo das áreas da prova.

### Grão

`uma linha por CO_GRUPO`

### Colunas

```text
CO_GRUPO
AREA_PROVA
```

São esperadas 17 áreas.

A dimensão será derivada exclusivamente dos pares únicos `CO_GRUPO + AREA_PROVA` existentes na Silver da PND.

A validação deverá confirmar relação `1:1` entre código e rótulo.

---

## 5.5 `DIM_MUNICIPIO`

### Objetivo

Separar da fato PND o domínio dos municípios efetivamente presentes na população analítica.

### Grão

`uma linha por CO_MUNICIPIO_PROVA`

### Colunas

```text
CO_MUNICIPIO
UF
```

São esperados 750 municípios na população Silver atualmente validada.

### Decisão sobre nome do município

A Silver atual da PND contém o código do município e a UF, mas não contém o nome do município.

Por isso, a Gold não fará leitura direta do dicionário RAW para acrescentar `NOME_MUNICIPIO`.

Essa decisão preserva a regra arquitetural:

`Gold ← Silver`

e evita um atalho:

`Gold ← Raw`

Se o nome do município se tornar necessário para a experiência final no Power BI, será criada uma etapa de enriquecimento explicitamente documentada antes de sua implementação.

### Relacionamentos

`DIM_MUNICIPIO` será relacionada diretamente à `FATO_PND`.

Ela não será relacionada à `DIM_UF`, evitando caminhos de filtro ambíguos no modelo.

---

## 6. Tabelas fato

## 6.1 `FATO_RENDIMENTO`

### Origem

`data/silver/rendimento/rendimento_2007_2023.parquet`

### Grão

`ANO + UF + ETAPA + REDE + INDICADOR`

### Cardinalidade esperada

`2.754 registros`

### Colunas analíticas

```text
ANO
UF
ETAPA
REDE
INDICADOR
VALOR
```

A Gold não recalculará taxas.

`VALOR` deverá reproduzir exatamente o valor analítico existente na Silver.

### Indicadores

Os indicadores permanecem na própria fato.

Não será criada `DIM_INDICADOR` nesta etapa porque:

- o domínio é pequeno;
- somente a fato de Rendimento utiliza esse atributo;
- uma dimensão separada não acrescentaria vantagem analítica relevante no escopo atual.

---

## 6.2 `FATO_TDI`

### Origem

`data/silver/tdi/tdi_2007_2023.parquet`

### Grão

`ANO + UF + ETAPA + REDE`

### Cardinalidade esperada

`918 registros`

### Colunas analíticas

```text
ANO
UF
ETAPA
REDE
VALOR
```

Os valores deverão ser copiados da Silver sem nova agregação.

---

## 6.3 `FATO_IDEB`

### Origem

`data/silver/ideb/ideb_2007_2023.parquet`

### Grão

`ANO + UF + ETAPA + REDE`

### Cardinalidade esperada

`486 registros`

### Colunas analíticas

```text
ANO
UF
ETAPA
REDE
VALOR
```

A Gold preservará somente as edições efetivamente existentes.

Não será criada interpolação para anos sem IDEB.

---

## 6.4 `FATO_SAEB`

### Origem

`data/silver/saeb/saeb_2007_2023.parquet`

### Grão

`ANO + UF + ETAPA + REDE + DISCIPLINA`

### Cardinalidade esperada

`972 registros`

### Colunas analíticas

```text
ANO
UF
ETAPA
REDE
DISCIPLINA
VALOR
```

### Regra crítica

A Gold utilizará diretamente os valores oficiais já selecionados na Silver.

Não serão criados:

```text
SOMA_PESO
SOMA_VALOR_PONDERADO
```

nem qualquer outra reconstrução por média de escolas.

A comparação metodológica realizada para o SAEB 2023 demonstrou que a média escolar ponderada por `NU_PRESENTES` não reproduz o agregado oficial de UF.

Portanto, a Gold não repetirá uma regra já rejeitada na Silver.

### Disciplina

`DISCIPLINA` permanecerá na própria fato.

Não será criada `DIM_DISCIPLINA` nesta etapa porque:

- existem apenas `LP` e `MT`;
- somente o SAEB utiliza o atributo;
- separar duas categorias em uma dimensão não oferece benefício suficiente para justificar a complexidade adicional.

---

## 6.5 `FATO_PND`

### Origem

`data/silver/pnd/pnd_2025.parquet`

### Grão

`um registro individual válido da prova`

### Cardinalidade esperada

`759.140 registros`

### Colunas analíticas previstas

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

A fato não transportará:

- `AREA_PROVA`, porque esse atributo ficará em `DIM_AREA_PND`;
- metadados físicos de proveniência;
- vetores de respostas;
- respostas do Questionário de Percepção de Prova.

### Identificador individual

A fonte não fornece identificador pessoal ou de participante.

A Gold não inventará uma chave de participante.

A unicidade e rastreabilidade física continuam disponíveis na Silver por `LINHA_ORIGEM_BRONZE`.

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

### Direção de filtro

A direção padrão será:

`dimensão → fato`

Não serão criados filtros bidirecionais por padrão.

Qualquer exceção futura deverá ser justificada pelo caso analítico específico.

---

## 8. Limites entre Gold e Power BI

A Gold armazenará dados analíticos de base.

Cálculos de apresentação e indicadores derivados deverão permanecer, preferencialmente, na camada semântica do Power BI.

Exemplos de medidas que não precisam ser materializadas como colunas Gold:

- média de IDEB;
- média SAEB por disciplina;
- média de aprovação, reprovação ou abandono;
- média da TDI;
- variação entre primeiro e último ano selecionado;
- média de `NT_OBJ`;
- média de `NT_DIS`;
- média de `NT_GER`;
- média de `QT_ACERTOS`;
- percentual de participantes PND abaixo de um limiar;
- contagem de participantes.

### Justificativa

Esses cálculos dependem do contexto de filtro do relatório.

Persisti-los na Gold como colunas ou agregados fixos poderia:

- duplicar lógica;
- gerar inconsistência entre Python e DAX;
- limitar a interatividade;
- criar dados derivados desnecessários.

---

## 9. Tratamento dos valores PND

A Gold preservará os valores numéricos da Silver sem modificar seu domínio.

Em particular:

- `PROFICIENCIA` pode assumir valores negativos;
- `NT_OBJ` permanece entre os valores publicados pela fonte;
- `NT_DIS` permanece entre os valores publicados pela fonte;
- `NT_GER` permanece entre os valores publicados pela fonte;
- `QT_ACERTOS` permanece uma contagem não negativa.

Não haverá:

- truncamento;
- substituição de valores negativos por zero;
- normalização adicional;
- arredondamento adicional.

A Silver é a referência semântica para esses valores.

---

## 10. Validações da Gold

Toda transformação Gold deverá possuir validação independente.

As validações deverão confirmar, conforme aplicável:

- existência dos arquivos Silver esperados;
- cardinalidade esperada das fatos;
- unicidade das chaves das dimensões;
- inexistência de chaves órfãs nas fatos;
- domínio das 27 UFs;
- domínio das duas etapas;
- relação `CO_GRUPO → AREA_PROVA` sem ambiguidade;
- 750 municípios na população atual da PND;
- igualdade dos valores analíticos entre Silver e Gold;
- ausência de agregações não documentadas;
- ausência de duplicidades no grão de cada fato.

### Integridade referencial

Para cada chave estrangeira presente em uma fato, deverá existir exatamente uma chave correspondente na dimensão.

Exemplo:

```text
FATO_SAEB[UF] ⊆ DIM_UF[UF]
```

A execução deverá falhar se uma chave órfã for encontrada.

---

## 11. Regra de transformação

A Gold não realizará nova interpretação das fontes oficiais.

O fluxo será:

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
RAW     → preservação da fonte original
BRONZE  → ingestão reproduzível e rastreável
SILVER  → padronização, seleção semântica e validação
GOLD    → modelagem dimensional
POWER BI → medidas, contexto de filtro e visualização
```

---

## 12. Estratégia de implementação

A implementação seguirá esta ordem:

1. documentar o modelo dimensional;
2. gerar e validar as dimensões;
3. gerar e validar `FATO_RENDIMENTO`;
4. gerar e validar `FATO_TDI`;
5. gerar e validar `FATO_IDEB`;
6. gerar e validar `FATO_SAEB`;
7. gerar e validar `FATO_PND`;
8. validar integridade referencial global;
9. conectar a Gold ao Power BI;
10. recriar as medidas DAX sobre o novo modelo.

Essa ordem reduz o risco de criar relacionamentos antes de as chaves dimensionais estarem estáveis.

---

## 13. Política de falha

A Gold deverá falhar explicitamente se:

- uma Silver esperada não existir;
- uma dimensão possuir chave duplicada;
- uma fato possuir chave órfã;
- a cardinalidade esperada mudar sem documentação;
- o grão de uma fato deixar de ser único;
- surgir UF fora do domínio esperado;
- surgir etapa fora do domínio esperado;
- surgir `CO_GRUPO` sem área correspondente;
- a Gold alterar valores da Silver sem regra documentada.

É preferível interromper a execução do que produzir um modelo dimensional aparentemente válido com perda semântica.

---

## 13.1 Implementação das dimensões

Arquivos implementados:

`src/gold/dimensoes/transformar_dimensoes.py`

`src/gold/dimensoes/validar_dimensoes.py`

Saídas:

```text
data/gold/dimensoes/dim_uf.parquet
data/gold/dimensoes/dim_tempo.parquet
data/gold/dimensoes/dim_etapa.parquet
data/gold/dimensoes/dim_area_pnd.parquet
data/gold/dimensoes/dim_municipio.parquet
```

O transformador lê exclusivamente as Silvers concluídas.

Regras implementadas:

- `DIM_UF`: união das UFs das cinco Silvers, com exatamente 27 chaves únicas;
- `DIM_TEMPO`: união dos anos observados nas Silvers, preservando 2007–2023 e 2025, sem criar 2024 artificialmente;
- `DIM_ETAPA`: domínio `ANOS_INICIAIS` / `ANOS_FINAIS`, com `ORDEM_ETAPA` 1 e 2;
- `DIM_AREA_PND`: pares únicos `CO_GRUPO + AREA_PROVA`, com 17 áreas e relação 1:1;
- `DIM_MUNICIPIO`: pares únicos `CO_MUNICIPIO_PROVA + UF_PROVA`, com 750 municípios e uma única UF por código.

O validador é independente do transformador e reconstrói cada dimensão diretamente das Silvers.

A execução foi concluída com sucesso e a validação independente retornou:

`DIMENSÕES GOLD: OK`

Resultados confirmados:

- `DIM_UF`: 27 linhas, chave `UF` única;
- `DIM_TEMPO`: 18 linhas, cobrindo 2007–2023 e 2025;
- `DIM_ETAPA`: 2 linhas, com chave `ETAPA` única;
- `DIM_AREA_PND`: 17 linhas, com `CO_GRUPO` único;
- `DIM_MUNICIPIO`: 750 linhas, com `CO_MUNICIPIO` único;
- reprodução das Silvers: OK;
- domínios dimensionais: OK.

Status:

`DIMENSÕES GOLD ✅ concluídas e validadas`

---

## 13.2 Implementação da FATO_RENDIMENTO

Arquivos implementados:

`src/gold/rendimento/transformar_rendimento.py`

`src/gold/rendimento/validar_fato_rendimento.py`

Saída:

`data/gold/fatos/fato_rendimento.parquet`

A transformação lê exclusivamente:

`data/silver/rendimento/rendimento_2007_2023.parquet`

e mantém apenas as colunas analíticas:

```text
ANO
UF
ETAPA
REDE
INDICADOR
VALOR
```

Nenhuma taxa é recalculada.

A validação implementada verifica:

- 2.754 registros;
- grão único `ANO + UF + ETAPA + REDE + INDICADOR`;
- 17 anos;
- 27 UFs;
- duas etapas;
- rede única `PUBLICA`;
- três indicadores: `APROVACAO`, `REPROVACAO`, `ABANDONO`;
- ausência de valores nulos;
- domínio de taxas entre 0 e 100;
- igualdade dos 2.754 valores Gold ↔ Silver;
- inexistência de UFs órfãs em `DIM_UF`;
- inexistência de anos órfãos em `DIM_TEMPO`;
- inexistência de etapas órfãs em `DIM_ETAPA`.

A transformação e a validação independente foram executadas com sucesso.

Resultados confirmados:

- 2.754 registros;
- 17 anos;
- 27 UFs;
- 2 etapas;
- 3 indicadores;
- rede única `PUBLICA`;
- zero valores ausentes;
- grão `ANO + UF + ETAPA + REDE + INDICADOR` único;
- 2.754 registros comparados diretamente com a Silver;
- valores Gold = Silver;
- domínio das taxas 0–100;
- zero chaves órfãs em `DIM_UF`, `DIM_TEMPO` e `DIM_ETAPA`.

Resultado final:

`FATO_RENDIMENTO GOLD: OK`

Status:

`FATO_RENDIMENTO ✅ concluída e validada`

---

## 13.3 Implementação da FATO_TDI

Arquivos implementados:

`src/gold/tdi/transformar_tdi.py`

`src/gold/tdi/validar_fato_tdi.py`

Saída:

`data/gold/fatos/fato_tdi.parquet`

A transformação lê exclusivamente:

`data/silver/tdi/tdi_2007_2023.parquet`

e mantém as colunas analíticas:

```text
ANO
UF
ETAPA
REDE
TDI
```

Nenhuma taxa é recalculada.

A coluna `TDI` é preservada com o valor analítico definido na Silver.

A validação implementada verifica:

- 918 registros;
- grão único `ANO + UF + ETAPA + REDE`;
- 17 anos;
- 27 UFs;
- duas etapas;
- rede única `PUBLICA`;
- ausência de valores nulos;
- domínio da TDI entre 0 e 100;
- igualdade dos 918 valores Gold ↔ Silver;
- inexistência de UFs órfãs em `DIM_UF`;
- inexistência de anos órfãos em `DIM_TEMPO`;
- inexistência de etapas órfãs em `DIM_ETAPA`.

A transformação e a validação independente foram executadas com sucesso.

Resultados confirmados:

- 918 registros;
- 17 anos;
- 27 UFs;
- 2 etapas;
- rede única `PUBLICA`;
- zero valores ausentes;
- grão `ANO + UF + ETAPA + REDE` único;
- 918 registros comparados diretamente com a Silver;
- valores Gold = Silver;
- domínio da TDI entre 0 e 100;
- zero chaves órfãs em `DIM_UF`, `DIM_TEMPO` e `DIM_ETAPA`.

Resultado final:

`FATO_TDI GOLD: OK`

Status:

`FATO_TDI ✅ concluída e validada`

---

## 13.4 Implementação da FATO_IDEB

Arquivos implementados:

`src/gold/ideb/transformar_ideb.py`

`src/gold/ideb/validar_fato_ideb.py`

Saída:

`data/gold/fatos/fato_ideb.parquet`

A transformação lê exclusivamente:

`data/silver/ideb/ideb_2007_2023.parquet`

e mantém as colunas analíticas:

```text
ANO
UF
ETAPA
REDE
IDEB
```

Nenhum valor do IDEB é recalculado.

A Gold preserva somente as nove edições efetivamente existentes no recorte:

```text
2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021, 2023
```

Não são criadas observações para os anos intermediários.

A validação implementada verifica:

- 486 registros;
- grão único `ANO + UF + ETAPA + REDE`;
- nove edições;
- 27 UFs;
- duas etapas;
- rede única `PUBLICA`;
- ausência de valores nulos;
- domínio do IDEB entre 0 e 10;
- igualdade dos 486 valores Gold ↔ Silver;
- inexistência de UFs órfãs em `DIM_UF`;
- inexistência de anos órfãos em `DIM_TEMPO`;
- inexistência de etapas órfãs em `DIM_ETAPA`.

A transformação e a validação independente foram executadas com sucesso.

Resultados confirmados:

- 486 registros;
- 9 edições;
- 27 UFs;
- 2 etapas;
- rede única `PUBLICA`;
- zero valores ausentes;
- grão `ANO + UF + ETAPA + REDE` único;
- 486 registros comparados diretamente com a Silver;
- valores Gold = Silver;
- domínio do IDEB entre 0 e 10;
- zero chaves órfãs em `DIM_UF`, `DIM_TEMPO` e `DIM_ETAPA`.

Resultado final:

`FATO_IDEB GOLD: OK`

Status:

`FATO_IDEB ✅ concluída e validada`

---

## 13.5 Implementação da FATO_SAEB

Arquivos implementados:

`src/gold/saeb/transformar_saeb.py`

`src/gold/saeb/validar_fato_saeb.py`

Saída:

`data/gold/fatos/fato_saeb.parquet`

A transformação lê exclusivamente:

`data/silver/saeb/saeb_2007_2023.parquet`

e mantém as colunas analíticas:

```text
ANO
UF
ETAPA
REDE
DISCIPLINA
PROFICIENCIA
```

Nenhuma proficiência é recalculada ou recomposta.

A Gold preserva diretamente os valores oficiais já selecionados e validados na Silver.

### Regra metodológica crítica

Não são criadas colunas como:

```text
SOMA_PESO
SOMA_VALOR_PONDERADO
```

e não é aplicada média ponderada a partir dos microdados escolares.

Essa decisão é deliberada. A auditoria do SAEB 2023 demonstrou que a recomposição escolar ponderada por participantes não reproduz o agregado oficial de UF. Por isso, a Gold utiliza a Silver como referência semântica definitiva.

A política histórica de rede pública também é herdada da Silver. A Gold não tenta recompor redes administrativas por conta própria.

A validação implementada verifica:

- 972 registros;
- grão único `ANO + UF + ETAPA + REDE + DISCIPLINA`;
- nove edições;
- 27 UFs;
- duas etapas;
- duas disciplinas: `LP` e `MT`;
- rede única `PUBLICA`;
- ausência de proficiências nulas;
- domínio da proficiência entre 0 e 500;
- igualdade das 972 proficiências Gold ↔ Silver;
- inexistência de UFs órfãs em `DIM_UF`;
- inexistência de anos órfãos em `DIM_TEMPO`;
- inexistência de etapas órfãs em `DIM_ETAPA`.

Não será criada `DIM_DISCIPLINA` nesta versão da Gold. O domínio possui somente duas categorias e é utilizado apenas pela FATO_SAEB.

A transformação e a validação independente foram executadas com sucesso.

Resultados confirmados:

- 972 registros;
- 9 edições;
- 27 UFs;
- 2 etapas;
- 2 disciplinas: `LP` e `MT`;
- rede única `PUBLICA`;
- zero valores ausentes;
- grão `ANO + UF + ETAPA + REDE + DISCIPLINA` único;
- 972 registros comparados diretamente com a Silver;
- proficiências Gold = Silver;
- domínio da proficiência entre 0 e 500;
- zero chaves órfãs em `DIM_UF`, `DIM_TEMPO` e `DIM_ETAPA`.

Resultado final:

`FATO_SAEB GOLD: OK`

Status:

`FATO_SAEB ✅ concluída e validada`

---

## 13.6 Implementação da FATO_PND

Arquivos implementados:

`src/gold/pnd/transformar_pnd.py`

`src/gold/pnd/validar_fato_pnd.py`

Saída:

`data/gold/fatos/fato_pnd.parquet`

A transformação lê exclusivamente:

`data/silver/pnd/pnd_2025.parquet`

e preserva o grão individual já definido e validado na Silver:

`um registro individual válido da prova`

A fato mantém os campos necessários ao modelo analítico e acrescenta a classificação oficial de desempenho:

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

- `AREA_PROVA`, porque o rótulo passa a ser fornecido por `DIM_AREA_PND`;
- `TP_INSCRICAO_PND`;
- `IN_REAPLICACAO`;
- `CO_CADERNO`;
- `TP_PRES`;
- `TP_SIT_DISC`;
- `ARQUIVO_ORIGEM`;
- `LINHA_ORIGEM_BRONZE`;
- `GRANULARIDADE_ORIGEM`.

Os campos técnicos e variáveis que não participam do escopo atual continuam preservados na Silver. Sua retirada da Gold reduz redundância e mantém a fato orientada ao consumo analítico no Power BI.

A Gold não cria identificador artificial de participante. A fonte não disponibiliza um identificador pessoal, e registros distintos podem possuir os mesmos valores analíticos. Portanto, não será imposta uma falsa chave de unicidade baseada na combinação de notas, área ou localização.

### Integridade dimensional da PND

A validação verifica quatro relacionamentos:

```text
DIM_TEMPO[ANO] 1 ─── * FATO_PND[ANO]
DIM_UF[UF] 1 ─── * FATO_PND[UF_PROVA]
DIM_AREA_PND[CO_GRUPO] 1 ─── * FATO_PND[CO_GRUPO]
DIM_MUNICIPIO[CO_MUNICIPIO] 1 ─── * FATO_PND[CO_MUNICIPIO_PROVA]
```

Além da ausência de chaves órfãs, é verificada a coerência:

`CO_MUNICIPIO_PROVA → UF_PROVA`

contra o par correspondente em `DIM_MUNICIPIO`.

`DIM_MUNICIPIO` não será relacionada diretamente a `DIM_UF` no Power BI. Assim, evita-se criar um segundo caminho geográfico de filtro entre UF e FATO_PND.

### Preservação dos resultados

A transformação não recalcula:

- `PROFICIENCIA`;
- `NT_OBJ`;
- `NT_DIS`;
- `NT_GER`;
- `QT_ACERTOS`.

Os 759.140 registros da Gold deverão reproduzir diretamente os valores da Silver.

Valores negativos de `PROFICIENCIA` são preservados.

Não será imposto na Gold limite inferior adicional a `PROFICIENCIA`, `NT_OBJ`, `NT_DIS` ou `NT_GER`, porque isso alteraria uma decisão metodológica já resolvida e validada na Silver.

`QT_ACERTOS` permanece sujeito à regra semântica de contagem não negativa.

### Padrão oficial de proficiência da PND 2025

A classificação de desempenho utilizada na Gold não será baseada em um ponto médio arbitrário da escala.

A referência adotada é o padrão oficial estabelecido pelo Inep para a PND 2025.

A **Nota Técnica nº 1/2026/GPP/GAB-INEP** documenta que os pontos de corte foram definidos por meio do **Método de Angoff Modificado** e posteriormente transpostos para a escala de proficiência da Teoria de Resposta ao Item (TRI). Na seção 8.1, o Inep estabelece, para todas as áreas da PND:

```text
Básico: 50 pontos
Adequado: 70 pontos
```

Fonte oficial:

INSTITUTO NACIONAL DE ESTUDOS E PESQUISAS EDUCACIONAIS ANÍSIO TEIXEIRA. **Nota Técnica nº 1/2026/GPP/GAB-INEP**. Apresentação dos procedimentos adotados para estabelecimento dos pontos de corte da Prova Nacional Docente – PND por meio da aplicação do Método de Angoff Modificado, e subsequente transposição dos resultados para a escala de proficiência da Teoria de Resposta ao Item (TRI). Brasília: Inep, 2026. Disponível em: <https://download.inep.gov.br/pnd/notas_tecnicas/SEI_1873050_nota_tecnica_1.pdf>. Acesso em: 19 ago. 2026.

A **Nota Técnica nº 44/2025/CEI/CGGI/DAES-INEP** demonstra que a proficiência individual das questões objetivas é estimada pela TRI e que a `NT_OBJ` é obtida pela transformação dessa proficiência para a escala de divulgação de 0 a 100, com constantes específicas de cada área. Essas constantes são ancoradas no ponto de corte definido pelo método de Angoff. A nota objetiva é, portanto, a variável dos microdados compatível com os pontos de corte oficiais.

Fonte oficial:

INSTITUTO NACIONAL DE ESTUDOS E PESQUISAS EDUCACIONAIS ANÍSIO TEIXEIRA. **Nota Técnica nº 44/2025/CEI/CGGI/DAES-INEP**. Metodologia de cálculo da nota geral dos participantes do Enade das Licenciaturas e da Prova Nacional Docente (PND), edições de 2025. Brasília: Inep, 2025. Disponível em: <https://download.inep.gov.br/pnd/notas_tecnicas/SEI_1854638_nota_tecnica_44.pdf>. Acesso em: 19 ago. 2026.

A apresentação oficial dos resultados da PND e do Enade das Licenciaturas 2025 confirma a interpretação: são considerados **proficientes** os participantes com desempenho igual ou superior a 50 pontos na escala de cada área e são apresentados dois padrões de proficiência.

Fonte oficial:

INSTITUTO NACIONAL DE ESTUDOS E PESQUISAS EDUCACIONAIS ANÍSIO TEIXEIRA. **PND e Enade das Licenciaturas: resultados de 2025**. Brasília: Inep, 2026. p. 22. Disponível em: <https://download.inep.gov.br/educacao_superior/enade/pnd_e_enade_2025_cursos.pdf>. Acesso em: 19 ago. 2026.

Com base nessas fontes, a Gold aplica a seguinte classificação sobre `NT_OBJ`:

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

O corte de 50 pontos **não representa "50% de acertos" nem simplesmente a metade de uma escala escolhida pelo projeto**. Ele representa o ponto de corte oficial de proficiência definido pelo Inep mediante procedimento de estabelecimento de padrões, com Método de Angoff Modificado e ancoragem na TRI.

O valor de 70 pontos corresponde ao segundo ponto de corte oficial, denominado `Adequado` na Nota Técnica nº 1/2026. Na apresentação dos resultados, os participantes proficientes são organizados nos padrões 1 e 2; por isso, a Gold operacionaliza o primeiro intervalo proficiente como `PADRAO_1` e o segundo como `PADRAO_2`.

### Por que o corte não é aplicado a NT_GER ou NT_DIS

A regra anterior do projeto, que considerava simultaneamente:

```text
NT_OBJ < 50
NT_GER < 50
NT_DIS < 5
```

foi **descartada antes da execução da FATO_PND Gold**.

Após consulta à documentação técnica oficial, não foi encontrada base para interpretar `NT_GER < 50` ou `NT_DIS < 5` como pontos de corte oficiais de proficiência.

A nota geral possui finalidade distinta. O Guia de Apoio Técnico da PND informa que a Nota Geral resulta da ponderação de 80% da nota objetiva e 20% da nota discursiva. Portanto, ela continuará disponível para análises de média e distribuição, mas não será utilizada para reproduzir o padrão oficial de proficiência.

Referência complementar:

INSTITUTO NACIONAL DE ESTUDOS E PESQUISAS EDUCACIONAIS ANÍSIO TEIXEIRA. **Guia de Apoio Técnico – Prova Nacional Docente**. Brasília: Inep, 2026. Disponível em: <https://download.inep.gov.br/pnd/guia_apoio_tecnico_pnd_2026.pdf>. Acesso em: 19 ago. 2026.

`NT_DIS` também continuará como resultado descritivo. Não será criado um limite de 5 pontos como se representasse proficiência oficial.

`PROFICIENCIA` permanece preservada na escala original da TRI encontrada nos microdados. Seus valores negativos continuam válidos e não são truncados. A classificação de desempenho não é realizada diretamente sobre esse campo porque os próprios microdados já disponibilizam `NT_OBJ`, que corresponde à transformação da proficiência objetiva para a escala oficial de divulgação.

### Materialização do padrão na Gold

Diferentemente de médias, percentuais e variações, `PADRAO_DESEMPENHO` não depende do contexto de filtro do Power BI. É uma classificação determinística de cada registro a partir de um padrão oficial.

Por esse motivo, a Gold passa a materializar:

```text
PADRAO_DESEMPENHO
```

Essa coluna permite que o Power BI calcule, de forma simples e auditável:

```text
total de não proficientes
total de proficientes
% de proficientes
% de não proficientes
distribuição entre Padrão 1 e Padrão 2
```

Os percentuais e contagens continuam sendo medidas DAX, pois dependem do contexto de filtro por UF, município e área.

### Validação prevista

A validação independente verifica:

- 759.140 registros;
- ano único 2025;
- 27 UFs de prova;
- 17 áreas;
- 750 municípios de prova;
- zero ausências nos dez campos Gold;
- igualdade dos nove campos de origem nos 759.140 registros Gold ↔ Silver;
- `NT_OBJ` dentro da escala oficial 0–100;
- classificação independente de `PADRAO_DESEMPENHO` a partir dos cortes oficiais de 50 e 70 pontos;
- domínio exclusivo `NAO_PROFICIENTE`, `PADRAO_1` e `PADRAO_2`;
- ausência de chaves órfãs nas quatro dimensões relacionadas;
- coerência município → UF;
- `QT_ACERTOS` não negativo;
- preservação dos valores negativos de `PROFICIENCIA`;
- diagnóstico dos valores mínimos, máximos e negativos sem impor domínio artificial a `PROFICIENCIA`, `NT_DIS` ou `NT_GER`.

A transformação e a validação independente foram executadas com sucesso.

Resultados confirmados:

- 759.140 registros;
- ano único 2025;
- 27 UFs de prova;
- 17 áreas;
- 750 municípios de prova;
- zero resultados ausentes;
- 759.140 registros comparados diretamente com a Silver;
- resultados Gold = Silver;
- `NT_OBJ` integralmente na escala 0–100;
- zero chaves órfãs em `DIM_UF`, `DIM_TEMPO`, `DIM_AREA_PND` e `DIM_MUNICIPIO`;
- coerência `CO_MUNICIPIO_PROVA → UF_PROVA`: OK;
- valores negativos de `PROFICIENCIA` preservados.

A classificação oficial derivada de `NT_OBJ` resultou em:

```text
NAO_PROFICIENTE (NT_OBJ < 50):        265.932
PADRAO_1 (50 <= NT_OBJ < 70):         304.638
PADRAO_2 (NT_OBJ >= 70):              188.570
PROFICIENTES (PADRAO_1 + PADRAO_2):   493.208
PERCENTUAL DE PROFICIENTES:           64,97%
```

O percentual de 64,97% reproduz, com arredondamento, o patamar de aproximadamente 65% divulgado oficialmente pelo Inep para a PND 2025, funcionando como evidência externa adicional de coerência da classificação implementada. Essa comparação não substitui a validação registro a registro com a Silver, mas reforça a plausibilidade do resultado agregado.

Diagnóstico numérico observado:

```text
PROFICIENCIA: mín=-3,976610 | máx=2,688530 | negativos=389.188
NT_OBJ:       mín=0        | máx=100      | negativos=0
NT_DIS:       mín=0        | máx=10       | negativos=0
NT_GER:       mín=0        | máx=100      | negativos=0
QT_ACERTOS:   mín=0        | máx=77       | negativos=0
```

Resultado final:

`FATO_PND GOLD: OK`

Status:

`FATO_PND ✅ concluída e validada`

---

## 13.7 Validação global da camada Gold

Após a validação individual das cinco dimensões e das cinco tabelas fato, foi implementado um validador transversal do modelo dimensional:

`src/gold/validar_gold.py`

### Objetivo

A validação global não substitui os validadores específicos de cada fonte.

Os validadores individuais verificam a transformação de cada tabela e, quando aplicável, sua reprodução direta da Silver.

O validador global possui outro objetivo: confirmar que **o conjunto das tabelas Gold forma um modelo dimensional internamente coerente antes de ser consumido pelo Power BI**.

Essa separação é deliberada:

```text
validação individual
    ↓
confirma cada tabela isoladamente

validação global
    ↓
confirma o funcionamento do conjunto dimensional
```

### Arquivos verificados

O script exige a existência das cinco dimensões:

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

A ausência de qualquer arquivo provoca falha explícita.

### Validação das dimensões

São verificados:

- esquema e ordem das colunas;
- quantidade esperada de registros;
- ausência de valores nulos;
- unicidade das chaves dimensionais;
- domínio completo das 27 UFs;
- 18 anos em `DIM_TEMPO`, correspondentes a 2007–2023 e 2025;
- duas etapas e sua ordem analítica;
- 17 códigos de área da PND;
- 750 municípios de prova;
- pertencimento das UFs de `DIM_MUNICIPIO` ao domínio de `DIM_UF`.

### Validação das fatos

O script verifica os esquemas e as cardinalidades já confirmadas pelas validações individuais:

```text
FATO_RENDIMENTO: 2.754
FATO_TDI:           918
FATO_IDEB:          486
FATO_SAEB:          972
FATO_PND:       759.140
```

Também são reavaliados os grãos das quatro fatos agregadas:

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

A `FATO_PND` é tratada de forma diferente. Como a fonte pública não disponibiliza identificador individual do participante, o validador **não inventa uma chave composta artificial nem exige unicidade de uma combinação de notas e atributos**. Ele preserva a decisão metodológica de que cada linha corresponde a um registro individual válido da prova.

### Domínios analíticos

O validador global confirma:

- `PUBLICA` como única rede das quatro fatos históricas;
- Rendimento entre 0 e 100;
- TDI entre 0 e 100;
- IDEB entre 0 e 10;
- proficiência do SAEB entre 0 e 500;
- `LP` e `MT` como disciplinas do SAEB;
- as três categorias de Rendimento: `APROVACAO`, `REPROVACAO` e `ABANDONO`;
- `NT_OBJ` da PND entre 0 e 100;
- `QT_ACERTOS` da PND não negativo;
- `PADRAO_DESEMPENHO` restrito a `NAO_PROFICIENTE`, `PADRAO_1` e `PADRAO_2`;
- consistência da classificação da PND com os cortes oficiais de 50 e 70 pontos aplicados a `NT_OBJ`.

Os valores negativos de `PROFICIENCIA` da PND continuam preservados. O validador global não cria domínio artificial para essa variável.

### Integridade referencial

As quatro fatos históricas são verificadas contra:

```text
DIM_UF
DIM_TEMPO
DIM_ETAPA
```

A PND é verificada contra:

```text
DIM_UF
DIM_TEMPO
DIM_AREA_PND
DIM_MUNICIPIO
```

Qualquer chave da fato sem correspondência na respectiva dimensão provoca falha.

Também é validada a coerência:

`CO_MUNICIPIO_PROVA → UF_PROVA`

contra `DIM_MUNICIPIO`.

### Reprodução dos domínios pelas dimensões

Além de verificar se não existem chaves órfãs, o script realiza a validação inversa.

As dimensões devem representar exatamente os domínios efetivamente utilizados pelas fatos:

- `DIM_UF` = conjunto de UFs das fatos;
- `DIM_TEMPO` = união dos anos das fatos;
- `DIM_ETAPA` = conjunto de etapas das fatos históricas;
- `DIM_AREA_PND` = conjunto de `CO_GRUPO` da `FATO_PND`;
- `DIM_MUNICIPIO` = conjunto de municípios da `FATO_PND`.

Essa regra evita dimensões com categorias artificiais, registros sem uso ou anos criados apenas para preencher lacunas do calendário.

### Relações previstas no Power BI

A validação global confirma os dados necessários para as seguintes relações `1:*`:

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

A direção de filtro recomendada permanece:

`dimensão → fato`

Não será criada relação direta `DIM_MUNICIPIO → DIM_UF`, pois a FATO_PND já possui relacionamento direto com ambas e a relação adicional criaria um segundo caminho geográfico de filtragem.

### Regra de fechamento

A validação global foi executada com sucesso.

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
Fatos históricas
    → DIM_UF
    → DIM_TEMPO
    → DIM_ETAPA

FATO_PND
    → DIM_UF
    → DIM_TEMPO
    → DIM_AREA_PND
    → DIM_MUNICIPIO
```

Também foram confirmados:

- coerência `CO_MUNICIPIO_PROVA → UF_PROVA`;
- dimensões correspondendo exatamente aos domínios efetivamente utilizados pelas fatos;
- classificação oficial da PND com 265.932 não proficientes, 304.638 no Padrão 1 e 188.570 no Padrão 2;
- 493.208 participantes proficientes, equivalentes a 64,97%.

Resultado final:

`MODELO DIMENSIONAL GOLD: OK`

Status:

`CAMADA GOLD ✅ concluída e validada globalmente`

A camada Gold está pronta para consumo no Power BI.

---

## 14. Situação atual

Todas as cinco dimensões e as cinco tabelas fato da camada Gold estão concluídas e validadas individualmente e em conjunto.
A validação global retornou `MODELO DIMENSIONAL GOLD: OK`. A camada Gold está pronta para ser consumida pelo Power BI.


| Componente | Situação |
|---|---|
| Modelo dimensional | ✅ definido |
| Dimensões | ✅ concluídas e validadas |
| FATO_RENDIMENTO | ✅ concluída e validada |
| FATO_TDI | ✅ concluída e validada |
| FATO_IDEB | ✅ concluída e validada |
| FATO_SAEB | ✅ concluída e validada |
| FATO_PND | ✅ concluída e validada |
| Validação referencial global | ⏳ não implementada |
| Power BI sobre Gold | ⏳ não migrado |

A presença de `⏳` nesta seção representa trabalho realmente ainda não executado na camada Gold.

---

## 15. Histórico de decisões

| Data | Decisão |
|---|---|
| 19/08/2026 | Iniciada a definição da camada Gold após conclusão integral da Silver |
| 19/08/2026 | Definido modelo dimensional com fatos separadas por fonte, preservando os diferentes grãos |
| 19/08/2026 | Definidas dimensões conformadas `DIM_UF`, `DIM_TEMPO` e `DIM_ETAPA` para as séries históricas |
| 19/08/2026 | Definidas `DIM_AREA_PND` e `DIM_MUNICIPIO` para reduzir repetição na fato individual da PND |
| 19/08/2026 | Definido uso de chaves naturais estáveis em vez de chaves substitutas artificiais |
| 19/08/2026 | Definido que a Gold será construída somente a partir da Silver, sem leitura direta de RAW ou Bronze |
| 19/08/2026 | Definido que não haverá `DIM_REDE`, pois o escopo histórico atual possui apenas a rede canônica `PUBLICA` |
| 19/08/2026 | Definido que `DISCIPLINA` e `INDICADOR` permanecerão em suas respectivas fatos, evitando dimensões sem ganho analítico no escopo atual |
| 19/08/2026 | Definido que `FATO_SAEB` usará diretamente os valores oficiais da Silver, sem `SOMA_PESO`, `SOMA_VALOR_PONDERADO` ou recomposição a partir de escolas |
| 19/08/2026 | Definido que medidas agregadas e percentuais dependentes de filtro serão calculados no Power BI, não persistidos como colunas derivadas na Gold |
| 19/08/2026 | Definido que `DIM_MUNICIPIO` não receberá nome do município por leitura direta do RAW; qualquer enriquecimento futuro será documentado antes da implementação |
| 19/08/2026 | Implementados transformador e validador independente das cinco dimensões Gold; conclusão depende da execução e validação contra as Silvers |
| 19/08/2026 | Transformação das dimensões Gold executada com sucesso: 27 UFs, 18 anos, 2 etapas, 17 áreas PND e 750 municípios |
| 19/08/2026 | Validação independente das dimensões concluída; chaves únicas, reprodução das Silvers e domínios dimensionais confirmados; resultado `DIMENSÕES GOLD: OK` |
| 19/08/2026 | Implementados transformador e validador independente da `FATO_RENDIMENTO`, preservando os 2.754 valores da Silver sem recálculo e com validação referencial contra `DIM_UF`, `DIM_TEMPO` e `DIM_ETAPA` |
| 19/08/2026 | `FATO_RENDIMENTO` executada e validada com 2.754 registros; igualdade Gold ↔ Silver e integridade referencial confirmadas; resultado `FATO_RENDIMENTO GOLD: OK` |
| 19/08/2026 | Implementados transformador e validador independente da `FATO_TDI`, preservando 918 valores da Silver sem recálculo e validando `DIM_UF`, `DIM_TEMPO` e `DIM_ETAPA` |
| 19/08/2026 | `FATO_TDI` executada e validada com 918 registros; igualdade Gold ↔ Silver e integridade referencial confirmadas; resultado `FATO_TDI GOLD: OK` |
| 19/08/2026 | Implementados transformador e validador independente da `FATO_IDEB`, preservando as nove edições 2007–2023, os 486 valores da Silver e a integridade referencial com as dimensões |
| 19/08/2026 | `FATO_IDEB` executada e validada com 486 registros e 9 edições; igualdade Gold ↔ Silver e integridade referencial confirmadas; resultado `FATO_IDEB GOLD: OK` |
| 19/08/2026 | Implementados transformador e validador independente da `FATO_SAEB`, preservando as 972 proficiências oficiais da Silver, sem ponderação escolar ou recomposição, e validando integridade com as dimensões |
| 19/08/2026 | `FATO_SAEB` executada e validada com 972 registros e 9 edições; proficiências Gold = Silver, domínio 0–500 e integridade referencial confirmados; resultado `FATO_SAEB GOLD: OK` |
| 19/08/2026 | Implementados transformador e validador independente da `FATO_PND`, preservando o grão individual de 759.140 registros e relacionamentos com tempo, UF, área e município |
| 19/08/2026 | Retificada a metodologia da PND antes da execução da Gold: descartados os cortes arbitrários em `NT_GER` e `NT_DIS`; adotados os pontos de corte oficiais do Inep aplicados a `NT_OBJ` |
| 19/08/2026 | Documentadas as referências oficiais dos cortes: Nota Técnica nº 1/2026/GPP/GAB-INEP (Angoff Modificado; Básico=50 e Adequado=70), Nota Técnica nº 44/2025/CEI/CGGI/DAES-INEP (transformação TRI → `NT_OBJ`) e apresentação oficial dos resultados de 2025 |
| 19/08/2026 | `PADRAO_DESEMPENHO` passou a ser materializado na FATO_PND como classificação determinística: `NAO_PROFICIENTE`, `PADRAO_1` e `PADRAO_2`; percentuais permanecem medidas DAX |
| 19/08/2026 | `FATO_PND` executada e validada com 759.140 registros; resultados Gold = Silver e integridade referencial confirmados; resultado `FATO_PND GOLD: OK` |
| 19/08/2026 | Classificação oficial da PND validada: 265.932 não proficientes, 304.638 no Padrão 1, 188.570 no Padrão 2 e 493.208 proficientes (64,97%) |
| 19/08/2026 | Concluídas e validadas todas as cinco tabelas fato da camada Gold; próxima etapa definida como validação referencial global do modelo dimensional |
| 19/08/2026 | Implementado `src/gold/validar_gold.py` para validação transversal das cinco dimensões e cinco fatos antes do consumo no Power BI |
| 19/08/2026 | Documentada a distinção entre validação individual das tabelas e validação global do modelo dimensional |
| 19/08/2026 | Definido que a Gold só será considerada integralmente pronta para o Power BI após o retorno `MODELO DIMENSIONAL GOLD: OK` |
| 19/08/2026 | Executada a validação global da camada Gold; todas as dimensões, fatos, domínios e relacionamentos foram aprovados |
| 19/08/2026 | Confirmado `MODELO DIMENSIONAL GOLD: OK`; camada Gold concluída e liberada para consumo no Power BI |
