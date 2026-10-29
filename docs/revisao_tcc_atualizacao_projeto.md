# Revisao final do TCC em relacao ao projeto

## 1. Objetivo

Este documento registra a verificacao de coerencia entre o TCC e o estado atual
do repositorio `portfolio-pipeline-dados-educacionais`.

A revisao anterior descrevia uma versao antiga do trabalho e listava alteracoes
que ja foram incorporadas. O presente registro substitui aquele diagnostico e
considera como fonte principal o projeto LaTeX versionado em `tcc/` e o PDF
gerado em `output/pdf/Template_TCC_UEMG_revisado.pdf`.

Data desta revisao: 29 de outubro de 2026.

## 2. Materiais verificados

- `README.md`;
- `src/pipeline.py` e scripts das camadas;
- documentacao em `docs/`;
- manifesto e hashes das fontes;
- `powerbi/medidas_power_bi.dax`;
- arquivo PBIX e capturas do dashboard;
- cinco notebooks demonstrativos;
- fontes LaTeX em `tcc/`;
- bibliografia em `tcc/bib/abntex2-modelo-references.bib`;
- PDF final compilado pelo template institucional com 95 paginas.

## 3. Situacao geral

O TCC esta coerente com a implementacao atual do projeto nos aspectos tecnicos,
metodologicos e analiticos verificados. A versao atual nao descreve mais o Power
Query como responsavel principal pela transformacao. O texto apresenta o
pipeline Python, a arquitetura Raw, Bronze, Silver e Gold e o Power BI como
camada de consumo analitico.

O trabalho mantem carater descritivo e exploratorio. Os resultados nao sao
apresentados como evidencia causal, e as limitacoes de granularidade,
periodicidade e comparabilidade das fontes estao registradas.

## 4. Coerencia por componente

### 4.1 Fontes e recorte

O TCC utiliza e descreve as cinco fontes efetivamente tratadas:

- IDEB;
- SAEB;
- Taxas de Rendimento Escolar;
- Taxa de Distorcao Idade-Serie;
- Prova Nacional Docente de 2025.

O recorte historico permanece em 2007-2023 para IDEB, SAEB, Rendimento e TDI.
A PND e apresentada separadamente em 2025 e nao e tratada como continuidade da
serie historica da Educacao Basica.

A analise historica esta delimitada principalmente a Unidade Federativa, rede
publica, Anos Iniciais e Anos Finais do Ensino Fundamental. O Ensino Medio nao
integra o recorte analitico final.

### 4.2 Arquitetura e ETL

O TCC documenta corretamente:

```text
Raw -> Bronze -> Silver -> Gold -> Power BI
```

- Raw: preservacao organizada dos insumos oficiais;
- Bronze: ingestao tecnica e metadados de origem;
- Silver: recorte, harmonizacao e validacao semantica;
- Gold: fatos e dimensoes em Parquet para consumo analitico;
- Power BI: relacionamentos, medidas DAX e visualizacoes.

O texto tambem registra que o Power Query conecta o modelo aos Parquets da Gold
e nao substitui o pipeline Python.

### 4.3 Reprodutibilidade

O TCC registra os mecanismos realmente existentes no projeto:

- inventario de 54 arquivos Raw;
- caminhos e finalidades no manifesto;
- hashes SHA-256 dos insumos;
- links para fontes oficiais;
- aquisicao, selecao, extracao e nomenclatura automatizadas por `scripts/baixar_raw.py`;
- convencao de nomenclatura local;
- metadados de linhagem;
- validadores por camada;
- orquestracao por `src/pipeline.py`;
- verificacao por `python scripts/gerar_manifesto_raw.py --check`;
- inspecao da sequencia com `python src/pipeline.py full --dry-run`.

A copia organizada da Raw e tratada como conveniencia de reproducao e nao como
substituta das fontes oficiais.

As orientacoes operacionais de aquisicao manual foram substituidas pelo
procedimento automatizado no README e na documentacao de fontes. O TCC
descreve a automacao e suas limitacoes metodologicas, preservando as referencias
oficiais e os criterios de selecao. As tabelas de arquivos permanecem como
inventario e evidencia de procedencia, nao como instrucoes de download manual.

A aquisicao automatizada tambem consta do Resumo/Abstract, do objetivo
especifico c e do ultimo item das contribuicoes da Introducao. A secao 4.3
foi denominada "Arquitetura e processo de ingestao", distinguindo aquisicao
(fontes oficiais para Raw) de ingestao (Raw para Bronze). O fluxo das camadas
foi preservado e complementado por figura LaTeX do percurso completo, incluindo
fontes oficiais e aquisicao automatizada. A afirmacao sobre ausencia de preparo
manual foi delimitada ao conjunto de fontes coberto nesta versao do projeto.

A captura `tcc/figs/dashboard-metodologia.png` continua retratando a pagina
do Power BI e suas camadas a partir da Raw. O novo fluxo metodologico e uma
figura independente escrita em LaTeX, sem alteracao dessa captura.

### 4.4 Regras especificas dos indicadores

O SAEB utiliza resultados oficiais agregados por UF na serie analitica. O TCC
nao afirma que os valores estaduais foram recompostos por media simples ou
ponderada de escolas.

O IDEB utiliza o arquivo local canonico
`data/raw/ideb/divulgacao_regioes_ufs_ideb.xlsx`. O texto distingue o arquivo
fisico corrente, que pode conter edicoes posteriores, do recorte deliberado de
2007-2023 aplicado pela Silver e pela Gold.

Rendimento e TDI preservam as categorias de origem necessarias para auditoria e
produzem categorias analiticas padronizadas. A distincao entre campos de origem
e campos harmonizados esta explicada na metodologia.

A PND adota como populacao analitica 759.140 registros. A classificacao de
desempenho usa `NT_OBJ` e os pontos de corte documentados:

```text
NT_OBJ < 50        -> NAO_PROFICIENTE
50 <= NT_OBJ < 70  -> PADRAO_1
NT_OBJ >= 70       -> PADRAO_2
```

O TCC esclarece que `UF_PROVA` e `CO_MUNICIPIO_PROVA` representam o local de
aplicacao, e nao necessariamente a residencia do participante.

### 4.5 Modelo dimensional

O TCC e o projeto apresentam cinco dimensoes e cinco fatos:

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

Os relacionamentos sao descritos como `1:*`, ativos e com filtro unidirecional
da dimensao para a fato. O TCC tambem registra corretamente que nao existe
relacao fisica direta entre `DIM_UF` e `DIM_MUNICIPIO`, evitando um segundo
caminho geografico ate `FATO_PND`.

### 4.6 Power BI e DAX

O modelo semantico possui 27 medidas DAX, documentadas em
`docs/modelagem_power_bi.md` e implementadas em
`powerbi/medidas_power_bi.dax`.

O TCC contempla medidas de Rendimento, TDI, IDEB, SAEB, PND, apoio temporal e
variacoes. As variacoes comparam o primeiro e o ultimo ano com dado disponivel
no intervalo selecionado, respeitando a periodicidade anual ou bienal de cada
indicador.

As paginas de dashboard apresentadas no TCC correspondem aos temas versionados
no projeto: panorama, comparacao por UF, aprendizagem e fluxo, variacoes, TDI,
PND e metodologia.

### 4.7 Resultados e limites interpretativos

As cardinalidades e os numeros apresentados no capitulo de resultados estao
alinhados ao projeto documentado. Para a PND, o texto registra:

- 265.932 nao proficientes;
- 304.638 participantes no Padrao 1;
- 188.570 participantes no Padrao 2;
- 493.208 proficientes;
- 64,97% de proficientes na populacao analitica.

O texto diferencia media das linhas do modelo de media nacional ponderada por
matricula. Tambem evita atribuir diferencas territoriais a causas que nao foram
testadas pelo pipeline.

## 5. Bibliografia

O arquivo `.bib` possui 23 entradas e nao apresenta chaves ou obras duplicadas
identificadas. Todas as entradas sao citadas e aparecem na bibliografia gerada.
As definicoes dos indicadores permanecem apoiadas nas fontes oficiais do INEP;
os trabalhos academicos complementam a fundamentacao e a discussao.

Os PDFs usados para consulta permanecem localmente em `referencias/`, mas sao
ignorados pelo Git por tamanho e possiveis restricoes de redistribuicao. A
compilacao depende do `.bib`, nao dessas copias locais.

## 6. Notebooks, testes e entrega

O repositorio possui um notebook demonstrativo para cada indicador. Os
notebooks chamam os scripts oficiais e nao substituem a implementacao em
`src/`.

Os testes estruturais foram executados com:

```powershell
python -m unittest discover -s tests -v
```

Resultado da verificacao de 29/10/2026: 27 testes aprovados, incluindo os
testes de download automatico. O comando `python scripts/baixar_raw.py`
prepara os 54 insumos diretamente em `data/raw`, antes do pipeline, com
extracao seletiva, verificacao de hashes e limpeza dos temporarios.

Na mesma data foi incorporada a revisao oficial de 09/09/2026 do dicionario
PND. O manifesto, os checksums e a documentacao de fontes foram atualizados
pelo gerador oficial. Os outros 53 arquivos mantiveram os hashes anteriores;
os dados analiticos e os resultados apresentados no TCC nao mudaram. Consulte
`docs/automacao_raw.md` para o procedimento e a evidencia da revisao.

O download tambem compara arquivos novos com hash diferente contra uma copia
anterior validada. Quando o conteudo protegido for igual, atualiza automaticamente
a Raw e o manifesto, com backup e registro da comparacao. Diferencas historicas
ou falhas de verificacao preservam a versao anterior e sao explicadas no terminal
e no relatorio. No IDEB, anos posteriores a 2023 podem ser incorporados fisicamente
sem expandir o periodo analitico. O modo `--estrito` mantem reproducao binaria.

O projeto LaTeX foi reorganizado em `tcc/`, preservando a classe
`tccUEMG.cls`. A compilacao completa com `pdflatex`, `bibtex`, `makeindex` e
duas novas passagens de `pdflatex` produziu um PDF de 95 paginas, sem citacoes
ou referencias indefinidas e sem erros criticos de compilacao.

O PDF foi recompilado a partir de `tcc/main_tcc_uemg.tex` e da classe
institucional `tccUEMG.cls` apos a atualizacao da aquisicao automatizada.
As paginas alteradas foram renderizadas e conferidas. O arquivo consolidado
permanece em `output/pdf/Template_TCC_UEMG_revisado.pdf`.

### 6.1 Conferencia posterior a automacao da aquisicao

Em 29/10/2026, foram conferidos os links locais do README, da documentacao,
dos notebooks e do TCC, sem caminhos ausentes. O manifesto validou 54/54
insumos; a validacao global da Gold confirmou as cardinalidades publicadas,
os graos e a integridade referencial, com `MODELO DIMENSIONAL GOLD: OK`.
Os 27 testes e a compilacao dos arquivos Python foram aprovados.

As auditorias de fontes tiveram os status de rede e fonte atualizados para
referenciar as decisoes ja consolidadas, preservando os achados originais.
A imutabilidade da Raw foi delimitada ao periodo das transformacoes, distinguindo
a atualizacao controlada anterior. Os metadados de citacao foram alinhados
a tag existente `v1.1.0`, de 02/10/2026, sem criar uma nova release.

O PDF consolidado coincide com o compilado pelo template e contem 95 paginas.
A bibliografia tem 23 entradas e 23 itens na lista gerada. As notas de release
anteriores preservam suas contagens historicas e nao descrevem a versao em
desenvolvimento. As verificacoes desta revisao nao regeneraram Bronze, Silver
ou Gold nem alteraram os resultados analiticos.

Foi corrigida uma falha de codificacao na impressao do validador Gold em
terminais Windows. O orquestrador tambem configura a saida dos subprocessos
para UTF-8 por padrao, respeitando uma configuracao explicita do ambiente.

## 7. Pendencias que nao sao erros do projeto

Os seguintes itens dependem do processo academico ou institucional e nao podem
ser considerados concluidos apenas pelo repositorio:

- aprovacao do conteudo pelo orientador e pela banca;
- confirmacao das regras formais vigentes da UEMG para a entrega;
- ficha catalografica emitida pela biblioteca, quando exigida;
- folha de aprovacao definitiva apos a defesa;
- eventuais ajustes solicitados pela banca;
- decisao institucional sobre publicacao ou hospedagem do dashboard.

Esses pontos nao representam divergencia entre o TCC e o pipeline.

## 8. Conclusao

O TCC atual esta tecnicamente alinhado ao repositorio. A metodologia, as fontes,
os recortes, as regras dos indicadores, o modelo dimensional, as medidas DAX,
os resultados e as limitacoes descritas correspondem ao estado versionado do
projeto.

Nao foi identificada pendencia tecnica que impeca a apresentacao do trabalho.
A etapa seguinte e a revisao academica final pelo orientador e a adequacao dos
elementos institucionais exigidos para deposito e defesa.
