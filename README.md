# Monitor Eleitoral 2026

MVP para coleta de resultados oficiais do TSE, reprodução de cálculos de uma planilha de estimativa eleitoral em Python, geração de CSV e futura publicação de HTML no GitHub Pages.

**Estado:** coleta de 27 UFs + exterior, cálculos da planilha e logs implementados. Workflow manual validado em duas execuções reais, com histórico preservado. A homologação geral e o painel permanecem pendentes.

## Referências
- [Projeto Master](PROJETO_MASTER.md): escopo, fases, critérios de sucesso, evidências e situação.
- [Protocolo de testes](docs/TESTES.md)
- [Decisões](docs/DECISOES.md)
- [Backlog](docs/BACKLOG.md)
- [Identidade visual do dashboard — proposta v1.0](docs/IDENTIDADE_VISUAL.md)
- [Implementação T2/T3, auditoria e logs](docs/IMPLEMENTACAO_T2_T3.md)
- [Diagnóstico Python do Acre](scripts/teste_t2_acre.py)

## Protótipo visual (dados inteiramente fictícios)
- [Dashboard HTML — versão 3](site/prototipo-simulacao.html): linha do tempo de 17h a 00h, extensão após meia-noite, percentuais simulados e placar à direita.
- Não está publicado em GitHub Pages nem conectado à API do TSE. Para testar, baixar o HTML e abrir no navegador.

- [Metodologia do protótipo](docs/METODOLOGIA_DASHBOARD.md): fórmulas sintéticas e limites da série temporal.\n\n## Execução local
Requer Python 3.9+; sem dependências externas para o diagnóstico inicial.

```bash
python -m monitor.pipeline --eleicao 6258
python -m unittest discover -s tests -v
```

A coleta grava `dados/conjunto_6258.json`, `dados/conjunto_6258.csv`, estado de atualização em `dados/estado_conjunto_6258.json` e logs em `dados/abrangencias/logs/atualizacoes.csv`. Use `--eleicao 6257` para primeiro turno. Uma falha parcial preserva o último conjunto completo e sinaliza desatualização. Para reprocessar um arquivo individual, utilize `python -m monitor.atualizacao --entrada caminho.json --eleicao 6257`.

Os resultados oficiais e o modelo da planilha ficam separados. Denominador zero ou entradas ausentes deixam a estimativa indisponível. A resposta do segundo turno verificada estava sem totalização; não a interpretar como apuração atual. Não ativar agendamento antes da validação das próximas etapas.

Fonte: https://resultados.tse.jus.br/oficial/app/index.html

## Falhas e execução manual
A metodologia da planilha está aceita; a saída L chama-se **PRESENTES ESTIMADOS**. O monitor coleta 27 UFs + exterior, preserva o último conjunto válido em falha e sinaliza desatualização em um arquivo de estado separado. [Procedimento, logs e evidências de Actions](docs/FALHAS_E_ACTIONS.md). Disparo apenas manual, sem agendamento ou deploy.

Execuções verificadas: [segundo turno](https://github.com/marcelo7bastos/monitor-eleitoral-2026/actions/runs/40217703133) e [primeiro turno](https://github.com/marcelo7bastos/monitor-eleitoral-2026/actions/runs/40217771870). A segunda recuperou o estado da primeira e acumulou 56 registros de atualização.
