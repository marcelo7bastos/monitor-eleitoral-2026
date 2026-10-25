import copy
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path
from urllib.error import URLError, HTTPError
from monitor.atualizacao import atualizar
from monitor.pipeline import executar, UFS
from monitor.calculos import ROTULOS

BASE = Path(__file__).resolve().parents[1]
ORIGINAL = json.loads((BASE / "evidencias/tse_acre_6257.json").read_bytes())


class Resposta(io.BytesIO):
    status = 200


def resposta(req, timeout=25):
    d = copy.deepcopy(ORIGINAL)
    d["cdabr"] = req.full_url.split("/dados/")[1].split("/")[0]
    return Resposta(json.dumps(d).encode())


class Falhas(unittest.TestCase):
    def test_matriz_preserva_dados_e_sinaliza_falha(self):
        for tipo in ("timeout", "dns", "http", "json", "ausente", "identidade"):
            with self.subTest(tipo=tipo), tempfile.TemporaryDirectory(dir=BASE / "tests") as pasta:
                pasta = Path(pasta)
                atualizar("6257", pasta, abrir=resposta)
                antes = (pasta / "acre_6257.json").read_bytes()
                def falhar(req, timeout=25):
                    if tipo == "timeout": raise TimeoutError("teste")
                    if tipo == "dns": raise URLError("teste DNS")
                    if tipo == "http": raise HTTPError(req.full_url, 503, "teste", {}, None)
                    if tipo == "json": return Resposta(b"<html>erro</html>")
                    d = copy.deepcopy(ORIGINAL)
                    if tipo == "ausente": del d["e"]["c"]
                    if tipo == "identidade": d["cdabr"] = "sp"
                    return Resposta(json.dumps(d).encode())
                self.assertEqual(atualizar("6257", pasta, abrir=falhar)["status"], "erro")
                self.assertEqual((pasta / "acre_6257.json").read_bytes(), antes)
                estado = json.loads((pasta / "estado_ac_6257.json").read_text())
                self.assertTrue(estado["desatualizado"])
                self.assertEqual(estado["motivo"], "falha_coleta")
                self.assertIsNotNone(estado["ultima_coleta_valida_utc"])

    def test_fonte_antiga_sinalizada_sem_apagar(self):
        with tempfile.TemporaryDirectory(dir=BASE / "tests") as pasta:
            pasta = Path(pasta)
            atualizar("6257", pasta, abrir=resposta, max_idade_minutos=0)
            estado = json.loads((pasta / "estado_ac_6257.json").read_text())
            self.assertTrue(estado["desatualizado"])
            self.assertEqual(estado["motivo"], "fonte_antiga")
            self.assertTrue((pasta / "acre_6257.json").exists())

    def test_conjunto_28_e_falha_parcial_nao_substitui(self):
        with tempfile.TemporaryDirectory(dir=BASE / "tests") as pasta:
            pasta = Path(pasta)
            x = executar("6257", pasta, abrir=resposta)
            self.assertEqual(x["aceitas_nesta_tentativa"], 28)
            alvo = pasta / "conjunto_6257.json"
            antes = alvo.read_bytes()
            csv_antes = (pasta / "conjunto_6257.csv").read_bytes()
            d = json.loads(antes)
            self.assertEqual({r["oficial"]["uf"] for r in d["abrangencias"]}, set(UFS))
            self.assertEqual(d["rotulos"]["L"], "PRESENTES ESTIMADOS")
            def uma_falha(req, timeout=25):
                if "/dados/sp/" in req.full_url: raise TimeoutError("SP fictícia")
                return resposta(req)
            x = executar("6257", pasta, abrir=uma_falha)
            self.assertEqual(x["status"], "erro")
            self.assertEqual(x["falhas"], ["SP"])
            self.assertTrue(x["desatualizado"] and x["conjunto_preservado"])
            self.assertEqual(alvo.read_bytes(), antes)
            self.assertEqual((pasta / "conjunto_6257.csv").read_bytes(), csv_antes)
            with (pasta / "abrangencias/logs/atualizacoes.csv").open(encoding="utf-8-sig", newline="") as f:
                self.assertEqual(len(list(csv.DictReader(f, delimiter=";"))), 56)

    def test_sem_conjunto_anterior_nao_inventa_dados(self):
        with tempfile.TemporaryDirectory(dir=BASE / "tests") as pasta:
            def falha(*a, **kw): raise TimeoutError("teste")
            pasta = Path(pasta)
            x = executar("6257", pasta, abrir=falha)
            self.assertFalse(x["conjunto_disponivel"])
            self.assertTrue(x["desatualizado"])
            self.assertFalse((pasta / "conjunto_6257.json").exists())


if __name__ == "__main__":
    unittest.main()
