"""Equivalência matemática com Planilha1!I:N; sem arredondamento intermediário."""
from decimal import Decimal, InvalidOperation

ROTULOS = {"I": "TAXA DE PRESENÇA", "J": "LULA — ESTIMATIVA", "K": "FLÁVIO — ESTIMATIVA", "L": "PRESENTES ESTIMADOS"}


def numero(valor):
    if valor is None or isinstance(valor, bool):
        raise ValueError("Valor numérico ausente ou inválido")
    try:
        n = Decimal(str(valor).replace(",", "."))
    except InvalidOperation as exc:
        raise ValueError("Valor numérico inválido") from exc
    if not n.is_finite():
        raise ValueError("Valor não finito")
    return n


def calcular_linha(lula, flavio, comparecimento, abstencao, aptos):
    """D/E são frações 0..1; F/G/H são quantidades, não percentuais.

    Ausência e denominador zero retornam indisponível, nunca um zero inventado.
    Nenhuma fórmula foi ajustada para descontar votos brancos/nulos.
    """
    if any(v is None for v in (lula, flavio, comparecimento, abstencao, aptos)):
        return {"status": "indisponivel", "motivo": "entrada_ausente", "I": None, "J": None, "K": None, "L": None}
    d, e, f, g, h = map(numero, (lula, flavio, comparecimento, abstencao, aptos))
    if not (0 <= d <= 1 and 0 <= e <= 1) or d + e > Decimal("1.00000000001"):
        raise ValueError("Percentuais devem ser frações 0..1 e somar no máximo 1")
    if min(f, g, h) < 0 or any(n != n.to_integral_value() for n in (f, g, h)):
        raise ValueError("Comparecimento, abstenção e aptos devem ser inteiros não negativos")
    if f + g > h:
        raise ValueError("Comparecimento + abstenção excede eleitorado apto")
    if f + g == 0:
        return {"status": "indisponivel", "motivo": "sem_comparecimento_e_abstencao", "I": None, "J": None, "K": None, "L": None}
    i = f / (f + g)
    return {"status": "calculado", "motivo": "", "I": i, "J": h * i * d, "K": h * i * e, "L": h * i}


def consolidar(entradas):
    """Reproduz H30/J30:L30/M30:N30. Exige as 28 linhas, sem ignorar lacunas."""
    if len(entradas) != 28:
        return {"status": "indisponivel", "motivo": "exige_28_linhas"}
    linhas = [calcular_linha(*linha) for linha in entradas]
    if any(linha["status"] != "calculado" for linha in linhas):
        return {"status": "indisponivel", "motivo": "linha_indisponivel"}
    h = sum(numero(linha[4]) for linha in entradas)
    j, k, l = (sum(linha[col] for linha in linhas) for col in "JKL")
    if l == 0:
        return {"status": "indisponivel", "motivo": "denominador_nacional_zero"}
    return {"status": "calculado", "H30": h, "J30": j, "K30": k, "L30": l, "M30": j / l, "N30": k / l}
