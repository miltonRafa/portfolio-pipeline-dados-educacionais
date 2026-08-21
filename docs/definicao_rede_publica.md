# Definicao Metodologica — Rede Publica

## 1. Objetivo

Este documento registra a definicao metodologica adotada para a dimensao de rede de ensino no projeto de pipeline de dados educacionais.

A definicao foi estabelecida apos as auditorias individuais das bases:

- SAEB;
- IDEB;
- Rendimento Escolar;
- Taxa de Distorcao Idade-Serie (TDI).

O objetivo e garantir que o conceito de rede publica seja utilizado de maneira consistente no modelo analitico, sem apagar as diferencas historicas e estruturais existentes entre as fontes originais.

A definicao e necessaria porque as bases do Inep nao utilizam uma unica forma de representar a dependencia administrativa ao longo de todos os anos e indicadores.

Dependendo da fonte e da edicao, a rede publica pode aparecer como:

- Publica;
- Publico;
- agregado de dependencias publicas;
- codigo de tipo de rede;
- indicador binario de escola publica;
- categorias individuais Federal, Estadual e Municipal.

Portanto, a padronizacao nao pode ser realizada apenas por igualdade textual entre os arquivos.

---

## 2. Conceito adotado

Para este projeto, considera-se rede publica o conjunto formado pelas dependencias administrativas:

- Federal;
- Estadual;
- Municipal.

A rede privada nao pertence a esse conjunto.

Na camada analitica padronizada, esse conceito sera representado como:

REDE = PUBLICA

Entretanto, a forma utilizada para identificar esse universo dependera da estrutura da fonte original.

A regra geral e:

> Sempre que a fonte disponibilizar diretamente um agregado oficial correspondente a rede publica, esse agregado sera utilizado. Quando a fonte estiver em nivel de escola ou utilizar codigos especificos, sera utilizado o campo oficial que identifica as escolas ou a categoria pertencente a rede publica.

Nao sera criada uma media simples entre Federal, Estadual e Municipal para representar a rede publica quando a propria fonte ja fornecer o resultado agregado.

---

## 3. Por que nao somar ou calcular uma media simples das redes

A consolidacao da rede publica nao significa somar ou tirar a media aritmetica dos valores das redes:

Federal
Estadual
Municipal

Esse procedimento seria metodologicamente inadequado para varios indicadores.

Por exemplo:

- uma taxa de aprovacao da rede estadual nao possui o mesmo numero de estudantes que a taxa municipal;
- a TDI estadual e a TDI municipal tambem possuem populacoes diferentes;
- medias de proficiencia do SAEB dependem da quantidade de participantes;
- o IDEB e um indicador composto e nao pode ser reconstruido pela media simples dos IDEBs das dependencias administrativas.

Portanto:

Federal + Estadual + Municipal

e a definicao conceitual do universo publico, mas nao uma formula aritmetica aplicada aos indicadores.

Quando existe um agregado publico oficial, ele possui prioridade sobre qualquer reconstrucao.

---

## 4. Rendimento Escolar

### 4.1 Estrutura encontrada

A auditoria dos arquivos de Rendimento Escolar identificou categorias como:

- Federal;
- Estadual;
- Municipal;
- Particular / Privada;
- Publico / Publica;
- Total.

Tambem foram encontradas as categorias de localizacao:

- Rural;
- Urbana;
- Total.

### 4.2 Resultado da auditoria

Em todos os anos auditados entre 2007 e 2023 foi encontrado diretamente o agregado correspondente a rede publica.

Para a combinacao:

Rede = Publica
Localizacao = Total

foram encontrados:

27 / 27 UFs

em todos os anos.

Nao foram encontradas duplicidades para esse recorte.

### 4.3 Decisao

O pipeline utilizara diretamente o registro:

Rede = Publico / Publica
Localizacao = Total

Nao sera realizada reconstrucao da rede publica a partir de:

Federal
Estadual
Municipal

### 4.4 Justificativa

As taxas de:

- aprovacao;
- reprovacao;
- abandono

sao calculadas sobre populacoes escolares distintas em cada dependencia administrativa.

Uma media simples das taxas Federal, Estadual e Municipal nao reproduziria necessariamente a taxa da rede publica.

Como a propria fonte fornece o agregado publico, esse resultado oficial e metodologicamente preferivel.

---

## 5. Taxa de Distorcao Idade-Serie — TDI

### 5.1 Estrutura encontrada

A TDI apresenta estrutura semelhante a do Rendimento Escolar.

Foram identificadas categorias como:

- Federal;
- Estadual;
- Municipal;
- Particular / Privada;
- Publico / Publica;
- Total.

As categorias de localizacao sao:

- Rural;
- Urbana;
- Total.

### 5.2 Resultado da auditoria

Entre 2007 e 2023, o agregado publico esta disponivel diretamente para as 27 UFs.

No recorte:

Rede = Publica
Localizacao = Total

a auditoria encontrou:

27 / 27 UFs

para todos os anos.

Tambem foram confirmados:

- Anos Iniciais;
- Anos Finais;
- ausencia de duplicidades;
- ausencia de valores faltantes no recorte utilizado.

### 5.3 Decisao

Sera utilizado diretamente:

Rede = Publico / Publica
Localizacao = Total

### 5.4 Justificativa

A TDI e uma taxa calculada sobre matriculas.

Assim como no Rendimento Escolar, nao e metodologicamente adequado obter a TDI publica pela media simples das taxas:

Federal
Estadual
Municipal

A existencia do agregado publico oficial elimina a necessidade dessa reconstrucao.

---

## 6. IDEB

### 6.1 Estrutura encontrada

Os arquivos do IDEB apresentam resultados dimensionados por rede de ensino.

Entre as categorias encontradas estao:

- Total;
- Publica;
- Privada;
- Estadual;
- Municipal;
- outras categorias disponiveis conforme a edicao.

Em algumas edicoes, a denominacao publica apresenta marcacoes de notas metodologicas, por exemplo:

Publica (4)

Essas marcacoes nao representam uma rede diferente.

Sao referencias a notas da propria fonte.

### 6.2 Decisao

Para o IDEB sera utilizado diretamente o resultado publicado para:

Rede = Publica

Esse valor sera padronizado internamente para:

REDE = PUBLICA

As marcacoes associadas a notas, como:

Publica (4)

serao interpretadas como pertencentes a mesma categoria semantica:

PUBLICA

mas a nota metodologica correspondente devera ser preservada na documentacao.

### 6.3 Por que nao reconstruir o IDEB publico

O IDEB resulta da combinacao entre:

- desempenho no SAEB;
- indicador de rendimento/fluxo escolar.

Portanto, nao e possivel calcular corretamente o IDEB da rede publica simplesmente por:

media(IDEB Federal, IDEB Estadual, IDEB Municipal)

Essa media nao representa a metodologia oficial do indicador.

Por esse motivo, sera utilizado o agregado publico calculado e publicado pelo Inep.

---

## 7. Particularidades historicas do IDEB e do SAEB

As planilhas historicas possuem notas metodologicas que afetam a composicao dos resultados em determinadas edicoes.

Entre as observacoes identificadas estao:

2009:
Medias do SAEB 2009 e IDEB 2009 calculadas sem as escolas privadas em determinados registros indicados pela nota da fonte.

2011:
Medias do SAEB 2011 e IDEB 2011 calculadas sem as escolas federais nos registros associados a respectiva nota.

Essas observacoes fazem parte da metodologia oficial das edicoes.

O pipeline nao devera tentar corrigir retrospectivamente essas situacoes.

A regra sera:

- preservar os valores publicados;
- registrar a nota metodologica;
- nao inserir artificialmente redes que a propria edicao excluiu do calculo.

Isso e necessario para preservar a comparabilidade com a publicacao oficial do Inep.

---

## 8. SAEB

O SAEB exige tratamento especifico porque sua estrutura varia significativamente entre as edicoes.

Diferentemente de Rendimento, TDI e IDEB, nao existe uma unica coluna textual utilizada em todos os arquivos para representar a rede publica.

A definicao conceitual permanece:

Federal + Estadual + Municipal

mas a identificacao desse universo depende da estrutura do arquivo de cada edicao.

---

## 9. SAEB — arquivos agregados por UF

Nos arquivos em nivel de Unidade da Federacao, existem diferentes categorias de dependencia administrativa.

E necessario distinguir:

Total geral

de:

Total da rede publica

O total geral nao pode ser utilizado como sinonimo de rede publica quando inclui escolas privadas.

Por exemplo, algumas fontes apresentam explicitamente uma categoria equivalente a:

Total - Federal, Estadual, Municipal e Privada

Esse registro representa todas as dependencias administrativas e, portanto, nao corresponde ao recorte publico.

Quando estiver disponivel o agregado correspondente somente as redes:

Federal
Estadual
Municipal

esse sera o registro utilizado para representar:

REDE = PUBLICA

---

## 10. SAEB 2011

O arquivo de 2011 possui estrutura especifica em nivel de UF.

Entre suas variaveis estao:

ID_SAEB
ID_REGIAO
SIGLA_UF
ID_UF
ID_SERIE
ID_TIPO_REDE
ID_LOCALIZACAO
ID_CAPITAL
NU_PARTICIPANTES
MEDIA_LP
MEDIA_MT

Nessa edicao, a identificacao da rede nao e feita por uma descricao textual como "Publica", mas por:

ID_TIPO_REDE

Conforme definido na auditoria do SAEB, o codigo correspondente ao recorte publico utilizado pelo projeto e:

ID_TIPO_REDE = 5

Essa regra devera ficar explicita no codigo de transformacao correspondente a 2011.

Nao devera ser inferida a partir de outros anos.

---

## 11. SAEB — arquivos em nivel de escola

Em arquivos do SAEB em nivel escolar existe a variavel:

IN_PUBLICA

O dicionario da fonte identifica esse campo como indicador de escola publica.

As categorias sao utilizadas para distinguir:

escola privada

de:

escola publica

Para os arquivos escolares, o recorte sera:

IN_PUBLICA = 1

Esse filtro identifica as escolas pertencentes as redes publicas.

Posteriormente, os resultados serao agregados ao nivel de UF conforme a metodologia definida na auditoria especifica do SAEB.

A definicao da rede e o calculo da media sao duas etapas diferentes:

1. IN_PUBLICA define quais escolas pertencem ao universo publico;
2. a regra de agregacao define como seus resultados serao consolidados em nivel de UF.

---

## 12. Harmonizacao entre os indicadores

Embora as estruturas das fontes sejam diferentes, a dimensao final tera um unico significado.

| Indicador | Identificacao na fonte | Regra |
|---|---|---|
| Rendimento | Publico / Publica | usar agregado oficial |
| TDI | Publico / Publica | usar agregado oficial |
| IDEB | Publica / Publica com nota | usar agregado oficial |
| SAEB — agregado UF | agregado publico oficial | utilizar resultado correspondente a Federal + Estadual + Municipal |
| SAEB — 2011 | ID_TIPO_REDE = 5 | interpretar como rede publica conforme auditoria |
| SAEB — escola | IN_PUBLICA = 1 | selecionar escolas publicas |

Na camada padronizada, todos serao representados como:

PUBLICA

Essa padronizacao e semantica.

Ela nao significa que os arquivos de origem possuam estruturas identicas.

---

## 13. Preservacao da informacao original

A transformacao nao devera apagar a forma como a fonte originalmente representava a rede.

Sempre que tecnicamente util, a camada intermediaria devera preservar a categoria de origem.

Exemplo:

REDE_ORIGEM = Publico
REDE = PUBLICA

ou:

REDE_ORIGEM = Publica (4)
REDE = PUBLICA

ou:

REDE_ORIGEM = IN_PUBLICA=1
REDE = PUBLICA

Essa estrategia aumenta a rastreabilidade do pipeline.

Caso um resultado final apresente divergencia, sera possivel identificar qual regra da fonte originou aquele registro.

---

## 14. Regra para a camada Silver

A camada Silver sera responsavel pela harmonizacao da dimensao de rede.

O valor padronizado sera:

PUBLICA

A transformacao devera respeitar as regras especificas de cada fonte.

Nao havera uma regra generica como:

se rede em [Federal, Estadual, Municipal]:
    rede = PUBLICA

seguida de media simples dos valores.

Essa abordagem poderia produzir resultados metodologicamente incorretos.

A selecao devera ocorrer antes da consolidacao, utilizando a representacao oficial disponivel em cada fonte.

---

## 15. Regra para a camada Gold

As tabelas analiticas destinadas ao Power BI utilizarao:

REDE = PUBLICA

A dimensao podera possuir apenas essa categoria caso o escopo final permaneca restrito a rede publica.

Mesmo nesse cenario, a coluna de rede devera ser preservada nas tabelas fato quando contribuir para clareza, rastreabilidade e possibilidade de expansao futura do projeto.

---

## 16. O significado de PUBLICA no modelo final

No modelo analitico:

PUBLICA

deve ser interpretado como:

> Resultado correspondente ao universo das redes publicas de ensino — federal, estadual e municipal — obtido por meio do agregado oficial da fonte quando disponivel ou por meio do identificador oficial de escola/rede publica quando a estrutura da fonte exigir.

Essa definicao e mais precisa do que afirmar simplesmente:

"Federal + Estadual + Municipal"

porque distingue:

conceito da populacao

de:

procedimento matematico utilizado para calcular o indicador.

---

## 17. Regras que nao serao utilizadas

O pipeline nao devera:

1. utilizar a categoria Total quando ela incluir a rede privada;
2. considerar Total como sinonimo automatico de Publica;
3. calcular media simples entre Federal, Estadual e Municipal para criar uma rede publica;
4. somar taxas de dependencias administrativas;
5. recalcular IDEB publico a partir dos IDEBs das redes individuais;
6. ignorar notas metodologicas historicas do Inep;
7. transformar categorias privadas em publicas;
8. substituir resultados oficiais por estimativas proprias quando ja existir agregado publicado;
9. modificar os arquivos raw para padronizar nomenclaturas.

---

## 18. Rastreabilidade

As regras de rede deverao ser reproduziveis.

O pipeline devera permitir identificar, para cada indicador:

- arquivo de origem;
- ano;
- categoria original de rede;
- regra utilizada para selecionar o recorte publico;
- categoria padronizada resultante.

Exemplo conceitual:

INDICADOR | ANO | REDE_ORIGEM | REGRA | REDE
Rendimento | 2007 | Publico | AGREGADO_OFICIAL | PUBLICA
TDI | 2007 | Publico | AGREGADO_OFICIAL | PUBLICA
IDEB | 2011 | Publica (4) | AGREGADO_OFICIAL | PUBLICA
SAEB | 2011 | ID_TIPO_REDE=5 | CODIGO_OFICIAL | PUBLICA
SAEB | 2023 | IN_PUBLICA=1 | INDICADOR_ESCOLA | PUBLICA

Os nomes tecnicos definitivos dessas colunas serao definidos durante a implementacao da camada Silver.

---

## 19. Relacao com as auditorias

Esta decisao nao substitui os documentos de auditoria individuais.

Os documentos:

auditoria_saeb.md
auditoria_ideb.md
auditoria_rendimento.md
auditoria_tdi.md

registram as caracteristicas e problemas especificos de cada base.

Este documento registra a decisao transversal utilizada para integrar essas bases em um mesmo modelo analitico.

Portanto:

auditorias individuais
        ↓
comparacao das estruturas
        ↓
definicao transversal
        ↓
regra da camada Silver
        ↓
modelo Gold / Power BI

---

## 20. Conclusao

As auditorias demonstraram que o conceito de rede publica esta presente em todas as bases historicas utilizadas, mas sua representacao nao e uniforme.

Rendimento Escolar e TDI fornecem diretamente agregados de rede publica.

O IDEB fornece resultados oficiais para a categoria Publica.

O SAEB apresenta diferentes representacoes conforme a edicao, incluindo agregados por dependencia administrativa, codigos de tipo de rede e indicadores de escola publica.

Diante dessas diferencas, o projeto adotara uma harmonizacao semantica, e nao uma formula aritmetica universal.

A dimensao final sera:

REDE = PUBLICA

e representara o universo publico definido pelas dependencias:

Federal
Estadual
Municipal

respeitando a metodologia, o nivel de agregacao e as excecoes historicas de cada fonte.

Nenhum indicador sera reconstruido por media simples das dependencias administrativas quando existir um resultado oficial correspondente ao recorte publico.

Essa decisao passa a ser a regra metodologica oficial do projeto para a dimensao de rede de ensino.

---

## Historico de atualizacao

| Data | Alteracao |
|---|---|
| 18/08/2026 | Criacao da definicao transversal de rede publica |
| 18/08/2026 | Consolidacao das decisoes das auditorias de SAEB, IDEB, Rendimento e TDI |
| 18/08/2026 | Definidas regras especificas para agregado oficial, ID_TIPO_REDE e IN_PUBLICA |
| 18/08/2026 | Definida padronizacao final REDE = PUBLICA |