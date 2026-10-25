import json
import tempfile
import unittest
from pathlib import Path
from urllib.error import URLError
from monitor.pipeline import executar
from monitor.publicacao import gerar
from test_resiliencia import resposta, BASE


class Publicacao(unittest.TestCase):
    def test_dados_exatos_historico_sem_duplicacao_e_falha(self):
        with tempfile.TemporaryDirectory(dir=BASE/'tests') as t:
            p=Path(t);dados=p/'dados';dist=p/'dist'
            executar('6257',dados,abrir=resposta)
            a=gerar(dados,dist,BASE/'site')
            v=a['eleicoes']['6257']['vistas']['AC']
            self.assertEqual(v['aptos'],613742)
            self.assertEqual(str(v['lula']),'28.731564428')
            self.assertEqual(v['votos_lula'],134770)
            self.assertEqual(len(a['eleicoes']['6257']['vistas']),29)
            gerar(dados,dist,BASE/'site')
            self.assertEqual(len(json.loads((dados/'historico_dashboard.json').read_text(encoding='utf-8'))),1)
            anterior=(dados/'conjunto_6257.json').read_bytes()
            def falha(*a,**k):raise URLError('Falha controlada da API')
            executar('6257',dados,abrir=falha)
            b=gerar(dados,dist,BASE/'site')
            self.assertEqual((dados/'conjunto_6257.json').read_bytes(),anterior)
            self.assertEqual((dist/'data/conjunto_6257.json').read_bytes(),anterior)
            self.assertEqual(len(b['eleicoes']['6257']['historico']),1)
            self.assertTrue(b['eleicoes']['6257']['estado']['desatualizado'])
            self.assertEqual(b['eleicoes']['6257']['estado']['status'],'erro')
            self.assertEqual(b['eleicoes']['6257']['vistas']['AC']['votos_lula'],134770)

    def test_sem_dados_nao_fabrica_serie(self):
        with tempfile.TemporaryDirectory(dir=BASE/'tests') as t:
            p=Path(t);r=gerar(p/'dados',p/'dist',BASE/'site')
            self.assertEqual(r['eleicoes']['6258']['historico'],[])
            self.assertEqual(r['eleicoes']['6258']['vistas'],{})
            self.assertTrue(r['eleicoes']['6258']['estado']['desatualizado'])

    def test_snapshot_zerado_e_indisponivel(self):
        from monitor.indicadores import extrair
        from monitor.calculos import calcular_linha
        from monitor.publicacao import vista
        raw=json.loads((BASE/'evidencias/tse_acre_6258.json').read_bytes())
        d=extrair(raw,'6258','2')
        r={'oficial':d,'estimativa_planilha':calcular_linha(None,None,0,0,d['eleitorado_apto']),
           'coleta_utc':'2026-10-25T18:00:00Z','fonte':'https://resultados.tse.jus.br/','sha256':'teste'}
        v=vista(r)
        self.assertFalse(v['apurado'])
        self.assertIsNone(v['lula'])
        self.assertIsNone(v['votos_lula'])
        self.assertIsNone(v['estimativa']['lula'])

    def test_brasil_preserva_votos_disponiveis_com_uf_sem_concorrentes(self):
        from monitor.publicacao import compilar
        with tempfile.TemporaryDirectory(dir=BASE/'tests') as t:
            dados=Path(t)/'dados'
            executar('6257',dados,abrir=resposta)
            conjunto=json.loads((dados/'conjunto_6257.json').read_text(encoding='utf-8'))
        zz=next(r for r in conjunto['abrangencias'] if r['oficial']['uf']=='ZZ')['oficial']
        zz['votos_concorrentes']=0
        for c in zz['candidatos'].values():c['votos']=0
        v=compilar(conjunto)
        self.assertGreater(v['ZZ']['totalizadas'],0)
        self.assertFalse(v['ZZ']['apurado'])
        self.assertIsNone(v['ZZ']['lula'])
        self.assertTrue(v['BR']['apurado'])
        self.assertEqual(v['BR']['votos_lula'],134770*27)
        self.assertEqual(v['BR']['concorrentes'],v['AC']['concorrentes']*27)
        self.assertIsNotNone(v['BR']['lula'])

    def test_brasil_indisponivel_se_uf_com_votos_nao_e_divulgada(self):
        from monitor.publicacao import compilar
        with tempfile.TemporaryDirectory(dir=BASE/'tests') as t:
            dados=Path(t)/'dados'
            executar('6257',dados,abrir=resposta)
            conjunto=json.loads((dados/'conjunto_6257.json').read_text(encoding='utf-8'))
        next(r for r in conjunto['abrangencias'] if r['oficial']['uf']=='SP')['oficial']['divulga_votacao']='n'
        v=compilar(conjunto)
        self.assertIsNone(v['BR']['lula'])
        self.assertIsNone(v['BR']['votos_lula'])

if __name__=='__main__':unittest.main()
