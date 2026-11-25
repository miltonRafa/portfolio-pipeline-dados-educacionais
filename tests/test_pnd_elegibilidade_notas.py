"""Regressões PND-01 com Bronze e Silver sintéticas em diretório isolado."""
from contextlib import redirect_stdout
import io
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import pandas as pd

from src.silver.pnd import validar_silver_pnd as v


class FidelidadePndTest(unittest.TestCase):
    def setUp(self):
        pasta = Path(self.enterContext(TemporaryDirectory()))
        self.bronze = pasta / "bronze.parquet"
        self.silver = pasta / "silver.parquet"
        self.enterContext(patch.multiple(
            v, BRONZE_FILE=self.bronze, SILVER_FILE=self.silver, UFS={"AC"},
            ler_areas_oficiais=lambda: {702: "MATEMÁTICA (LICENCIATURA)"},
            TOTAL_DADOS_ESPERADO=5, TOTAL_555_ESPERADO=3,
            TOTAL_RESULTADOS_COMPLETOS_ESPERADO=3, TOTAL_POPULACAO_ANALITICA_ESPERADO=2,
            TOTAL_555_SEM_RESULTADO_ESPERADO=1, TOTAL_888_COM_RESULTADO_ESPERADO=1,
        ))
        # Ordem física diferente da ingestão oficial. A referência deve ler os rótulos.
        nomes = ["NU_ANO", "CO_GRUPO", "CO_MUNICIPIO_PROVA", "SG_UF_MUNICIPIO_PROVA",
                 "TP_INSCRICAO_PND", "IN_REAPLICACAO", "CO_CADERNO", "TP_PRES",
                 "TP_SIT_DISC", "QT_ACERTOS", "NT_GER", "PROFICIENCIA", "NT_DIS", "NT_OBJ", "OUTRO"]
        fixos = ["2025", "702", "1200401", "AC", "1", "0", "3"]
        linhas = [
            nomes, fixos + ["555", "333", "30", "40", "-1,23456", "0", "50", "x"],
            fixos + ["555", "555", "40", "49", "0", "4,5", "50", "x"],
            fixos + ["555", "555", "NA", None, "", "NA", "NA", "x"],
            fixos + ["222", "222", ".", ".", ".", ".", ".", "x"],
            fixos + ["888", "555", "40", "49", "0", "4,5", "50", "x"],
        ]
        self.fonte = pd.DataFrame(linhas, columns=[f"col_{i+1:03d}" for i in range(len(nomes))])
        self.fonte = self.fonte.assign(_arquivo_origem="pnd.txt", _linha_origem=range(1, 7),
                                       _indice_cabecalho_origem=0,
                                       _granularidade_origem="REGISTRO_INDIVIDUAL")
        self.fonte.to_parquet(self.bronze, index=False)
        self.legitima = pd.DataFrame({
            "ANO": [2025, 2025], "CO_GRUPO": 702, "AREA_PROVA": "MATEMÁTICA (LICENCIATURA)",
            "CO_MUNICIPIO_PROVA": 1200401, "UF_PROVA": "AC", "TP_INSCRICAO_PND": 1,
            "IN_REAPLICACAO": 0, "CO_CADERNO": 3, "TP_PRES": 555, "TP_SIT_DISC": [333, 555],
            "PROFICIENCIA": [-1.23456, 0.0], "NT_OBJ": 50.0, "NT_DIS": [0.0, 4.5],
            "NT_GER": [40.0, 49.0], "QT_ACERTOS": [30, 40], "ARQUIVO_ORIGEM": "pnd.txt",
            "LINHA_ORIGEM_BRONZE": [2, 3], "GRANULARIDADE_ORIGEM": "REGISTRO_INDIVIDUAL",
        })

    def validar(self, silver):
        silver.to_parquet(self.silver, index=False)
        with redirect_stdout(io.StringIO()):
            v.main()

    def test_elegiveis_por_cabecalho_zeros_e_theta_negativo(self):
        self.validar(self.legitima)

    def test_trocas_de_notas(self):
        for a, b in [("NT_OBJ", "NT_GER"), ("NT_DIS", "PROFICIENCIA")]:
            with self.subTest(campos=(a, b)):
                d = self.legitima.copy()
                d[a], d[b] = d[b].copy(), d[a].copy()
                with self.assertRaisesRegex(RuntimeError, "divergências"):
                    self.validar(d)

    def test_exclusao_de_elegivel(self):
        with self.assertRaisesRegex(RuntimeError, "Linhas Silver"):
            self.validar(self.legitima.iloc[:1])

    def test_inclusao_de_ausente(self):
        extra = self.legitima.iloc[:1].assign(TP_PRES=222, LINHA_ORIGEM_BRONZE=5)
        with self.assertRaisesRegex(RuntimeError, "Linhas Silver"):
            self.validar(pd.concat([self.legitima, extra]))

    def test_substituicoes_preservando_cardinalidade(self):
        # 4: presente incompleto, 5: ausente, 6: desconsiderado com notas.
        for linha in (4, 5, 6):
            with self.subTest(linha=linha):
                d = self.legitima.copy()
                d.loc[1, "LINHA_ORIGEM_BRONZE"] = linha
                if linha in (4, 5):
                    d.loc[1, v.CAMPOS_RESULTADO] = 0
                with self.assertRaisesRegex(RuntimeError, "linhas de origem"):
                    self.validar(d)

    def test_erro_espelhado_na_conversao_da_presenca_nao_altera_a_selecao(self):
        # A linha 6 (888) possui as mesmas notas da linha 3 (555).
        # Mesmo atribuindo 555 na saída, a linha 6 permanece inelegível.
        d = self.legitima.copy()
        d.loc[1, "LINHA_ORIGEM_BRONZE"] = 6
        converter = v.inteiro

        def trocar_codigos(serie, nome):
            valores = converter(serie, nome)
            if nome == "TP_PRES":
                for indice, codigo in [(2, 888), (5, 555)]:
                    if indice in valores.index:
                        valores.at[indice] = codigo
            return valores

        with patch.object(v, "inteiro", trocar_codigos):
            with self.assertRaisesRegex(RuntimeError, "linhas de origem"):
                self.validar(d)

    def test_completude_exige_cada_um_dos_cinco_campos(self):
        for nome in v.CAMPOS_RESULTADO:
            with self.subTest(nome=nome):
                fonte = self.fonte.copy()
                coluna = fonte.columns[fonte.iloc[0].eq(nome)][0]
                fonte.loc[1, coluna] = "NA"
                fonte.to_parquet(self.bronze, index=False)
                with self.assertRaisesRegex(RuntimeError, "Diagnóstico independente"):
                    self.validar(self.legitima)

    def test_valor_invalido_nao_se_converte_em_ausencia(self):
        self.fonte.loc[3, "col_011"] = "erro"
        self.fonte.to_parquet(self.bronze, index=False)
        with self.assertRaises(ValueError):
            self.validar(self.legitima)

    def test_presenca_nula_na_silver(self):
        d = self.legitima.astype({"TP_PRES": "Int64"})
        d.loc[0, "TP_PRES"] = pd.NA
        with self.assertRaisesRegex(RuntimeError, "TP_PRES"):
            self.validar(d)

    def test_cabecalhos_ausentes_e_ambiguos(self):
        for coluna, rotulo, erro in [("col_015", "NT_GER", "ambíguo"), ("col_011", "OUTRA", "ausentes")]:
            with self.subTest(erro=erro):
                fonte = self.fonte.copy()
                fonte.loc[0, coluna] = rotulo
                fonte.to_parquet(self.bronze, index=False)
                with self.assertRaisesRegex(RuntimeError, erro):
                    self.validar(self.legitima)

    def test_nota_geral_errada_mesmo_se_a_referencia_concordar(self):
        d = self.legitima.copy()
        d.loc[1, "NT_GER"] = 50
        with patch.object(v, "reconstruir_referencia", return_value=d.copy()):
            with self.assertRaisesRegex(RuntimeError, "Nota Técnica 44/2025.*linha Bronze 3"):
                self.validar(d)

    def test_precisao_publicada_sem_recalcular_nota(self):
        d = self.legitima.copy()
        d.loc[1, ["NT_OBJ", "NT_DIS", "NT_GER"]] = [49.9, 4.53, 48.98]
        v.validar_nota_geral(d)
        self.assertEqual(d.loc[1, "NT_GER"], 48.98)
        d.loc[1, "NT_GER"] += 0.01
        with self.assertRaisesRegex(RuntimeError, "NT_GER incompatível"):
            v.validar_nota_geral(d)
