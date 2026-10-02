# Pipeline de Dados Educacionais — v1.0.0

Primeira versão pública completa do projeto de pipeline e análise de dados
educacionais do Inep.

## Escopo

- SAEB: 2007–2023
- IDEB: 2007–2023
- Rendimento Escolar: 2007–2023
- Taxa de Distorção Idade-Série: 2007–2023
- PND: análise complementar de 2025
- abrangência histórica: 27 Unidades Federativas
- rede pública
- Ensino Fundamental — Anos Iniciais e Anos Finais

## Arquitetura

RAW → BRONZE → SILVER → GOLD → POWER BI

## Destaques

- ingestão de múltiplos formatos oficiais;
- 54 arquivos Raw inventariados;
- rastreabilidade por SHA-256;
- auditorias metodológicas por indicador;
- validações independentes das camadas;
- modelo dimensional Gold;
- 5 dimensões e 5 tabelas fato;
- dashboard Power BI;
- 27 medidas DAX documentadas;
- testes automatizados;
- GitHub Actions para validação estrutural do repositório;
- documentação detalhada das fontes e da reprodução dos dados.

## Reprodutibilidade

Os dados Raw não são versionados no Git.

As fontes oficiais, arquivos utilizados e instruções para reconstrução da camada
Raw estão documentados em:

`docs/fontes_dados.md`

## Power BI

O arquivo Power BI Desktop e as medidas DAX encontram-se versionados no
repositório.

As imagens das páginas do dashboard estão disponíveis em:

`prints/`

## Licença e autoria

O projeto é disponibilizado sob a:

PolyForm Noncommercial License 1.0.0

Usos não comerciais são permitidos nos termos da licença.

Uso comercial não é autorizado pela licença e depende de autorização ou
licenciamento separado do autor.

As informações de autoria e orientação para citação acadêmica estão disponíveis
em:

`CITATION.cff`
