"""Mapeamento EA20/2026, restrito a Presidente/Acre e às candidaturas verificadas."""
from decimal import Decimal
from .calculos import numero

CANDIDATOS = {"lula": ("13", "280002542548"), "flavio": ("22", "280002551544")}


def inteiro(valor):
    n = numero(valor)
    if n < 0 or n != n.to_integral_value():
        raise ValueError("Quantidade deve ser inteiro não negativo")
    return int(n)


def extrair(dados, eleicao, turno, uf="ac"):
    if not isinstance(dados, dict):
        raise ValueError("Raiz JSON deve ser objeto")
    for campo, esperado in {"ele": eleicao, "t": turno, "tpabr": "uf", "cdabr": uf.lower(), "f": "o"}.items():
        if dados.get(campo) != esperado:
            raise ValueError(f"Identidade incorreta: {campo}")
    cargos = dados.get("carg")
    if not isinstance(cargos, list) or len(cargos) != 1 or not isinstance(cargos[0], dict) or cargos[0].get("cd") != "1" or cargos[0].get("nmn") != "Presidente":
        raise ValueError("Cargo incorreto")
    e, s, v = (dados[chave] for chave in ("e", "s", "v"))
    aptos, presentes, ausentes = (inteiro(e[chave]) for chave in ("te", "c", "a"))
    instalados = inteiro(e["esi"])
    if presentes + ausentes > aptos or instalados > aptos or presentes + ausentes > instalados:
        raise ValueError("Totais de eleitorado inconsistentes")
    secoes, totalizadas = inteiro(s["ts"]), inteiro(s["st"])
    if totalizadas > secoes:
        raise ValueError("Seções totalizadas excedem total")
    denominador = inteiro(v["vvc"])
    total_votos = inteiro(v["tv"])
    if denominador > total_votos or total_votos != presentes:
        raise ValueError("Total de votos incompatível com comparecimento")
    soma_votos = sum(inteiro(v[chave]) for chave in ("vb", "vn", "vnt", "van", "vansj", "vv"))
    if soma_votos != total_votos:
        raise ValueError("Composição do total de votos inconsistente")
    def objetos(valor):
        if not isinstance(valor, list) or any(not isinstance(x, dict) for x in valor):
            raise ValueError("Estrutura de candidatos inválida")
        return valor
    candidatos = [c for a in objetos(cargos[0]["agr"]) for p in objetos(a["par"]) for c in objetos(p["cand"])]
    if sum(inteiro(c["vap"]) for c in candidatos) != denominador:
        raise ValueError("Soma de votos dos candidatos difere de vvc")
    saida = {"eleicao": eleicao, "turno": turno, "uf": uf.upper(), "comparecimento": presentes,
             "abstencao": ausentes, "eleitorado_apto": aptos, "secoes_totalizadas": totalizadas,
             "secoes_total": secoes, "cobertura_fracao": Decimal(totalizadas) / secoes if secoes else None,
             "votos_validos_oficiais": inteiro(v["vv"]), "votos_concorrentes": denominador,
             "idg": dados["idg"], "data_fonte": dados["dg"], "hora_fonte": dados["hg"],
             "data_totalizacao": dados.get("dt", ""), "hora_totalizacao": dados.get("ht", ""),
             "andamento": dados["and"], "divulga_votacao": dados["dv"], "candidatos": {}}
    for nome, (urna, sequencial) in CANDIDATOS.items():
        encontrados = [c for c in candidatos if c.get("n") == urna and c.get("sqcand") == sequencial]
        if len(encontrados) != 1:
            raise ValueError(f"Candidato ausente ou duplicado: {nome}")
        c = encontrados[0]
        pct, pct_tela, votos = numero(c["pvapn"]), numero(c["pvap"]), inteiro(c["vap"])
        if not 0 <= pct <= 100 or not 0 <= pct_tela <= 100 or votos > denominador:
            raise ValueError("Votação ou percentual inválido")
        if denominador:
            calculado = Decimal(votos) * 100 / denominador
            if abs(calculado - pct) > Decimal("0.00000000051") or abs(calculado - pct_tela) > Decimal("0.005000001"):
                raise ValueError(f"Percentual não confere com votos/vvc: {nome}")
        elif pct != 0 or pct_tela != 0 or votos != 0:
            raise ValueError("Percentual não zero sem votos concorrentes")
        saida["candidatos"][nome] = {"numero": urna, "sequencial": sequencial, "nome": c["nmu"],
                "votos": votos, "percentual_tse": pct_tela, "percentual_preciso_tse": pct,
                "fracao_calculo": pct / 100 if denominador and dados["dv"] == "s" else None,
                "denominador": "v.vvc", "base_fracao": "cand.pvapn / 100"}
    return saida
