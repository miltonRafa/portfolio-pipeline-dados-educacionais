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

## 14. Situação atual

| Componente | Situação |
|---|---|
| Modelo dimensional | ✅ definido |
| Dimensões | ✅ concluídas e validadas |
| FATO_RENDIMENTO | ✅ concluída e validada |
| FATO_TDI | ✅ concluída e validada |
| FATO_IDEB | ✅ concluída e validada |
| FATO_SAEB | ⏳ não implementada |
| FATO_PND | ⏳ não implementada |
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
