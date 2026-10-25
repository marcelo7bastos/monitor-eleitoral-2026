import copy
import io
import json
import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET
from decimal import Decimal
from pathlib import Path
from monitor.pipeline import executar
from monitor.planilha import LINHAS, gerar_xlsx
from monitor.publicacao import gerar
from test_resiliencia import Resposta, resposta, BASE

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
ZERADO = json.loads((BASE / "evidencias/tse_acre_6258.json").read_bytes())


def resposta_zerada(req, timeout=25):
    d = copy.deepcopy(ZERADO)
    d["cdabr"] = req.full_url.split("/dados/")[1].split("/")[0]
    return Resposta(json.dumps(d).encode())


def celulas(xlsx, aba=1):
    with zipfile.ZipFile(io.BytesIO(xlsx)) as z:
        raiz = ET.fromstring(z.read(f"xl/worksheets/sheet{aba}.xml"))
    saida = {}
    for c in raiz.iter("{%s}c" % NS["m"]):
        f, v, t = c.find("m:f", NS), c.find("m:v", NS), c.find("m:is/m:t", NS)
        saida[c.get("r")] = {"f": f.text if f is not None else None, "v": t.text if t is not None else v.text if v is not None else None, "t": c.get("t")}
    return saida


def conjunto(eleicao, abrir):
    with tempfile.TemporaryDirectory(dir=BASE / "tests") as t:
        executar(eleicao, Path(t), abrir=abrir)
        return json.loads((Path(t) / f"conjunto_{eleicao}.json").read_text(encoding="utf-8"))


class Planilha(unittest.TestCase):
    def test_formulas_vivas_identicas_a_referencia(self):
        c = celulas(gerar_xlsx(conjunto("6257", resposta)))
        for n in range(2, 30):
            self.assertEqual(c[f"I{n}"]["f"], f"F{n}/SUM(F{n}:G{n})")
            self.assertEqual(c[f"J{n}"]["f"], f"H{n}*I{n}*D{n}")
            self.assertEqual(c[f"K{n}"]["f"], f"H{n}*I{n}*E{n}")
            self.assertEqual(c[f"L{n}"]["f"], f"H{n}*I{n}")
        for ref, f in {"H30": "SUM(H2:H29)", "J30": "SUM(J2:J29)", "K30": "SUM(K2:K29)", "L30": "SUM(L2:L29)", "M30": "J30/L30", "N30": "K30/L30"}.items():
            self.assertEqual(c[ref]["f"], f)
        self.assertEqual([c[f"C{n}"]["v"] for n in range(2, 30)], [uf for _, _, uf in LINHAS])
        self.assertEqual((c["M28"]["v"], c["M29"]["v"], c["N29"]["v"]), ("resultado final", "% LULA", "% FLAVIO"))

    def test_valores_em_cache_conferem_com_python(self):
        dados = conjunto("6257", resposta)
        c = celulas(gerar_xlsx(dados))
        ac = next(r for r in dados["abrangencias"] if r["oficial"]["uf"] == "AC")
        self.assertEqual(Decimal(c["D2"]["v"]), Decimal(str(ac["oficial"]["candidatos"]["lula"]["fracao_calculo"])))
        self.assertEqual(int(c["H2"]["v"]), 613742)
        self.assertEqual(Decimal(c["L2"]["v"]), Decimal(str(ac["estimativa_planilha"]["L"])))
        for k in ("J30", "K30", "L30", "M30", "N30"):
            self.assertEqual(Decimal(c[k]["v"]), Decimal(str(dados["consolidado_planilha"][k])), k)
        self.assertEqual(c["Z2"]["v"], ac["fonte"])
        self.assertEqual(c["AA2"]["v"], ac["sha256"])

    def test_sem_apuracao_nao_inventa_zero(self):
        c = celulas(gerar_xlsx(conjunto("6258", resposta_zerada)))
        self.assertEqual((c["D2"]["t"], c["D2"]["v"]), ("e", "#N/A"))
        self.assertEqual((c["I2"]["t"], c["I2"]["v"]), ("e", "#DIV/0!"))
        self.assertEqual(c["J2"]["t"], "e")
        self.assertEqual(c["M30"]["t"], "e")
        self.assertEqual(c["Q2"]["v"], "indisponivel")

    def test_publicacao_entrega_xlsx_e_mantem_csv(self):
        with tempfile.TemporaryDirectory(dir=BASE / "tests") as t:
            dados, dist = Path(t) / "dados", Path(t) / "dist"
            executar("6257", dados, abrir=resposta)
            gerar(dados, dist, BASE / "site")
            self.assertTrue((dist / "data/conjunto_6257.csv").exists())
            with zipfile.ZipFile(dist / "data/conjunto_6257.xlsx") as z:
                self.assertIsNone(z.testzip())


if __name__ == "__main__":
    unittest.main()
