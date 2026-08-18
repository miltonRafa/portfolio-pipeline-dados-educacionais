# Camada Silver — Pipeline de Dados Educacionais

## 1. Objetivo

A camada Silver é responsável por transformar as representações técnicas e rastreáveis da Bronze em tabelas analíticas semanticamente harmonizadas.

Enquanto a Bronze preserva a estrutura efetiva de cada arquivo de origem, a Silver passa a aplicar regras de interpretação necessárias ao uso comparável dos indicadores.

A Silver não substitui a Bronze.

Cada tabela Silver deverá ser integralmente reconstruível a partir dos arquivos Bronze e das regras documentadas neste arquivo.

---

## 2. Princípio de trabalho

A transformação de cada fonte seguirá a sequência:

1. auditar a estrutura efetivamente preservada na Bronze;
2. documentar as regras semânticas;
3. implementar a transformação;
4. executar validação independente;
5. somente então considerar a fonte concluída na Silver.

Não serão implementadas regras por suposição a partir do nome de uma coluna ou da aparência de uma planilha.

Mudanças estruturais entre anos deverão ser configuradas explicitamente.

---

## 3. Relação entre Bronze e Silver

A Bronze preserva:

- estrutura de origem;
- linhas físicas necessárias à rastreabilidade;
- cabeçalhos originais;
- categorias textuais;
- granularidade publicada;
- metadados técnicos;
- SHA-256 do arquivo RAW.

A Silver poderá:

- excluir linhas físicas de título, notas e cabeçalhos;
- selecionar a população analítica definida para o projeto;
- harmonizar nomes de redes;
- harmonizar etapas de ensino;
- harmonizar indicadores;
- converter valores numéricos;
- transformar tabelas largas em formato analítico longo;
- harmonizar granularidade quando metodologicamente necessário;
- criar campos canônicos utilizados pela Gold.

Toda transformação deverá ter justificativa documentada.

---

## 4. Escopo analítico do projeto

### Série histórica

Para os indicadores históricos:

- período principal: 2007–2023;
- geografia analítica: Unidade Federativa;
- rede: pública;
- etapas: Ensino Fundamental — Anos Iniciais e Anos Finais.

### PND

A PND 2025 é complementar à série histórica e será tratada separadamente.

Sua população analítica será definida na Silver, conforme a auditoria já realizada.

---

## 5. Definição canônica de rede pública

Para este projeto, `PUBLICA` representa o universo das redes públicas de ensino:

- Federal;
- Estadual;
- Municipal.

A implementação deverá preferir o agregado público oficial quando a própria fonte o disponibilizar.

Quando a estrutura da fonte não possuir esse agregado, será utilizada a regra específica previamente auditada para a edição.

Não será utilizada média aritmética simples de Federal, Estadual e Municipal para reconstruir um resultado público.

Também não será utilizado um agregado geral que inclua rede privada.

A coluna canônica será:

`REDE = PUBLICA`

A origem da classificação deverá continuar rastreável em campo específico quando necessário, como:

`REDE_ORIGEM`

---

## 6. Granularidade e tabelas previstas

### Rendimento Escolar

Grão previsto:

`ANO + UF + ETAPA + REDE + INDICADOR`

Estrutura prevista:

- `ANO`;
- `UF`;
- `ETAPA`;
- `REDE`;
- `INDICADOR`;
- `VALOR`;
- `ARQUIVO_ORIGEM`.

Indicadores:

- `APROVACAO`;
- `REPROVACAO`;
- `ABANDONO`.

### TDI

Grão previsto:

`ANO + UF + ETAPA + REDE`

Estrutura prevista:

- `ANO`;
- `UF`;
- `ETAPA`;
- `REDE`;
- `TDI`;
- `ARQUIVO_ORIGEM`.

### IDEB

Grão previsto:

`ANO + UF + ETAPA + REDE`

Estrutura prevista:

- `ANO`;
- `UF`;
- `ETAPA`;
- `REDE`;
- `IDEB`;
- `ARQUIVO_ORIGEM`.

### SAEB

Grão previsto:

`ANO + UF + ETAPA + REDE + DISCIPLINA`

Estrutura prevista:

- `ANO`;
- `UF`;
- `ETAPA`;
- `REDE`;
- `DISCIPLINA`;
- `PROFICIENCIA_MEDIA`;
- `ARQUIVO_ORIGEM`.

Disciplinas principais do projeto:

- Língua Portuguesa;
- Matemática.

### PND 2025

A estrutura final será definida após a transformação da população analítica auditada.

A PND permanecerá separada das séries históricas de IDEB, SAEB, Rendimento e TDI.

---

## 7. Valores ausentes e marcadores da fonte

Valores ausentes não serão imputados na Silver.

Marcadores textuais da fonte, como `--`, `NA`, células vazias ou códigos específicos, não serão automaticamente tratados como equivalentes.

Cada marcador deverá ser interpretado segundo a estrutura auditada da respectiva fonte.

Quando um marcador significar indisponibilidade de resultado, a Silver poderá convertê-lo para valor ausente, desde que essa regra esteja explicitamente documentada.

---

## 8. Conversão numérica

A Bronze preserva muitos valores como texto técnico.

Na Silver, os campos analíticos poderão ser convertidos para tipos numéricos.

A conversão deverá considerar explicitamente:

- vírgula decimal;
- ponto decimal;
- marcadores de ausência;
- valores zero substantivos;
- códigos que não representam medidas.

Não haverá conversão numérica genérica aplicada indistintamente a todas as colunas.

---

## 9. Rastreamento da origem

A Silver não precisa preservar todas as colunas técnicas da Bronze, mas deve manter rastreabilidade suficiente para identificar a fonte utilizada.

No mínimo, as tabelas analíticas deverão manter:

`ARQUIVO_ORIGEM`

Quando uma decisão depender de uma categoria original relevante, também deverá ser preservado um campo como:

`REDE_ORIGEM`

ou equivalente.

---

## 10. Validações mínimas

Cada transformação Silver deverá possuir validação independente.

As validações deverão verificar, conforme aplicável:

- existência dos arquivos Bronze esperados;
- anos esperados;
- UFs esperadas;
- etapas esperadas;
- rede pública corretamente selecionada;
- ausência de rede privada;
- indicadores esperados;
- unicidade do grão analítico;
- tipos numéricos;
- valores dentro de domínios plausíveis;
- ausência de duplicidades indevidas;
- rastreabilidade de arquivo de origem;
- quantidade de registros por ano;
- consistência entre transformação e regras documentadas.

A validação não deverá apenas conferir se o Parquet foi criado.

---

## 11. Regra de falha

A Silver deverá falhar explicitamente quando:

- uma estrutura anual não corresponder à configuração auditada;
- uma categoria necessária não existir;
- uma rede pública não puder ser identificada com segurança;
- uma etapa não puder ser mapeada;
- houver duplicidade no grão esperado;
- uma conversão numérica produzir perda não documentada;
- um novo padrão estrutural surgir sem regra definida.

É preferível interromper o pipeline a harmonizar silenciosamente uma estrutura desconhecida.

---

## 12. Ordem de implementação

A implementação será realizada fonte a fonte:

1. Rendimento Escolar;
2. TDI;
3. IDEB;
4. SAEB;
5. PND 2025.

Essa ordem permite iniciar pelas estruturas históricas mais diretamente comparáveis e deixar para o SAEB e a PND as transformações que exigem maior cuidado de granularidade e população.

---

## 13. Rendimento Escolar — etapa atual

A Bronze do Rendimento Escolar está concluída e validada para 2007–2023.

Antes de implementar a transformação Silver, será executada auditoria diretamente sobre os Parquets Bronze para confirmar:

- posição e profundidade dos cabeçalhos;
- colunas que representam UF;
- categorias de rede;
- categorias de localização;
- etapas;
- indicadores de aprovação, reprovação e abandono;
- diferenças estruturais entre os períodos;
- marcadores de ausência;
- estrutura efetiva dos registros.

O script utilizado será:

`src/silver/auditar_silver_rendimento.py`

Essa auditoria não altera dados.

Somente após sua leitura serão fixadas no código as regras de transformação de cada período.

---

## 14. Situação atual

| Fonte | Bronze | Silver |
|---|---|---|
| Rendimento Escolar | ✅ | 🔎 auditoria em preparação |
| TDI | ✅ | ⏳ |
| IDEB | ✅ | ⏳ |
| SAEB | ✅ | ⏳ |
| PND 2025 | ✅ | ⏳ |

---

## 15. Histórico de decisões

| Data | Decisão |
|---|---|
| 18/08/2026 | Iniciada a camada Silver após conclusão integral da Bronze |
| 18/08/2026 | Definido que cada fonte será auditada diretamente a partir dos Parquets Bronze antes da implementação semântica |
| 18/08/2026 | Rendimento Escolar escolhido como primeira fonte da Silver |
