# Monitor Eleitoral 2026

MVP para coleta de resultados oficiais do TSE, reprodução de cálculos de uma planilha de estimativa eleitoral em Python, geração de CSV e futura publicação de HTML no GitHub Pages.

**Estado local:** coleta do Acre, cálculos equivalentes à planilha e logs implementados e testados. A homologação ponta a ponta permanece pendente. **Etapa atual:** validar o workflow manual completo nas 28 abrangências.

## Referências
- [Projeto Master](PROJETO_MASTER.md): escopo, fases, critérios de sucesso, evidências e situação.
- [Protocolo de testes](docs/TESTES.md)
- [Decisões](docs/DECISOES.md)
- [Backlog](docs/BACKLOG.md)
- [Identidade visual do dashboard — proposta v1.0](docs/IDENTIDADE_VISUAL.md)
- [Implementação T2/T3, auditoria e logs](docs/IMPLEMENTACAO_T2_T3.md)
- [Diagnóstico Python do Acre](scripts/teste_t2_acre.py)

## Execução local
Requer Python 3.9+; sem dependências externas para o diagnóstico inicial.

```bash
python -m monitor.pipeline --eleicao 6258
python -m unittest discover -s tests -v
```

A coleta grava `dados/acre_6258.json`, snapshots por hash e a tabela `dados/logs/atualizacoes.csv` com data, hora, minuto e situação de cada tentativa. Use `--eleicao 6257` para primeiro turno e `--entrada caminho.json` para reprocessar um arquivo local, identificado como tal no log.

Os resultados oficiais e o modelo da planilha ficam separados. Denominador zero ou entradas ausentes deixam a estimativa indisponível. A resposta do segundo turno verificada estava sem totalização; não a interpretar como apuração atual. Não ativar agendamento antes da validação das próximas etapas.

Fonte: https://resultados.tse.jus.br/oficial/app/index.html

## Falhas e execução manual
A metodologia da planilha está aceita; a saída L chama-se **PRESENTES ESTIMADOS**. O monitor coleta 27 UFs + exterior, preserva o último conjunto válido em falha e sinaliza desatualização em um arquivo de estado separado. [Procedimento, logs e evidências de Actions](docs/FALHAS_E_ACTIONS.md). Disparo apenas manual, sem agendamento ou deploy.
