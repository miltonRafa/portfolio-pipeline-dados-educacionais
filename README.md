# Pipeline de Dados Educacionais

Pipeline reproduzível de Engenharia de Dados e Analytics Engineering para dados
oficiais do Inep. O projeto organiza fontes educacionais em camadas
`Raw -> Bronze -> Silver -> Gold` e entrega um modelo analítico consumido no
Power BI.

## Visão Geral

Indicadores históricos:

- SAEB
- IDEB
- Rendimento Escolar
- Taxa de Distorção Idade-Série (TDI)

Escopo da série histórica:

| Dimensão | Recorte |
|---|---|
| Período | 2007-2023 |
| Abrangência | 27 UFs |
| Rede | Pública |
| Etapas | Anos Iniciais e Anos Finais |

A Prova Nacional Docente (PND) 2025 é tratada como análise complementar e
separada da série histórica.

## Destaques Técnicos

- múltiplos formatos de origem: XLS, XLSX, XLSB, CSV e TXT;
- 54 arquivos Raw inventariados;
- aquisição, seleção, extração e nomenclatura da Raw automatizadas;
- hashes SHA-256 para rastreabilidade dos insumos;
- camadas Raw, Bronze, Silver e Gold;
- validações independentes por camada;
- modelo dimensional com 5 dimensões e 5 fatos;
- Power BI Desktop com medidas DAX versionadas;
- documentação metodológica e auditorias por fonte;
- auditoria específica do SAEB 2023;
- classificação PND baseada em `NT_OBJ`, conforme documentação oficial usada no
  projeto.

## Arquitetura

```mermaid
flowchart LR
    INEP[Fontes oficiais Inep] --> AQUISICAO[Download e validação]
    AQUISICAO --> RAW
    RAW[Raw] --> BRONZE[Bronze]
    BRONZE --> SILVER[Silver]
    SILVER --> GOLD[Gold]
    GOLD --> POWERBI[Power BI]
```

| Camada | Função |
|---|---|
| Raw | Arquivos brutos obtidos das fontes oficiais, com convenção de nomenclatura local documentada |
| Bronze | Ingestão técnica e preservação rastreável dos dados lidos |
| Silver | Padronização semântica, harmonização e aplicação do recorte analítico |
| Gold | Modelo dimensional em Parquet para consumo analítico |
| Power BI | Modelo semântico, medidas DAX e visualizações |

## Dashboard Power BI

O arquivo Power BI Desktop está em:

[powerbi/pbix/analise dos indicadores da educação.pbix](powerbi/pbix/analise%20dos%20indicadores%20da%20educação.pbix)

Para atualizar o relatório no seu computador, siga [a configuração do PBIX](#6-abrir-e-configurar-o-power-bi).

Medidas e documentação do modelo:

- [powerbi/medidas_power_bi.dax](powerbi/medidas_power_bi.dax)
- [docs/modelagem_power_bi.md](docs/modelagem_power_bi.md)

Prévia das páginas:

<p>
  <img src="prints/Panorama%20da%20Educação%20Básica%20Brasileira.png" width="48%" alt="Panorama da Educação Básica Brasileira">
  <img src="prints/Aprendizagem%20x%20Fluxo%20Escolar.png" width="48%" alt="Aprendizagem x Fluxo Escolar">
</p>

<p>
  <img src="prints/PND%202025.png" width="48%" alt="PND 2025">
  <img src="prints/Metodologia%20e%20Dados.png" width="48%" alt="Metodologia e Dados">
</p>

[Ver todas as páginas do dashboard](prints/)

## Modelo Gold

Tabelas dimensionais:

| Tabela | Registros |
|---|---:|
| `DIM_UF` | 27 |
| `DIM_TEMPO` | 18 |
| `DIM_ETAPA` | 2 |
| `DIM_AREA_PND` | 17 |
| `DIM_MUNICIPIO` | 750 |

Tabelas fato:

| Tabela | Registros |
|---|---:|
| `FATO_RENDIMENTO` | 2.754 |
| `FATO_TDI` | 918 |
| `FATO_IDEB` | 486 |
| `FATO_SAEB` | 972 |
| `FATO_PND` | 759.140 |

A validação global confirma grãos, domínios e integridade referencial antes do
consumo no Power BI.

## Fontes

Os dados são provenientes de bases oficiais do Instituto Nacional de Estudos e
Pesquisas Educacionais Anísio Teixeira (Inep/MEC).

| Base | Período | Link oficial |
|---|---:|---|
| SAEB — Microdados | 2007-2023 | [Inep/MEC — Microdados do SAEB](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/saeb) |
| SAEB — Resultados agregados | 2007-2023 | [Inep/MEC — Resultados do SAEB](https://www.gov.br/inep/pt-br/areas-de-atuacao/avaliacao-e-exames-educacionais/saeb/resultados) |
| IDEB — Resultados | 2007-2023 | [Inep/MEC — Resultados do IDEB](https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados) |
| Taxas de Rendimento Escolar | 2007-2023 | [Inep/MEC — Taxas de Rendimento Escolar](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais/taxas-de-rendimento-escolar) |
| Taxas de Distorção Idade-Série (TDI) | 2007-2023 | [Inep/MEC — Taxas de Distorção Idade-Série](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais/taxas-de-distorcao-idade-serie) |
| Prova Nacional Docente (PND) — Microdados | 2025 | [Inep/MEC — Microdados da PND](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/pnd) |

O Inep/MEC permanece como fonte primária. A cópia abaixo é apenas uma cópia
organizada de conveniência da camada Raw:

[Google Drive — Raw organizada](https://drive.google.com/file/d/1Jm2v8Er4m5dgjOLOLLcaNssn_YN1Wsja/view?usp=sharing)

O inventário completo, os hashes SHA-256 e a convenção de nomes locais estão em
[docs/fontes_dados.md](docs/fontes_dados.md).

## Como Reproduzir

### 1. Clone

```bash
git clone <url-do-repositorio>
cd portfolio-pipeline-dados-educacionais
```

### 2. Ambiente Python

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

O projeto é validado em Python 3.12. Para pacotes RAR, disponibilize `tar`
com suporte libarchive; o `tar.exe` do Windows utilizado no projeto atende
a esse requisito.

### 3. Dados Raw

A pasta `data/raw` não é versionada no Git.

Para preparar a Raw, execute o download automático das fontes oficiais:

```bash
python scripts/baixar_raw.py
```

O script baixa, extrai e organiza os 54 arquivos diretamente em `data/raw`,
valida os hashes do manifesto e remove os pacotes e candidatos temporários.
Arquivos existentes corretos são reaproveitados. Para consultar novamente as
fontes e verificar atualizações, execute:

```bash
python scripts/baixar_raw.py --rebaixar
```

Se um download tiver hash diferente, o script compara o conteúdo usado pelo
projeto com a versão anterior validada. No IDEB, preserva o histórico até 2023
e permite anos posteriores; nos demais arquivos, compara todas as linhas e
campos das abas usadas, incluindo todo o conteúdo dos arquivos de apoio.
Se forem iguais, instala a nova versão e atualiza automaticamente o hash no
manifesto, os checksums e a documentação de fontes, mantendo backup e histórico.
Se houver mudança histórica, erro de leitura ou falta da referência anterior,
preserva a versão atual e mostra o motivo no terminal e no relatório em
`data/raw/.download/relatorio_download.json`. Uma Raw nova sem referência
anterior só aceita diretamente os hashes já registrados. Use `--estrito` para
exigir sempre identidade binária e impedir atualizações automáticas.

Para os pacotes RAR, é necessário `tar` com suporte libarchive.
Se o HTTPS do servidor de downloads falhar, use `python scripts/baixar_raw.py --http`.
Veja [o procedimento de download](docs/automacao_raw.md) para opções e relatórios.
O manifesto já inclui a revisão oficial de 09/09/2026 do dicionário PND.

### 4. Verificar Integridade da Raw

```bash
python scripts/gerar_manifesto_raw.py --check
```

Esse comando apenas verifica os arquivos locais contra o manifesto versionado.
Ele não reescreve `docs/fontes_dados.md`, `docs/fontes_dados.csv` nem
`docs/raw_checksums_sha256.txt`.

### 5. Executar o Pipeline Completo

```bash
python src/pipeline.py full
```

O comando executa Bronze, Silver, Gold e validações. Em um clone limpo, a
execução completa exige que os arquivos Raw estejam disponíveis em `data/raw`.

### 6. Abrir e Configurar o Power BI

Use o **Power BI Desktop no Windows**. Primeiro conclua as etapas anteriores:
o download prepara a Raw, e `python src/pipeline.py full` gera e valida a Gold.
Clonar o repositório ou baixar somente a Raw não prepara os arquivos lidos pelo
PBIX. O pipeline Python é executado no terminal; as consultas do relatório leem
Parquet, sem exigir configuração de Python dentro do Power BI.

Ao final, a estrutura esperada é:

```text
data/gold/
├── dimensoes/
│   ├── dim_area_pnd.parquet
│   ├── dim_etapa.parquet
│   ├── dim_municipio.parquet
│   ├── dim_tempo.parquet
│   └── dim_uf.parquet
└── fatos/
    ├── fato_ideb.parquet
    ├── fato_pnd.parquet
    ├── fato_rendimento.parquet
    ├── fato_saeb.parquet
    └── fato_tdi.parquet
```

Abra `powerbi/pbix/analise dos indicadores da educação.pbix` no Power BI Desktop
e ajuste a origem para o local em que você clonou o projeto:

1. Em **Página Inicial**, clique em **Transformar dados** para abrir o Editor do Power Query.
2. Na lista de consultas à esquerda, selecione **`gold`** e a etapa **Fonte**.
3. Na barra de fórmulas, altere somente o caminho entre aspas de `Folder.Files`. Se a barra não aparecer, habilite **Barra de fórmulas** na guia **Exibição**. Por exemplo, para um clone em `D:\Projetos\portfolio-pipeline-dados-educacionais`:

   ```powerquery
   = Folder.Files("D:\Projetos\portfolio-pipeline-dados-educacionais\data\gold")
   ```

   O caminho `C:\portfolio-pipeline-dados-educacionais\data\gold` usado no ambiente de desenvolvimento é apenas uma referência. Informe o caminho absoluto da **sua** pasta `data\gold`.

4. Confirme a fórmula. Na coluna **Name**, confira a presença dos dez nomes `.parquet` listados acima. `Folder.Files` também percorre as subpastas `dimensoes` e `fatos`; mantenha os arquivos nesses diretórios. A listagem pode incluir outros arquivos, como `.gitkeep`.
5. Selecione **`DIM_UF`** para conferir a leitura. A consulta já usa `= fnParquetGold("dim_uf.parquet")` e deve exibir as 27 UFs. As outras dimensões e fatos usam a mesma função, cada uma com seu arquivo. A tela **Inserir Parâmetro / Invocar** ao selecionar `fnParquetGold` é a interface normal de uma função; não é necessário invocá-la manualmente nem recriar consultas.
6. Clique em **Fechar e Aplicar**, aguarde a carga terminar e salve o PBIX. Quando os Parquets forem regenerados pelo pipeline, use **Página Inicial → Atualizar** para carregar os novos dados.

A consulta `gold` centraliza o caminho, `fnParquetGold` faz a leitura por nome de
arquivo e as dez consultas analíticas alimentam o modelo existente. Preserve
esses nomes e mantenha a carga das auxiliares `gold` e `fnParquetGold`
desabilitada. Os relacionamentos, as medidas e as páginas já estão no PBIX;
não é necessário importar e montar as dez tabelas novamente.

| Problema na atualização | O que conferir |
|---|---|
| Pasta ou caminho não encontrado | Corrija a etapa Fonte de `gold` para o caminho absoluto local, terminando em `data\gold`. |
| Arquivo não encontrado ou seleção sem linhas em `fnParquetGold` | Confira os dez nomes esperados na consulta `gold`. Se algum faltar, conclua o pipeline; preserve os nomes gerados e evite cópias com o mesmo nome em subpastas da Gold. |
| Acesso negado | Verifique se o usuário do Windows pode ler a pasta. Se houver solicitação de acesso à fonte, confira **Configurações da fonte de dados** para a pasta local. |
| O relatório continua com os dados anteriores | Termine o pipeline e depois atualize o PBIX. Atualizar o Power BI não baixa a Raw nem executa o pipeline Python. |

Detalhes do modelo em [docs/modelagem_power_bi.md](docs/modelagem_power_bi.md).
A leitura recursiva da pasta segue a documentação de
[Folder.Files da Microsoft](https://learn.microsoft.com/en-us/powerquery-m/folder-files).

### 7. Outras Opções

```bash
python src/pipeline.py bronze
python src/pipeline.py silver
python src/pipeline.py gold
python src/pipeline.py validate-gold
python src/pipeline.py --list
python src/pipeline.py full --dry-run
```

`full --dry-run` lista a sequência completa e valida a existência dos scripts
referenciados, sem executar transformações analíticas.

Para verificar o código e os contratos do repositório sem baixar os dados:

```bash
python -m unittest discover -s tests -v
python -m compileall -q src scripts tests
```

A integração contínua executa essas verificações e confere a sequência do
pipeline. A integridade da Raw e a validação dos dados Gold são verificações
locais adicionais, pois os dados não são versionados.

## Resultado Validado

A validação global da Gold retorna:

```text
MODELO DIMENSIONAL GOLD: OK
```

Cardinalidades confirmadas:

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

## Documentação

- [docs/fontes_dados.md](docs/fontes_dados.md)
- [docs/automacao_raw.md](docs/automacao_raw.md)
- [docs/camada_bronze.md](docs/camada_bronze.md)
- [docs/camada_silver.md](docs/camada_silver.md)
- [docs/camada_gold.md](docs/camada_gold.md)
- [docs/definicao_rede_publica.md](docs/definicao_rede_publica.md)
- [docs/modelagem_power_bi.md](docs/modelagem_power_bi.md)
- [docs/auditoria/](docs/auditoria/)
- [Fonte LaTeX do TCC](tcc/README.md)
- [PDF do TCC](output/pdf/Template_TCC_UEMG_revisado.pdf)
- [Slides, roteiro e imagens de apoio da defesa](tcc/apresentacao/README.md)
- [Orientações sobre as referências acadêmicas](referencias/README.md)

## Escopo Temporal

A versão atual das séries históricas permanece em 2007-2023 para manter
coerência entre SAEB, IDEB, Rendimento Escolar e TDI.

O fato de páginas oficiais atualmente possuírem edições de 2025 não altera
automaticamente o escopo desta versão. A PND 2025 permanece como análise
complementar.

## Observações

A versão `v1.2.0` inclui a aquisição automatizada da Raw, atualizações por
equivalência do conteúdo histórico e os materiais revisados do TCC e da defesa.
Veja as [notas da versão](docs/release_v1.2.0.md).

As notas em `docs/release_v*.md` descrevem as respectivas versões publicadas.
As contagens e procedimentos atuais estão neste README e nos documentos de
fontes, automação e revisão do TCC; notas de releases anteriores são registros
históricos.

Os arquivos de dados são ignorados por padrão no Git por tamanho e por serem
fontes locais ou artefatos reproduzíveis. O arquivo `.pbix` foi mantido como
entrega visual do portfólio; em repositórios maiores, recomenda-se avaliar Git
LFS.

## Licença e Citação

Este projeto é disponibilizado sob a
[PolyForm Noncommercial License 1.0.0](LICENSE).

Usos não comerciais, incluindo estudo, pesquisa, uso acadêmico, modificação e
redistribuição não comercial, são permitidos nos termos da licença. Uso
comercial não é autorizado por esta licença e depende de autorização ou
licenciamento separado pelo autor.

O arquivo [LICENSE](LICENSE) define as condições jurídicas de utilização do
código. O arquivo [CITATION.cff](CITATION.cff) registra os metadados de autoria
e orienta a citação acadêmica do projeto.
