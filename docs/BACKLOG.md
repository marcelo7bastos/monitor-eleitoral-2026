# Backlog de testes

Issues do repositório são o quadro operacional; este arquivo documenta a ordem e as dependências.

| Teste | Entrega | Dependência |
|---|---|---|
| T1 | Conexão programática com JSON do Acre | Nenhuma |
| T2 | Cinco indicadores conferidos | T1 |
| T3 | Fórmulas Excel auditadas e replicadas | Planilha disponível; pode ocorrer paralelamente ao T2 |
| T4 | CSV de 28 abrangências | T2 e T3 |
| T5 | Workflow Actions manual | T4 |
| T6 | Cron de 10 minutos | T5 |
| T7 | HTML GitHub Pages | T4 e T5 |
| T8 | Homologação ponta a ponta e falhas | T5, T6, T7 |

Não fechar issues sem evidências registradas. Não criar workflow de produção antes da aprovação da coleta e dos cálculos.
