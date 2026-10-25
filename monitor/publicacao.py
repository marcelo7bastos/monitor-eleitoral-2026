"""Contrato público e histórico real do dashboard; não altera as fórmulas do modelo."""
import argparse
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from .atualizacao import atomico, json_texto
from .pipeline import UFS


def n(x):
    return Decimal(str(x)) if x is not None else None


def vista(registro):
    d=registro['oficial']; e=registro['estimativa_planilha']
    apurado=d['secoes_totalizadas']>0 and d['votos_concorrentes']>0 and d.get('divulga_votacao')=='s'
    valido=e['status']=='calculado'
    return {'uf':d['uf'],'aptos':d['eleitorado_apto'],'comparecimento':d['comparecimento'],
            'abstencao':d['abstencao'],'secoes':d['secoes_total'],'totalizadas':d['secoes_totalizadas'],
            'cobertura':n(d['cobertura_fracao'])*100 if d['cobertura_fracao'] is not None else None,
            'validos':d['votos_validos_oficiais'],'concorrentes':d['votos_concorrentes'],
            'apurado':apurado,'lula':n(d['candidatos']['lula']['percentual_preciso_tse']) if apurado else None,
            'flavio':n(d['candidatos']['flavio']['percentual_preciso_tse']) if apurado else None,
            'votos_lula':d['candidatos']['lula']['votos'] if apurado else None,
            'votos_flavio':d['candidatos']['flavio']['votos'] if apurado else None,
            'estimativa':{'lula':n(e['J'])/n(e['L'])*100 if valido and n(e['L']) else None,
                         'flavio':n(e['K'])/n(e['L'])*100 if valido and n(e['L']) else None,
                         'votos_lula':e['J'],'votos_flavio':e['K'],'presentes':e['L'],'taxa_presenca':e['I'],'status':e['status']},
            'data_fonte':d['data_fonte'],'hora_fonte':d['hora_fonte'],
            'data_totalizacao':d.get('data_totalizacao',''),'hora_totalizacao':d.get('hora_totalizacao',''),
            'coleta_utc':registro['coleta_utc'],'fonte':registro['fonte'],'sha256':registro['sha256'],'idg':d['idg'],
            'andamento':d['andamento']}


def compilar(conjunto):
    registros=conjunto['abrangencias']
    if len(registros)!=28 or {r['oficial']['uf'] for r in registros}!=set(UFS):
        raise ValueError('Conjunto público exige as 28 abrangências únicas')
    vistas={r['oficial']['uf']:vista(r) for r in registros}
    br={'uf':'BR'}
    for campo in ('aptos','comparecimento','abstencao','secoes','totalizadas','validos','concorrentes'):
        br[campo]=sum(v[campo] for v in vistas.values())
    br['apurado']=br['concorrentes']>0 and all(v['apurado'] or v['totalizadas']==0 for v in vistas.values())
    br['cobertura']=Decimal(br['totalizadas'])*100/br['secoes'] if br['secoes'] else None
    for nome in ('lula','flavio'):
        br['votos_'+nome]=sum(v['votos_'+nome] or 0 for v in vistas.values()) if br['apurado'] else None
        br[nome]=Decimal(br['votos_'+nome])*100/br['concorrentes'] if br['apurado'] else None
    e=conjunto['consolidado_planilha']; valido=e['status']=='calculado'
    br['estimativa']={'lula':n(e.get('M30'))*100 if valido else None,'flavio':n(e.get('N30'))*100 if valido else None,
        'votos_lula':e.get('J30'),'votos_flavio':e.get('K30'),'presentes':e.get('L30'),'taxa_presenca':None,'status':e['status']}
    br.update(data_fonte='Varia por UF',hora_fonte='Consultar tabela',coleta_utc=conjunto['coleta_utc'],
              fonte='Agregado dos arquivos oficiais das 27 UFs + ZZ',sha256=hashlib.sha256(json_texto(conjunto).encode()).hexdigest(),
              idg='Consultar cada UF',andamento='f' if all(v['andamento']=='f' for v in vistas.values()) else 'p' if br['totalizadas'] else 'n')
    vistas['BR']=br
    return vistas


def gerar(pasta=Path('dados'), destino=Path('dist'), site=Path('site')):
    pasta.mkdir(parents=True,exist_ok=True)
    destino.mkdir(parents=True,exist_ok=True)
    (destino/'data').mkdir(exist_ok=True)
    agora=datetime.now(timezone.utc).isoformat()
    histpath=pasta/'historico_dashboard.json'
    historico=json.loads(histpath.read_text(encoding='utf-8')) if histpath.exists() else []
    publicacao={'gerado_utc':agora,'inicio_eixo':'2026-10-25T17:00:00-03:00','fim_eixo_inicial':'2026-10-26T00:00:00-03:00','eleicoes':{}}
    for eleicao in ('6257','6258'):
        arq=pasta/f'conjunto_{eleicao}.json'; estado=pasta/f'estado_conjunto_{eleicao}.json'
        s=json.loads(estado.read_text(encoding='utf-8')) if estado.exists() else {'desatualizado':True,'aviso':'Nenhuma coleta validada disponível.','status':'indisponivel'}
        conjunto=json.loads(arq.read_text(encoding='utf-8')) if arq.exists() else None
        vistas=compilar(conjunto) if conjunto else {}
        if conjunto:
            chave=eleicao+':'+conjunto['coleta_utc']
            if not any(h['id']==chave for h in historico):
                historico.append({'id':chave,'eleicao':eleicao,'coleta_utc':conjunto['coleta_utc'],'vistas':vistas})
            atomico(destino/'data'/arq.name, arq.read_bytes())
            csvpath=pasta/f'conjunto_{eleicao}.csv'
            if csvpath.exists(): shutil.copyfile(csvpath,destino/'data'/csvpath.name)
        publicacao['eleicoes'][eleicao]={'estado':s,'coleta_utc':conjunto['coleta_utc'] if conjunto else None,'vistas':vistas,
            'historico':[h for h in historico if h['eleicao']==eleicao]}
    historico.sort(key=lambda h:(h['coleta_utc'],h['eleicao']))
    atomico(histpath,json_texto(historico).encode('utf-8'))
    atomico(destino/'data/dashboard.json',json_texto(publicacao).encode('utf-8'))
    log=pasta/'abrangencias/logs/atualizacoes.csv'
    if log.exists(): shutil.copyfile(log,destino/'data/atualizacoes.csv')
    for nome in ('index.html','dashboard.css','dashboard.js'):
        shutil.copyfile(site/nome,destino/nome)
    (destino/'.nojekyll').write_text('',encoding='utf-8')
    return publicacao


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pasta',type=Path,default=Path('dados'))
    p.add_argument('--destino',type=Path,default=Path('dist'))
    a=p.parse_args(); d=gerar(a.pasta,a.destino)
    print(json.dumps({'destino':str(a.destino),'gerado_utc':d['gerado_utc'],'abrangencias':{e:len(x['vistas']) for e,x in d['eleicoes'].items()}}))

if __name__=='__main__': main()
