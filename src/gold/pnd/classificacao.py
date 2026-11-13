"""Nível DD pela NT_GER publicada: Nota INEP 44/2025, item 9.3/Tabela 2.

Os rótulos seguem essa tabela; descritores pedagógicos complementares estão
nas Notas 3/2026 e 4/2026. Não há recálculo da TRI ou da nota geral aqui.
"""
import numpy as np
import pandas as pd

CORTE_BASICO = 50.0
CORTE_ADEQUADO = 70.0
PADROES_ESPERADOS = frozenset({"ABAIXO_DO_BASICO", "BASICO", "ADEQUADO"})


def classificar_nivel_desempenho(nt_ger: pd.Series) -> pd.Series:
    """Classifica notas completas de 0 a 100, preservando índice e precisão."""
    if not isinstance(nt_ger, pd.Series):
        raise TypeError("NT_GER deve ser uma Series pandas.")
    if nt_ger.map(lambda valor: isinstance(valor, (bool, np.bool_))).any():
        raise ValueError("NT_GER não aceita valores booleanos.")
    try:
        notas = pd.to_numeric(nt_ger, errors="raise")
    except (TypeError, ValueError) as exc:
        raise ValueError("NT_GER contém valor não numérico.") from exc
    if notas.isna().any():
        raise ValueError("NT_GER contém valor ausente; não é possível classificar.")
    if np.iscomplexobj(notas):
        raise ValueError("NT_GER deve conter notas reais.")
    if not np.isfinite(notas.to_numpy(dtype=float)).all():
        raise ValueError("NT_GER contém valor não finito.")
    if ((notas < 0) | (notas > 100)).any():
        raise ValueError("NT_GER fora da escala publicada de 0 a 100.")
    resultado = pd.Series("BASICO", index=nt_ger.index, dtype="string")
    resultado.loc[notas < CORTE_BASICO] = "ABAIXO_DO_BASICO"
    resultado.loc[notas >= CORTE_ADEQUADO] = "ADEQUADO"
    return resultado
