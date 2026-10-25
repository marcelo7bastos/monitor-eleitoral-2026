# Monitor Eleitoral 2026

MVP para coleta de resultados oficiais do TSE, reprodução de cálculos de uma planilha de estimativa eleitoral em Python, geração de CSV e futura publicação de HTML no GitHub Pages.

**Estado:** protótipo; nenhum teste ponta a ponta homologado. **Próxima ação:** T1, testar conexão programática ao JSON do Acre.

## Referências
- [Projeto Master](PROJETO_MASTER.md): escopo, fases, critérios de sucesso, evidências e situação.
- [Protocolo de testes](docs/TESTES.md)
- [Decisões](docs/DECISOES.md)
- [Backlog](docs/BACKLOG.md)
- [Diagnóstico Python do Acre](scripts/teste_t2_acre.py)

## Execução local
Requer Python 3.9+; sem dependências externas para o diagnóstico inicial.

```bash
python scripts/teste_t2_acre.py
```

O script tenta baixar um JSON do TSE e grava `tse_acre_6257.json` localmente. O arquivo de resposta não é versionado. **A URL e o esquema ainda precisam de validação programática.** Não confundir resultado oficial com estimativa. Não ativar agendamento antes da homologação da coleta e dos cálculos.

Fonte: https://resultados.tse.jus.br/oficial/app/index.html
