"""Gera tabela de conferência contra os bytes oficiais já arquivados."""
import csv
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from monitor.indicadores import extrair

base = Path(__file__).resolve().parents[1]
linhas = []
for eleicao, turno in (("6257", "1"), ("6258", "2")):
    raw = (base / f"evidencias/tse_acre_{eleicao}.json").read_bytes()
    fonte = json.loads(raw)
    x = extrair(fonte, eleicao, turno)
    atual = json.loads((base / f"dados/acre_{eleicao}.json").read_text(encoding="utf-8"))
    assert atual["sha256"] == hashlib.sha256(raw).hexdigest(), "Fonte mudou: arquivar nova versão antes de comparar"
    for nome, chave in (("comparecimento", "c"), ("abstencao", "a"), ("eleitorado_apto", "te")):
        oficial = fonte["e"][chave]
        assert int(oficial) == x[nome]
        linhas.append([eleicao, turno, "AC", nome, f"e.{chave}", "pessoas", oficial, str(x[nome]), "exato", x["data_fonte"], x["hora_fonte"], atual["sha256"]])
    for nome in ("lula", "flavio"):
        c = x["candidatos"][nome]
        linhas.append([eleicao, turno, "AC", f"percentual_{nome}", "carg[].agr[].par[].cand[].pvap", "percentual 0..100", str(c["percentual_tse"]), str(c["percentual_tse"]), "conferido com votos/v.vvc quando denominador > 0", x["data_fonte"], x["hora_fonte"], atual["sha256"]])
with (base / "evidencias/indicadores_acre.csv").open("w", newline="", encoding="utf-8-sig") as f:
    w=csv.writer(f, delimiter=";")
    w.writerow(["eleicao", "turno", "uf", "indicador", "campo", "unidade", "tse", "python", "conferencia", "data_fonte", "hora_fonte", "sha256"])
    w.writerows(linhas)
print(f"{len(linhas)} indicadores conferidos nos snapshots oficiais dos dois turnos")
