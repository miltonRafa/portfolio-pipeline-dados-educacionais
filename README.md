# Pipeline de Dados Educacionais

Projeto de Engenharia de Dados e Business Intelligence que automatiza a integração, a transformação e a validação de indicadores educacionais oficiais do INEP.

Desenvolvido em Python, o pipeline transforma arquivos historicamente heterogêneos em tabelas analíticas padronizadas, rastreáveis e reprodutíveis, organizadas em uma arquitetura de quatro camadas e utilizadas em painéis interativos no Power BI.

## O problema e a solução

As bases públicas do INEP são publicadas em planilhas, CSV e arquivos de texto
com estruturas e categorias diferentes. O layout pode mudar entre edições, e
um mesmo indicador pode estar disponível em granularidades distintas. Sem
auditar essas diferenças, uma integração automática pode comparar populações
incompatíveis ou substituir um agregado oficial por uma estimativa própria.

O projeto automatiza a aquisição e o processamento, preserva a origem dos
dados e valida os resultados entre as camadas. Assim, a análise no Power BI
fica acompanhada de regras metodológicas e evidências que permitem reconstruir
o percurso de cada indicador.

## Escopo e resultados

A série histórica cobre **2007–2023**, as **27 UFs**, a **rede pública** e os
**Anos Iniciais e Finais do Ensino Fundamental**. Analisa IDEB, SAEB,
Rendimento Escolar e Taxa de Distorção Idade-Série (TDI). A PND 2025 é uma
análise complementar, separada da série histórica.

| Evidência da versão validada | Resultado |
|---|---:|
| Insumos Raw oficiais | 54 |
| Etapas de processamento e validação | 35, além da verificação inicial da Raw |
| Parquets Bronze / Silver / Gold | 48 / 5 / 10 |
| Parquets nas três camadas | 63 |
| Observações nas quatro fatos históricas | 5.130 |
| Registros analíticos da PND 2025 | 759.140 |
| Testes automatizados de software aprovados | 178 de 178 |
| Parquets idênticos por SHA-256 em duas execuções isoladas no Windows | 63 de 63 |

Na Gold, as séries históricas totalizam 5.130 observações: 2.754 de
Rendimento, 918 de TDI, 486 de IDEB e 972 de SAEB. A PND contém 759.140
registros analíticos; esses registros não representam necessariamente pessoas
únicas.

Um controle metodológico importante foi comparar, a duas casas decimais, o
agregado estadual oficial do SAEB 2023 com médias escolares reconstruídas e
ponderadas pelos presentes. Elas coincidiram em **0 de 108** comparações; essa
diferença não foi interpretada como erro nos dados escolares. Para esse recorte,
a Silver e a Gold preservam o agregado oficial por UF, validado em **108 de 108**
comparações.

Na PND, os níveis são classificados pela nota geral publicada `NT_GER`.
`NT_OBJ` e `NT_DIS` representam, respectivamente, as notas objetiva e
discursiva; os níveis e percentuais abaixo usam `NT_GER`, não essas notas
isoladamente. No recorte do projeto, 265.915 registros ficaram Abaixo do
Básico, 309.425 Básicos e 183.800 Adequados; Básico ou Adequado soma 493.225
registros (64,97%). Essa classificação não representa aprovação em concurso.

## Como os dados são organizados

| Camada | Responsabilidade |
|---|---|
| **Raw** | Adquirir e preservar os arquivos oficiais; conferir os hashes SHA-256 do manifesto. |
| **Bronze** | Ler as fontes e convertê-las para Parquet, preservando valores, estrutura e metadados de origem. |
| **Silver** | Aplicar recortes e harmonizações documentadas, com rastreabilidade e validação independente. |
| **Gold** | Organizar os resultados em cinco fatos e cinco dimensões, com validação de grão e integridade referencial. |
| **Power BI** | Consumir os Parquets Gold e apresentar medidas DAX e visualizações. |

## Diferenciais de engenharia

- **Harmonização histórica:** adapta layouts, categorias e granularidades sem
  apagar as particularidades de cada fonte.
- **Fidelidade e validação:** compara cabeçalhos e valores integralmente com as
  fontes e valida as transformações por mecanismos independentes.
- **Rastreabilidade e precisão:** mantém a origem dos dados e controla a
  precisão numérica conforme as regras de cada indicador.
- **Reprodutibilidade:** fixa o ambiente e compara execuções isoladas. A
  evidência binária acima é restrita às execuções em Windows; não demonstra
  identidade entre sistemas operacionais ou arquiteturas diferentes.
- **Publicação controlada:** isola as execuções e permite recuperar a última
  publicação válida após uma interrupção.

## Tecnologias utilizadas

| Tecnologia | Finalidade no projeto |
|---|---|
| Python 3.12 | Implementação e orquestração do pipeline. |
| Pandas e NumPy | Leitura, transformação, comparação e validação tabular e numérica. |
| PyArrow e Parquet | Armazenamento colunar e leitura/escrita das camadas analíticas. |
| OpenPyXL, xlrd, Pyxlsb e Python-Calamine | Leitura e comparação dos formatos de planilha usados pelas fontes. |
| Jupyter | Demonstração exploratória e didática do fluxo por indicador. |
| Unittest | Testes automatizados de contratos e regressões do software. |
| Git e GitHub Actions | Histórico de versões e verificações automatizadas em Windows e Linux. |
| Power BI, Power Query e DAX | Conexão às tabelas Gold, modelagem semântica, medidas e visualizações. |

Esses controles apoiam a análise e a rastreabilidade, mas não substituem a
avaliação metodológica nem eliminam toda possibilidade de erro.

O modelo contém **16 relacionamentos** e **27 medidas DAX**. O painel tem sete
páginas. As 27 expressões extraídas diretamente do PBIX foram comparadas com
[`powerbi/medidas_power_bi.dax`](powerbi/medidas_power_bi.dax). O PBIX é o único
artefato oficial do painel; o projeto PBIP foi removido.

## Painel Power BI

O arquivo oficial é
[`powerbi/pbix/analise_indicadores_PND_oficial.pbix`](powerbi/pbix/analise_indicadores_PND_oficial.pbix).
Abra-o diretamente no Power BI Desktop para Windows. Para atualizar os dados
em outro computador, gere e valide a Gold e ajuste a origem da consulta para a
pasta `data/gold` local, conforme o
[guia de configuração do PBIX](docs/modelagem_power_bi.md).

<p>
  <img src="prints/Panorama%20da%20Educação%20Básica%20Brasileira.png" width="48%" alt="Panorama da Educação Básica Brasileira">
  <img src="prints/Aprendizagem%20x%20Fluxo%20Escolar.png" width="48%" alt="Aprendizagem x Fluxo Escolar">
</p>
<p>
  <img src="prints/PND%202025.png" width="48%" alt="PND 2025 — níveis por nota geral">
  <img src="prints/Metodologia%20e%20Dados.png" width="48%" alt="Metodologia e Dados">
</p>

As capturas documentam páginas e recortes específicos; não certificam todas as
interações visuais possíveis. A TDI é exibida como percentual, e sua variação
temporal é expressa em pontos percentuais. A documentação detalha também a
formatação das medidas PND.

## Instalação e execução

Use **CPython 3.12.10 de 64 bits**. `requirements.txt` declara as dependências
diretas; `requirements.lock` fixa também as versões transitivas e é a
especificação usada para instalar o ambiente. A configuração é verificada no
GitHub Actions em Windows e Linux.

Instale o Python pela
[distribuição oficial 3.12.10](https://www.python.org/downloads/release/python-31210/)
e crie um ambiente virtual.

**Windows PowerShell**

```powershell
py -3.12 -c "import sys; assert sys.version_info[:3] == (3, 12, 10)"
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.lock
python -m pip check
```

**Linux / Bash**

```bash
python3.12 -c 'import sys; assert sys.version_info[:3] == (3, 12, 10)'
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock
python -m pip check
```

Para extrair os pacotes RAR usados pelas fontes, disponibilize `bsdtar` ou um
`tar` baseado em libarchive no `PATH`. GNU tar sem suporte a RAR não é
suficiente.

Com o ambiente ativo, obtenha os insumos e confira sua integridade:

```bash
python scripts/baixar_raw.py --estrito
python scripts/gerar_manifesto_raw.py --check
```

O modo estrito exige os hashes registrados e não atualiza o manifesto para
aceitar arquivos divergentes. Para investigar atualizações das fontes, opções
e relatórios, consulte [aquisição da Raw](docs/automacao_raw.md).

Execute o pipeline completo:

```bash
python src/pipeline.py full
```

O comando verifica a Raw antes das 35 etapas e interrompe a execução se os
insumos não passarem. Para conferir os comandos disponíveis sem processar os
dados, use `python src/pipeline.py --list` ou
`python src/pipeline.py full --dry-run`.

## Testes e validação

Os controles têm objetivos diferentes e complementares:

- **Testes de software:** os 178 testes automatizados aprovados verificam
  contratos e comportamentos do código; não substituem a validação dos
  arquivos reais.
- **Validadores de dados:** conferem hashes, estruturas, valores, completude,
  grãos, unicidade, consistência entre camadas e integridade referencial nos
  dados processados.
- **Auditorias metodológicas:** fundamentam recortes e escolhas de fonte,
  como o uso do agregado oficial do SAEB 2023. Nenhum desses controles garante
  ausência absoluta de erros.

Comandos de verificação:

```bash
python -m unittest discover -s tests -v
python -m compileall -q src scripts tests
python src/pipeline.py validate-gold
python src/pipeline.py validate-gold --last-valid
```

`validate-gold` verifica a publicação atual em relação à Raw e à execução mais
recente. `--last-valid` valida a Gold que permanece publicada mesmo quando ela
vem de uma execução anterior; não seleciona outro snapshot arbitrário do
histórico. A opção usa o dicionário PND arquivado correspondente, conferido
contra o manifesto daquela execução, sem fallback silencioso para a Raw atual.
Veja os detalhes dos validadores e da recuperação de publicação em
[Gold](docs/camada_gold.md).

O workflow de qualidade executa instalação pelo lock, `pip check`,
`compileall`, os testes, a listagem de comandos e o `dry-run` em
`ubuntu-24.04` e `windows-latest`. Ele não baixa a Raw nem executa o pipeline
completo.

## Recortes e limitações

- Os resultados históricos são agregados por UF e restritos à rede pública e
  às duas etapas do Ensino Fundamental indicadas. As fontes têm coberturas e
  particularidades metodológicas próprias; SAEB 2007/2009 tem ressalvas de
  composição de rede.
- O exemplo de TDI com sete UFs é ilustrativo, não uma taxa nacional ponderada.
  Médias simples não são automaticamente ponderadas pelo número de estudantes.
- Na PND, a contagem se refere a registros, não a pessoas únicas; o município
  representa o local de aplicação da prova, não necessariamente a residência.
- As comparações são descritivas. O painel não identifica relações causais.
- O lock controla as versões das dependências; não comprova identidade binária
  dos Parquets entre sistemas operacionais ou arquiteturas diferentes.

## Documentação do projeto

- [Fontes oficiais, inventário e hashes](docs/fontes_dados.md)
- [Aquisição e atualização da Raw](docs/automacao_raw.md)
- [Reprodutibilidade do ambiente Python](docs/reproducibilidade_ambiente.md)
- [Camada Bronze](docs/camada_bronze.md)
- [Camada Silver](docs/camada_silver.md)
- [Camada Gold e publicação](docs/camada_gold.md)
- [Definição metodológica de rede pública](docs/definicao_rede_publica.md)
- [Modelagem e medidas Power BI](docs/modelagem_power_bi.md)
- [Notebooks demonstrativos](notebooks/README.md)
- [Fontes LaTeX do TCC](tcc/README.md)
- [Apresentação e roteiro da defesa](tcc/apresentacao/README.md)
- [Referências acadêmicas](referencias/README.md)
- [Notas históricas das versões](docs/release_v1.2.0.md)

## Licença e citação

O projeto é disponibilizado sob a
[PolyForm Noncommercial License 1.0.0](LICENSE). Usos não comerciais são
permitidos nos termos da licença; uso comercial depende de autorização ou
licenciamento separado. Os metadados para citação estão em
[`CITATION.cff`](CITATION.cff).
