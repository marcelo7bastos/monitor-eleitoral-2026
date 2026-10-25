"""Coleta manual completa: 27 UFs + ZZ. Aceitação atômica do conjunto."""
import argparse
import csv
import io
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
from .atualizacao import atualizar, atomico, json_texto
from .calculos import consolidar, ROTULOS

UFS = tuple("AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO ZZ".split())


def executar(eleicao="6258", pasta=Path("dados"), abrir=urlopen):
    pasta.mkdir(parents=True, exist_ok=True)
    lock = pasta / "pipeline.lock"
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.close(fd)
    try:
        return _executar(eleicao, pasta, abrir)
    finally:
        lock.unlink()


def _executar(eleicao, pasta, abrir):
    eventos = [atualizar(eleicao, pasta / "abrangencias", abrir=abrir, uf=uf) for uf in UFS]
    falhas = [e["uf"] for e in eventos if e["status"] == "erro"]
    alvo = pasta / f"conjunto_{eleicao}.json"
    anterior = json.loads(alvo.read_text(encoding="utf-8")) if alvo.exists() else None
    agora = datetime.now(timezone.utc).isoformat()
    if not falhas:
        registros = []
        for uf in UFS:
            nome = "acre" if uf == "AC" else uf.lower()
            registros.append(json.loads((pasta / "abrangencias" / f"{nome}_{eleicao}.json").read_text(encoding="utf-8")))
        assert len(registros) == 28 and {r["oficial"]["uf"] for r in registros} == set(UFS)
        entradas = [[r["oficial"]["candidatos"][n]["fracao_calculo"] for n in ("lula", "flavio")] +
                    [r["oficial"][c] for c in ("comparecimento", "abstencao", "eleitorado_apto")] for r in registros]
        conjunto = {"eleicao": eleicao, "coleta_utc": agora, "rotulos": ROTULOS,
                    "abrangencias": registros, "consolidado_planilha": consolidar(entradas)}
        texto = io.StringIO(newline="")
        w = csv.writer(texto, delimiter=";")
        w.writerow(["uf", "eleicao", "turno", "comparecimento", "abstencao", "eleitorado_apto", "fracao_lula", "fracao_flavio", "presentes_estimados", "status_estimativa", "data_fonte", "hora_fonte", "coleta_utc", "fonte", "sha256"])
        for r in registros:
            d = r["oficial"]
            w.writerow([d["uf"], eleicao, d["turno"], d["comparecimento"], d["abstencao"], d["eleitorado_apto"],
                        d["candidatos"]["lula"]["fracao_calculo"], d["candidatos"]["flavio"]["fracao_calculo"],
                        r["estimativa_planilha"]["L"], r["estimativa_planilha"]["status"], d["data_fonte"], d["hora_fonte"], r["coleta_utc"], r["fonte"], r["sha256"]])
        # O JSON é o conjunto autoritativo; CSV é uma exportação derivada dele.
        atomico(pasta / f"conjunto_{eleicao}.csv", texto.getvalue().encode("utf-8-sig"))
        atomico(alvo, json_texto(conjunto).encode("utf-8"))
        anterior = conjunto
    antigas = [e["uf"] for e in eventos if e.get("fonte_antiga") == 1]
    estado = {"eleicao": eleicao, "ultima_tentativa_utc": agora,
              "ultima_coleta_valida_utc": anterior["coleta_utc"] if anterior else None,
              "conjunto_disponivel": anterior is not None, "conjunto_preservado": bool(falhas and anterior),
              "status": "erro" if falhas else "sucesso", "esperadas": 28, "aceitas_nesta_tentativa": 28 - len(falhas),
              "falhas": falhas, "fontes_antigas": antigas, "desatualizado": bool(falhas or antigas),
              "aviso": "Falha na coleta; exibindo último conjunto válido." if falhas else "Fonte com horário antigo; não interpretar como apuração atual." if antigas else "",
              "consolidacao": anterior["consolidado_planilha"]["status"] if anterior else "indisponivel"}
    atomico(pasta / f"estado_conjunto_{eleicao}.json", json_texto(estado).encode("utf-8"))
    return estado


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--eleicao", choices=("6257", "6258"), default="6258")
    p.add_argument("--pasta", type=Path, default=Path("dados"))
    args = p.parse_args()
    resultado = executar(args.eleicao, args.pasta)
    print(json_texto(resultado))
    return 1 if resultado["status"] == "erro" else 0


if __name__ == "__main__":
    raise SystemExit(main())
