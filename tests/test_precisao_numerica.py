from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import pandas as pd

from src.gold.ideb import validar_fato_ideb
from src.gold.pnd import validar_fato_pnd
from src.gold.rendimento import validar_fato_rendimento
from src.gold.saeb import validar_fato_saeb
from src.gold.tdi import validar_fato_tdi
from src.silver.ideb import validar_silver_ideb as ideb


class PrecisaoNumericaTest(unittest.TestCase):
    def test_ideb_contra_celula_publicada(self):
        pasta = Path(self.enterContext(TemporaryDirectory()))
        arquivo = pasta / "ideb.parquet"
        etapa = "ANOS_INICIAIS"
        self.enterContext(patch.object(ideb, "ARQUIVOS", {etapa: arquivo}))
        self.enterContext(patch.object(ideb, "ANOS", {2007}))
        pd.DataFrame({
            "col_001": [None, "Acre", "Acre"], "col_002": [None, "Pública (4)", "Pública (4)"],
            "col_003": ["VL_OBSERVADO_2007", "3,70", "--"], "_linha_origem": [1, 2, 3],
            "_indice_cabecalho_origem": 0, "_arquivo_origem": "ideb.xlsx", "_aba_origem": "UF",
        }).to_parquet(arquivo)
        silver = pd.DataFrame({
            "ANO": 2007, "UF": "AC", "ETAPA": etapa, "LINHA_ORIGEM_BRONZE": [2, 3],
            "COLUNA_ORIGEM": "col_003", "ARQUIVO_ORIGEM": "ideb.xlsx", "ABA_ORIGEM": "UF",
            "IDEB": [3.7, None],
        })
        self.assertEqual(ideb.validar_rastreabilidade_contra_bronze(silver), 2)
        for indice, valor in [(0, 3.71), (1, 0.0)]:
            with self.subTest(indice=indice):
                alterada = silver.copy()
                alterada.loc[indice, "IDEB"] = valor
                with self.assertRaisesRegex(RuntimeError, "Silver="):
                    ideb.validar_rastreabilidade_contra_bronze(alterada)

    def test_fatos_historicos_preservam_valor_copiado(self):
        chave = dict(ANO=2007, UF="AC", ETAPA="ANOS_INICIAIS", REDE="PUBLICA",
                     INDICADOR="APROVACAO", DISCIPLINA="LP")
        for validador, campo, valor in [(validar_fato_ideb, "IDEB", 3.7),
                                       (validar_fato_rendimento, "VALOR", 78.3),
                                       (validar_fato_tdi, "TDI", 3.4),
                                       (validar_fato_saeb, "PROFICIENCIA", 223.8)]:
            with self.subTest(campo=campo):
                silver = pd.DataFrame([{**chave, campo: valor}])[validador.COLUNAS]
                validador.comparar_com_silver(silver.copy(), silver)
                gold = silver.copy()
                gold.loc[0, campo] += 5e-13
                with self.assertRaises(RuntimeError):
                    validador.comparar_com_silver(gold, silver)

    def test_fato_pnd_preserva_resultados_inclusive_acertos(self):
        silver = pd.DataFrame([dict(ANO=2025, UF_PROVA="AC", CO_MUNICIPIO_PROVA=1200401,
                                    CO_GRUPO=702, PROFICIENCIA=-1.23456, NT_OBJ=0.0, NT_DIS=10.0,
                                    NT_GER=20.0, QT_ACERTOS=0)])
        validar_fato_pnd.comparar_com_silver(silver.copy(), silver)
        for campo in validar_fato_pnd.COLUNAS_RESULTADO:
            with self.subTest(campo=campo):
                gold = silver.copy()
                gold[campo] = gold[campo] + (0.25 if campo == "QT_ACERTOS" else 5e-13)
                with self.assertRaisesRegex(RuntimeError, campo):
                    validar_fato_pnd.comparar_com_silver(gold, silver)
