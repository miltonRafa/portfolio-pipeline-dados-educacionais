"""AUD-04B: critérios da Nota 44/2025, item 9.3/Tabela 2, sobre NT_GER."""
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from src.gold.pnd.classificacao import PADROES_ESPERADOS, classificar_nivel_desempenho
from src.gold.pnd import transformar_pnd as transformar
from src.gold.pnd import validar_fato_pnd as validar
from src.gold import validar_gold as global_gold


def silver_exemplo():
    # Notas objetivas intencionalmente contrárias às faixas da nota geral.
    return pd.DataFrame({
        "ANO": [2025] * 6, "UF_PROVA": ["AC"] * 6,
        "CO_MUNICIPIO_PROVA": [1200401] * 6, "CO_GRUPO": [702] * 6,
        "PROFICIENCIA": [-1., 0., 1., -1., 0., 1.],
        "NT_OBJ": [100., 100., 0., 0., 0., 0.],
        "NT_DIS": [0.] * 6, "NT_GER": [0., np.nextafter(50., 0.), 50., np.nextafter(70., 0.), 70., 100.],
        "QT_ACERTOS": [1] * 6,
    })


class ClassificacaoPndTest(unittest.TestCase):
    def test_limites_da_tabela_oficial_sem_arredondar(self):
        notas = pd.Series([0., np.nextafter(50., 0.), 50., np.nextafter(70., 0.), 70., 100.])
        self.assertEqual(classificar_nivel_desempenho(notas).tolist(),
                         ["ABAIXO_DO_BASICO"] * 2 + ["BASICO"] * 2 + ["ADEQUADO"] * 2)

    def test_nullable_sem_ausencias(self):
        self.assertEqual(classificar_nivel_desempenho(pd.Series([0, 50, 70, 100], dtype="Float64")).tolist(),
                         ["ABAIXO_DO_BASICO", "BASICO", "ADEQUADO", "ADEQUADO"])

    def test_ausencias_nao_recebem_categoria(self):
        for dtype, value in [("float64", np.nan), ("Float64", pd.NA), ("object", None), ("object", "")]:
            with self.subTest(dtype=dtype, value=value), self.assertRaises(ValueError):
                classificar_nivel_desempenho(pd.Series([value], dtype=dtype))

    def test_nao_numericos_rejeitados(self):
        for value in ["abc", "NA", " ", object()]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                classificar_nivel_desempenho(pd.Series([value]))

    def test_valores_nao_finitos_rejeitados(self):
        for value in [np.inf, -np.inf]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                classificar_nivel_desempenho(pd.Series([value]))

    def test_fora_da_escala_rejeitado(self):
        for value in [np.nextafter(0., -1.), np.nextafter(100., np.inf)]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                classificar_nivel_desempenho(pd.Series([value]))

    def test_booleanos_e_complexos_rejeitados(self):
        for value in [True, False, 50 + 1j]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                classificar_nivel_desempenho(pd.Series([value]))

    def test_indice_quantidade_e_entrada_preservados(self):
        notas = pd.Series([70., 49., 50.], index=pd.Index([8, 8, 3], name="registro"))
        copia = notas.copy(deep=True)
        resultado = classificar_nivel_desempenho(notas)
        self.assertEqual(len(resultado), len(notas))
        pd.testing.assert_index_equal(resultado.index, notas.index)
        pd.testing.assert_series_equal(notas, copia)
        self.assertEqual(str(resultado.dtype), "string")

    def test_serie_vazia_preserva_quantidade(self):
        self.assertEqual(len(classificar_nivel_desempenho(pd.Series([], dtype=float))), 0)

    def test_dominio_exclusivo_sem_categorias_antigas(self):
        resultado = classificar_nivel_desempenho(pd.Series([0., 50., 70.]))
        self.assertEqual(set(resultado), PADROES_ESPERADOS)
        self.assertTrue(set(resultado).isdisjoint({"NAO_PROFICIENTE", "PADRAO_1", "PADRAO_2"}))

    def test_tres_consumidores_usam_a_mesma_funcao(self):
        for module in [transformar, validar, global_gold]:
            self.assertIs(module.classificar_nivel_desempenho, classificar_nivel_desempenho)

    def test_transformacao_usa_nota_geral_e_preserva_notas_e_registros(self):
        silver = silver_exemplo()
        gold = transformar.construir_fato(silver)
        pd.testing.assert_frame_equal(gold[silver.columns], silver, check_dtype=False)
        self.assertEqual(len(gold), len(silver))
        self.assertEqual(gold.PADRAO_DESEMPENHO.tolist(),
                         ["ABAIXO_DO_BASICO"] * 2 + ["BASICO"] * 2 + ["ADEQUADO"] * 2)
        validar.validar_padrao_oficial(gold)

    def test_validador_rejeita_categoria_trocada_e_antiga(self):
        for categoria in ["ADEQUADO", "PADRAO_1"]:
            gold = transformar.construir_fato(silver_exemplo())
            gold.loc[0, "PADRAO_DESEMPENHO"] = categoria
            with self.subTest(categoria=categoria), self.assertRaises(RuntimeError):
                validar.validar_padrao_oficial(gold)

    def test_validador_rejeita_nota_geral_ausente(self):
        gold = transformar.construir_fato(silver_exemplo())
        gold.loc[0, "NT_GER"] = np.nan
        with self.assertRaises(ValueError):
            validar.validar_padrao_oficial(gold)

    def test_estrutura_rejeita_perda_e_duplicacao_de_linhas(self):
        gold = transformar.construir_fato(silver_exemplo())
        with patch.object(validar, "TOTAL_ESPERADO", len(gold)):
            validar.validar_estrutura_gold(gold)
            for incorreta in [gold.iloc[:-1], pd.concat([gold, gold.iloc[:1]])]:
                with self.subTest(linhas=len(incorreta)), self.assertRaises(RuntimeError):
                    validar.validar_estrutura_gold(incorreta)


if __name__ == "__main__":
    unittest.main()
