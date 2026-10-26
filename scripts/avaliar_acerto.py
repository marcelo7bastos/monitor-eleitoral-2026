"""Análise retrospectiva reproduzível; usa apenas o acervo preservado, sem rede."""
import json
import zipfile
from datetime import datetime, timezone, timedelta
from decimal import Decimal as D
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
with zipfile.ZipFile(ROOT/'arquivo-final/monitor-estado.zip') as z:
    hs = sorted((h for h in json.loads(z.read('historico_dashboard.json')) if h['eleicao']=='6258'), key=lambda h:h['coleta_utc'])
final = hs[-1]['vistas']['BR']
referencia = D(final['lula'])
validos = [h for h in hs if h['vistas']['BR']['estimativa']['lula'] is not None]
def b(h): return h['vistas']['BR']
def erro(h, modo='estimativa'):
    v = b(h)['estimativa'] if modo=='estimativa' else b(h)
    return abs(D(v['lula'])-referencia)
def hora(h): return datetime.fromisoformat(h['coleta_utc']).astimezone(timezone(timedelta(hours=-3))).strftime('%d/%m %H:%M:%S')
def fmt(v, casas=3): return f'{D(v):.{casas}f}'.replace('.',',')
def estavel(t):
    return next(h for i,h in enumerate(validos) if all(erro(x)<=D(t) for x in validos[i:]))
def lider(m):
    return next(h for i,h in enumerate(validos) if all(D((b(x)['estimativa'] if m=='estimativa' else b(x))['lula'])>50 for x in validos[i:]))
def minimo(h): return min(D(v['cobertura']) for k,v in h['vistas'].items() if k not in ('BR','ZZ'))
melhor = min(validos,key=erro)
lider_est,lider_of = lider('estimativa'),lider('oficial')
marcos = [('Liderança definitiva no histórico',lider_est)]+[(f'Erro permanece ≤ {t} p.p.',estavel(t)) for t in ['1','0.5','0.25','0.1']]
corte = next(h for h in hs if int(b(h)['totalizadas'])*1000 >= int(b(h)['secoes'])*999)
linhas = ['# Avaliação retrospectiva — Monitor Eleitoral 2026','',
'Análise do segundo turno, gerada exclusivamente a partir de `arquivo-final/monitor-estado.zip`. Todos os horários são de Brasília (UTC−03:00). “Apuração” significa seções totalizadas / total de seções; não contagem independente de equipamentos físicos. Os horários são de coleta, não o instante exato em que o TSE cruzou um limiar.','',
f'Referência: último resultado preservado, com 100% das seções totalizadas: Lula {fmt(referencia,6)}% e Flávio {fmt(final["flavio"],6)}%. Há {len(hs)} coletas do segundo turno. Erro = diferença absoluta, em pontos percentuais, entre a estimativa de Lula em cada coleta e essa referência. Como os percentuais dos dois candidatos somam 100%, o erro absoluto é igual para ambos.','',
'## O que melhor demonstra o desempenho','',
f'O melhor marco de antecipação é {hora(lider_est)}: {fmt(b(lider_est)["cobertura"])}% de apuração nacional, com estimativa de Lula em {fmt(b(lider_est)["estimativa"]["lula"])}%. A liderança indicada permaneceu até o fim do histórico. O agregado oficial somente passou a indicar essa mesma liderança de forma permanente em {hora(lider_of)}, com {fmt(b(lider_of)["cobertura"])}%. A antecipação observada foi de cerca de 20 minutos. Isso não prova que uma chamada de vencedor seria segura naquele instante.','',
f'Para precisão percentual com alguma antecedência, destaca-se {hora(estavel("0.5"))}: {fmt(b(estavel("0.5"))["cobertura"])}% nacional, estimativa de Lula de {fmt(b(estavel("0.5"))["estimativa"]["lula"])}%, erro de {fmt(erro(estavel("0.5")))} p.p., mantido abaixo de 0,5 p.p. em todas as coletas posteriores. Os limites de erro são critérios descritivos escolhidos para esta análise, não intervalos de confiança.','',
'| Marco | Coleta (Brasília) | Apuração nacional | Estimativa Lula | Erro estimativa (p.p.) | Erro agregado oficial (p.p.) | UF menos apurada, sem ZZ |','|---|---|---:|---:|---:|---:|---:|']
for nome,h in marcos:
    linhas.append(f'| {nome} | {hora(h)} | {fmt(b(h)["cobertura"])}% | {fmt(b(h)["estimativa"]["lula"])}% | {fmt(erro(h))} | {fmt(erro(h,"oficial"))} | {fmt(minimo(h))}% |')
linhas += ['',f'O menor erro isolado de todo o histórico ocorreu em {hora(melhor)}, com apenas {fmt(b(melhor)["cobertura"])}% nacional: {fmt(erro(melhor),6)} p.p. A estimativa ainda excluía Sergipe (27 de 28 abrangências) e depois chegou a indicar o outro candidato. Portanto, esse ponto isolado não é evidência de estabilidade nem fundamento para escolher um percentual mínimo de apuração.','',
'A estimativa não foi sempre melhor que o agregado oficial parcial. A comparação das duas colunas de erro mostra momentos em que cada método ficou mais próximo da referência. Acerto de liderança e precisão do percentual são critérios diferentes.','',
'## Composição por UF','',
'Não é possível identificar a composição com maior probabilidade de acerto a partir de uma única eleição. Uma combinação que minimiza o erro depois de conhecido o resultado sofre ajuste retrospectivo. Mesmo com todas as UFs presentes, a ordem de apuração de municípios e seções pode produzir viés dentro de cada UF. Percentuais de apuração são medidas de cobertura, não probabilidades de acerto.','',
'Como referência operacional para estudar em outras eleições, esta trajetória sugere acompanhar simultaneamente todas as UFs e o exterior, com um piso de cobertura por UF, além da cobertura nacional e da estabilidade entre coletas. São marcos observados, não regras validadas:','',
'| Piso de apuração em cada uma das 27 UFs | Primeiro registro | Nacional | Erro estimativa (p.p.) |','|---|---|---:|---:|']
for piso in [25,50,70,90]:
    h=next(h for h in validos if minimo(h)>=piso)
    linhas.append(f'| ≥ {piso}% | {hora(h)} | {fmt(b(h)["cobertura"])}% | {fmt(erro(h))} |')
linhas += ['','O marco de 20h51 combina 77,70% nacional com pelo menos 29,21% em cada UF. Às 21h01, a cobertura nacional sobe a 88,74% e todas as UFs superam 50,59%; o erro cai para 0,227 p.p. Esses dois pontos ilustram a troca entre antecedência e precisão observada. Para afirmar maior chance de acerto, seria necessário validar critérios previamente definidos em várias eleições, sem usar o resultado de teste para escolher os limites.','',
'Composição completa dos três marcos úteis (ZZ = exterior; não é UF):','',
'| Abrangência | 20h06: liderança estável | 20h51: erro ≤ 0,5 p.p. | 21h01: erro ≤ 0,25 p.p. |','|---|---:|---:|---:|']
selecoes=[lider_est,estavel('0.5'),estavel('0.25')]
for uf in sorted(k for k in hs[-1]['vistas'] if k!='BR'):
    linhas.append('| '+uf+' | '+' | '.join(fmt(h['vistas'][uf]['cobertura'],2)+'%' for h in selecoes)+' |')
linhas += ['', '## Corte do gráfico','',
f'Primeira coleta nacional com pelo menos 99,9%: {hora(corte)}, com {fmt(b(corte)["cobertura"],6)}%. A coleta anterior ainda estava abaixo do limite. O gráfico inclui esse primeiro ponto acima do limiar e omite os seguintes; não inventa um ponto exatamente em 99,900%. Em cada UF selecionada, usa-se o primeiro cruzamento da própria abrangência. Se não houver cruzamento, usa-se a última coleta disponível e informa-se a limitação.','',
'O histórico completo e os dados finais permanecem preservados. Apenas a janela do gráfico e sua tabela de pontos são limitadas.']
(ROOT/'docs/AVALIACAO_RETROSPECTIVA.md').write_text('\n'.join(linhas)+'\n',encoding='utf-8')
print('Relatório gerado: docs/AVALIACAO_RETROSPECTIVA.md')
