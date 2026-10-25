"""Uma coleta manual do Acre, com histórico de atualização em tabela CSV."""
import argparse
import csv
import hashlib
import json
import os
import tempfile
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from .calculos import calcular_linha, ROTULOS
from .indicadores import extrair

FUSO = timezone(timedelta(hours=-3), "America/Sao_Paulo")
COLUNAS = ("id", "inicio_utc", "fim_utc", "data_local", "hora_local", "minuto_local", "fuso",
           "eleicao", "turno", "uf", "status", "http", "url", "data_fonte", "hora_fonte",
           "data_totalizacao", "hora_totalizacao", "idg", "sha256", "mudou", "fonte_antiga", "erro")


def json_texto(valor):
    return json.dumps(valor, ensure_ascii=False, indent=2, default=str) + "\n"


def atomico(destino, conteudo):
    destino.parent.mkdir(parents=True, exist_ok=True)
    fd, temporario = tempfile.mkstemp(dir=destino.parent, prefix=".tmp-")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(conteudo)
        os.replace(temporario, destino)
    finally:
        if os.path.exists(temporario):
            os.unlink(temporario)


def registrar(pasta, evento):
    """Histórico CSV com escrita atômica e exclusão mútua entre escritores locais."""
    pasta.mkdir(parents=True, exist_ok=True)
    lock = pasta / "atualizacoes.lock"
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.close(fd)
    try:
        arquivo = pasta / "atualizacoes.csv"
        rows = []
        if arquivo.exists():
            with arquivo.open(encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f, delimiter=";")
                if tuple(reader.fieldnames or ()) != COLUNAS:
                    raise ValueError("Cabeçalho do histórico não corresponde ao esquema esperado")
                rows = list(reader)
        rows.append({c: str(evento.get(c, "")) for c in COLUNAS})
        import io
        texto = io.StringIO(newline="")
        writer = csv.DictWriter(texto, fieldnames=COLUNAS, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
        atomico(arquivo, texto.getvalue().encode("utf-8-sig"))
    finally:
        lock.unlink()


def atualizar(eleicao="6258", pasta=Path("dados"), entrada=None, abrir=urlopen, max_idade_minutos=30, uf="ac"):
    turno = {"6257": "1", "6258": "2"}[eleicao]
    inicio = datetime.now(timezone.utc)
    evento = {"id": uuid.uuid4().hex, "inicio_utc": inicio.isoformat(), "eleicao": eleicao,
              "turno": turno, "uf": uf.upper(), "status": "erro", "fuso": "America/Sao_Paulo (UTC-03:00 em 2026)",
              "url": f"https://resultados.tse.jus.br/oficial/ele2026/{eleicao}/dados/{uf.lower()}/{uf.lower()}-c0001-e{int(eleicao):06d}-u.json"}
    alvo = pasta / f"{'acre' if uf.lower() == 'ac' else uf.lower()}_{eleicao}.json"
    try:
        if entrada is None:
            req = Request(evento["url"], headers={"User-Agent": "MonitorEleitoral2026/0.3", "Accept": "application/json"})
            with abrir(req, timeout=25) as r:
                evento["http"] = r.status
                if r.status != 200:
                    raise ValueError(f"HTTP inesperado: {r.status}")
                raw = r.read()
        else:
            evento["url"] = "arquivo_local:" + str(Path(entrada).resolve())
            raw = Path(entrada).read_bytes()
        hash_ = hashlib.sha256(raw).hexdigest()
        dados = extrair(json.loads(raw), eleicao, turno, uf)
        data_fonte = datetime.strptime(dados["data_fonte"] + " " + dados["hora_fonte"], "%d/%m/%Y %H:%M:%S")
        # Convenção operacional: interpretar o relógio da fonte em UTC-03:00.
        # O EA20 descreve o formato, mas não explicita o fuso; manter campos brutos.
        fonte = data_fonte.replace(tzinfo=FUSO)
        evento.update({k: dados[k] for k in ("data_fonte", "hora_fonte", "data_totalizacao", "hora_totalizacao", "idg")})
        evento.update(sha256=hash_, fonte_antiga=int((inicio - fonte).total_seconds() > max_idade_minutos * 60))
        anterior = json.loads(alvo.read_text(encoding="utf-8")) if alvo.exists() else {}
        if anterior and data_fonte < datetime.strptime(anterior["oficial"]["data_fonte"] + " " + anterior["oficial"]["hora_fonte"], "%d/%m/%Y %H:%M:%S"):
            raise ValueError("Resposta anterior ao último snapshot aceito")
        mudou = anterior.get("sha256") != hash_
        evento["mudou"] = int(mudou)
        estimativa = calcular_linha(dados["candidatos"]["lula"]["fracao_calculo"],
                                   dados["candidatos"]["flavio"]["fracao_calculo"],
                                   dados["comparecimento"], dados["abstencao"], dados["eleitorado_apto"])
        resultado = {"sha256": hash_, "coleta_utc": inicio.isoformat(), "fonte": evento["url"],
                     "oficial": dados, "estimativa_planilha": estimativa, "rotulos": ROTULOS,
                     "aviso": "Estimativa reproduz a planilha; não representa votação oficial. L estima presentes, sem descontar brancos/nulos."}
        atomico(pasta / "snapshots" / f"{hash_}.json", raw)
        # Registrar a coleta mais recente mesmo se o conteúdo oficial não mudou.
        atomico(alvo, json_texto(resultado).encode("utf-8"))
        evento["status"] = "atualizado" if mudou else "sem_alteracao"
    except (OSError, ValueError, KeyError, TypeError, ArithmeticError) as exc:
        evento["erro"] = f"{type(exc).__name__}: {exc}"
        evento["http"] = getattr(exc, "code", evento.get("http", ""))
    finally:
        fim = datetime.now(timezone.utc)
        local = fim.astimezone(FUSO)
        evento.update(fim_utc=fim.isoformat(), data_local=local.strftime("%Y-%m-%d"),
                      hora_local=local.strftime("%H:%M:%S"), minuto_local=local.strftime("%H:%M"))
        registrar(pasta / "logs", evento)
        ultimo = json.loads(alvo.read_text(encoding="utf-8")) if alvo.exists() else None
        estado = {"ultima_tentativa_utc": evento["fim_utc"], "ultima_coleta_valida_utc": ultimo.get("coleta_utc") if ultimo else None,
                  "desatualizado": evento["status"] == "erro" or evento.get("fonte_antiga") == 1,
                  "motivo": "falha_coleta" if evento["status"] == "erro" else "fonte_antiga" if evento.get("fonte_antiga") else "",
                  "erro": evento.get("erro", ""), "dados_disponiveis": ultimo is not None}
        atomico(pasta / f"estado_{uf.lower()}_{eleicao}.json", json_texto(estado).encode("utf-8"))
    return evento


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eleicao", choices=("6257", "6258"), default="6258")
    parser.add_argument("--pasta", type=Path, default=Path("dados"))
    parser.add_argument("--entrada", type=Path, help="Reprocessa JSON local; origem fica identificada no log")
    args = parser.parse_args()
    evento = atualizar(args.eleicao, args.pasta, args.entrada)
    print(json_texto(evento))
    return 1 if evento["status"] == "erro" else 0


if __name__ == "__main__":
    raise SystemExit(main())
