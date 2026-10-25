# PROJETO MASTER — Monitor Eleitoral 2026

**Versão:** 1.1 · **Atualização:** 25/10/2026 · **Status:** protótipo em homologação · **Repositório:** https://github.com/marcelo7bastos/monitor-eleitoral-2026

## Objetivo
Coletar resultados oficiais das eleições presidenciais de 2026 do TSE, reproduzir em Python os cálculos de estimativa da planilha de referência, produzir CSV/JSON validados e publicar HTML no GitHub Pages, com atualização planejada a cada dez minutos.

**Sucesso do MVP:** coleta manual e automatizada de 27 UFs + exterior (ZZ), cálculos consistentes com a planilha, publicação com horário/fonte e preservação do último conjunto válido quando a coleta falhar. Resultados oficiais e estimativas devem ser diferenciados claramente.

## Escopo e fontes
- Fonte primária: https://resultados.tse.jus.br/oficial/app/index.html
- JSON candidato para teste AC/1º turno: https://resultados.tse.jus.br/oficial/ele2026/6257/dados/ac/ac-c0001-e006257-u.json
- Eleições: 6257 (1º turno) e 6258 (2º turno), **a confirmar programaticamente**.
- Planilha de referência: [estimativa voto 2T.xlsx](https://docs.google.com/spreadsheets/d/1E-mMblCw63jZYxaY1ApmvJdb-dzRvW4w/edit), mantida fora do repositório até revisão de fórmulas e dados.
- Cinco entradas: % Lula, % Flávio Bolsonaro, comparecimento, abstenção, eleitorado apto. 28 abrangências = 27 UFs + ZZ.
- Fora do MVP: R, navegador automatizado, banco de dados, VPS, Power BI.

## Arquitetura pretendida
TSE JSON → Python (coleta, validação e cálculo) → CSV/JSON → GitHub Actions → GitHub Pages.

**Sequência obrigatória:** validar a API → validar os indicadores → validar as fórmulas → expandir para 28 abrangências → testar Actions manualmente → agendar → publicar → homologar.

## Governança de etapas
Uma etapa só está **concluída** se houver evidência verificável (log, arquivo, comparação, commit ou URL) registrada na issue correspondente. Código escrito não equivale a teste aprovado. Estados: pendente, em andamento, bloqueado, aprovado, reprovado.

| Teste | Etapa | Critério de sucesso | Evidência | Estado |
|---|---|---|---|---|
| T1 | Conexão TSE em Python | HTTP 200, JSON válido, eleição/UF corretas | Log e JSON bruto | Em andamento |
| T2 | Cinco indicadores do Acre | Cinco valores mapeados e conferidos contra TSE | Tabela comparativa e fonte | Pendente |
| T3 | Fórmulas Excel → Python | Fórmulas auditadas, paridade nos casos de teste | Inventário de células e testes | Pendente |
| T4 | 28 abrangências | 28 identificadores únicos, dados consistentes, CSV gerado | CSV, validações e log | Pendente |
| T5 | Actions manual | Workflow manual executa coleta/cálculo com sucesso | URL da execução e artefato | Pendente |
| T6 | Agendamento | Cron de 10 minutos habilitado, duas execuções verificadas | URLs e horários | Pendente |
| T7 | GitHub Pages | HTML público, acessível e distinguindo estimativa de apuração | URL e conferência visual | Pendente |
| T8 | Homologação geral | Falha da API não substitui último snapshot válido | Testes de falha e relatório | Pendente |

## Pontos de atenção
- A abertura do JSON no navegador foi observada em captura enviada pelo usuário; não substitui o teste Python.
- Em execução anterior, o ambiente remoto teve falha de DNS. Não atribuir a falha ao TSE.
- Os campos e percentuais do JSON ainda precisam de mapeamento e verificação semântica.
- A planilha apresentava entradas vazias e `#DIV/0!` nos cálculos; fórmulas não estão homologadas.
- Agendamento GitHub Actions não garante execução pontual a cada dez minutos.
- Não versionar dados pessoais, credenciais nem respostas grandes sem necessidade.

## Registro de execução
**25/10/2026:** criado o repositório público e publicada a estrutura inicial. T1 segue em andamento; T2 ainda não homologado. O script de diagnóstico está em `scripts/teste_t2_acre.py`. Nenhum workflow foi habilitado.

## Próximo passo
Executar `python scripts/teste_t2_acre.py` em ambiente com acesso à internet; anexar log e validar estrutura. Somente depois iniciar o mapeamento dos cinco indicadores.

Ver também [TESTES](docs/TESTES.md), [DECISOES](docs/DECISOES.md) e [BACKLOG](docs/BACKLOG.md).
