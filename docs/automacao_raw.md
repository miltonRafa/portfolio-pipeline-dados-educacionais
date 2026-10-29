# Download automático da Raw

O procedimento de obtenção dos insumos é implementado em
`scripts/baixar_raw.py`. O script consulta as páginas oficiais, segue as abas
das edições usadas e prepara os 54 arquivos nos nomes e diretórios definidos
em `docs/fontes_dados.csv`. O destino padrão é `data/raw`.

## Procedimento de reprodução

```powershell
python -m pip install -r requirements.txt
python scripts/baixar_raw.py
python scripts/gerar_manifesto_raw.py --check
python src/pipeline.py full
```

Se o HTTPS do servidor `download.inep.gov.br` falhar neste ambiente, execute
`python scripts/baixar_raw.py --http`. Essa opção usa HTTP somente no servidor
de downloads; as páginas oficiais continuam sendo consultadas por HTTPS e
o SHA-256 de cada arquivo continua sendo calculado e registrado. Um hash
diferente exige a comparação integral descrita abaixo.

O download é uma etapa de preparação anterior à Bronze, executada
separadamente do pipeline. A Raw permanece imutável durante as transformações.
O download pode atualizar o manifesto somente após comprovar equivalência
do conteúdo protegido. Os critérios e o período analíticos permanecem iguais.

Para ler pacotes RAR, é necessário `tar` com suporte a RAR/libarchive no PATH.
O `tar.exe` do Windows usado na validação atende a esse requisito. Em outros
sistemas, instale uma implementação compatível de `bsdtar`/libarchive e
disponibilize-a como `tar`. O Python 3.11 ou superior é necessário; o projeto
é validado em Python 3.12.

## Opções

```powershell
# Resolver os links sem baixar pacotes
python scripts/baixar_raw.py --planejar

# Consultar novamente as fontes e transferir até arquivos já existentes
python scripts/baixar_raw.py --rebaixar --http

# Reproduzir estritamente os hashes registrados, sem atualização automática
python scripts/baixar_raw.py --rebaixar --estrito --http

# Selecionar indicador e ano (as opções podem ser repetidas)
python scripts/baixar_raw.py --indicador tdi --ano 2023 --http

# Usar outra Raw, com a mesma organização interna
python scripts/baixar_raw.py --destino C:/dados/raw --http
```

Arquivos existentes com hash correto são reaproveitados; use `--rebaixar`
para consultar mudanças nas fontes. Um arquivo local que já diverge do
manifesto é preservado e causa falha: ele não é uma referência confiável para
a comparação. A aceitação automática aplica-se ao novo download comparado
com uma referência anterior validada. Não execute duas instâncias para o mesmo
destino, nem execute o download durante as transformações do pipeline.

Atualizações que alteram o hash são instaladas somente na Raw canônica
`data/raw` do projeto, pois também alteram seu manifesto. Em `--destino`
alternativo, continua disponível a reprodução exata, sem atualização do
manifesto do projeto.

O código de saída é zero quando todos os arquivos selecionados foram
validados e um quando algum arquivo não foi obtido/validado. No planejamento,
zero indica resolução dos links, sem comprovar transferência dos pacotes.

## Hash diferente e conteúdo equivalente

A regra é aplicada a todos os 54 insumos. Um hash idêntico permite a
instalação direta. Um hash diferente segue esta sequência:

1. Localizar a cópia anterior e confirmar seu hash contra o manifesto.
2. Ler e comparar integralmente o conteúdo protegido, sem amostragem.
3. Se houver equivalência, guardar backup da versão anterior e preparar a
   nova Raw, o CSV, o Markdown e os checksums antes de substituí-los.
4. Instalar a atualização e registrar hashes anterior/novo, fonte, membro do
   pacote, instante UTC, política e quantidade de linhas/abas comparadas.
5. Em erro de instalação tratado, restaurar o arquivo e os documentos anteriores.

| Insumo | Conteúdo protegido |
|---|---|
| IDEB | Três abas lidas pela Bronze (AI, AF, EM); geografia/rede e todas as colunas técnicas sem ano ou com anos até 2023, incluindo 2005. Exige os nove `VL_OBSERVADO_2007` a `VL_OBSERVADO_2023`. Compara todas as linhas na mesma ordem. Colunas de anos posteriores a 2023 são ignoradas na comparação. |
| Rendimento e TDI | Todas as células das abas configuradas na Bronze para cada edição anual. |
| SAEB agregado | Todas as células da aba configurada para a edição; CSV inteiro em 2011. |
| CSVs escolares SAEB e TXT PND | Todas as linhas e campos, incluindo cabeçalho, ordem, duplicatas e campos não selecionados pela Silver. |
| Dicionários e parâmetros | Todas as abas e células, mantendo nomes e ordem das abas. |

Nos arquivos de texto, a comparação usa o delimitador e a codificação do
projeto. Mudanças de terminação de linha ou aspas que preservem os campos
podem ser aceitas. Nas planilhas, compara valores lidos pelos mesmos engines
usados pelo projeto, não estilos, metadados do Excel ou fórmulas sem mudança
no valor armazenado. Textos como `NA` não são confundidos com células vazias.
A regra é conservadora: alterações em conteúdo de apoio ou em linhas fora
do recorte final da Gold também são rejeitadas se estiverem na área protegida.

O IDEB passa a consultar a aba física mais recente na página oficial, sem
fixar 2025 na URL. A versão aceita mantém o nome local estável; pacote, nome
original e anos disponíveis são atualizados no manifesto. Isso não adiciona
anos à análise. As demais fontes permanecem nas edições usadas pelo projeto.

A comparação requer uma referência física anterior cujo hash seja confiável.
Se a Raw estiver vazia e a fonte já tiver mudado, não é possível provar o
histórico apenas com o hash antigo. Nesse caso o script rejeita a novidade
e explica que a referência deve ser restaurada; não inventa uma equivalência.

O gerador preserva os metadados aprovados quando o hash local coincide com o
manifesto, permitindo regenerar os documentos sem perder a procedência. A
Bronze e o validador PND consultam o hash corrente no manifesto, mantendo as
outras validações de esquema, linhas e valores.

## Falhas, motivos e fallback

Uma rejeição apresenta o motivo no terminal e no relatório JSON. Os motivos
incluem campo/aba/linha divergente, quantidade de linhas/colunas, aba ou ano
obrigatório ausente, referência inexistente, falha de leitura, rede, extração
e gravação. A primeira diferença é suficiente para rejeitar o candidato;
não é gerado um inventário de todas as diferenças.

O fallback preserva a Raw anterior e o manifesto daquele arquivo. Erros de
comparação incluem o erro original; erros de rede/extração indicam a URL e
orientam verificar conexão, `--http`, tar/libarchive e permissões. Se o
servidor não oferecer Range, há fallback para baixar o ZIP inteiro, com o
motivo informado. O script não aceita uma divergência apenas para continuar.

Cada atualização é tratada por arquivo. Se uma atualização for aceita e uma
outra falhar, a aceita permanece registrada; o comando retorna erro para o
conjunto incompleto. Interrupções forçadas ou falhas do sistema podem exigir
conferir `--check` e restaurar backups: a restauração automática cobre erros
tratados durante a instalação, não interrupção abrupta do processo.

## Seleção, extração e limpeza

Não foi encontrada uma API pública documentada específica para esses pacotes.
A implementação segue os links publicados pelo Inep, sem presumir URLs anuais.

| Fonte | Seleção |
|---|---|
| Rendimento e TDI | Edições de 2007 a 2023, item Brasil, regiões e UFs |
| IDEB | Pacote de regiões e estados da edição física mais recente; histórico protegido até 2023 e nome local estável |
| SAEB | Pacotes de microdados com planilhas por UF, dicionários e arquivos escolares de auditoria; resultados agregados de 2023 no RAR da página de resultados |
| PND | Pacote RAR da edição 2025, com microdados, parâmetros de itens e dicionário revisado |

O processamento ocorre inteiramente na Raw de destino. Cada pacote utiliza
um diretório temporário exclusivo em `data/raw/.download/pacote-*`. Nos ZIPs,
HTTP Range permite baixar o diretório e os membros selecionados, evitando
transferir microdados desnecessários. Se Range não for oferecido, o ZIP é
baixado integralmente. Nos RARs, o pacote é baixado inteiro e os membros
necessários são lidos por `tar`, sem extrair os demais.

Os nomes dos membros do pacote não são usados como caminhos de extração.
Arquivos com SHA-256 igual ao manifesto ou conteúdo protegido comprovadamente
equivalente são instalados no destino canônico, por meio de arquivo parcial
e renomeação. Pacotes, candidatos e
parciais são removidos ao terminar a operação, inclusive em falhas tratadas.
Uma versão anterior substituída após comparação permanece no backup. Uma interrupção forçada do
processo pode deixar temporários da execução interrompida.

Registros operacionais e backups permanecem em `data/raw/.download`:

- `plano_download.json`: páginas, URLs e hashes das fontes resolvidas; é
  preservado entre execuções que reaproveitam arquivos;
- `relatorio_download.json`: resultado da última execução de download;
- `relatorio_planejamento.json`: resultado do último planejamento;
- `historico_atualizacoes.json`: registro cumulativo das atualizações equivalentes;
- `historico/<caminho relativo>/<hash anterior>`: cópias anteriores para recuperação;
- `verificacao_comparadores.json`: evidência local da leitura dos 54 insumos atuais.

Esses registros e backups não são insumos analíticos, não entram no manifesto dos 54
arquivos e são ignorados pelo Git junto com `data/`.

## Revisão incorporada do dicionário PND

Em 29/10/2026 foi adotado o dicionário oficial atualizado em 09/09/2026.
Seu SHA-256 canônico passou a ser
`1653b2a166f3d322fcc3cee7dca2fba886651dd805fca7d15ecd60e1239eb4f2`.
O hash anterior era
`dcc59019462bed0478649c2f914cb132387379d190d18a7cd676327b7bef825e`.

| Metadado interno | Cópia anterior | Revisão adotada |
|---|---|---|
| Criação (UTC) | 30/03/2026 18:54:16 | 30/03/2026 18:54:16 |
| Modificação (UTC) | 29/05/2026 21:12:33 | 09/09/2026 14:23:32 |
| Último editor registrado | Pedro Henrique Barros Vasconcelos | Suzi Mesquita Vargas |

A página oficial informa atualização do arquivo em 09/09/2026. O nome do
membro no RAR contém literalmente `09-09-2029`; essa grafia foi registrada
como nome original, mas não é usada para determinar a data real da revisão.
O nome local esperado pelo projeto foi mantido.

A comparação dos valores das quatro abas encontrou o esclarecimento de
`DS_VT_ACE_OBJ` na célula D67 de `DICIONÁRIO_DE_VARIAVÉIS`: os acertos estão
rotacionados segundo a sequência das questões do Caderno 1. A aba `Versões`
registra a revisão e duas datas anteriores passaram de texto ISO para números
seriais do Excel. As abas de arquivos e municípios mantiveram os mesmos
valores. A comparação foi feita sobre os XMLs OOXML e strings compartilhadas,
pois a cópia anterior usa OOXML Strict; não incluiu estilos ou fórmulas.

Os outros 53 arquivos conservaram seus hashes anteriores. O dicionário não
é lido pelas transformações Bronze/Silver/Gold, e os microdados analíticos
continuam idênticos. A revisão foi autorizada, incorporada à Raw e registrada
no gerador do manifesto; CSV, Markdown e checksums foram regenerados pelo
procedimento do projeto. Não há exceção de hash no downloader: o dicionário
é validado pelo mesmo manifesto dos demais arquivos.

A revisão adotada integra o manifesto usado pela aquisição automatizada.
Uma cópia antiga da Raw com dicionário divergente é identificada pela
verificação de integridade. A cópia de conveniência externa pode ainda conter
a versão anterior; sua validade depende dos hashes do manifesto corrente.

## Verificação

```powershell
python scripts/gerar_manifesto_raw.py --check
python -m unittest discover -s tests -v
python -m compileall -q src scripts tests
python src/pipeline.py full --dry-run
```

Os testes de download usam pacotes simulados, sem rede. Cobrem extração
restrita, seleção histórica, validação de hash, limpeza dos temporários,
comparação de conteúdo, IDEB com ano adicional, rejeição de história alterada,
atualização de manifesto e checksums, backup e restauração após falha simulada.
A transferência
real dos arquivos oficiais é verificada separadamente com `--rebaixar` e
checagem de integridade da Raw.

Na verificação de 29/10/2026, as transferências oficiais foram conferidas
diretamente em `data/raw`. O manifesto validou 54/54 arquivos, sem ausências
ou hashes divergentes. Os 27 testes passaram, a compilação dos arquivos
Python passou e a sequência completa do pipeline foi conferida em modo
`dry-run`, sem regenerar as camadas analíticas. Não restaram diretórios de
pacotes temporários, e a pasta de experimentação foi excluída. Os comparadores
também foram exercitados na leitura integral dos 54 arquivos existentes;
isso comprova suporte às fontes atuais, não garante layouts futuros desconhecidos.
