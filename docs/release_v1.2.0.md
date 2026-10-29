# Pipeline de Dados Educacionais - v1.2.0

Publicada em 29/10/2026. Esta versão amplia a reprodutibilidade para incluir a
aquisição dos insumos oficiais, além do processamento e da análise. Mantém os
contratos das camadas, o recorte analítico e os resultados históricos.

## Aquisição automatizada e atualização da Raw

- Download, seleção, extração e organização dos 54 insumos diretamente em `data/raw`, com nomes locais definidos pelo manifesto e limpeza dos temporários.
- Reaproveitamento de arquivos já válidos e opção `--rebaixar` para consultar novamente as fontes oficiais.
- Verificação de integridade dos arquivos por SHA-256.
- Quando o hash muda, comparação do conteúdo protegido com uma versão anterior validada. No IDEB, novas colunas anuais podem ser aceitas sem ampliar o recorte analítico; alterações no histórico protegido são rejeitadas.
- Nos demais arquivos, comparação integral das linhas e campos das abas usadas e do conteúdo dos arquivos de apoio, conforme a política documentada por fonte.
- Atualização coordenada dos hashes, manifesto e documentação quando o conteúdo é equivalente, mantendo backup e histórico. Falhas de instalação tratadas acionam rollback.
- Preservação da versão anterior e diagnóstico quando há mudança histórica, erro de leitura ou falta de referência confiável. Uma instalação sem referência anterior exige os hashes já registrados.
- Opção `--estrito` para exigir identidade binária. Suporte aos pacotes ZIP e RAR utilizados pelas fontes.
- Manifesto atualizado para a revisão oficial de 09/09/2026 do dicionário da PND, sem alteração dos microdados analíticos.

O procedimento e suas dependências estão em [automacao_raw.md](automacao_raw.md).

## Documentação, TCC e Power BI

- Orientações de aquisição atualizadas para o fluxo automatizado, preservando referências e decisões metodológicas.
- Revisão de coerência entre fontes, auditorias, camadas, TCC e Power BI.
- Aquisição automatizada explicitada no resumo, abstract, objetivos e contribuições do TCC; distinção entre aquisição externa e ingestão da Raw.
- PDF do TCC gerado pelo template LaTeX, com 95 páginas nesta versão.
- Imagens atualizadas dos dashboards e documentação da procedência das referências acadêmicas.
- Instruções no README para gerar a Gold, ajustar a origem da consulta `gold` ao diretório local e atualizar o PBIX usando `fnParquetGold`.
- Apresentação da defesa com 12 slides principais e um de reserva; roteiro impresso de quatro páginas com lembretes, sem falas prontas.
- Três evidências visuais de transformações: mudanças de layout, formato amplo para longo e auditoria do SAEB 2023.

Os materiais da defesa estão organizados em [tcc/apresentacao/](../tcc/apresentacao/README.md).

## Escopo e compatibilidade

- IDEB e SAEB: nove edições bienais de 2007 a 2023.
- Rendimento e TDI: 17 edições anuais de 2007 a 2023.
- Séries históricas: 27 UFs, rede pública, Anos Iniciais e Finais do Ensino Fundamental, com exceções de composição de rede documentadas para SAEB 2007/2009.
- PND: análise complementar de 2025, com 759.140 registros analíticos.
- Cinco fatos, cinco dimensões e 27 medidas DAX; nomes e contratos analíticos preservados.
- Novas edições presentes fisicamente nas fontes não ampliam automaticamente o período da análise.

A preparação da Raw passa a ser automatizada antes do comando habitual
`python src/pipeline.py full`. O PBIX continua consumindo exclusivamente os
Parquets da Gold; sua atualização não executa o download nem o pipeline Python.

## Validação desta versão

Verificações executadas localmente antes da criação da tag:

- 27 testes automatizados aprovados com `unittest`.
- Compilação dos módulos Python de `src`, `scripts` e `tests` sem erros.
- Sequência completa do pipeline conferida com `full --dry-run`; esse modo não reexecuta as transformações.
- Raw: 54/54 arquivos encontrados e nenhuma divergência de hash.
- Validador global: `MODELO DIMENSIONAL GOLD: OK`, incluindo domínios, grãos, chaves, integridade referencial e coerência município/UF da PND.
- Afirmações e valores da apresentação conferidos contra código, dados e auditorias. Comparação SAEB 2023 reexecutada: 108 valores e nenhuma coincidência a duas casas na ponderação escolar por presentes, justificando o uso do agregado oficial por UF.
- Apresentação e roteiro inspecionados visualmente; PDF do TCC confirmado com 95 páginas.

Cardinalidades confirmadas:

| Tabela | Registros |
|---|---:|
| DIM_UF | 27 |
| DIM_TEMPO | 18 |
| DIM_ETAPA | 2 |
| DIM_AREA_PND | 17 |
| DIM_MUNICIPIO | 750 |
| FATO_RENDIMENTO | 2.754 |
| FATO_TDI | 918 |
| FATO_IDEB | 486 |
| FATO_SAEB | 972 |
| FATO_PND | 759.140 |

## Artefatos e publicação

- Código, documentação, PBIX, notebooks e imagens: disponíveis no repositório e nos arquivos-fonte da tag.
- Anexos da release: PDF do TCC, apresentação PowerPoint e roteiro impresso em Word.
- Dados Raw e camadas derivadas: permanecem fora do Git; a reprodução segue o README.
- `CITATION.cff` atualizado para a versão 1.2.0 e a data desta publicação.
- Publicação automática pelo envio de tags `v*`, usando as notas e os artefatos do próprio commit da tag. Também é possível executar o workflow manualmente para uma tag existente.

As notas das versões anteriores permanecem como registros históricos, incluindo
as contagens de páginas e testes correspondentes àquelas entregas.
