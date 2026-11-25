from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import pandas as pd

from src.silver.rendimento import validar_silver_rendimento as rendimento
from src.silver.tdi import validar_silver_tdi as tdi


class RastreabilidadeHistoricaTest(unittest.TestCase):
    def preparar(self, validador):
        """Recorte dos títulos visíveis de 2023, com uma linha de dados por UF."""
        pasta = Path(self.enterContext(TemporaryDirectory()))
        self.enterContext(patch.object(validador, "BRONZE_DIR", pasta))
        self.enterContext(patch.object(validador, "ANOS", [2023]))
        fonte = "tdi" if validador is tdi else "rendimento"
        metrica = "TDI" if validador is tdi else "VALOR"
        nivel = {"col_005": "Ensino Fundamental"}
        etapas = {"col_005": "Total", "col_006": "Anos Iniciais", "col_007": "Anos Finais"}
        valores = {"col_005": "24", "col_006": "12", "col_007": "33"}
        cabecalho = [nivel, etapas]
        if validador is rendimento:
            titulos = {}
            for numero, taxa in [(5, "Aprovação"), (23, "Reprovação"), (41, "Abandono")]:
                coluna = f"col_{numero:03d}"
                titulos[coluna] = f"Taxa de {taxa}"
                nivel[coluna] = "Ensino Fundamental de 8 e 9 anos"
                etapas[f"col_{numero + 1:03d}"] = "Anos Iniciais"
                etapas[f"col_{numero + 2:03d}"] = "Anos Finais"
            cabecalho.insert(0, titulos)
            valores.update({"col_006": "90", "col_024": "8"})

        bronze = list(cabecalho)
        silver = []
        for uf in sorted(validador.UFS):
            numero = len(bronze) + 1
            bronze.append({"col_001": "2023", "col_002": uf, "col_003": "Total",
                           "col_004": "Pública", **valores})
            for coluna in ("col_006", "col_007" if validador is tdi else "col_024"):
                silver.append({
                    "ANO": 2023, "UF": uf, "LINHA_ORIGEM_BRONZE": numero,
                    "ARQUIVO_ORIGEM": "fonte.xlsx", "COLUNA_ORIGEM": coluna,
                    "ETAPA": "ANOS_FINAIS" if coluna == "col_007" else "ANOS_INICIAIS",
                    metrica: float(valores[coluna]),
                })
                if validador is rendimento:
                    silver[-1]["INDICADOR"] = "REPROVACAO" if coluna == "col_024" else "APROVACAO"
        dados = pd.DataFrame(bronze).assign(
            _linha_origem=range(1, len(bronze) + 1),
            _indice_cabecalho_origem=0, _arquivo_origem="fonte.xlsx",
        )
        dados.to_parquet(pasta / f"{fonte}_2023.parquet")
        return pd.DataFrame(silver), valores, metrica

    def verificar_troca(self, validador, trocas, quantidade):
        silver, valores, metrica = self.preparar(validador)
        validar = validador.validar_rastreabilidade_contra_bronze
        self.assertEqual(validar(silver), len(silver))
        afetadas = silver.COLUNA_ORIGEM.isin(trocas)
        self.assertEqual(afetadas.sum(), quantidade)
        for indice in silver.index[afetadas]:
            coluna = trocas[silver.at[indice, "COLUNA_ORIGEM"]]
            silver.at[indice, "COLUNA_ORIGEM"] = coluna
            silver.at[indice, metrica] = float(valores[coluna])
        with self.assertRaisesRegex(RuntimeError, "COLUNA_ORIGEM=.*cabeçalho indica"):
            validar(silver)

    def test_aprovacao_e_reprovacao_trocadas(self):
        self.verificar_troca(rendimento, {"col_006": "col_024", "col_024": "col_006"}, 54)

    def test_tdi_total_como_anos_iniciais(self):
        self.verificar_troca(tdi, {"col_006": "col_005"}, 27)

    def test_tdi_etapas_invertidas(self):
        self.verificar_troca(tdi, {"col_006": "col_007", "col_007": "col_006"}, 54)

    def test_tdi_exige_um_unico_rotulo_para_a_etapa(self):
        bronze = pd.DataFrame({
            "_indice_cabecalho_origem": [0, 0], "_linha_origem": [1, 2],
            "col_005": ["Ensino Fundamental", "Total"],
            "col_006": [None, "Anos Iniciais"], "col_007": [None, "Anos Finais"],
        })
        for rotulo in ("Anos Iniciais", "Total"):
            with self.subTest(rotulo=rotulo):
                bronze.loc[1, "col_007"] = rotulo
                with self.assertRaisesRegex(RuntimeError, "ausente ou ambíguo"):
                    tdi.identificar_colunas_pelo_cabecalho(bronze, 2023)
