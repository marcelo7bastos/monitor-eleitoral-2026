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

## Decisões de implementação local — 25/10/2026
- D-010: tabela de logs em CSV (`;`, UTF-8 BOM), sem banco de dados; preservar início/fim UTC, data/hora/minuto local e os horários brutos da fonte. Persistência entre runners será tratada em T5.
- D-011: reproduzir integralmente as fórmulas da referência, expondo suas limitações. L calcula presentes estimados, sem descontar votos brancos/nulos. Não confundir paridade matemática com validação da metodologia.
- D-012: usar `pvapn / 100` como fração para o cálculo e preservar `pvap` para a conferência de exibição. Selecionar candidatos por número e sequencial.
- D-013: falta de entrada ou denominador zero gera estado indisponível; não preencher abrangências ausentes com zero para produzir resultado nacional.
- D-014: horário de coleta em America/Sao_Paulo, UTC-03:00 em 2026. Os campos brutos TSE não têm fuso explícito no EA20 consultado; assumir UTC-03:00 apenas para o aviso operacional de idade, sem alterar a fonte.

## Aceite e execução manual — 25/10/2026
- D-015: usuário aceitou a metodologia da planilha. Preservar fórmulas e alterar apenas o rótulo L para PRESENTES ESTIMADOS no modelo, sem modificar o XLSX original.
- D-016: aceitar um conjunto nacional somente com 28 abrangências válidas. Falha parcial preserva o conjunto anterior; estado de desatualização é gravado separadamente.
- D-017: Actions somente manual; persistir dados e logs por artefatos por até 90 dias e serializar execuções. Não habilitar cron ou Pages nesta entrega.

## Composição do dashboard — 25/10/2026
- D-018: colaboradores Marcelo Cabreira Bastos e Ernesto Galindo apresentados na barra lateral acima do modo demonstração. Apenas links profissionais do Marcelo (incluindo ORCID 0009-0002-4215-3446); não incluir e-mail ou telefone de Ernesto. Mensagem de responsabilidade: “Este não é um sistema oficial do TSE”.
