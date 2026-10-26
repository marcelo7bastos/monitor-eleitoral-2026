# Avaliação retrospectiva — Monitor Eleitoral 2026

Análise do segundo turno, gerada exclusivamente a partir de `arquivo-final/monitor-estado.zip`. Todos os horários são de Brasília (UTC−03:00). “Apuração” significa seções totalizadas / total de seções; não contagem independente de equipamentos físicos. Os horários são de coleta, não o instante exato em que o TSE cruzou um limiar.

Referência: último resultado preservado, com 100% das seções totalizadas: Lula 51,785183% e Flávio 48,214817%. Há 54 coletas do segundo turno. Erro = diferença absoluta, em pontos percentuais, entre a estimativa de Lula em cada coleta e essa referência. Como os percentuais dos dois candidatos somam 100%, o erro absoluto é igual para ambos.

## O que melhor demonstra o desempenho

O melhor marco de antecipação é 25/10 20:06:30: 27,589% de apuração nacional, com estimativa de Lula em 50,120%. A liderança indicada permaneceu até o fim do histórico. O agregado oficial somente passou a indicar essa mesma liderança de forma permanente em 25/10 20:26:28, com 48,320%. A antecipação observada foi de cerca de 20 minutos. Isso não prova que uma chamada de vencedor seria segura naquele instante.

Para precisão percentual com alguma antecedência, destaca-se 25/10 20:51:38: 77,701% nacional, estimativa de Lula de 51,361%, erro de 0,424 p.p., mantido abaixo de 0,5 p.p. em todas as coletas posteriores. Os limites de erro são critérios descritivos escolhidos para esta análise, não intervalos de confiança.

| Marco | Coleta (Brasília) | Apuração nacional | Estimativa Lula | Erro estimativa (p.p.) | Erro agregado oficial (p.p.) | UF menos apurada, sem ZZ |
|---|---|---:|---:|---:|---:|---:|
| Liderança definitiva no histórico | 25/10 20:06:30 | 27,589% | 50,120% | 1,666 | 2,219 | 1,128% |
| Erro permanece ≤ 1 p.p. | 25/10 20:36:35 | 60,022% | 50,886% | 0,899 | 1,275 | 13,234% |
| Erro permanece ≤ 0.5 p.p. | 25/10 20:51:38 | 77,701% | 51,361% | 0,424 | 0,593 | 29,208% |
| Erro permanece ≤ 0.25 p.p. | 25/10 21:01:26 | 88,741% | 51,558% | 0,227 | 0,245 | 50,599% |
| Erro permanece ≤ 0.1 p.p. | 25/10 21:11:29 | 99,491% | 51,753% | 0,033 | 0,031 | 98,028% |

O menor erro isolado de todo o histórico ocorreu em 25/10 19:08:13, com apenas 1,367% nacional: 0,003310 p.p. A estimativa ainda excluía Sergipe (27 de 28 abrangências) e depois chegou a indicar o outro candidato. Portanto, esse ponto isolado não é evidência de estabilidade nem fundamento para escolher um percentual mínimo de apuração.

A estimativa não foi sempre melhor que o agregado oficial parcial. A comparação das duas colunas de erro mostra momentos em que cada método ficou mais próximo da referência. Acerto de liderança e precisão do percentual são critérios diferentes.

## Composição por UF

Não é possível identificar a composição com maior probabilidade de acerto a partir de uma única eleição. Uma combinação que minimiza o erro depois de conhecido o resultado sofre ajuste retrospectivo. Mesmo com todas as UFs presentes, a ordem de apuração de municípios e seções pode produzir viés dentro de cada UF. Percentuais de apuração são medidas de cobertura, não probabilidades de acerto.

Como referência operacional para estudar em outras eleições, esta trajetória sugere acompanhar simultaneamente todas as UFs e o exterior, com um piso de cobertura por UF, além da cobertura nacional e da estabilidade entre coletas. São marcos observados, não regras validadas:

| Piso de apuração em cada uma das 27 UFs | Primeiro registro | Nacional | Erro estimativa (p.p.) |
|---|---|---:|---:|
| ≥ 25% | 25/10 20:51:38 | 77,701% | 0,424 |
| ≥ 50% | 25/10 21:01:26 | 88,741% | 0,227 |
| ≥ 70% | 25/10 21:06:30 | 94,160% | 0,169 |
| ≥ 90% | 25/10 21:11:29 | 99,491% | 0,033 |

O marco de 20h51 combina 77,70% nacional com pelo menos 29,21% em cada UF. Às 21h01, a cobertura nacional sobe a 88,74% e todas as UFs superam 50,59%; o erro cai para 0,227 p.p. Esses dois pontos ilustram a troca entre antecedência e precisão observada. Para afirmar maior chance de acerto, seria necessário validar critérios previamente definidos em várias eleições, sem usar o resultado de teste para escolher os limites.

Composição completa dos três marcos úteis (ZZ = exterior; não é UF):

| Abrangência | 20h06: liderança estável | 20h51: erro ≤ 0,5 p.p. | 21h01: erro ≤ 0,25 p.p. |
|---|---:|---:|---:|
| AC | 67,00% | 99,03% | 99,07% |
| AL | 47,09% | 95,45% | 99,66% |
| AM | 71,12% | 92,22% | 97,39% |
| AP | 39,86% | 99,22% | 99,84% |
| BA | 9,72% | 67,04% | 83,21% |
| CE | 17,26% | 82,52% | 92,00% |
| DF | 92,01% | 97,52% | 98,02% |
| ES | 64,43% | 96,60% | 97,40% |
| GO | 18,16% | 90,63% | 97,85% |
| MA | 45,18% | 95,26% | 97,99% |
| MG | 21,54% | 73,45% | 89,25% |
| MS | 79,79% | 99,04% | 99,62% |
| MT | 49,67% | 91,77% | 97,06% |
| PA | 56,54% | 91,77% | 96,50% |
| PB | 79,86% | 95,74% | 97,70% |
| PE | 15,00% | 83,32% | 92,19% |
| PI | 6,75% | 81,84% | 96,91% |
| PR | 68,37% | 98,69% | 98,99% |
| RJ | 1,13% | 29,21% | 50,60% |
| RN | 37,77% | 93,42% | 97,55% |
| RO | 48,17% | 94,57% | 98,25% |
| RR | 20,28% | 92,43% | 99,80% |
| RS | 34,79% | 89,56% | 97,12% |
| SC | 26,98% | 95,13% | 99,54% |
| SE | 2,97% | 31,74% | 69,49% |
| SP | 5,84% | 67,97% | 84,70% |
| TO | 86,79% | 96,88% | 98,18% |
| ZZ | 62,40% | 66,91% | 72,32% |

## Corte do gráfico

Primeira coleta nacional com pelo menos 99,9%: 25/10 21:46:29, com 99,909864%. A coleta anterior ainda estava abaixo do limite. O gráfico inclui esse primeiro ponto acima do limiar e omite os seguintes; não inventa um ponto exatamente em 99,900%. Em cada UF selecionada, usa-se o primeiro cruzamento da própria abrangência. Se não houver cruzamento, usa-se a última coleta disponível e informa-se a limitação.

O histórico completo e os dados finais permanecem preservados. Apenas a janela do gráfico e sua tabela de pontos são limitadas.
