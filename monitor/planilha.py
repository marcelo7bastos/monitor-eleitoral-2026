"""Exporta o conjunto no leiaute da Planilha1 (A1:N30), com fórmulas vivas; só biblioteca padrão.

As fórmulas de I:L e da linha 30 são as da planilha de referência, sem ajuste.
Fração indisponível vira #N/A em D/E, para que J/K não mostrem zero inventado.
"""
import io
import zipfile
from decimal import Decimal
from xml.sax.saxutils import escape

# Ordem, nomes e códigos exatamente como na planilha de referência.
LINHAS = (("Acre", 12, "AC"), ("Alagoas", 27, "AL"), ("Amapá", 16, "AP"), ("Amazonas", 13, "AM"),
          ("Bahia", 29, "BA"), ("Ceará", 23, "CE"), ("Distrito Federal", 53, "DF"), ("Espírito Santo", 32, "ES"),
          ("Exterior", 99, "ZZ"), ("Goiás", 52, "GO"), ("Maranhão", 21, "MA"), ("Mato Grosso", 51, "MT"),
          ("Mato Grosso do Sul", 50, "MS"), ("Minas Gerais", 31, "MG"), ("Paraná", 41, "PR"), ("Paraíba", 25, "PB"),
          ("Pará", 15, "PA"), ("Pernambuco", 26, "PE"), ("Piauí", 22, "PI"), ("Rio de Janeiro", 33, "RJ"),
          ("Rio Grande do Norte", 24, "RN"), ("Rio Grande do Sul", 43, "RS"), ("Rondônia", 11, "RO"),
          ("Roraima", 14, "RR"), ("Santa Catarina", 42, "SC"), ("Sergipe", 28, "SE"), ("São Paulo", 35, "SP"),
          ("Tocantins", 17, "TO"))
CABECALHO = ["Nome_UF", "UF", "", "LULA", "FLAVIO", "COMPARECIMENTO", "ABSTENÇÃO", "ELEITORADO APTO",
             "TAXA DE PRESENÇA", "LULA — ESTIMATIVA", "FLÁVIO — ESTIMATIVA", "PRESENTES ESTIMADOS", "", ""]
AUDITORIA = ["eleicao", "turno", "status_estimativa", "votos_lula_oficial", "votos_flavio_oficial",
             "votos_concorrentes", "secoes_totalizadas", "secoes_total", "data_fonte", "hora_fonte",
             "coleta_utc", "fonte", "sha256"]
# Estilos: 0 padrão, 1 negrito, 2 0,00%, 3 #.##0,00, 4 #.##0, 5 0,000000%
PCT, DEC, INT, FRAC = 2, 3, 4, 5
NA, DIV0 = "#N/A", "#DIV/0!"


def coluna(i):
    s = ""
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def celula(ref, valor=None, formula=None, estilo=0):
    s = f' s="{estilo}"' if estilo else ""
    if isinstance(valor, str) and valor in (NA, DIV0):
        cache = f"<v>{valor}</v>"
        return f'<c r="{ref}"{s} t="e">' + (f"<f>{escape(formula)}</f>" if formula else "") + cache + "</c>"
    if formula:
        return f'<c r="{ref}"{s}><f>{escape(formula)}</f>' + (f"<v>{valor}</v>" if valor is not None else "") + "</c>"
    if valor is None or valor == "":
        return f'<c r="{ref}"{s}/>' if estilo else ""
    if isinstance(valor, (int, float, Decimal)) and not isinstance(valor, bool):
        return f'<c r="{ref}"{s}><v>{valor}</v></c>'
    return f'<c r="{ref}"{s} t="inlineStr"><is><t xml:space="preserve">{escape(str(valor))}</t></is></c>'


def planilha(linhas, larguras):
    cols = "".join(f'<col min="{i}" max="{i}" width="{w}" customWidth="1"/>' for i, w in enumerate(larguras, 1))
    corpo = "".join(f'<row r="{n}">{"".join(c)}</row>' for n, c in linhas)
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>'
            f'<cols>{cols}</cols><sheetData>{corpo}</sheetData></worksheet>')


def _div(a, b):
    return DIV0 if b == 0 else a / b


def _mul(*xs):
    for x in xs:
        if isinstance(x, str):
            return x
    r = Decimal(1)
    for x in xs:
        r *= x
    return r


def _soma(xs):
    for x in xs:
        if isinstance(x, str):
            return x
    return sum(xs, Decimal(0))


def estimativa(conjunto):
    por_uf = {r["oficial"]["uf"]: r for r in conjunto["abrangencias"]}
    if set(por_uf) != {uf for _, _, uf in LINHAS}:
        raise ValueError("Planilha exige as 28 abrangências da referência")
    linhas = [(1, [celula(coluna(i) + "1", t, estilo=1) for i, t in enumerate(CABECALHO + AUDITORIA, 1)])]
    cache = {}
    for n, (nome, codigo, uf) in enumerate(LINHAS, 2):
        r = por_uf[uf]; d = r["oficial"]; e = r["estimativa_planilha"]
        fr = [d["candidatos"][c]["fracao_calculo"] for c in ("lula", "flavio")]
        D, E = (Decimal(str(x)) if x is not None else NA for x in fr)
        F, G, H = (Decimal(d[c]) for c in ("comparecimento", "abstencao", "eleitorado_apto"))
        I = _div(F, F + G); L = _mul(H, I); J = _mul(H, I, D); K = _mul(H, I, E)
        cache[n] = {"H": H, "J": J, "K": K, "L": L}
        c = [celula(f"A{n}", nome), celula(f"B{n}", codigo), celula(f"C{n}", uf),
             celula(f"D{n}", D, estilo=FRAC), celula(f"E{n}", E, estilo=FRAC),
             celula(f"F{n}", F, estilo=INT), celula(f"G{n}", G, estilo=INT), celula(f"H{n}", H, estilo=INT),
             celula(f"I{n}", I, f"F{n}/SUM(F{n}:G{n})", PCT), celula(f"J{n}", J, f"H{n}*I{n}*D{n}", DEC),
             celula(f"K{n}", K, f"H{n}*I{n}*E{n}", DEC), celula(f"L{n}", L, f"H{n}*I{n}", DEC)]
        if n == 28: c.append(celula("M28", "resultado final", estilo=1))
        if n == 29: c += [celula("M29", "% LULA", estilo=1), celula("N29", "% FLAVIO", estilo=1)]
        aud = [conjunto["eleicao"], d["turno"], e["status"], d["candidatos"]["lula"]["votos"],
               d["candidatos"]["flavio"]["votos"], d["votos_concorrentes"], d["secoes_totalizadas"],
               d["secoes_total"], d["data_fonte"], d["hora_fonte"], r["coleta_utc"], r["fonte"], r["sha256"]]
        c += [celula(coluna(15 + i) + str(n), v) for i, v in enumerate(aud)]
        linhas.append((n, c))
    tot = {k: _soma([cache[n][k] for n in cache]) for k in "HJKL"}
    M = tot["L"] if isinstance(tot["L"], str) else _div(tot["J"], tot["L"]) if not isinstance(tot["J"], str) else tot["J"]
    N = tot["L"] if isinstance(tot["L"], str) else _div(tot["K"], tot["L"]) if not isinstance(tot["K"], str) else tot["K"]
    linhas.append((30, [celula("A30", "Brasil (27 UFs + exterior)", estilo=1),
                        celula("H30", tot["H"], "SUM(H2:H29)", INT), celula("J30", tot["J"], "SUM(J2:J29)", DEC),
                        celula("K30", tot["K"], "SUM(K2:K29)", DEC), celula("L30", tot["L"], "SUM(L2:L29)", DEC),
                        celula("M30", M, "J30/L30", PCT), celula("N30", N, "K30/L30", PCT),
                        celula("O30", conjunto["eleicao"]), celula("Y30", conjunto["coleta_utc"])]))
    return planilha(linhas, [20, 7, 5, 12, 12, 16, 14, 17, 15, 20, 20, 20, 15, 12] + [10, 7, 16, 17, 17, 17, 16, 13, 12, 10, 32, 70, 66])


def leia_me(conjunto):
    textos = ["Monitor Eleitoral 2026 — projeto pessoal e independente; não é publicação do TSE.",
              f"Eleição {conjunto['eleicao']} · coleta UTC {conjunto['coleta_utc']}.",
              "Aba Estimativa: leiaute e fórmulas da planilha de referência (I = F/SOMA(F:G); J = H*I*D; K = H*I*E; L = H*I; linha 30 = somas; M30 = J30/L30; N30 = K30/L30).",
              "D e E são frações oficiais do TSE (cand.pvapn / 100); F, G e H são quantidades oficiais (e.c, e.a, e.te).",
              "As fórmulas recalculam ao abrir; altere D:H para simular cenários sem afetar o painel.",
              "L = PRESENTES ESTIMADOS: não desconta brancos e nulos. M30 e N30 não somam 100% e não equivalem ao percentual oficial de votos válidos.",
              "A estimativa extrapola a participação observada para o eleitorado; não é resultado oficial nem previsão probabilística.",
              "#DIV/0! = sem comparecimento nem abstenção informados (sem apuração). #N/A = fração do candidato ainda não divulgada; nenhum zero é inventado.",
              "Colunas O em diante: dados de auditoria do CSV (fonte, horário, coleta, sha256) e votos oficiais."]
    return planilha([(i, [celula(f"A{i}", t, estilo=1 if i == 1 else 0)]) for i, t in enumerate(textos, 1)], [140])


ESTILOS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
           '<numFmts count="1"><numFmt numFmtId="164" formatCode="0.000000%"/></numFmts>'
           '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
           '<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>'
           '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
           '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
           '<cellXfs count="6"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
           '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>'
           '<xf numFmtId="10" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>'
           '<xf numFmtId="4" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>'
           '<xf numFmtId="3" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>'
           '<xf numFmtId="164" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/></cellXfs>'
           '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>')


def gerar_xlsx(conjunto):
    abas = [("Estimativa", estimativa(conjunto)), ("Leia-me", leia_me(conjunto))]
    tipos = "".join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' for i in range(1, len(abas) + 1))
    arquivos = {
        "[Content_Types].xml": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>' + tipos + '</Types>',
        "_rels/.rels": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        "xl/workbook.xml": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
            + "".join(f'<sheet name="{n}" sheetId="{i}" r:id="rId{i}"/>' for i, (n, _) in enumerate(abas, 1)) + '</sheets><calcPr calcId="191029" fullCalcOnLoad="1"/></workbook>',
        "xl/_rels/workbook.xml.rels": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            + "".join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>' for i in range(1, len(abas) + 1))
            + f'<Relationship Id="rId{len(abas) + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>',
        "xl/styles.xml": ESTILOS}
    for i, (_, xml) in enumerate(abas, 1):
        arquivos[f"xl/worksheets/sheet{i}.xml"] = xml
    saida = io.BytesIO()
    with zipfile.ZipFile(saida, "w", zipfile.ZIP_DEFLATED) as z:
        for nome, xml in arquivos.items():
            z.writestr(zipfile.ZipInfo(nome, (2026, 1, 1, 0, 0, 0)), xml.encode("utf-8"), zipfile.ZIP_DEFLATED)
    return saida.getvalue()
