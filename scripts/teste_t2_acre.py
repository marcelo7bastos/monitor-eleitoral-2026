"""Diagnóstico inicial do JSON oficial do TSE para Acre (T1/T2).
Python 3.9+, sem dependências externas.
Uso: python scripts/teste_t2_acre.py
"""
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

URL = "https://resultados.tse.jus.br/oficial/ele2026/6257/dados/ac/ac-c0001-e006257-u.json"
DESTINO = Path("tse_acre_6257.json")


def main():
    try:
        req = Request(URL, headers={"User-Agent": "MonitorEleitoral2026/0.1", "Accept": "application/json"})
        with urlopen(req, timeout=25) as response:
            raw = response.read()
            print("HTTP:", response.status)
            print("Content-Type:", response.headers.get("Content-Type"))
            if response.status != 200:
                return 1
    except (HTTPError, URLError, TimeoutError) as exc:
        print("FALHA DE CONEXAO:", exc)
        return 1

    try:
        dados = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        print("FALHA: resposta nao e JSON valido:", exc)
        return 1

    if not isinstance(dados, dict):
        print("FALHA: raiz do JSON nao e objeto")
        return 1

    print("Chaves da raiz:", ", ".join(sorted(dados)))
    for chave in ("ele", "uf", "abr", "cdabr", "car", "dg", "hg"):
        if chave in dados:
            valor = dados[chave]
            if chave == "car":
                print("car: lista com", len(valor) if isinstance(valor, list) else "formato inesperado", "itens")
            else:
                print(f"{chave}: {valor}")
    for chave in ("e", "c", "a", "te", "tc", "ta", "v", "vap", "pvap", "vv"):
        if chave in dados:
            print(f"Campo {chave}: {dados[chave]}")

    for cargo in dados.get("car", []):
        if not isinstance(cargo, dict):
            continue
        print("Cargo:", cargo.get("nm"), "codigo:", cargo.get("cd"))
        for agrupamento in cargo.get("agr", []):
            for partido in agrupamento.get("par", []):
                for candidato in partido.get("cand", []):
                    nome = candidato.get("nm") or candidato.get("nmu")
                    if nome and ("LULA" in nome.upper() or "FLAVIO" in nome.upper() or "FLÁVIO" in nome.upper()):
                        print("Candidato encontrado:", json.dumps(candidato, ensure_ascii=False))

    DESTINO.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    print("JSON salvo em:", DESTINO.resolve())
    print("T1 parcialmente verificável; T2 requer mapeamento e conferência dos cinco indicadores.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
