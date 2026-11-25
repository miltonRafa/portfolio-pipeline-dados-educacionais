"""PND-02: referências independentes para a Tabela 2 e para CO_GRUPO."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import pandas as pd

from src import referencias_pnd as oficial
from src.gold import validar_gold
from src.gold.dimensoes import validar_dimensoes as dimensoes
from src.gold.pnd import classificacao, transformar_pnd, validar_fato_pnd


class PadroesOficiaisTest(unittest.TestCase):
    def setUp(self):
        self.notas = [49.99, 50.00, 50.01, 69.99, 70.00, 70.01]
        self.silver = pd.DataFrame({
            "ANO": 2025, "UF_PROVA": "AC", "CO_MUNICIPIO_PROVA": 1200401, "CO_GRUPO": 702,
            "PROFICIENCIA": 1.0, "NT_OBJ": 75.0, "NT_DIS": 0.0, "NT_GER": self.notas,
            "QT_ACERTOS": 40,
        })
        self.esperados = ["ABAIXO_DO_BASICO", "BASICO", "BASICO", "BASICO", "ADEQUADO", "ADEQUADO"]

    def test_seis_vizinhos_dos_limites(self):
        fato = transformar_pnd.construir_fato(self.silver)
        self.assertEqual(fato.PADRAO_DESEMPENHO.tolist(), self.esperados)
        validar_fato_pnd.validar_padrao_oficial(fato)
        for i, errado in [(1, "ABAIXO_DO_BASICO"), (4, "BASICO")]:
            with self.subTest(nota=self.notas[i]):
                copia = fato.copy()
                copia.at[i, "PADRAO_DESEMPENHO"] = errado
                with self.assertRaisesRegex(RuntimeError, "Tabela 2"):
                    validar_fato_pnd.validar_padrao_oficial(copia)

    def test_mudanca_no_classificador_compartilhado(self):
        for constante, corte in [("CORTE_BASICO", 55), ("CORTE_ADEQUADO", 75)]:
            with self.subTest(corte=corte), patch.object(classificacao, constante, corte):
                fato = transformar_pnd.construir_fato(self.silver)
                self.assertNotEqual(fato.PADRAO_DESEMPENHO.tolist(), self.esperados)
                with self.assertRaisesRegex(RuntimeError, "Tabela 2"):
                    validar_fato_pnd.validar_padrao_oficial(fato)

    def test_global_rejeita_o_corte_compartilhado_mesmo_com_tres_categorias(self):
        silver = pd.concat([self.silver, self.silver.iloc[[-1]].assign(NT_GER=80)], ignore_index=True)
        with (patch.object(classificacao, "CORTE_ADEQUADO", 75),
              patch.dict(validar_gold.LINHAS_ESPERADAS, FATO_PND=len(silver)),
              patch.object(validar_gold, "UFS_ESPERADAS", {"AC"})):
            fato = transformar_pnd.construir_fato(silver)
            with self.assertRaisesRegex(RuntimeError, "Tabela 2"):
                validar_gold.validar_fato_pnd(fato)

    def test_nota_objetiva_em_lugar_da_geral(self):
        fato = transformar_pnd.construir_fato(self.silver)
        fato["PADRAO_DESEMPENHO"] = classificacao.classificar_nivel_desempenho(fato.NT_OBJ)
        with self.assertRaisesRegex(RuntimeError, "Tabela 2"):
            validar_fato_pnd.validar_padrao_oficial(fato)

    def test_inversao_de_rotulos(self):
        fato = transformar_pnd.construir_fato(self.silver)
        fato["PADRAO_DESEMPENHO"] = fato.PADRAO_DESEMPENHO.replace({"BASICO": "ADEQUADO", "ADEQUADO": "BASICO"})
        with self.assertRaisesRegex(RuntimeError, "Tabela 2"):
            validar_fato_pnd.validar_padrao_oficial(fato)


class AreasOficiaisTest(unittest.TestCase):
    def setUp(self):
        pasta = Path(self.enterContext(TemporaryDirectory()))
        self.dicionario = pasta / "dicionario.xlsx"
        self.enterContext(patch.object(oficial, "DICIONARIO", self.dicionario))
        self.pares = {702: "MATEMÁTICA (LICENCIATURA)", 905: "LETRAS - PORTUGUÊS E INGLÊS (LICENCIATURA)",
                      **{i: f"ÁREA {i}" for i in range(1000, 1015)}}
        self.dim = pd.DataFrame(self.pares.items(), columns=["CO_GRUPO", "AREA_PROVA"])
        self.dim["AREA_PROVA"] = self.dim["AREA_PROVA"].astype("string")
        linhas = [["OUTRA_VARIAVEL", "99998 = OUTRO"]]
        for i, (codigo, nome) in enumerate(self.pares.items()):
            categoria = nome.replace(" - ", "  -").replace(" (", "  (")
            linhas.append(["CO_GRUPO" if i == 0 else None, f"{codigo} = {categoria}"])
        linhas.append(["VARIAVEL_SEGUINTE", "99999 = OUTRO"])
        self.planilha = pd.DataFrame([[v, None, None, None, c] for v, c in linhas])
        self.gravar_dicionario()
        self.dim_file = pasta / "dim.parquet"
        self.silver_file = pasta / "silver.parquet"
        self.enterContext(patch.dict(dimensoes.GOLD_FILES, dim_area_pnd=self.dim_file))
        self.enterContext(patch.dict(dimensoes.SILVER_FILES, pnd=self.silver_file))

    def gravar_dicionario(self):
        self.planilha.to_excel(self.dicionario, sheet_name="DICIONÁRIO_DE_VARIAVÉIS",
                               header=False, index=False)

    def validar_pares(self, pares):
        pares.to_parquet(self.dim_file, index=False)
        pares.to_parquet(self.silver_file, index=False)
        return dimensoes.validar_dim_area_pnd()

    def test_referencia_lida_somente_do_bloco_co_grupo(self):
        self.assertEqual(oficial.ler_areas_oficiais(), self.pares)
        self.assertEqual(self.validar_pares(self.dim), 17)

    def test_rotulos_trocados_na_silver_e_na_dimensao(self):
        self.dim.loc[[0, 1], "AREA_PROVA"] = self.dim.loc[[1, 0], "AREA_PROVA"].tolist()
        with self.assertRaisesRegex(RuntimeError, "dicionário"):
            self.validar_pares(self.dim)

    def test_codigo_inexistente_mesmo_com_17_areas(self):
        self.dim.at[0, "CO_GRUPO"] = 99999
        with self.assertRaisesRegex(RuntimeError, "17 áreas oficiais"):
            self.validar_pares(self.dim)

    def test_dicionario_ambiguo_rejeitado(self):
        self.planilha.iat[2, 4] = "702 = OUTRA ÁREA"
        self.gravar_dicionario()
        with self.assertRaisesRegex(RuntimeError, "ambígua"):
            oficial.ler_areas_oficiais()

    def test_chave_da_fato_ausente_na_dimensao(self):
        pasta = self.dim_file.parent
        tabelas = {
            "uf": pd.DataFrame({"UF": ["AC"]}), "tempo": pd.DataFrame({"ANO": [2025]}),
            "area": self.dim, "municipio": pd.DataFrame({"CO_MUNICIPIO": [1200401], "UF": ["AC"]}),
        }
        arquivos = {nome: pasta / f"{nome}.parquet" for nome in tabelas}
        for nome, tabela in tabelas.items():
            tabela.to_parquet(arquivos[nome], index=False)
        fato = pd.DataFrame({"UF_PROVA": ["AC"], "ANO": [2025], "CO_MUNICIPIO_PROVA": [1200401], "CO_GRUPO": [99999]})
        with patch.dict(validar_fato_pnd.DIM_FILES, arquivos), self.assertRaisesRegex(RuntimeError, "órfãs"):
            validar_fato_pnd.validar_integridade_dimensional(fato)
