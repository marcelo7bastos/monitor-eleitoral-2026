import copy
import csv
import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from urllib.error import URLError

from monitor.calculos import calcular_linha, consolidar
from monitor.indicadores import extrair
from monitor.atualizacao import atualizar

BASE = Path(__file__).resolve().parents[1]


class Indicadores(unittest.TestCase):
    def setUp(self):
        self.dados = json.loads((BASE / "evidencias/tse_acre_6257.json").read_bytes())

    def test_cinco_valores_reais_conferem_com_snapshot(self):
        x = extrair(self.dados, "6257", "1")
        self.assertEqual((x["comparecimento"], x["abstencao"], x["eleitorado_apto"]), (488330, 125412, 613742))
        self.assertEqual(x["candidatos"]["lula"]["percentual_tse"], Decimal("28.73"))
        self.assertEqual(x["candidatos"]["flavio"]["percentual_tse"], Decimal("64.56"))
        self.assertEqual(x["candidatos"]["lula"]["fracao_calculo"], Decimal("0.28731564428"))
        self.assertEqual(x["cobertura_fracao"], 1)

    def test_segundo_turno_zerado_nao_produz_estimativa(self):
        dados = json.loads((BASE / "evidencias/tse_acre_6258.json").read_bytes())
        x = extrair(dados, "6258", "2")
        self.assertEqual(x["cobertura_fracao"], 0)
        self.assertEqual(x["eleitorado_apto"], 613715)
        self.assertIsNone(x["candidatos"]["lula"]["fracao_calculo"])

    def test_rejeita_percentual_divergente(self):
        self.dados["carg"][0]["agr"][0]["par"][0]["cand"][0]["pvapn"] = "99"
        with self.assertRaises(ValueError): extrair(self.dados, "6257", "1")

    def test_identidade_nao_depende_do_nome(self):
        self.dados["carg"][0]["agr"][0]["par"][0]["cand"][0]["nmu"] = "Nome alterado"
        self.assertEqual(extrair(self.dados, "6257", "1")["candidatos"]["flavio"]["numero"], "22")

    def test_rejeita_duplicado_e_campo_ausente(self):
        dados = copy.deepcopy(self.dados)
        lista = dados["carg"][0]["agr"][0]["par"][0]["cand"]
        lista.append(copy.deepcopy(lista[0]))
        with self.assertRaises(ValueError): extrair(dados, "6257", "1")
        del self.dados["e"]["c"]
        with self.assertRaises(KeyError): extrair(self.dados, "6257", "1")

    def test_nao_exige_apuracao_total(self):
        self.dados["s"]["st"] = "1"
        self.assertLess(extrair(self.dados, "6257", "1")["cobertura_fracao"], 1)


class Calculos(unittest.TestCase):
    def test_exemplo_manual_independente(self):
        x = calcular_linha("0.4", "0.6", 80, 20, 100)
        self.assertEqual([x[c] for c in "IJKL"], [Decimal("0.8"), 32, 48, 80])
        total = consolidar([["0.4", "0.6", 80, 20, 100]] * 28)
        self.assertEqual((total["J30"], total["L30"], total["M30"]), (896, 2240, Decimal("0.4")))

    def test_ausencia_nao_vira_zero(self):
        self.assertEqual(calcular_linha(None, "0.6", 80, 20, 100)["motivo"], "entrada_ausente")
        self.assertEqual(calcular_linha(0, 1, 80, 20, 100)["J"], 0)

    def test_denominador_zero(self):
        self.assertEqual(calcular_linha(0, 0, 0, 0, 100)["status"], "indisponivel")
        self.assertEqual(consolidar([[0, 0, 0, 100, 100]] * 28)["motivo"], "denominador_nacional_zero")

    def test_entradas_invalidas(self):
        for linha in ([40, 60, 80, 20, 100], ["NaN", 0, 80, 20, 100], [0, 1, -1, 20, 100],
                      [0, 1, 100, 20, 100], [0, 1, 1.5, 20, 100], [True, 0, 80, 20, 100]):
            with self.subTest(linha=linha), self.assertRaises(ValueError): calcular_linha(*linha)

    def test_nacional_nao_ignora_lacunas(self):
        self.assertEqual(consolidar([[0, 1, 80, 20, 100]])["status"], "indisponivel")
        linhas = [[0, 1, 80, 20, 100]] * 27 + [[None, 1, 80, 20, 100]]
        self.assertEqual(consolidar(linhas)["status"], "indisponivel")

    def test_peso_nacional_nao_e_media_simples(self):
        linhas = [[1, 0, 100, 0, 100]] + [[0, 1, 10, 0, 10]] * 27
        self.assertEqual(consolidar(linhas)["M30"], Decimal(100) / 370)


class Atualizacoes(unittest.TestCase):
    def test_historico_sem_mudanca_e_falha_preservam_dados(self):
        with tempfile.TemporaryDirectory(dir=BASE / "tests") as d:
            pasta = Path(d)
            entrada = BASE / "evidencias/tse_acre_6257.json"
            self.assertEqual(atualizar("6257", pasta, entrada)["status"], "atualizado")
            alvo = pasta / "acre_6257.json"; antes = alvo.read_bytes()
            self.assertEqual(atualizar("6257", pasta, entrada)["status"], "sem_alteracao")
            self.assertEqual(json.loads(alvo.read_bytes())["oficial"], json.loads(antes)["oficial"])
            antes = alvo.read_bytes()
            ruim = pasta / "ruim.json"; ruim.write_text("{}")
            self.assertEqual(atualizar("6257", pasta, ruim)["status"], "erro")
            self.assertEqual(alvo.read_bytes(), antes)
            with (pasta / "logs/atualizacoes.csv").open(encoding="utf-8-sig", newline="") as f:
                rows = list(csv.DictReader(f, delimiter=";"))
            self.assertEqual(len(rows), 3)
            self.assertEqual([r["status"] for r in rows], ["atualizado", "sem_alteracao", "erro"])
            self.assertEqual([r["mudou"] for r in rows[:2]], ["1", "0"])
            for row in rows:
                self.assertRegex(row["data_local"], r"^\d{4}-\d{2}-\d{2}$")
                self.assertRegex(row["hora_local"], r"^\d{2}:\d{2}:\d{2}$")
                self.assertRegex(row["minuto_local"], r"^\d{2}:\d{2}$")
                self.assertIn("-03:00", row["fuso"])

    def test_falha_de_rede_fica_no_log(self):
        def falha(*args, **kwargs): raise URLError("DNS de teste")
        with tempfile.TemporaryDirectory(dir=BASE / "tests") as d:
            evento = atualizar("6258", Path(d), abrir=falha)
            self.assertEqual(evento["status"], "erro")
            self.assertIn("DNS de teste", evento["erro"])
            self.assertFalse((Path(d) / "acre_6258.json").exists())

    def test_rejeita_snapshot_regressivo(self):
        with tempfile.TemporaryDirectory(dir=BASE / "tests") as d:
            pasta = Path(d)
            entrada = BASE / "evidencias/tse_acre_6257.json"
            atualizar("6257", pasta, entrada)
            antes = (pasta / "acre_6257.json").read_bytes()
            dados = json.loads(entrada.read_bytes()); dados["dg"] = "04/10/2026"
            velho = pasta / "velho.json"; velho.write_text(json.dumps(dados), encoding="utf-8")
            evento = atualizar("6257", pasta, velho)
            self.assertEqual(evento["status"], "erro")
            self.assertIn("anterior", evento["erro"])
            self.assertEqual((pasta / "acre_6257.json").read_bytes(), antes)


if __name__ == "__main__":
    unittest.main()

