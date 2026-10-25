# Registro de decisões (ADR simplificado)

| ID | Decisão | Justificativa | Estado |
|---|---|---|---|
| D-001 | Python como linguagem principal, sem R | Simplicidade e execução no GitHub | Adotada |
| D-002 | Priorizar JSON oficial do TSE, não scraping visual | Rastreabilidade e robustez | Adotada; endpoint em validação |
| D-003 | Primeiro testar Acre, depois expandir | Reduzir variáveis e facilitar diagnóstico | Adotada |
| D-004 | Usar Excel como referência, executar cálculos em Python | Reprodutibilidade sem Excel instalado | Adotada; fórmulas pendentes |
| D-005 | GitHub Actions somente após testes locais | Evitar automatizar extração incorreta | Adotada |
| D-006 | GitHub Pages e CSV como publicação inicial | Infraestrutura mínima | Planejada |
| D-007 | Separar apuração oficial de estimativa | Evitar interpretação enganosa | Obrigatória |
| D-008 | Preservar último snapshot válido em falhas | Integridade da publicação | Planejada |
| D-009 | Repositório público, criado pelo usuário | Transparência e colaboração | Adotada |

Alterações de escopo ou de método devem ser registradas aqui com data, motivo e impacto nos critérios de aceite.
