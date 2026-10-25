# PROJETO MASTER — Monitor Eleitoral 2026

**Versão:** 1.3 · **Atualização:** 25/10/2026 · **Status:** protótipo em homologação · **Repositório:** https://github.com/marcelo7bastos/monitor-eleitoral-2026

## Objetivo
Coletar resultados oficiais das eleições presidenciais de 2026 do TSE, reproduzir em Python os cálculos de estimativa da planilha de referência, produzir CSV/JSON validados e publicar HTML no GitHub Pages, com atualização planejada a cada dez minutos.

**Sucesso do MVP:** coleta manual e automatizada de 27 UFs + exterior (ZZ), cálculos consistentes com a planilha, publicação com horário/fonte e preservação do último conjunto válido quando a coleta falhar. Resultados oficiais e estimativas devem ser diferenciados claramente.

## Escopo e fontes
- Fonte primária: https://resultados.tse.jus.br/oficial/app/index.html
- JSON validado AC/1º turno: https://resultados.tse.jus.br/oficial/ele2026/6257/dados/ac/ac-c0001-e006257-u.json
- Eleições: 6257 (1º turno) e 6258 (2º turno), **confirmadas programaticamente para Presidente/AC em 25/10/2026**; ver docs/VALIDACAO_T1.md. Atualidade da resposta não homologada.
- Planilha de referência: [estimativa voto 2T.xlsx](https://docs.google.com/spreadsheets/d/1E-mMblCw63jZYxaY1ApmvJdb-dzRvW4w/edit), disponível em `referencias/estimativa voto 2T.xlsx`; original preservado e fórmulas auditadas em docs/IMPLEMENTACAO_T2_T3.md.
- Cinco entradas: % Lula, % Flávio Bolsonaro, comparecimento, abstenção, eleitorado apto. 28 abrangências = 27 UFs + ZZ.
- Fora do MVP: R, navegador automatizado, banco de dados, VPS, Power BI.

## Arquitetura pretendida
TSE JSON → Python (coleta, validação e cálculo) → CSV/JSON → GitHub Actions → GitHub Pages.

**Sequência obrigatória:** validar a API → validar os indicadores → validar as fórmulas → expandir para 28 abrangências → testar Actions manualmente → agendar → publicar → homologar.

## Governança de etapas
Uma etapa só está **concluída** se houver evidência verificável (log, arquivo, comparação, commit ou URL) registrada na issue correspondente. Código escrito não equivale a teste aprovado. Estados: pendente, em andamento, bloqueado, aprovado, reprovado.

| Teste | Etapa | Critério de sucesso | Evidência | Estado |
|---|---|---|---|---|
| T1 | Conexão TSE em Python | HTTP 200, JSON válido, eleição/UF corretas | Log e JSON bruto em evidencias/; docs/VALIDACAO_T1.md | Aprovado localmente |
| T2 | Cinco indicadores do Acre | Cinco valores mapeados e conferidos contra TSE | evidencias/indicadores_acre.csv; conferência programática | Implementado e verificado localmente; visual pendente |
| T3 | Fórmulas Excel → Python | Fórmulas auditadas, paridade nos casos de teste | 118 fórmulas; 590 comparações; docs/IMPLEMENTACAO_T2_T3.md | Equivalência matemática aprovada localmente |
| T4 | 28 abrangências | 28 identificadores únicos, dados consistentes, CSV gerado | 28/28 nos dois turnos, execução local; docs/FALHAS_E_ACTIONS.md | Validado tecnicamente |
| T5 | Actions manual | Workflow manual executa coleta/cálculo com sucesso | Execuções 40217703133 e 40217771870; artefatos inspecionados | Aprovado tecnicamente |
| T6 | Agendamento | Cron de 10 minutos habilitado, duas execuções verificadas | URLs e horários | Pendente |
| T7 | GitHub Pages | HTML público, acessível e distinguindo estimativa de apuração | URL e conferência visual | Pendente |
| T8 | Homologação geral | Falha da API não substitui último snapshot válido | Testes de falha e relatório | Pendente |

## Pontos de atenção
- A abertura do JSON no navegador foi observada em captura enviada pelo usuário; não substitui o teste Python.
- Em execução anterior, o ambiente remoto teve falha de DNS. Não atribuir a falha ao TSE.
- Campos mapeados e validados em monitor/indicadores.py, conforme EA20/2026. Preservar denominadores e unidades documentados.
- A planilha original tem entradas vazias e resultados salvos como `#DIV/0!`. A equivalência das fórmulas foi testada em 590 comparações. A metodologia de estimativa tem limitações documentadas e não equivale a votos oficiais.
- Agendamento GitHub Actions não garante execução pontual a cada dez minutos.
- Não versionar dados pessoais, credenciais nem respostas grandes sem necessidade.

## Registro de execução
**25/10/2026:** criado o repositório público e publicada a estrutura inicial. T1 segue em andamento; T2 ainda não homologado. O script de diagnóstico está em `scripts/teste_t2_acre.py`. Nenhum workflow foi habilitado.

## Próximo passo
Execução manual completa validada no GitHub Actions, incluindo restauração e crescimento do histórico de 28 para 56 registros. Próxima etapa do plano: preparar painel e sua indicação de atualização antes de avaliar agendamento. A metodologia da planilha está aceita pelo usuário; no modelo apenas o rótulo L foi corrigido para PRESENTES ESTIMADOS. Sem cron ou Pages nesta etapa.

Ver também [TESTES](docs/TESTES.md), [DECISOES](docs/DECISOES.md) e [BACKLOG](docs/BACKLOG.md).

## Evidência local adicional — 25/10/2026
T1 aprovado localmente; o registro inicial acima descreve o estado histórico da publicação. Script corrigido para usar carg e validar eleição, turno, cargo e UF. Nenhuma publicação ou fechamento de issue realizado nesta execução. Consulte docs/VALIDACAO_T1.md.


## Implementação local — indicadores, cálculos e logs
25/10/2026: implementados monitor/indicadores.py, monitor/calculos.py e monitor/atualizacao.py. As cinco entradas do Acre são extraídas nos dois turnos e confrontadas com os snapshots oficiais; o segundo turno zerado produz estimativa indisponível. Auditoria da referência e paridade matemática verificadas em motor independente, sem alterar a planilha e sem executar Excel nativo. Histórico CSV registra cada tentativa, data, hora, minuto, fonte, hash e situação. Evidências e limitações: [IMPLEMENTACAO_T2_T3](docs/IMPLEMENTACAO_T2_T3.md). Alterações permanecem locais; nenhuma issue foi fechada e nenhum workflow foi criado.

## Falhas, 28 abrangências e Actions manual — 25/10/2026
Metodologia aceita pelo usuário. Fórmulas preservadas; rótulo L corrigido apenas nos produtos do monitor. Coleta real local passou em 28/28 abrangências nos dois turnos. Testes controlados preservaram o último conjunto e sinalizaram desatualização. Workflow manual criado com persistência por artefatos e execução remota em validação. Consulte [FALHAS_E_ACTIONS](docs/FALHAS_E_ACTIONS.md). Os registros anteriores descrevem os estados históricos das etapas.

## Resultado da execução manual — 25/10/2026
T5 aprovado tecnicamente: execuções [40217703133](https://github.com/marcelo7bastos/monitor-eleitoral-2026/actions/runs/40217703133) e [40217771870](https://github.com/marcelo7bastos/monitor-eleitoral-2026/actions/runs/40217771870), 28 abrangências em cada uma, 24 testes por execução, artefatos conferidos e histórico restaurado com 56 linhas. Testes de falhas controladas aprovados; T8 geral permanece pendente por envolver painel e operação ainda não implementados. Nenhuma issue foi fechada nesta entrega.

## Dashboard de produção — andamento em 25/10/2026
Branch `codex/dashboard-producao`, vinculada à issue #7. Conferência visual T2 concluída no TSE para os dois turnos do Acre. Frontend segue o protótipo aprovado, com dados reais, histórico persistente e avisos de falha. Testes locais passaram. Pages e cron ainda em validação, sem conclusão antecipada. Detalhes: [DASHBOARD_PRODUCAO](docs/DASHBOARD_PRODUCAO.md).

## Pages validado — 25/10/2026
Dashboard disponível em https://marcelo7bastos.github.io/monitor-eleitoral-2026/ após PR #9 e execução manual 40223454439 aprovada. Conferência pública desktop/celular e indicadores oficiais passaram. Etapa seguinte: habilitar cron e observar duas execuções automáticas com restauração do histórico. Evidências em docs/DASHBOARD_PRODUCAO.md.
