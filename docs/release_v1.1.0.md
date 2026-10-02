# Pipeline de Dados Educacionais - v1.1.0

Esta versao amplia a entrega publica da `v1.0.0` com os artefatos academicos e
demonstrativos associados ao projeto. O pipeline, o recorte analitico e os
resultados validados permanecem consistentes com a primeira versao publica.

## Novidades

- projeto LaTeX completo do TCC organizado em `tcc/`;
- PDF compilado do TCC com 65 paginas em `output/pdf/`;
- cinco notebooks demonstrativos, um para cada indicador;
- dashboard Power BI atualizado;
- documentacao da organizacao das referencias academicas;
- revisao final de alinhamento entre TCC, pipeline, Gold e Power BI;
- instrucoes para compilacao local e uso no Overleaf.

## Notebooks

Foram adicionados notebooks para:

- Rendimento Escolar;
- Taxa de Distorcao Idade-Serie;
- IDEB;
- SAEB;
- PND 2025.

Os notebooks apresentam o percurso entre a fonte Raw e a tabela fato Gold. Eles
chamam os scripts oficiais e nao reimplementam as regras do pipeline.

## TCC

O TCC documenta:

- arquitetura `Raw -> Bronze -> Silver -> Gold -> Power BI`;
- fontes oficiais, manifesto e hashes SHA-256;
- regras de tratamento por indicador;
- modelo dimensional com cinco fatos e cinco dimensoes;
- 27 medidas DAX;
- resultados descritivos e limitacoes metodologicas;
- bibliografia academica e institucional.

O PDF foi compilado com bibliografia e referencias cruzadas atualizadas, sem
citacoes ou referencias indefinidas.

## Escopo preservado

- SAEB: 2007-2023;
- IDEB: 2007-2023;
- Rendimento Escolar: 2007-2023;
- Taxa de Distorcao Idade-Serie: 2007-2023;
- PND: analise complementar de 2025;
- abrangencia historica: 27 Unidades Federativas;
- rede publica;
- Ensino Fundamental - Anos Iniciais e Anos Finais.

Esta release nao incorpora IDEB ou SAEB 2025 ao recorte historico e nao altera
os resultados analiticos validados da versao anterior.

## Validacao

- 10 testes estruturais aprovados com `unittest`;
- cinco notebooks validados sem caminhos absolutos ou saidas de erro;
- PBIX validado como pacote integro;
- TCC compilado com 65 paginas e zero erros criticos;
- repositorio sem alteracoes pendentes no momento da criacao da tag.

## Artefatos principais

- `tcc/`: fontes LaTeX;
- `output/pdf/Template_TCC_UEMG_revisado.pdf`: PDF do TCC;
- `notebooks/`: demonstracoes por indicador;
- `powerbi/pbix/`: arquivo Power BI Desktop;
- `docs/revisao_tcc_atualizacao_projeto.md`: verificacao final de coerencia;
- `referencias/README.md`: politica de organizacao das referencias.

## Compatibilidade

A `v1.1.0` e compativel com a `v1.0.0`. Os comandos do pipeline, contratos das
camadas, nomes das tabelas Gold e medidas DAX permanecem preservados.
