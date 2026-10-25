# Protocolo de testes e homologação

Para cada teste, registrar: data/hora, ambiente, comando, URL/fonte, resultado observado, resultado esperado, evidência, decisão e responsável.

**Status possíveis:** pendente, em andamento, bloqueado, aprovado, reprovado. Aprovado exige evidência reproduzível.

## T1 — Conexão API
Executar `python scripts/teste_t2_acre.py`. Aprovar somente se HTTP 200, JSON válido, eleição 6257 e UF AC identificadas, arquivo salvo. Se falhar DNS, registrar bloqueio de rede, não reprovação da API.

## T2 — Cinco indicadores
Mapear % Lula, % Flávio, comparecimento, abstenção e eleitorado apto. Documentar chaves e denominadores; confrontar com a página oficial do TSE na mesma abrangência/turno/horário. Divergências não explicadas reprovam.

## T3 — Cálculo
Auditar a planilha `estimativa voto 2T.xlsx` e suas fórmulas reais com openpyxl. Criar casos numéricos e conferir resultados e arredondamento. Registrar eventuais inconsistências da planilha antes de decidir ajustes.

## T4 — Abrangências
Conferir 27 UFs + ZZ, sem duplicações, e testar ausência de campos e apuração parcial. Gerar CSV com metadados de fonte e horário.

## T5 — Actions manual
Criar workflow apenas após T1–T4. Executar por workflow_dispatch; validar logs e artefatos, sem publicação de dados inválidos.

## T6 — Cron
Habilitar `*/10 * * * *` após T5; observar duas execuções reais e registrar eventuais atrasos.

## T7 — HTML
Verificar acessibilidade pública, responsividade, fonte, data/hora, cobertura e separação visual entre resultados oficiais e estimativas.

## T8 — Resiliência
Simular timeout, JSON inválido e ausência de dados; preservar último snapshot válido e emitir log explícito.

**Modelo de evidência:** link para issue + commit + log/artefato + valores comparados + decisão de aceite.

## Evidências da implementação local — 25/10/2026
- T1: [VALIDACAO_T1](VALIDACAO_T1.md).
- T2: [indicadores_acre.csv](../evidencias/indicadores_acre.csv), cinco indicadores por turno, mesma versão bruta da fonte. Conferência visual do portal não realizada.
- T3: [inventário de 118 fórmulas](../evidencias/auditoria/inventario_formulas.csv) e [590 comparações](../evidencias/auditoria/equivalencia.csv), sem divergências acima das tolerâncias documentadas. Motor independente, sem Excel nativo.
- Testes de implementação: `python -m unittest discover -s tests -v`. Cobrem entradas inválidas, zero e ausência, parciais, pesos nacionais, logs e preservação em falha. Evidência: [testes_monitor.txt](../evidencias/testes_monitor.txt).
- A equivalência não homologa premissas estatísticas da estimativa nem demonstra atualização atual da apuração. Detalhes em [IMPLEMENTACAO_T2_T3](IMPLEMENTACAO_T2_T3.md).
