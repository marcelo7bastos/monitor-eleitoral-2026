# Indicadores, cálculos e histórico de atualização

Implementação local em 25/10/2026. Abrangência de coleta: Acre, Presidente, eleições 6257 e 6258. Não há coleta nacional, workflow, agendamento ou publicação nesta entrega.

## T2 — Mapeamento e conferência

Referência técnica: [EA20/2026 oficial do TSE](https://www.tse.jus.br/eleicoes/eleicoes-2026-content/arquivos/divulgacao-de-resultados/tse-ea20-arquivo-de-resultado-unificado), consultada em 25/10/2026. Códigos eleitorais também conferidos na [página técnica de 2026](https://www.tse.jus.br/eleicoes/informacoes-tecnicas-sobre-a-divulgacao-de-resultados).

| Entrada da planilha | Campo EA20 | Unidade no Python |
|---|---|---|
| D: percentual Lula | candidato 13 / sequencial 280002542548, pvapn | fração 0..1 (dividido por 100) |
| E: percentual Flávio | candidato 22 / sequencial 280002551544, pvapn | fração 0..1 (dividido por 100) |
| F: comparecimento | e.c | pessoas |
| G: abstenção | e.a | pessoas |
| H: eleitorado apto | e.te | pessoas |

Os percentuais de candidatos usam votos a concorrentes (`v.vvc`) como denominador, conforme EA20; não presumir que sejam sempre os votos válidos (`v.vv`). `pvap` é preservado para exibição, e `pvapn` alimenta os cálculos com a precisão disponível. A extração confere votos/denominador contra ambos, com tolerâncias de arredondamento de 0,005000001 ponto percentual (duas casas) e 0,00000000051 ponto percentual (nove casas). Candidatos são identificados por número e sequencial, sem busca por nome. Se não houver votos concorrentes, a fração para cálculo fica indisponível.

Na execução real, ambos os endpoints responderam HTTP 200. Os hashes coincidiram com os snapshots arquivados em T1. A [tabela de conferência](../evidencias/indicadores_acre.csv) contém dez linhas: cinco indicadores por turno, identificadores, unidades, data/hora da fonte e hash. A conferência foi programática contra os arquivos oficiais e as relações aritméticas; não foi realizada conferência visual do portal.

| Indicador | Acre / 1º turno | Acre / 2º turno |
|---|---:|---:|
| Lula (pvap, %) | 28,73 | 0,00 |
| Flávio (pvap, %) | 64,56 | 0,00 |
| Comparecimento | 488.330 | 0 |
| Abstenção | 125.412 | 0 |
| Eleitorado apto | 613.742 | 613.715 |
| Seções totalizadas / total | 2.270 / 2.270 | 0 / 2.270 |

O segundo turno está sem totalização no snapshot recebido, gerado em 13/10/2026. Os zeros recebidos não são uma estimativa eleitoral de 0%. O primeiro turno informa geração em 05/10/2026. Datas de coleta e geração ficam separadas. Esses arquivos não comprovam apuração atual do segundo turno.

## T3 — Auditoria e equivalência

A referência original foi preservada integralmente. SHA-256: `800597732267e423bce09308647a2a8d0ea8fdecd67828b27e552216c894331e`.

Uma aba, `Planilha1`, 28 linhas de abrangência (2 a 29), 140 entradas vazias e 118 fórmulas. O [inventário](../evidencias/auditoria/inventario_formulas.csv) expande as fórmulas compartilhadas do XLSX e informa cada célula, fórmula e cache. O original contém resultados salvos como `#DIV/0!`; não possui exemplos numéricos preenchidos para comparação direta.

| Célula/família | Fórmula original | Resultado Python |
|---|---|---|
| I2:I29 | F / SUM(F:G) | taxa de presença entre comparecimento + abstenção contabilizados |
| J2:J29 | H * I * D | quantidade estimada para Lula |
| K2:K29 | H * I * E | quantidade estimada para Flávio |
| L2:L29 | H * I | quantidade estimada de presentes |
| H30 | SUM(H2:H29) | eleitorado agregado |
| J30:L30 | SUM das respectivas colunas | agregados do modelo |
| M30 / N30 | J30/L30 / K30/L30 | participações ponderadas no modelo |

`monitor/calculos.py` usa Decimal, sem arredondamento intermediário. As quantidades estimadas permanecem decimais; não são contagens oficiais. Frações exigem 0..1, enquanto quantidades exigem inteiros não negativos. Entradas ausentes ou denominador zero produzem `indisponivel`, com motivo e resultados nulos. Isso substitui a coerção de vazios e os erros de divisão da planilha por um estado explícito, sem inventar zeros. A consolidação exige 28 linhas completas; não ignora abrangências ausentes.

Cinco cenários foram recalculados usando as fórmulas originais no motor `@oai/artifact-tool`: uniforme, heterogêneo com apuração parcial, comparecimento total, candidato zero e entradas reais do Acre replicadas exclusivamente para testar as 28 posições. Os cenários artificiais não representam resultados nacionais. Foram 590 comparações numéricas, sem divergências acima da tolerância. Cada comparação consta em [equivalencia.csv](../evidencias/auditoria/equivalencia.csv), com valores Python/motor, delta e tolerância. Taxas: tolerância absoluta 1e-12; quantidades: 1e-6; acrescida de tolerância relativa 1e-12. Denominador zero também foi conferido no motor.

O importador do motor não expandiu as fórmulas compartilhadas. Para o teste, as 118 fórmulas foram restauradas em memória a partir da leitura de openpyxl, conferida contra as famílias esperadas. Nenhuma alteração foi salva no XLSX. Trata-se de equivalência com as fórmulas da referência recalculadas em outro motor; não foi feita execução no Excel nativo.

### Limitações do modelo preservadas

- O rótulo L (“VOTOS VÁLIDOS PRESENTES”) não descreve sua fórmula: ela estima presentes, sem subtrair brancos/nulos.
- A participação de candidatos tem base em concorrentes, enquanto J/K aplicam essa participação aos presentes estimados. Mesmo com 100% de seções, J/K podem diferir dos votos oficiais.
- No Acre/1º turno, L = 488.330, mas votos válidos oficiais = 469.066. J ≈ 140.304,85 e K ≈ 315.242,93; são resultados da fórmula preservada, não os votos oficiais de 134.770 e 302.807.
- Em apuração parcial, extrapolar a taxa de presença e a composição dos votos para todo o eleitorado pressupõe representatividade da parcela já apurada. A paridade matemática não valida essa premissa nem fornece intervalo de confiança.

Nenhuma correção metodológica foi aplicada silenciosamente. Uma revisão futura pode escolher outro modelo; a entrega atual reproduz a referência e mantém os resultados identificados como estimativas.

## Tabela de logs

Arquivo operacional: `dados/logs/atualizacoes.csv`, delimitador `;`, UTF-8 com BOM. Uma linha por tentativa, incluindo sucesso com alteração, sucesso sem alteração e erro. [Cópia das quatro coletas verificadas nesta entrega](../evidencias/logs_atualizacoes.csv).

Campos: identificador da execução; início/fim UTC; data local; hora local com segundos; minuto local (`HH:MM`); fuso; eleição/turno/UF; situação; HTTP; URL; data/hora de geração e totalização na fonte; IDG; SHA-256; indicador de alteração; aviso de fonte antiga; erro. A data/hora local registra o término da tentativa em America/Sao_Paulo, UTC-03:00 em 2026.

O horário bruto do TSE é preservado. Para o aviso de idade, assume-se UTC-03:00 para o relógio da fonte: a documentação EA20 consultada não explicita fuso. O limite de 30 minutos é um parâmetro operacional do código, não regra do TSE, e não reprova automaticamente um resultado histórico finalizado. `atualizado` significa nova versão local aceita; não significa necessariamente apuração atual.

O CSV é regravado atomicamente com os registros anteriores e a nova linha. Um arquivo `.lock` impede escritores simultâneos; uma segunda execução concorrente falha explicitamente. Uma interrupção abrupta pode deixar um lock residual, que exige conferência antes de remoção. Não há banco de dados. Na futura execução em Actions será necessário persistir o histórico entre runners e serializar os jobs.

Falhas de rede, JSON ou identidade não substituem o último arquivo aceito. Snapshots brutos são guardados por hash, e respostas com data de geração anterior à última aceita são rejeitadas. Uma repetição sem mudança atualiza a hora da coleta, conserva o conteúdo oficial e acrescenta uma linha `sem_alteracao` no log. Esses testes iniciais não substituem a homologação integral de T8.

## Execução

Python 3.9+ para coleta/cálculo, sem bibliotecas externas:

```powershell
python -m monitor.atualizacao --eleicao 6258
python -m monitor.atualizacao --eleicao 6257
python -m unittest discover -s tests -v
python -m unittest discover -s scripts -p test_validacao_t1.py -v
```

Para reproduzir a auditoria: instalar as dependências de desenvolvimento (`requirements-dev.txt`), executar `python scripts/preparar_auditoria.py` e `node scripts/auditar_planilha.mjs`. O último requer o runtime de planilhas do Codex e o vínculo `node_modules` apontando para suas bibliotecas; não é dependência do monitor. O script `registrar_evidencias_t2.py` confere que o hash da coleta corresponde ao snapshot antes de gerar a tabela.

Próximo passo: T4, expandir a coleta real para 27 UFs + exterior e validar a cobertura do conjunto, mantendo logs e identificação da origem. A coleta das outras abrangências não está implementada nesta entrega.

## Atualização posterior
A metodologia foi aceita pelo usuário, e o rótulo do modelo passou a PRESENTES ESTIMADOS. A coleta foi expandida para as 28 abrangências e o workflow manual está sendo validado. Este documento conserva o registro histórico da implementação inicial. Estado atual: [FALHAS_E_ACTIONS](FALHAS_E_ACTIONS.md).
