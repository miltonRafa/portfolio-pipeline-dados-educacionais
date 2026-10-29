# Evidências visuais das transformações

Três imagens PNG em 1920 × 1080, preparadas com recortes reais dos dados locais em 29/10/2026. São tabelas renderizadas para leitura em projeção, e não capturas da interface do Excel ou do Power BI. Campos e linhas foram selecionados explicitamente; os valores não são fictícios.

| Imagem | O que torna visível | Encaixe na apresentação atual |
|---|---|---|
| `01_layouts_rendimento.png` | Aprovação dos Anos Iniciais de MG em cinco edições: mudanças da coluna física, da representação da UF e da grafia da rede. | Incorporado ao slide 6. |
| `02_amplo_para_longo.png` | Uma linha Bronze de 2007 gera seis observações Silver, mantendo valores e coluna de origem. | Incorporado ao slide 13, como reserva após a conclusão. |
| `03_saeb_2023_validacao.png` | Cinco exemplos reais da divergência entre ponderação por presentes e resultado oficial; síntese das 108 comparações. | Incorporado ao slide 7. Priorizar este exemplo na explicação técnica. |

A apresentação atual é `../Defesa_TCC_evidencias_integradas.pptx`, com 12 slides principais e um de reserva. O roteiro acompanha essa sequência. As três imagens desta pasta são as fontes das evidências incorporadas, preservadas para reutilização e verificação. Para dez minutos, apresentar os slides 1 a 12 e usar o 13 somente se necessário durante as perguntas.

## Fontes e verificações

- Imagens 1 e 2: `data/bronze/rendimento/rendimento_AAAA.parquet`, `data/silver/rendimento/rendimento_2007_2023.parquet` e mapeamentos `CONFIG` de `src/silver/rendimento/transformar_rendimento.py`.
- As posições `col_NNN` são nomes técnicos da Bronze, não títulos originais das planilhas. O recorte usa localização Total e o agregado público oficial. A imagem 2 usa a linha de origem 299 de 2007, MG; todas as seis observações correspondem aos valores das células Bronze e mantêm `REDE=PUBLICA` na Silver.
- Imagem 3: funções do script `src/silver/saeb/comparar_saeb_2023_oficial_bronze.py`, lendo a Bronze escolar e a aba Estados do XLSB oficial. Diagnóstico reexecutado: **108 comparações e 0 coincidências após arredondamento a duas casas**; diferença absoluta média de 1,3897135233 pontos.
- Amostra visível da imagem 3: AC, BA, CE, MG e SP, Língua Portuguesa/Anos Iniciais. O resultado global inclui 27 UFs, duas etapas e duas disciplinas. As diferenças foram calculadas antes do arredondamento de exibição; por isso, subtrair números já arredondados pode produzir uma diferença de um centésimo.
- A reconstrução ponderada é um teste rejeitado, não a fonte da fato final. O projeto utiliza o agregado oficial por UF e preserva os dados escolares para auditoria.

As três imagens foram inspecionadas visualmente, e os valores de Rendimento foram confrontados entre Bronze e Silver. Não houve alteração nos insumos ou nas camadas de dados.
