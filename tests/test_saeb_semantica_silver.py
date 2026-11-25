from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import pandas as pd

from src.silver.saeb import transformar_saeb as produtor
from src.silver.saeb import validar_silver_saeb as validador


PUBLICA = "Total - Federal, Estadual e Municipal"
COM_PRIVADA = "Total - Federal, Estadual, Municipal e Privada"


def bronze(ano, linhas, numeros=None, inicio=1):
    df = pd.DataFrame(linhas, columns=[f"col_{i + 1:03d}" for i in range(len(linhas[0]))])
    df = df.astype("string[pyarrow]")
    return df.assign(_linha_origem=numeros or list(range(1, len(df) + 1)),
                     _indice_cabecalho_origem=inicio - 1, _ano_referencia=ano,
                     _arquivo_origem=f"uf_{ano}", _aba_origem="Estados",
                     _granularidade_origem="UF")


def hierarquica(ano):
    inicio = 4 if ano == 2013 else 3
    return bronze(ano, [
        ["UF", "REDE", "LOCALIZAÇÃO", "CAPITAL", "MÉDIAS DE PROFICIÊNCIA", None,
         "MÉDIAS DE PROFICIÊNCIA", None],
        [None] * 4 + ["ANOS INICIAIS - 5º ANO", None, "ANOS FINAIS - 9º ANO", None],
        [None] * 4 + ["LÍNGUA PORTUGUESA", "MATEMÁTICA"] * 2,
        ["Acre", PUBLICA, "Total", "Total", "203", "218", "247", "261"],
        ["Acre", COM_PRIVADA, "Total", "Total", "204", "219", "248", "262"],
    ], numeros=list(range(inicio, inicio + 5)), inicio=inicio)


class SemanticaSaebTest(unittest.TestCase):
    def test_precisao_da_proficiencia_publicada(self):
        df = hierarquica(2013)
        df.loc[3, "col_005"] = "223,80000000000004"
        silver = pd.DataFrame(produtor.transformar_2013_2015(2013, df))
        ref = pd.DataFrame(validador.extrair_esperados_2013_2015(2013, df))
        alvo = silver.COLUNA_ORIGEM.eq("col_005")
        silver.loc[alvo, "PROFICIENCIA"] = 223.8
        self.assertEqual(validador.validar_contra_bronze(silver, ref), 4)
        silver.loc[alvo, "PROFICIENCIA"] = 223.801
        with self.assertRaisesRegex(RuntimeError, "divergências"):
            validador.validar_contra_bronze(silver, ref)
        # A referência também deve preservar eventuais casas adicionais da fonte.
        df.loc[3, "col_005"] = "223,801"
        ref = pd.DataFrame(validador.extrair_esperados_2013_2015(2013, df))
        self.assertEqual(validador.validar_contra_bronze(silver, ref), 4)

    def test_layouts_hierarquicos_legitimos(self):
        for ano in (2013, 2015):
            with self.subTest(ano=ano):
                df = hierarquica(ano)
                silver = pd.DataFrame(produtor.transformar_2013_2015(ano, df))
                ref = pd.DataFrame(validador.extrair_esperados_2013_2015(ano, df))
                self.assertEqual(validador.validar_contra_bronze(silver, ref), 4)

    def test_posicoes_espelhadas_nao_determinam_disciplina_ou_etapa(self):
        for ordem in ([5, 4, 7, 6], [6, 7, 4, 5]):
            with self.subTest(ordem=ordem):
                df = hierarquica(2013)
                # Layout sintético válido: realocar títulos e dados em conjunto.
                # Para inverter apenas as disciplinas, manter as âncoras mescladas.
                inicio = 2 if ordem[0] == 5 else 0
                df.iloc[inicio:, 4:8] = df.iloc[inicio:, ordem].to_numpy(copy=True)
                silver = pd.DataFrame(produtor.transformar_2013_2015(2013, df))
                ref = pd.DataFrame(validador.extrair_esperados_2013_2015(2013, df))
                with self.assertRaisesRegex(RuntimeError, "divergências"):
                    validador.validar_contra_bronze(silver, ref)

    def test_cabecalho_hierarquico_ausente_ou_ambiguo(self):
        for linha, coluna, rotulo in [(0, 6, None), (1, 6, None), (2, 5, None),
                                      (2, 5, "LÍNGUA PORTUGUESA")]:
            with self.subTest(linha=linha, coluna=coluna, rotulo=rotulo):
                df = hierarquica(2015)
                df.iat[linha, coluna] = rotulo
                with self.assertRaisesRegex(RuntimeError, "ausente ou ambíguo"):
                    validador.extrair_esperados_2013_2015(2015, df)

    def test_rede_valor_e_linhagem_trocados_em_conjunto(self):
        df = hierarquica(2015)
        silver = pd.DataFrame(produtor.transformar_2013_2015(2015, df))
        silver["PROFICIENCIA"] += 1
        silver["LINHA_ORIGEM_BRONZE"] += 1
        silver["REDE_ORIGEM"] = COM_PRIVADA
        ref = pd.DataFrame(validador.extrair_esperados_2013_2015(2015, df))
        with self.assertRaisesRegex(RuntimeError, "divergências"):
            validador.validar_contra_bronze(silver, ref)

    def test_nota_da_fonte_sobre_zero_vale_apenas_para_2015(self):
        for ano in (2013, 2015):
            df = hierarquica(ano)
            df.loc[3, "col_005"] = "0"
            ref = pd.DataFrame(validador.extrair_esperados_2013_2015(ano, df))
            valor = ref.loc[ref.COLUNA_ORIGEM_ESPERADA.eq("col_005"), "PROFICIENCIA_ESPERADA"].item()
            if ano == 2015:
                self.assertTrue(pd.isna(valor))
            else:
                self.assertEqual(valor, 0)

    def test_composicao_publica_por_edicao(self):
        redes = pd.Series(["Total - Estadual e Municipal", PUBLICA, COM_PRIVADA, "Estadual"])
        for ano in (2007, 2009, 2013, 2015, 2017, 2019, 2021, 2023):
            self.assertEqual(validador.rede_publica(redes, ano).tolist(),
                             [ano <= 2009, ano >= 2013, False, False])

    def test_medias_tecnicas_e_coluna_incorreta_com_linhagem(self):
        for ano, series in [(2007, (4, 8)), (2017, (5, 9)), (2023, (5, 9))]:
            with self.subTest(ano=ano):
                rede = "Total - Estadual e Municipal" if ano == 2007 else PUBLICA
                df = bronze(ano, [
                    ["CO_UF", "NO_UF", "DEPENDENCIA_ADM", "LOCALIZACAO", "CAPITAL",
                     *[f"MEDIA_{s}_{d}" for s in series for d in ("LP", "MT")], "MEDIA_12_MT"],
                    ["12", "Acre", rede, "Total", "Total", "203", "218", "247", "261", "278"],
                ])
                extrair = (validador.extrair_esperados_2007_2009 if ano == 2007
                           else validador.extrair_esperados_2013_2023)
                transformar = (produtor.transformar_2007_2009 if ano == 2007
                               else produtor.transformar_2013_2023)
                ref = pd.DataFrame(extrair(ano, df))
                silver = pd.DataFrame(transformar(ano, df))
                self.assertEqual(validador.validar_contra_bronze(silver, ref), 4)
                silver.loc[0, ["COLUNA_ORIGEM", "PROFICIENCIA"]] = ["col_010", 278]
                with self.assertRaisesRegex(RuntimeError, "divergências"):
                    validador.validar_contra_bronze(silver, ref)
                df.iat[0, 9] = df.iat[0, 5]
                with self.assertRaisesRegex(RuntimeError, "ambíguo"):
                    extrair(ano, df)
                df.iat[0, 9] = df.iat[0, 5] = None
                with self.assertRaisesRegex(RuntimeError, "ausente"):
                    extrair(ano, df)

    def test_codigo_e_nome_uf_devem_concordar(self):
        troca = {11: "AC", 12: "RO"}
        linha, mapa = {"a": "11", "b": "Rondônia"}, {"CO_UF": "a", "NO_UF": "b"}
        with patch.dict(produtor.UF_CODIGO_SIGLA, troca), patch.dict(validador.UF_CODIGO_SIGLA, troca):
            self.assertEqual(produtor.obter_uf(linha, mapa), "AC")
            with self.assertRaisesRegex(RuntimeError, "UF divergentes"):
                validador.obter_uf(linha, mapa)

    def test_referencia_rejeita_troca_de_arquivos_entre_edicoes(self):
        df = hierarquica(2015)
        with TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "fonte.parquet"
            df.to_parquet(caminho)
            with patch.object(validador, "ANOS", [2013]), patch.dict(validador.ARQUIVOS, {2013: caminho}):
                with self.assertRaisesRegex(RuntimeError, "edição"):
                    validador.construir_referencia_bronze()

    def test_2023_exige_fonte_estadual(self):
        df = bronze(2023, [["ANO_SAEB"], ["2023"]]).assign(_granularidade_origem="ESCOLA")
        with TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "escola.parquet"
            df.to_parquet(caminho)
            with patch.object(validador, "ANOS", [2023]), patch.dict(validador.ARQUIVOS, {2023: caminho}):
                with self.assertRaisesRegex(RuntimeError, "agregada por UF"):
                    validador.construir_referencia_bronze()

    def test_2011_resolve_codigos_pelo_significado_no_dicionario(self):
        linhas = [
            ("ID_SERIE", "5 - 4ª série/5º ano Ensino Fundamental"),
            (None, "9 - 8ª série/9º ano Ensino Fundamental"),
            ("ID_TIPO_REDE", "0 - Todas"), (None, "5 - Pública"),
            ("ID_LOCALIZACAO", "0 - Todas"), ("ID_CAPITAL", "0 - Todas"),
        ]
        with TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "dicionario.xlsx"
            pd.DataFrame([[v, None, None, None, c] for v, c in linhas]).to_excel(
                arquivo, sheet_name="TS_RESULTADO_UF", index=False, header=False)
            codigos = validador.codigos_2011(arquivo)
        df = bronze(2011, [
            ["ID_UF", "SIGLA_UF", "ID_SERIE", "ID_TIPO_REDE", "ID_LOCALIZACAO",
             "ID_CAPITAL", "MEDIA_LP", "MEDIA_MT"],
            ["12", "AC", "5", "5", "0", "0", "203", "218"],
            ["12", "AC", "9", "5", "0", "0", "247", "261"],
            ["12", "AC", "5", "0", "0", "0", "204", "219"],
        ])
        with patch.object(validador, "codigos_2011", return_value=codigos):
            ref = pd.DataFrame(validador.extrair_esperados_2011(df))
        silver = pd.DataFrame(produtor.transformar_2011(df))
        self.assertEqual(validador.validar_contra_bronze(silver, ref), 4)
        silver["ETAPA"] = silver.ETAPA.map({"ANOS_INICIAIS": "ANOS_FINAIS",
                                            "ANOS_FINAIS": "ANOS_INICIAIS"})
        with self.assertRaisesRegex(RuntimeError, "divergências"):
            validador.validar_contra_bronze(silver, ref)
