# Reprodutibilidade do ambiente Python

## Referência atual

O ambiente de referência deste registro usa CPython 3.12.10 de 64 bits. As
dependências diretas estão declaradas e fixadas em `requirements.txt`; as
versões resolvidas, incluindo transitivas, estão em `requirements.lock`. A
instalação reproduzível usa o arquivo de lock:

```shell
python -m pip install -r requirements.lock
python -m pip check
```

O lock foi resolvido em 25/11/2026 em Windows x64, com Python 3.12.10, a partir
das dependências diretas existentes no projeto. As versões não foram
deliberadamente atualizadas a partir de uma lista anterior: os commits,
documentação e registros versionados consultados não preservam versões exatas
dos pacotes utilizados na validação histórica. Eles registram apenas Python
3.12 e limites mínimos `>=` para dependências. Assim, a combinação fixada é
uma nova referência controlada, não uma afirmação de que reproduz o ambiente
antigo.

`pywinpty` é necessário somente no Windows e está condicionado a
`sys_platform == "win32"` no lock. Os demais pacotes têm versões fixadas comuns
aos dois sistemas. O workflow `quality.yml` verifica a instalação, os testes e
o dry-run em Windows e Linux.

## Limites de reprodução

Os hashes de Raw publicados no manifesto identificam os insumos oficiais
esperados. Eles não demonstram identidade binária dos Parquets históricos.
Sem os hashes históricos dos Parquets ou o ambiente anterior, uma execução
atual pode demonstrar consistência analítica validada e identidade binária
entre execuções feitas com esta referência; não pode comprovar identidade
binária com o computador anterior. Mesmo com as mesmas versões Python e
dependências, sistemas operacionais e arquiteturas diferentes podem produzir
arquivos Parquet binariamente distintos por diferenças de runtime ou
serialização.
