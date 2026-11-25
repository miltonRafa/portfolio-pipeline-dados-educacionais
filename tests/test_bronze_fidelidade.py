import csv
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import pandas as pd

from src.bronze.fidelidade import validar_delimitado, validar_planilha


class FidelidadePlanilhaTest(unittest.TestCase):
    def setUp(self):
        pasta = Path(self.enterContext(TemporaryDirectory()))
        self.raw = pasta / "indicadores.xlsx"
        self.parquet = pasta / "indicadores.parquet"
        linhas = [
            ["UF", "REDE", "VL_OBSERVADO_2019", "VL_OBSERVADO_2021", "MEDIA_5_LP", "MEDIA_5_MT"],
            [None] * 6,
            ["BA", "Pública", 3.4, 6.1, 210.123456789012, 198.23],
            ["AC", "Pública e privada", 4.4, 7, None, 0],
        ]
        pd.DataFrame(linhas).to_excel(self.raw, sheet_name="UF", header=False, index=False)
        self.df = pd.DataFrame([
            linhas[0], ["BA", "Pública", "3.4", "6.1", "210.123456789012", "198.23"],
            ["AC", "Pública e privada", "4.4", "7", None, "0"],
        ], columns=[f"col_{n:03d}" for n in range(1, 7)])
        self.df["_linha_origem"] = [1, 3, 4]
        self.df["_aba_origem"] = "UF"
        self.df["_sha256_arquivo"] = hashlib.sha256(self.raw.read_bytes()).hexdigest()

    def validar(self):
        self.df.to_parquet(self.parquet, index=False)
        return validar_planilha(self.raw, pd.read_parquet(self.parquet), "UF")

    def rejeitar(self, diagnostico):
        with self.assertRaisesRegex(RuntimeError, diagnostico):
            self.validar()

    def test_planilha_legitima_com_linha_vazia_e_precisao(self):
        self.assertEqual(self.validar(), 18)

    def test_taxa_tdi_e_valor_ideb(self):
        for coluna, valor in [("col_003", "4.4"), ("col_004", "7.0")]:
            with self.subTest(coluna=coluna):
                anterior = self.df.at[1, coluna]
                self.df.at[1, coluna] = valor
                self.rejeitar(f"aba='UF', linha=3, coluna={coluna}, esperado=.*encontrado=")
                self.df.at[1, coluna] = anterior

    def test_troca_entre_ufs_com_hash_preservado(self):
        self.df.loc[[1, 2], "col_003"] = ["4.4", "3.4"]
        self.rejeitar("linha=3, coluna=col_003")

    def test_troca_cabecalhos_de_ano(self):
        self.df.loc[0, ["col_003", "col_004"]] = ["VL_OBSERVADO_2021", "VL_OBSERVADO_2019"]
        self.rejeitar("linha=1, coluna=col_003")

    def test_proficiencia_sem_arredondamento(self):
        self.df.at[1, "col_005"] = "210.123456789013"
        self.rejeitar("linha=3, coluna=col_005")

    def test_inversao_disciplinas_inclusive_cabecalho(self):
        self.df["col_005"], self.df["col_006"] = self.df.col_006.copy(), self.df.col_005.copy()
        self.rejeitar("linha=1, coluna=col_005")

    def test_troca_de_redes(self):
        self.df.loc[[1, 2], "col_002"] = ["Pública e privada", "Pública"]
        self.rejeitar("linha=3, coluna=col_002")

    def test_ordem_fisica_das_colunas(self):
        self.df = self.df[self.df.columns[::-1]]
        self.rejeitar("campos de origem")

    def test_associacao_com_linha_original(self):
        self.df["_linha_origem"] = [1, 2, 4]
        self.rejeitar("linha=3, coluna=_linha_origem")


class FidelidadeDelimitadoTest(unittest.TestCase):
    def setUp(self):
        pasta = Path(self.enterContext(TemporaryDirectory()))
        self.raw, self.parquet = pasta / "pnd.txt", pasta / "pnd.parquet"
        linhas = [["NT_GER", "TP_PRES", "TEXTO"], ["49", "555", "NA"], ["", "0", "A;B"]]
        with self.raw.open("w", encoding="utf-8", newline="") as arquivo:
            csv.writer(arquivo, delimiter=";").writerows(linhas)
        self.df = pd.DataFrame(linhas, columns=["col_001", "col_002", "col_003"]).replace("", None)
        self.df["_linha_origem"] = [1, 2, 3]
        self.df["_sha256_arquivo"] = hashlib.sha256(self.raw.read_bytes()).hexdigest()

    def validar(self):
        self.df.to_parquet(self.parquet, index=False)
        return validar_delimitado(self.raw, self.parquet, "utf-8", bloco=2)

    def test_blocos_cabecalho_na_literal_e_delimitador_entre_aspas(self):
        self.assertEqual(self.validar(), 9)

    def test_nota_e_presenca_com_hash_preservado(self):
        for coluna, valor in [("col_001", "50"), ("col_002", "222")]:
            with self.subTest(coluna=coluna):
                anterior = self.df.at[1, coluna]
                self.df.at[1, coluna] = valor
                with self.assertRaisesRegex(RuntimeError, f"linha=2, coluna={coluna}"):
                    self.validar()
                self.df.at[1, coluna] = anterior

    def test_ausencia_por_zero_apos_fronteira_do_bloco(self):
        self.df.at[2, "col_001"] = "0"
        with self.assertRaisesRegex(RuntimeError, "linha=3, coluna=col_001"):
            self.validar()

    def test_registro_excluido_no_fim(self):
        self.df = self.df.iloc[:-1]
        with self.assertRaisesRegex(RuntimeError, "linha=3.*fim do Parquet"):
            self.validar()

    def test_registro_duplicado_no_fim(self):
        self.df = pd.concat([self.df, self.df.iloc[[-1]]], ignore_index=True)
        with self.assertRaisesRegex(RuntimeError, "quantidade de registros"):
            self.validar()

    def test_saeb_csv_preserva_linha_fisica_e_texto_cp1252(self):
        self.raw.write_bytes("UF;REDE\n;\nBA;Pública\n".encode("cp1252"))
        quadro = pd.DataFrame({"col_001": ["UF", "BA"], "col_002": ["REDE", "Pública"],
                               "_linha_origem": [1, 3]})
        quadro.to_parquet(self.parquet, index=False)
        self.assertEqual(validar_delimitado(self.raw, self.parquet, "cp1252",
                                            remover_vazias=True, bloco=1), 4)
