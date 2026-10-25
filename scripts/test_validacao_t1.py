"""Testes de identidade: respostas reais e adulterações controladas."""
import copy
import json
import unittest
from pathlib import Path
from teste_t2_acre import validar_identidade

BASE = Path(__file__).resolve().parents[1] / "evidencias"


class IdentidadeTSE(unittest.TestCase):
    def setUp(self):
        self.dados = json.loads((BASE / "tse_acre_6257.json").read_bytes())

    def test_respostas_reais_dos_dois_turnos(self):
        for eleicao, turno in (("6257", "1"), ("6258", "2")):
            with self.subTest(eleicao=eleicao):
                dados = json.loads((BASE / f"tse_acre_{eleicao}.json").read_bytes())
                self.assertEqual(validar_identidade(dados, eleicao, turno)["cargo_nome"], "Presidente")

    def test_rejeita_identificadores_incorretos(self):
        for campo, valor in (("ele", "6258"), ("t", "2"), ("tpabr", "mun"), ("cdabr", "sp")):
            with self.subTest(campo=campo):
                dados = copy.deepcopy(self.dados)
                dados[campo] = valor
                with self.assertRaises(ValueError):
                    validar_identidade(dados, "6257", "1")

    def test_rejeita_cargo_incorreto(self):
        for campo, valor in (("cd", "3"), ("nmn", "Governador")):
            with self.subTest(campo=campo):
                dados = copy.deepcopy(self.dados)
                dados["carg"][0][campo] = valor
                with self.assertRaises(ValueError):
                    validar_identidade(dados, "6257", "1")

    def test_rejeita_objeto_vazio_raiz_invalida_e_cargos_ausentes(self):
        for dados in ({}, [], None, {**self.dados, "carg": None}, {**self.dados, "carg": []}):
            with self.subTest(dados_tipo=type(dados).__name__):
                with self.assertRaises(ValueError):
                    validar_identidade(dados, "6257", "1")

    def test_rejeita_data_hora_ausentes(self):
        for campo in ("dg", "hg"):
            dados = copy.deepcopy(self.dados)
            del dados[campo]
            with self.subTest(campo=campo), self.assertRaises(ValueError):
                validar_identidade(dados, "6257", "1")


if __name__ == "__main__":
    unittest.main()
