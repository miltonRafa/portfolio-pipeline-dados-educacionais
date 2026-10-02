# TCC

Esta pasta contem o projeto LaTeX do Trabalho de Conclusao de Curso associado
ao pipeline de dados educacionais.

## Estrutura

```text
tcc/
|-- main_tcc_uemg.tex
|-- tccUEMG.cls
|-- bib/
|-- capitulos/
|-- elementos/
`-- figs/
```

- `main_tcc_uemg.tex`: arquivo principal de compilacao;
- `tccUEMG.cls`: classe fornecida pelo modelo institucional;
- `bib/`: base bibliografica utilizada pelo BibTeX;
- `capitulos/`: conteudo textual do trabalho;
- `elementos/`: materiais auxiliares do modelo;
- `figs/`: imagens incorporadas ao documento.

## Compilacao local

Com uma distribuicao LaTeX instalada, execute a partir desta pasta:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main_tcc_uemg.tex
bibtex main_tcc_uemg
makeindex main_tcc_uemg.idx
pdflatex -interaction=nonstopmode -halt-on-error main_tcc_uemg.tex
pdflatex -interaction=nonstopmode -halt-on-error main_tcc_uemg.tex
```

As execucoes finais do `pdflatex` atualizam sumario, numeracao, citacoes e
referencias cruzadas. Os arquivos auxiliares e o PDF produzido dentro desta
pasta sao ignorados pelo Git.

O PDF consolidado para consulta publica e mantido em:

```text
output/pdf/Template_TCC_UEMG_revisado.pdf
```

## Overleaf

Para usar o projeto no Overleaf, envie o conteudo desta pasta preservando a
estrutura de diretorios e defina `main_tcc_uemg.tex` como documento principal.
Os PDFs armazenados localmente em `referencias/` nao sao necessarios para a
compilacao.
