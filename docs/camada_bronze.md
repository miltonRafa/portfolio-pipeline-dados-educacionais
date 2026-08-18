# Camada Bronze — Ingestão dos Dados Educacionais

## 1. Objetivo

A camada Bronze é a primeira camada de dados processados do projeto.

Sua função é transformar os arquivos originais armazenados em `data/raw` em estruturas legíveis e reutilizáveis pelo pipeline, preservando o máximo possível da informação da fonte.

A Bronze não é responsável por harmonizar conceitos entre bases.

Portanto, nesta etapa não serão aplicadas decisões analíticas como:

- seleção definitiva da rede pública;
- padronização de etapas de ensino;
- cálculo de médias por UF;
- consolidação de categorias;
- exclusão de registros analíticos;
- reconstrução de indicadores;
- alteração de valores da fonte.

Essas transformações pertencem às camadas posteriores.

---

## 2. Relação entre Raw e Bronze

### Raw

A pasta:

`data/raw/`

contém os arquivos originais obtidos das fontes.

Esses arquivos são considerados imutáveis.

O pipeline não deverá sobrescrevê-los, renomeá-los ou modificar seu conteúdo.

### Bronze

A pasta:

`data/bronze/`

conterá representações estruturadas dos arquivos originais.

A Bronze poderá:

- ler XLS, XLSX, CSV e TXT;
- identificar a aba utilizada;
- identificar o cabeçalho real;
- converter os dados para formato tabular;
- armazenar os resultados em Parquet;
- adicionar metadados técnicos de origem.

A informação substantiva da fonte deverá ser preservada.

---

## 3. Por que utilizar Parquet

Os arquivos originais apresentam diferentes formatos:

- XLS;
- XLSX;
- CSV;
- TXT.

A camada Bronze utilizará preferencialmente o formato:

`Parquet`

porque ele:

- preserva tipos de dados de forma mais eficiente que CSV;
- possui leitura e escrita rápidas;
- ocupa menos espaço em disco;
- é adequado para pipelines analíticos;
- funciona bem com Python, Pandas, DuckDB e ferramentas de engenharia de dados;
- evita problemas recorrentes de delimitador e codificação encontrados em CSV.

O uso de Parquet na Bronze não altera o significado dos dados.

Ele apenas padroniza o formato técnico de armazenamento.

---

## 4. Metadados de rastreabilidade

Cada tabela Bronze deverá possuir, quando aplicável, colunas técnicas como:

- `_fonte`;
- `_arquivo_origem`;
- `_aba_origem`;
- `_ano_referencia`.

Esses campos não substituem variáveis originais da fonte.

Eles existem para permitir rastrear cada registro até o arquivo que o originou.

Exemplo:

| _fonte | _arquivo_origem | _ano_referencia |
|---|---|---:|
| RENDIMENTO | TX_REND_BRASIL_REGIOES_UFS_2023.xlsx | 2023 |

---

## 5. O que não será feito na Bronze

A Bronze não deverá:

1. substituir `Publico` por `PUBLICA`;
2. transformar `Pública (4)` em `PUBLICA`;
3. agregar Federal, Estadual e Municipal;
4. selecionar apenas Anos Iniciais ou Anos Finais;
5. converter nomes de estados para siglas;
6. excluir rede privada;
7. remover registros apenas porque não serão utilizados no dashboard;
8. calcular médias;
9. imputar valores ausentes;
10. recalcular indicadores;
11. aplicar a população analítica da PND;
12. alterar os arquivos originais.

Essas operações pertencem principalmente à Silver ou à Gold.

---

## 6. Tratamento permitido

Algumas operações técnicas são necessárias para tornar os arquivos utilizáveis.

São permitidas:

- identificação da aba correta;
- identificação da linha real de cabeçalho;
- remoção de linhas completamente vazias geradas pela estrutura da planilha;
- leitura correta de decimal e delimitador;
- conversão técnica de arquivos para DataFrame;
- criação de nomes técnicos temporários quando a biblioteca de leitura exigir;
- adição de metadados de origem;
- persistência em Parquet.

Essas operações devem ser distinguíveis de transformações semânticas.

---

### 6.1 Tipagem técnica das células na Bronze

Algumas planilhas de origem possuem títulos, cabeçalhos hierárquicos,
códigos técnicos e valores numéricos ocupando as mesmas colunas.

Por esse motivo, na ingestão de planilhas cuja estrutura completa será
preservada, as células de origem poderão ser armazenadas como texto na
camada Bronze.

Essa conversão possui finalidade exclusivamente técnica: garantir que a
estrutura heterogênea da planilha possa ser persistida de forma estável
em Parquet sem perda dos valores publicados.

A conversão para tipos analíticos, como inteiro, decimal ou categoria,
será realizada somente na camada Silver, após a identificação explícita
da estrutura de cada fonte.

Valores especiais existentes na fonte, como `--`, não serão convertidos
automaticamente em nulos na Bronze.

As células realmente vazias permanecerão como valores ausentes.

Além disso, a Bronze preservará o número da linha de origem para permitir
rastreabilidade até a posição original da informação na planilha.

---

## 7. Particularidades das fontes

### IDEB

Os arquivos possuem múltiplas abas e estrutura própria.

A Bronze deverá preservar a informação das abas necessárias sem ainda padronizar rede, etapa ou indicador.

### SAEB

A estrutura varia significativamente entre as edições.

Existem arquivos:

- agregados por UF;
- com códigos;
- em nível escolar.

A Bronze deverá respeitar a estrutura de cada edição.

Não será feita nesta etapa uma harmonização forçada entre todos os anos.

### Rendimento Escolar

Os arquivos apresentam mudanças de:

- nome de aba;
- linha do cabeçalho;
- nomenclatura das redes;
- estrutura entre períodos.

A Bronze deverá apenas estruturar esses arquivos.

#### Espaços finais em nomes de abas

Durante a implementação da camada Bronze foram identificados espaços finais
nos nomes de abas armazenados nos próprios arquivos de origem.

Foram confirmadas as seguintes estruturas:

- 2014: `UF `;
- 2015: `UF `;
- 2016: `UF `;
- 2017 a 2023: `BRASIL_REGIOES_UFS `.

Os espaços fazem parte dos nomes efetivamente armazenados nos workbooks,
embora não sejam facilmente perceptíveis durante a inspeção visual no Excel.

A configuração da ingestão utiliza os nomes exatos encontrados nos arquivos.

Não foi aplicada normalização automática com `strip()`, pois a estratégia da
camada Bronze é reconhecer explicitamente a estrutura auditada e interromper
a execução caso a estrutura da fonte seja diferente daquela esperada.

Essa decisão permitiu detectar uma irregularidade estrutural da fonte em vez
de corrigi-la silenciosamente.

### TDI

Assim como Rendimento, possui mudanças estruturais entre períodos e formatos XLS/XLSX.

A Bronze preservará as categorias encontradas na fonte.

### PND 2025

O arquivo principal possui mais de um milhão de registros e será lido de maneira eficiente.

Na Bronze serão preservados todos os registros do arquivo principal.

O filtro da população analítica de 759.140 participantes somente será aplicado em camada posterior.

Os registros `TP_PRES = 888` e os registros `TP_PRES = 555` sem resultados não serão removidos na Bronze.

---

## 8. Granularidade

A Bronze deverá manter a granularidade disponível na fonte utilizada.

Não será utilizada uma granularidade única artificial para todas as bases.

Exemplos:

- SAEB pode possuir dados por escola em determinadas edições;
- IDEB possui tabelas agregadas;
- Rendimento e TDI possuem agregados geográficos;
- PND possui registros individuais da prova.

A harmonização de granularidade será feita somente quando necessária para a análise.

---

## 9. Estrutura prevista

```text
data/
├── raw/
│   ├── ideb/
│   ├── saeb/
│   ├── rendimento/
│   ├── tdi/
│   └── pnd/
│
└── bronze/
    ├── ideb/
    ├── saeb/
    ├── rendimento/
    ├── tdi/
    └── pnd/
```

Os arquivos Bronze serão preferencialmente armazenados como:

`.parquet`

---

## 10. Validações da Bronze

Cada processo de ingestão deverá verificar pelo menos:

- existência do arquivo de origem;
- quantidade de linhas lidas;
- quantidade de colunas;
- existência de registros;
- ano esperado, quando disponível;
- arquivo de origem registrado;
- sucesso da gravação do Parquet.

A Bronze não deverá considerar uma ingestão válida apenas porque o arquivo foi criado.

O pipeline deverá produzir mensagens de controle.

Exemplo:

```text
[OK] Rendimento 2023
Arquivo: TX_REND_BRASIL_REGIOES_UFS_2023.xlsx
Linhas lidas: 1.234
Colunas: 58
Destino: data/bronze/rendimento/rendimento_2023.parquet
```

---

## 11. Reprodutibilidade

Nenhum arquivo da Bronze deverá depender de transformação manual em Excel ou Power BI.

A partir dos arquivos existentes em:

`data/raw/`

todo o conteúdo de:

`data/bronze/`

deverá poder ser reconstruído executando o pipeline.

Isso significa que a Bronze é descartável e reproduzível.

A Raw não é.

---

## 12. Regra de falha

Se o pipeline não reconhecer corretamente:

- uma aba;
- um cabeçalho;
- um ano;
- uma estrutura esperada;

a execução deverá falhar de forma explícita.

Não deverá selecionar silenciosamente outra aba ou estrutura semelhante.

É preferível interromper o pipeline do que produzir dados aparentemente válidos a partir de uma interpretação incorreta da fonte.

---

## 13. Separação de responsabilidades

O projeto adotará a seguinte divisão:

### RAW

Arquivo original.

### BRONZE

Arquivo original estruturado e rastreável.

### SILVER

Dados limpos, normalizados e semanticamente harmonizados.

### GOLD

Dados organizados para análise, indicadores e Power BI.

A regra pode ser resumida como:

```text
RAW
arquivo como publicado
       ↓
BRONZE
arquivo estruturado
       ↓
SILVER
dado padronizado
       ↓
GOLD
dado analítico
```

---

## 14. Conclusão

A camada Bronze será utilizada como fronteira entre os arquivos heterogêneos publicados pelas fontes e o pipeline analítico.

Seu principal compromisso é com:

- fidelidade;
- rastreabilidade;
- reprodutibilidade;
- mínima transformação semântica.

As decisões metodológicas já documentadas nas auditorias e em `definicao_rede_publica.md` serão aplicadas posteriormente na camada Silver.

---

## Histórico de atualização

| Data | Alteração |
|---|---|
| 18/08/2026 | Definição inicial da arquitetura da camada Bronze |
| 18/08/2026 | Definidos limites entre Raw, Bronze, Silver e Gold |
| 18/08/2026 | Definida adoção de Parquet e metadados de rastreabilidade |
