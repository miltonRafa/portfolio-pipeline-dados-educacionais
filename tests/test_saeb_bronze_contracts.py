"""Regressões AUD-01 com diretórios temporários e dados fictícios."""
from contextlib import redirect_stdout
import hashlib
import importlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

contratos = importlib.import_module("src.bronze.saeb.contratos_saeb")
historico = importlib.import_module("src.bronze.saeb.validar_bronze_saeb")
ingestao = importlib.import_module("src.bronze.saeb.ingest_saeb")
agregado = importlib.import_module("src.bronze.saeb.validar_bronze_saeb_resultados_2023")
produtor = importlib.import_module("src.bronze.saeb.ingest_saeb_resultados_2023")
pipeline = importlib.import_module("src.pipeline")
NOMES = [c["arquivo_bronze"] for c in historico.CONFIG.values()]


class InventarioSaebTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        for name in NOMES:
            (self.folder / name).touch()

    def validate(self, **kwargs):
        return contratos.validar_inventario_bronze(self.folder, NOMES, **kwargs)

    def test_nove_historicos_validos_antes_da_etapa_agregada(self):
        self.assertFalse(self.validate())

    def test_dez_arquivos_validos_com_agregado_exigido(self):
        (self.folder / contratos.NOME_AGREGADO_2023).touch()
        self.assertTrue(self.validate(exigir_agregado_2023=True))

    def test_agregado_ausente_quando_exigido(self):
        with self.assertRaisesRegex(RuntimeError, contratos.NOME_AGREGADO_2023):
            self.validate(exigir_agregado_2023=True)

    def test_cada_historico_e_obrigatorio_mesmo_com_agregado(self):
        (self.folder / contratos.NOME_AGREGADO_2023).touch()
        for name in NOMES:
            with self.subTest(name=name):
                (self.folder / name).unlink()
                with self.assertRaisesRegex(RuntimeError, name):
                    self.validate()
                (self.folder / name).touch()

    def test_arquivo_inesperado(self):
        (self.folder / "saeb_2025.parquet").touch()
        with self.assertRaisesRegex(RuntimeError, "saeb_2025"):
            self.validate()

    def test_aliases_extensoes_e_copias_invalidas(self):
        for name in ("saeb_2023_resultados_UF.parquet", "saeb_2007 (1).parquet",
                     "saeb_2023_resultados_uf.csv", "saeb2007.parquet", "outro.parquet"):
            with self.subTest(name=name):
                path = self.folder / name
                path.touch()
                with self.assertRaisesRegex(RuntimeError, "Inesperados"):
                    self.validate()
                path.unlink()

    def test_diretorio_nao_substitui_agregado(self):
        (self.folder / contratos.NOME_AGREGADO_2023).mkdir()
        with self.assertRaisesRegex(RuntimeError, "Inesperados"):
            self.validate(exigir_agregado_2023=True)

    def test_nomes_historicos_duplicados_na_configuracao(self):
        with self.assertRaisesRegex(RuntimeError, "duplicada"):
            contratos.validar_inventario_bronze(self.folder, NOMES + [NOMES[0]])

    def test_historicos_nao_podem_incorporar_agregado(self):
        with self.assertRaisesRegex(RuntimeError, "confundida"):
            contratos.validar_inventario_bronze(self.folder, NOMES + [contratos.NOME_AGREGADO_2023])

    def test_produtor_e_configuracoes_identificam_mesmos_arquivos(self):
        self.assertEqual(produtor.OUTPUT_FILE.name, contratos.NOME_AGREGADO_2023)
        self.assertEqual(list(historico.CONFIG), [2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021, 2023])
        self.assertEqual([f"saeb_{ano}.parquet" for ano in ingestao.CONFIG], NOMES)
        self.assertEqual([c["arquivo"] for c in ingestao.CONFIG.values()],
                         [c["arquivo_raw"] for c in historico.CONFIG.values()])
        self.assertEqual(historico.CONFIG[2023]["granularidade"], "ESCOLA")
        self.assertEqual(produtor.GRANULARIDADE_ORIGEM, "UF")

    def test_main_percorre_nove_historicos_sem_exigir_agregado_prematuro(self):
        with patch.object(historico, "BRONZE_DIR", self.folder), \
             patch.object(historico, "validar_arquivo", side_effect=lambda ano, cfg: cfg["linhas"]) as check, \
             patch.object(historico.agregado_2023, "main") as aggregate_check, redirect_stdout(io.StringIO()):
            historico.main()
        self.assertEqual([c.args[0] for c in check.call_args_list], list(historico.CONFIG))
        aggregate_check.assert_not_called()

    def test_agregado_presente_e_validado_sem_ser_contado_como_historico(self):
        (self.folder / contratos.NOME_AGREGADO_2023).touch()
        with patch.object(historico, "BRONZE_DIR", self.folder), \
             patch.object(historico, "validar_arquivo", side_effect=lambda ano, cfg: cfg["linhas"]) as check, \
             patch.object(historico.agregado_2023, "main") as aggregate_check, redirect_stdout(io.StringIO()):
            historico.main(exigir_agregado_2023=True)
        self.assertEqual(check.call_count, 9)
        aggregate_check.assert_called_once_with()

    def test_falha_do_validador_agregado_nao_e_suprimida(self):
        (self.folder / contratos.NOME_AGREGADO_2023).touch()
        with patch.object(historico, "BRONZE_DIR", self.folder), \
             patch.object(historico, "validar_arquivo", side_effect=lambda ano, cfg: cfg["linhas"]), \
             patch.object(historico.agregado_2023, "main", side_effect=RuntimeError("conteúdo inválido")), \
             redirect_stdout(io.StringIO()), self.assertRaisesRegex(RuntimeError, "conteúdo inválido"):
            historico.main()

    def test_ingestao_reexecutada_preserva_agregado_e_adota_contrato_estrito(self):
        path = self.folder / contratos.NOME_AGREGADO_2023
        path.write_bytes(b"agregado preservado")
        with patch.object(ingestao, "BRONZE_DIR", self.folder), \
             patch.object(ingestao, "processar_ano") as process, redirect_stdout(io.StringIO()):
            ingestao.main()
        self.assertEqual(process.call_count, 9)
        self.assertEqual(path.read_bytes(), b"agregado preservado")
        (self.folder / "saeb_2027.parquet").touch()
        with patch.object(ingestao, "BRONZE_DIR", self.folder), \
             patch.object(ingestao, "processar_ano"), redirect_stdout(io.StringIO()), \
             self.assertRaisesRegex(RuntimeError, "saeb_2027"):
            ingestao.main()

    def test_ordem_do_fluxo_exige_agregado_antes_da_silver(self):
        scripts = [s.script for s in pipeline.COMMANDS["full"]]
        paths = ["src/bronze/saeb/ingest_saeb.py", "src/bronze/saeb/validar_bronze_saeb.py",
                 "src/bronze/saeb/ingest_saeb_resultados_2023.py", "src/bronze/saeb/validar_bronze_saeb_resultados_2023.py",
                 "src/silver/saeb/transformar_saeb.py"]
        positions = [scripts.index(p) for p in paths]
        self.assertEqual(positions, sorted(positions))

    def test_dimensoes_existem_antes_dos_validadores_das_fatos(self):
        scripts = [s.script for s in pipeline.COMMANDS["gold"]]
        build = scripts.index("src/gold/dimensoes/transformar_dimensoes.py")
        validate = scripts.index("src/gold/dimensoes/validar_dimensoes.py")
        self.assertLess(build, validate)
        for path in scripts:
            if "/validar_fato_" in path:
                with self.subTest(path=path):
                    self.assertLess(validate, scripts.index(path))
        self.assertEqual(scripts[-1], "src/gold/validar_gold.py")


class ConteudoHistoricoTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.cfg = dict(historico.CONFIG[2007])
        self.cfg.update(linhas=2, sha256=hashlib.sha256(b"raw ficticio").hexdigest())
        (self.folder / self.cfg["arquivo_raw"]).write_bytes(b"raw ficticio")
        cols = [f"col_{i:03d}" for i in range(1, 13)]
        header = self.cfg["marcadores"] + ["campo"] * (12 - len(self.cfg["marcadores"]))
        self.df = pd.DataFrame([header, ["1"] * 12], columns=cols)
        for key, value in {"_fonte": "SAEB", "_sha256_arquivo": self.cfg["sha256"],
                           "_arquivo_origem": self.cfg["arquivo_raw"], "_aba_origem": self.cfg["aba"],
                           "_ano_referencia": 2007, "_granularidade_origem": "UF",
                           "_indice_cabecalho_origem": 0, "_linha_origem": [1, 2]}.items():
            self.df[key] = value

    def validate(self, frame=None):
        if frame is None:
            frame = self.df
        frame.to_parquet(self.folder / self.cfg["arquivo_bronze"], index=False)
        with patch.object(historico, "RAW_DIR", self.folder), \
             patch.object(historico, "BRONZE_DIR", self.folder), redirect_stdout(io.StringIO()):
            return historico.validar_arquivo(2007, self.cfg)

    def test_fixture_historica_valida(self):
        self.assertEqual(self.validate(), 2)

    def test_hash_raw_alterado_rejeitado(self):
        (self.folder / self.cfg["arquivo_raw"]).write_bytes(b"raw alterado")
        with self.assertRaisesRegex(RuntimeError, "SHA-256"):
            self.validate()

    def test_esquema_e_sequencia_fisica_preservados(self):
        for coluna in ("_fonte", "col_003"):
            with self.subTest(coluna=coluna), self.assertRaises(RuntimeError):
                self.validate(self.df.drop(columns=coluna))

    def test_proveniencia_historica_invalida_rejeitada(self):
        for coluna, value in {"_fonte": "OUTRA", "_sha256_arquivo": "0" * 64,
                              "_arquivo_origem": "errado.xlsx", "_aba_origem": "Outra",
                              "_ano_referencia": 2023, "_granularidade_origem": "ESCOLA",
                              "_indice_cabecalho_origem": 99}.items():
            with self.subTest(coluna=coluna):
                frame = self.df.copy(); frame[coluna] = value
                with self.assertRaises(RuntimeError):
                    self.validate(frame)

    def test_linhas_duplicadas_ausentes_ou_desordenadas_rejeitadas(self):
        for values in ([1, 1], [1, None], [2, 1]):
            with self.subTest(values=values):
                frame = self.df.copy(); frame["_linha_origem"] = values
                with self.assertRaises(RuntimeError):
                    self.validate(frame)

    def test_cabecalho_alterado_rejeitado(self):
        self.df.loc[0, "col_001"] = "INVALIDO"
        with self.assertRaisesRegex(RuntimeError, "Marcadores"):
            self.validate()

    def test_cardinalidade_alterada_rejeitada(self):
        with self.assertRaisesRegex(RuntimeError, "Quantidade de linhas"):
            self.validate(self.df.iloc[:1])


class ConteudoAgregadoTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.raw_file = self.folder / agregado.RAW_FILE.name
        self.raw_file.write_bytes(b"workbook oficial ficticio")
        self.bronze_file = self.folder / contratos.NOME_AGREGADO_2023
        header = ["ANO_SAEB", "CO_UF", "NO_UF", "DEPENDENCIA_ADM", "LOCALIZACAO", "CAPITAL",
                  "MEDIA_5_LP", "MEDIA_5_MT", "MEDIA_9_LP", "MEDIA_9_MT"]
        rows = [[2023, uf, "UF ficticia", "Total - Federal, Estadual e Municipal", "Total", "Total",
                 200.1, 210.2, 240.3, 250.4] for uf in sorted(agregado.UF_CODIGOS)]
        self.raw = pd.DataFrame([header, *rows])
        self.df = agregado.normalizar_raw(self.raw)
        for key, value in {"_sha256_arquivo": hashlib.sha256(self.raw_file.read_bytes()).hexdigest(),
                           "_arquivo_origem": self.raw_file.name, "_aba_origem": "Estados",
                           "_ano_referencia": 2023, "_indice_cabecalho_origem": 0,
                           "_granularidade_origem": "UF", "_linha_origem": list(range(1, 29))}.items():
            self.df[key] = value

    def validate(self):
        self.df.to_parquet(self.bronze_file, index=False)
        with patch.object(agregado, "RAW_FILE", self.raw_file), \
             patch.object(agregado, "BRONZE_FILE", self.bronze_file), \
             patch.object(agregado, "carregar_raw", return_value=self.raw), redirect_stdout(io.StringIO()):
            agregado.main()

    def test_fixture_agregada_com_27_ufs_e_108_proficiencias(self):
        self.validate()
        self.assertEqual(len(agregado.validar_estrato_publico(self.df)), 4)
        self.assertEqual((len(self.df) - 1) * 4, 108)

    def test_conteudo_agregado_alterado_rejeitado(self):
        self.df.loc[1, "col_007"] = "999"
        with self.assertRaisesRegex(RuntimeError, "divergências RAW"):
            self.validate()

    def test_esquema_agregado_incompleto_rejeitado(self):
        self.df = self.df.drop(columns="_granularidade_origem")
        with self.assertRaises(KeyError):
            self.validate()

    def test_proveniencia_agregada_invalida_rejeitada(self):
        self.df["_granularidade_origem"] = "ESCOLA"
        with self.assertRaisesRegex(RuntimeError, "Proveniência"):
            self.validate()

    def test_uf_ausente_ou_duplicada_rejeitada(self):
        for frame in (self.df.iloc[:-1], pd.concat([self.df, self.df.iloc[[1]]], ignore_index=True)):
            with self.subTest(linhas=len(frame)), self.assertRaisesRegex(RuntimeError, "27 linhas"):
                agregado.validar_estrato_publico(frame)
        frame = self.df.copy(); frame.loc[2, "col_002"] = frame.loc[1, "col_002"]
        with self.assertRaisesRegex(RuntimeError, "Conjunto de UFs"):
            agregado.validar_estrato_publico(frame)

    def test_proficiencia_ausente_rejeitada(self):
        frame = self.df.copy(); frame.loc[1, "col_007"] = "--"
        with self.assertRaisesRegex(RuntimeError, "valores ausentes"):
            agregado.validar_estrato_publico(frame)


if __name__ == "__main__":
    unittest.main()
