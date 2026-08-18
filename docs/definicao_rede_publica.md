# Definição Metodológica — Rede Pública

## 1. Objetivo

Este documento registra a definição metodológica adotada para a dimensão de rede de ensino no projeto de pipeline de dados educacionais.

A definição foi estabelecida após as auditorias individuais das bases:

- SAEB;
- IDEB;
- Rendimento Escolar;
- Taxa de Distorção Idade-Série (TDI).

O objetivo é garantir que o conceito de rede pública seja utilizado de maneira consistente no modelo analítico, sem apagar as diferenças históricas e estruturais existentes entre as fontes originais.

A definição é necessária porque as bases do Inep não utilizam uma única forma de representar a dependência administrativa ao longo de todos os anos e indicadores.

Dependendo da fonte e da edição, a rede pública pode aparecer como:

- Pública;
- Publico;
- agregado de dependências públicas;
- código de tipo de rede;
- indicador binário de escola pública;
- categorias individuais Federal, Estadual e Municipal.

Portanto, a padronização não pode ser realizada apenas por igualdade textual entre os arquivos.

---

## 2. Conceito adotado

Para este projeto, considera-se rede pública o conjunto formado pelas dependências administrativas:

- Federal;
- Estadual;
- Municipal.

A rede privada não pertence a esse conjunto.

Na camada analítica padronizada, esse conceito será representado como:

REDE = PUBLICA

Entretanto, a forma utilizada para identificar esse universo dependerá da estrutura da fonte original.

A regra geral é:

> Sempre que a fonte disponibilizar diretamente um agregado oficial correspondente à rede pública, esse agregado será utilizado. Quando a fonte estiver em nível de escola ou utilizar códigos específicos, será utilizado o campo oficial que identifica as escolas ou a categoria pertencente à rede pública.

Não será criada uma média simples entre Federal, Estadual e Municipal para representar a rede pública quando a própria fonte já fornecer o resultado agregado.

---

## 3. Por que não somar ou calcular uma média simples das redes

A consolidação da rede pública não significa somar ou tirar a média aritmética dos valores das redes:

Federal
Estadual
Municipal

Esse procedimento seria metodologicamente inadequado para vários indicadores.

Por exemplo:

- uma taxa de aprovação da rede estadual não possui o mesmo número de estudantes que a taxa municipal;
- a TDI estadual e a TDI municipal também possuem populações diferentes;
- médias de proficiência do SAEB dependem da quantidade de participantes;
- o IDEB é um indicador composto e não pode ser reconstruído pela média simples dos IDEBs das dependências administrativas.

Portanto:

Federal + Estadual + Municipal

é a definição conceitual do universo público, mas não uma fórmula aritmética aplicada aos indicadores.

Quando existe um agregado público oficial, ele possui prioridade sobre qualquer reconstrução.

---

## 4. Rendimento Escolar

### 4.1 Estrutura encontrada

A auditoria dos arquivos de Rendimento Escolar identificou categorias como:

- Federal;
- Estadual;
- Municipal;
- Particular / Privada;
- Publico / Pública;
- Total.

Também foram encontradas as categorias de localização:

- Rural;
- Urbana;
- Total.

### 4.2 Resultado da auditoria

Em todos os anos auditados entre 2007 e 2023 foi encontrado diretamente o agregado correspondente à rede pública.

Para a combinação:

Rede = Pública
Localização = Total

foram encontrados:

27 / 27 UFs

em todos os anos.

Não foram encontradas duplicidades para esse recorte.

### 4.3 Decisão

O pipeline utilizará diretamente o registro:

Rede = Publico / Pública
Localização = Total

Não será realizada reconstrução da rede pública a partir de:

Federal
Estadual
Municipal

### 4.4 Justificativa

As taxas de:

- aprovação;
- reprovação;
- abandono

são calculadas sobre populações escolares distintas em cada dependência administrativa.

Uma média simples das taxas Federal, Estadual e Municipal não reproduziria necessariamente a taxa da rede pública.

Como a própria fonte fornece o agregado público, esse resultado oficial é metodologicamente preferível.

---

## 5. Taxa de Distorção Idade-Série — TDI

### 5.1 Estrutura encontrada

A TDI apresenta estrutura semelhante à do Rendimento Escolar.

Foram identificadas categorias como:

- Federal;
- Estadual;
- Municipal;
- Particular / Privada;
- Publico / Pública;
- Total.

As categorias de localização são:

- Rural;
- Urbana;
- Total.

### 5.2 Resultado da auditoria

Entre 2007 e 2023, o agregado público está disponível diretamente para as 27 UFs.

No recorte:

Rede = Pública
Localização = Total

a auditoria encontrou:

27 / 27 UFs

para todos os anos.

Também foram confirmados:

- Anos Iniciais;
- Anos Finais;
- ausência de duplicidades;
- ausência de valores faltantes no recorte utilizado.

### 5.3 Decisão

Será utilizado diretamente:

Rede = Publico / Pública
Localização = Total

### 5.4 Justificativa

A TDI é uma taxa calculada sobre matrículas.

Assim como no Rendimento Escolar, não é metodologicamente adequado obter a TDI pública pela média simples das taxas:

Federal
Estadual
Municipal

A existência do agregado público oficial elimina a necessidade dessa reconstrução.

---

## 6. IDEB

### 6.1 Estrutura encontrada

Os arquivos do IDEB apresentam resultados dimensionados por rede de ensino.

Entre as categorias encontradas estão:

- Total;
- Pública;
- Privada;
- Estadual;
- Municipal;
- outras categorias disponíveis conforme a edição.

Em algumas edições, a denominação pública apresenta marcações de notas metodológicas, por exemplo:

Pública (4)

Essas marcações não representam uma rede diferente.

São referências a notas da própria fonte.

### 6.2 Decisão

Para o IDEB será utilizado diretamente o resultado publicado para:

Rede = Pública

Esse valor será padronizado internamente para:

REDE = PUBLICA

As marcações associadas a notas, como:

Pública (4)

serão interpretadas como pertencentes à mesma categoria semântica:

PUBLICA

mas a nota metodológica correspondente deverá ser preservada na documentação.

### 6.3 Por que não reconstruir o IDEB público

O IDEB resulta da combinação entre:

- desempenho no SAEB;
- indicador de rendimento/fluxo escolar.

Portanto, não é possível calcular corretamente o IDEB da rede pública simplesmente por:

média(IDEB Federal, IDEB Estadual, IDEB Municipal)

Essa média não representa a metodologia oficial do indicador.

Por esse motivo, será utilizado o agregado público calculado e publicado pelo Inep.

---

## 7. Particularidades históricas do IDEB e do SAEB

As planilhas históricas possuem notas metodológicas que afetam a composição dos resultados em determinadas edições.

Entre as observações identificadas estão:

2009:
Médias do SAEB 2009 e IDEB 2009 calculadas sem as escolas privadas em determinados registros indicados pela nota da fonte.

2011:
Médias do SAEB 2011 e IDEB 2011 calculadas sem as escolas federais nos registros associados à respectiva nota.

Essas observações fazem parte da metodologia oficial das edições.

O pipeline não deverá tentar corrigir retrospectivamente essas situações.

A regra será:

- preservar os valores publicados;
- registrar a nota metodológica;
- não inserir artificialmente redes que a própria edição excluiu do cálculo.

Isso é necessário para preservar a comparabilidade com a publicação oficial do Inep.

---

## 8. SAEB

O SAEB exige tratamento específico porque sua estrutura varia significativamente entre as edições.

Diferentemente de Rendimento, TDI e IDEB, não existe uma única coluna textual utilizada em todos os arquivos para representar a rede pública.

A definição conceitual permanece:

Federal + Estadual + Municipal

mas a identificação desse universo depende da estrutura do arquivo de cada edição.

---

## 9. SAEB — arquivos agregados por UF

Nos arquivos em nível de Unidade da Federação, existem diferentes categorias de dependência administrativa.

É necessário distinguir:

Total geral

de:

Total da rede pública

O total geral não pode ser utilizado como sinônimo de rede pública quando inclui escolas privadas.

Por exemplo, algumas fontes apresentam explicitamente uma categoria equivalente a:

Total - Federal, Estadual, Municipal e Privada

Esse registro representa todas as dependências administrativas e, portanto, não corresponde ao recorte público.

Quando estiver disponível o agregado correspondente somente às redes:

Federal
Estadual
Municipal

esse será o registro utilizado para representar:

REDE = PUBLICA

---

## 10. SAEB 2011

O arquivo de 2011 possui estrutura específica em nível de UF.

Entre suas variáveis estão:

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

Nessa edição, a identificação da rede não é feita por uma descrição textual como "Pública", mas por:

ID_TIPO_REDE

Conforme definido na auditoria do SAEB, o código correspondente ao recorte público utilizado pelo projeto é:

ID_TIPO_REDE = 5

Essa regra deverá ficar explícita no código de transformação correspondente a 2011.

Não deverá ser inferida a partir de outros anos.

---

## 11. SAEB — arquivos em nível de escola

Em arquivos do SAEB em nível escolar existe a variável:

IN_PUBLICA

O dicionário da fonte identifica esse campo como indicador de escola pública.

As categorias são utilizadas para distinguir:

escola privada

de:

escola pública

Para os arquivos escolares, o recorte será:

IN_PUBLICA = 1

Esse filtro identifica as escolas pertencentes às redes públicas.

Posteriormente, os resultados serão agregados ao nível de UF conforme a metodologia definida na auditoria específica do SAEB.

A definição da rede e o cálculo da média são duas etapas diferentes:

1. IN_PUBLICA define quais escolas pertencem ao universo público;
2. a regra de agregação define como seus resultados serão consolidados em nível de UF.

---

## 12. Harmonização entre os indicadores

Embora as estruturas das fontes sejam diferentes, a dimensão final terá um único significado.

| Indicador | Identificação na fonte | Regra |
|---|---|---|
| Rendimento | Publico / Pública | usar agregado oficial |
| TDI | Publico / Pública | usar agregado oficial |
| IDEB | Pública / Pública com nota | usar agregado oficial |
| SAEB — agregado UF | agregado público oficial | utilizar resultado correspondente a Federal + Estadual + Municipal |
| SAEB — 2011 | ID_TIPO_REDE = 5 | interpretar como rede pública conforme auditoria |
| SAEB — escola | IN_PUBLICA = 1 | selecionar escolas públicas |

Na camada padronizada, todos serão representados como:

PUBLICA

Essa padronização é semântica.

Ela não significa que os arquivos de origem possuam estruturas idênticas.

---

## 13. Preservação da informação original

A transformação não deverá apagar a forma como a fonte originalmente representava a rede.

Sempre que tecnicamente útil, a camada intermediária deverá preservar a categoria de origem.

Exemplo:

REDE_ORIGEM = Publico
REDE = PUBLICA

ou:

REDE_ORIGEM = Pública (4)
REDE = PUBLICA

ou:

REDE_ORIGEM = IN_PUBLICA=1
REDE = PUBLICA

Essa estratégia aumenta a rastreabilidade do pipeline.

Caso um resultado final apresente divergência, será possível identificar qual regra da fonte originou aquele registro.

---

## 14. Regra para a camada Silver

A camada Silver será responsável pela harmonização da dimensão de rede.

O valor padronizado será:

PUBLICA

A transformação deverá respeitar as regras específicas de cada fonte.

Não haverá uma regra genérica como:

se rede em [Federal, Estadual, Municipal]:
    rede = PUBLICA

seguida de média simples dos valores.

Essa abordagem poderia produzir resultados metodologicamente incorretos.

A seleção deverá ocorrer antes da consolidação, utilizando a representação oficial disponível em cada fonte.

---

## 15. Regra para a camada Gold

As tabelas analíticas destinadas ao Power BI utilizarão:

REDE = PUBLICA

A dimensão poderá possuir apenas essa categoria caso o escopo final permaneça restrito à rede pública.

Mesmo nesse cenário, a coluna de rede deverá ser preservada nas tabelas fato quando contribuir para clareza, rastreabilidade e possibilidade de expansão futura do projeto.

---

## 16. O significado de PUBLICA no modelo final

No modelo analítico:

PUBLICA

deve ser interpretado como:

> Resultado correspondente ao universo das redes públicas de ensino — federal, estadual e municipal — obtido por meio do agregado oficial da fonte quando disponível ou por meio do identificador oficial de escola/rede pública quando a estrutura da fonte exigir.

Essa definição é mais precisa do que afirmar simplesmente:

"Federal + Estadual + Municipal"

porque distingue:

conceito da população

de:

procedimento matemático utilizado para calcular o indicador.

---

## 17. Regras que não serão utilizadas

O pipeline não deverá:

1. utilizar a categoria Total quando ela incluir a rede privada;
2. considerar Total como sinônimo automático de Pública;
3. calcular média simples entre Federal, Estadual e Municipal para criar uma rede pública;
4. somar taxas de dependências administrativas;
5. recalcular IDEB público a partir dos IDEBs das redes individuais;
6. ignorar notas metodológicas históricas do Inep;
7. transformar categorias privadas em públicas;
8. substituir resultados oficiais por estimativas próprias quando já existir agregado publicado;
9. modificar os arquivos raw para padronizar nomenclaturas.

---

## 18. Rastreabilidade

As regras de rede deverão ser reproduzíveis.

O pipeline deverá permitir identificar, para cada indicador:

- arquivo de origem;
- ano;
- categoria original de rede;
- regra utilizada para selecionar o recorte público;
- categoria padronizada resultante.

Exemplo conceitual:

INDICADOR | ANO | REDE_ORIGEM | REGRA | REDE
Rendimento | 2007 | Publico | AGREGADO_OFICIAL | PUBLICA
TDI | 2007 | Publico | AGREGADO_OFICIAL | PUBLICA
IDEB | 2011 | Pública (4) | AGREGADO_OFICIAL | PUBLICA
SAEB | 2011 | ID_TIPO_REDE=5 | CODIGO_OFICIAL | PUBLICA
SAEB | 2023 | IN_PUBLICA=1 | INDICADOR_ESCOLA | PUBLICA

Os nomes técnicos definitivos dessas colunas serão definidos durante a implementação da camada Silver.

---

## 19. Relação com as auditorias

Esta decisão não substitui os documentos de auditoria individuais.

Os documentos:

auditoria_saeb.md
auditoria_ideb.md
auditoria_rendimento.md
auditoria_tdi.md

registram as características e problemas específicos de cada base.

Este documento registra a decisão transversal utilizada para integrar essas bases em um mesmo modelo analítico.

Portanto:

auditorias individuais
        ↓
comparação das estruturas
        ↓
definição transversal
        ↓
regra da camada Silver
        ↓
modelo Gold / Power BI

---

## 20. Conclusão

As auditorias demonstraram que o conceito de rede pública está presente em todas as bases históricas utilizadas, mas sua representação não é uniforme.

Rendimento Escolar e TDI fornecem diretamente agregados de rede pública.

O IDEB fornece resultados oficiais para a categoria Pública.

O SAEB apresenta diferentes representações conforme a edição, incluindo agregados por dependência administrativa, códigos de tipo de rede e indicadores de escola pública.

Diante dessas diferenças, o projeto adotará uma harmonização semântica, e não uma fórmula aritmética universal.

A dimensão final será:

REDE = PUBLICA

e representará o universo público definido pelas dependências:

Federal
Estadual
Municipal

respeitando a metodologia, o nível de agregação e as exceções históricas de cada fonte.

Nenhum indicador será reconstruído por média simples das dependências administrativas quando existir um resultado oficial correspondente ao recorte público.

Essa decisão passa a ser a regra metodológica oficial do projeto para a dimensão de rede de ensino.

---

## Histórico de atualização

| Data | Alteração |
|---|---|
| 18/08/2026 | Criação da definição transversal de rede pública |
| 18/08/2026 | Consolidação das decisões das auditorias de SAEB, IDEB, Rendimento e TDI |
| 18/08/2026 | Definidas regras específicas para agregado oficial, ID_TIPO_REDE e IN_PUBLICA |
| 18/08/2026 | Definida padronização final REDE = PUBLICA |