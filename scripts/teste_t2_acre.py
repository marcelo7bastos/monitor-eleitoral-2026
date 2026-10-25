"""Validação T1 do JSON do TSE. Python 3.9+, sem dependências externas."""
import argparse
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def validar_identidade(dados, eleicao, turno):
    if not isinstance(dados, dict):
        raise ValueError("Raiz deve ser objeto JSON")
    for campo, esperado in {"ele": eleicao, "t": turno, "tpabr": "uf", "cdabr": "ac"}.items():
        if dados.get(campo) != esperado:
            raise ValueError(f"{campo}: esperado {esperado!r}, recebido {dados.get(campo)!r}")
    cargos = dados.get("carg")
    if not isinstance(cargos, list) or len(cargos) != 1:
        raise ValueError("Esperado exatamente um cargo em carg")
    cargo = cargos[0]
    if not isinstance(cargo, dict) or cargo.get("cd") != "1" or cargo.get("nmn") != "Presidente":
        raise ValueError("Cargo deve ser 1 / Presidente")
    for campo in ("dg", "hg"):
        if not isinstance(dados.get(campo), str) or not dados[campo]:
            raise ValueError(f"Data/hora da fonte ausente: {campo}")
    return {"eleicao": dados["ele"], "turno": dados["t"], "tipo_abrangencia": dados["tpabr"],
            "uf": dados["cdabr"], "cargo_codigo": cargo["cd"], "cargo_nome": cargo["nmn"],
            "data_fonte": dados["dg"], "hora_fonte": dados["hg"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eleicao", choices=("6257", "6258"), default="6257")
    parser.add_argument("--turno", choices=("1", "2"), default="1")
    parser.add_argument("--saida", type=Path, default=Path("evidencias"))
    args = parser.parse_args()
    url = (f"https://resultados.tse.jus.br/oficial/ele2026/{args.eleicao}/dados/ac/"
           f"ac-c0001-e{int(args.eleicao):06d}-u.json")
    relatorio = {"coleta_utc": datetime.now(timezone.utc).isoformat(), "url": url,
                 "python": platform.python_version(), "aprovado": False}
    args.saida.mkdir(parents=True, exist_ok=True)
    destino = args.saida / f"tse_acre_{args.eleicao}.json"
    try:
        req = Request(url, headers={"User-Agent": "MonitorEleitoral2026/0.2", "Accept": "application/json"})
        with urlopen(req, timeout=25) as resposta:
            raw = resposta.read()
            relatorio.update(http=resposta.status, url_final=resposta.url,
                             content_type=resposta.headers.get("Content-Type"))
            if resposta.status != 200:
                raise ValueError(f"HTTP inesperado: {resposta.status}")
        dados = json.loads(raw)
        relatorio["identidade"] = validar_identidade(dados, args.eleicao, args.turno)
        destino.write_bytes(raw)
        relatorio.update(aprovado=True, sha256=hashlib.sha256(raw).hexdigest(),
                         bytes=len(raw), arquivo=destino.name)
    except (HTTPError, URLError, TimeoutError, ValueError, OSError) as exc:
        relatorio["erro"] = str(exc)
        if isinstance(exc, HTTPError):
            relatorio["http"] = exc.code
    texto = json.dumps(relatorio, ensure_ascii=False, indent=2)
    (args.saida / f"validacao_t1_{args.eleicao}.json").write_text(texto + "\n", encoding="utf-8")
    print(texto)
    return 0 if relatorio["aprovado"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
