# Notebooks demonstrativos do pipeline

Os notebooks desta pasta apresentam, para cada indicador, o percurso entre a
fonte Raw e a tabela fato Gold consumida pelo Power BI. Eles chamam os scripts
oficiais do repositorio e nao reimplementam as regras de transformacao.

| Notebook | Indicador | Saida para o BI |
|---|---|---|
| `01_rendimento.ipynb` | Rendimento Escolar | `fato_rendimento.parquet` |
| `02_tdi.ipynb` | Distorcao idade-serie | `fato_tdi.parquet` |
| `03_ideb.ipynb` | IDEB | `fato_ideb.parquet` |
| `04_saeb.ipynb` | SAEB | `fato_saeb.parquet` |
| `05_pnd.ipynb` | PND 2025 | `fato_pnd.parquet` |

## Uso

Prepare e confira os insumos a partir da raiz do repositorio antes de executar
as etapas dos notebooks:

```powershell
python scripts/baixar_raw.py
python scripts/gerar_manifesto_raw.py --check
```

Para consultar novas versoes das fontes, use `--rebaixar`; o procedimento de
comparacao e os diagnosticos estao em [automacao da Raw](../docs/automacao_raw.md).
Os notebooks nao executam a aquisicao nem atualizam o manifesto.

Execute o Jupyter a partir da raiz do repositorio:

```powershell
python -m pip install -r requirements.txt
python -m jupyter lab
```

Por padrao, os notebooks apenas leem os artefatos existentes. As variaveis
`EXECUTAR_AUDITORIAS` e `EXECUTAR_PIPELINE_INDICADOR` precisam ser habilitadas
explicitamente para chamar os scripts.

As dimensoes Gold sao compartilhadas. A reproducao integral do modelo e sua
validacao transversal continuam sob responsabilidade de:

```powershell
python src/pipeline.py full
```

Os notebooks sao material de demonstracao metodologica. O codigo-fonte em
`src/` permanece como implementacao oficial do pipeline.
