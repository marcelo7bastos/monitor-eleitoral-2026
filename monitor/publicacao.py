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
from .planilha import gerar_xlsx


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


def estimativa_parcial(vistas):
    """Brasil enquanto faltam UFs: soma(J)/soma(L) só das abrangências com estimativa calculada.

    Diverge de M30/N30 (que exigem as 28 linhas) e por isso sempre informa N de 28.
    """
    com=[v['estimativa'] for uf,v in vistas.items() if uf in UFS and v['estimativa']['status']=='calculado']
    j,k,l=(sum((n(x[c]) for x in com),Decimal(0)) for c in ('votos_lula','votos_flavio','presentes'))
    ok=bool(com) and l>0
    return {'lula':j/l*100 if ok else None,'flavio':k/l*100 if ok else None,
            'votos_lula':j if ok else None,'votos_flavio':k if ok else None,'presentes':l if ok else None,'taxa_presenca':None,
            'status':'parcial' if ok else 'indisponivel','parcial':True,'ufs_com_dados':len(com),'ufs_total':len(UFS)}


def compilar(conjunto):
    registros=conjunto['abrangencias']
    if len(registros)!=28 or {r['oficial']['uf'] for r in registros}!=set(UFS):
        raise ValueError('Conjunto público exige as 28 abrangências únicas')
    vistas={r['oficial']['uf']:vista(r) for r in registros}
    br={'uf':'BR'}
    for campo in ('aptos','comparecimento','abstencao','secoes','totalizadas','validos','concorrentes'):
        br[campo]=sum(v[campo] for v in vistas.values())
    br['apurado']=br['concorrentes']>0 and all(v['apurado'] or v['concorrentes']==0 for v in vistas.values())
    br['cobertura']=Decimal(br['totalizadas'])*100/br['secoes'] if br['secoes'] else None
    for nome in ('lula','flavio'):
        br['votos_'+nome]=sum(v['votos_'+nome] or 0 for v in vistas.values()) if br['apurado'] else None
        br[nome]=Decimal(br['votos_'+nome])*100/br['concorrentes'] if br['apurado'] else None
    e=conjunto['consolidado_planilha']; valido=e['status']=='calculado'
    br['estimativa']={'lula':n(e.get('M30'))*100 if valido else None,'flavio':n(e.get('N30'))*100 if valido else None,
        'votos_lula':e.get('J30'),'votos_flavio':e.get('K30'),'presentes':e.get('L30'),'taxa_presenca':None,'status':e['status'],
        'parcial':False,'ufs_com_dados':len(UFS) if valido else 0,'ufs_total':len(UFS)}
    if not valido: br['estimativa']=estimativa_parcial(vistas)
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
    for h in historico:  # coletas anteriores à regra parcial: recalcula só o Brasil a partir das UFs gravadas
        b=h['vistas'].get('BR')
        if b and 'ufs_total' not in b['estimativa']:
            b['estimativa']=json.loads(json_texto(estimativa_parcial(h['vistas']) if b['estimativa']['lula'] is None else
                {**b['estimativa'],'parcial':False,'ufs_com_dados':len(UFS),'ufs_total':len(UFS)}))
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
            atomico(destino/'data'/f'conjunto_{eleicao}.xlsx',gerar_xlsx(conjunto))
        publicacao['eleicoes'][eleicao]={'estado':s,'coleta_utc':conjunto['coleta_utc'] if conjunto else None,'vistas':vistas,
            'historico':[h for h in historico if h['eleicao']==eleicao]}
    historico.sort(key=lambda h:(h['coleta_utc'],h['eleicao']))
    atomico(histpath,json_texto(historico).encode('utf-8'))
    atomico(destino/'data/dashboard.json',json_texto(publicacao).encode('utf-8'))
    log=pasta/'abrangencias/logs/atualizacoes.csv'
    if log.exists(): shutil.copyfile(log,destino/'data/atualizacoes.csv')
    pagina=(site/'index.html').read_text(encoding='utf-8')
    for nome in ('dashboard.css','dashboard.js'):  # versão por conteúdo no endereço: o navegador nunca mistura JS/CSS antigos
        conteudo=(site/nome).read_bytes(); shutil.copyfile(site/nome,destino/nome)
        pagina=pagina.replace(f'"{nome}"',f'"{nome}?v={hashlib.sha256(conteudo).hexdigest()[:12]}"')
    atomico(destino/'index.html',pagina.encode('utf-8'))
    (destino/'.nojekyll').write_text('',encoding='utf-8')
    return publicacao


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pasta',type=Path,default=Path('dados'))
    p.add_argument('--destino',type=Path,default=Path('dist'))
    a=p.parse_args(); d=gerar(a.pasta,a.destino)
    print(json.dumps({'destino':str(a.destino),'gerado_utc':d['gerado_utc'],'abrangencias':{e:len(x['vistas']) for e,x in d['eleicoes'].items()}}))

if __name__=='__main__': main()
