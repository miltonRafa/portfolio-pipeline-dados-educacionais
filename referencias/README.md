# Referencias academicas

Esta pasta e reservada aos documentos consultados durante a elaboracao do TCC.
Os arquivos PDF sao mantidos apenas no ambiente local e nao sao versionados,
pois algumas obras podem possuir restricoes de redistribuicao e o conjunto
acrescentaria aproximadamente 54,5 MB ao repositorio.

A identificacao bibliografica utilizada pelo trabalho esta no arquivo
[`tcc/bib/abntex2-modelo-references.bib`](../tcc/bib/abntex2-modelo-references.bib).
O arquivo `.bib` e a fonte de referencia para autoria, titulo, ano, instituicao,
periodico, DOI e URL, conforme a disponibilidade desses elementos em cada obra.

## Convencao local

Quando uma copia local legalmente obtida for necessaria para consulta, o nome
deve seguir o formato:

```text
Autor_Ano_Titulo_resumido.pdf
```

Os nomes devem usar caracteres ASCII, sem espacos, para manter compatibilidade
com Windows, Git e Overleaf. A ausencia de um PDF nesta pasta nao impede a
compilacao do TCC: o LaTeX utiliza apenas os registros do arquivo `.bib`.

## Identificadores de acesso

Algumas publicacoes possuem identificadores persistentes registrados e
conferidos no material consultado:

| Chave BibTeX | Publicacao | Identificador |
|---|---|---|
| `soares2021` | Mineracao de dados da Educacao Basica brasileira usando as bases do INEP | DOI `10.22456/1679-1916.118526` |
| `ilha2021` | A construcao de um Data Warehouse utilizando os indicadores educacionais do INEP | DOI `10.1590/SciELOPreprints.2166` |
| `moreno2026tomada` | Tomada de decisao e qualidade dos dados | DOI `10.22167/2675-6528-202602262` |
| `dias2026avaliaccao` | Avaliacao e indicadores educacionais, politicas publicas e escola | DOI `10.63330/armv2n8-015` |

Para as demais obras, devem ser usados os dados bibliograficos do `.bib` e os
catalogos ou repositorios institucionais de origem. Nenhum endereco foi
acrescentado aqui sem confirmacao no documento consultado.

## Fontes localizadas pela identificacao bibliografica

Conferencia em 29/10/2026, usando os titulos, autores, ISBNs e DOIs registrados
no TCC. Os enderecos abaixo identificam a obra ou seu registro; nem todos
oferecem o texto integral. A autenticidade do registro nao certifica, por si
so, a qualidade metodologica de cada estudo ou a revisao por pares.

| Chave BibTeX | Tipo de fonte | Registro ou fonte de origem |
|---|---|---|
| `soares2021` | Artigo | [RENOTE/UFRGS](https://seer.ufrgs.br/index.php/renote/article/view/118526) |
| `martinsfilho2025` | TCC | [Repositorio da UFC](https://repositorio.ufc.br/handle/riufc/80326) |
| `ilha2021` | Preprint | [SciELO Preprints](https://preprints.scielo.org/index.php/scielo/preprint/view/2166) |
| `wanderley2021` | TCC | [Repositorio da UFCG](https://dspace.sti.ufcg.edu.br/handle/riufcg/19899) |
| `kimball2013data` | Livro | [Editora Wiley](https://www.wiley.com/en-gb/the-data-warehouse-toolkit-the-definitive-guide-to-dimensional-modeling-3rd-edition-p-9781118530801) |
| `gil2002` | Livro | [Registro bibliografico da UnB, com acesso a capitulos](https://bds.unb.br/handle/123456789/1132) |
| `prodanov2013` | Livro | [Editora Feevale](https://www.feevale.br/institucional/editora-feevale/metodologia-do-trabalho-cientifico---2-edicao) |
| `loh2014bi` | Livro | [Publicacao do proprio autor](https://miningtext.blogspot.com/2014/05/livro-gratis-free-e-book-sobre-bi.html) |
| `da2025proveniencia` | Dissertacao | [Repositorio da UFSCar](https://repositorio.ufscar.br/items/8076ed80-45a0-4641-9ac6-9ee3986f18aa) |
| `carvalho2025estudo` | TCC | [Repositorio da UFRN](https://repositorio.ufrn.br/handle/123456789/66889) |
| `ferreira2024dados` | Tese | [Lume/UFRGS](https://lume.ufrgs.br/handle/10183/275864) |
| `moreno2026tomada` | Artigo derivado de TCC | [DOI da Revista E&S](https://doi.org/10.22167/2675-6528-202602262) |
| `leal2025distorccao` | TCC | [Repositorio da UFOP](https://monografias.ufop.br/handle/35400000/8684) |
| `de2026desigualdades` | Artigo | [Cadernos da FUCAMP](https://revistas.fucamp.edu.br/index.php/cadernos/article/view/4387) |
| `dias2026avaliaccao` | Artigo | [Aurum Revista Multidisciplinar](https://aurumpublicacoes.com/index.php/MA/article/view/2210) |

O registro de Carvalho foi encontrado pela API publica do repositorio da UFRN,
mesmo sem resultado correspondente na busca comum. Titulo, autor, orientador,
banca e ano coincidem com a copia local. Identificador: `123456789/66889`.

O trabalho de Ilha e Moreira Junior deve ser identificado como preprint,
sem presumir revisao por pares. A pagina editorial consultada de Moreno e
Oliveira informa derivacao de TCC e adaptacao com apoio de ferramenta de IA;
isso nao substitui a leitura critica do metodo e do trabalho original.

As oito entradas institucionais do INEP e da Microsoft permanecem identificadas
pelas URLs oficiais no `.bib`. Sao as fontes de procedencia dos dados, das
regras oficiais e da documentacao do software, conforme o assunto citado.

Esta conferencia nao identificou quais obras foram retiradas antes da primeira
versao Git: ela ja registra as mesmas 23 chaves atuais. Nao se deve inferir uma
lista de exclusoes apenas da antiga contagem incorreta de 26 entradas.
