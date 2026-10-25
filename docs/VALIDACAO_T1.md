# T1 — Validação programática do endpoint TSE / Acre

Executado em 25/10/2026, às 14:04:27 e 14:04:30 (America/Sao_Paulo), Python 3.12.4.
Resultado: aprovado para acesso HTTP, JSON e identidade dos dois endpoints abaixo. Não aprova T2, cálculos, atualidade dos dados ou o monitor completo.

| Item | Primeiro turno | Segundo turno |
|---|---|---|
| HTTP | 200 | 200 |
| Content-Type | application/json | application/json |
| ele | 6257 | 6258 |
| t | 1 | 2 |
| tpabr / cdabr | uf / ac | uf / ac |
| carg[0].cd / carg[0].nmn | 1 / Presidente | 1 / Presidente |
| dg / hg da fonte | 05/10/2026 12:51:40 | 13/10/2026 17:42:47 |
| Tamanho recebido | 9293 bytes | 2867 bytes |

## Endereços efetivamente consultados

- https://resultados.tse.jus.br/oficial/ele2026/6257/dados/ac/ac-c0001-e006257-u.json
- https://resultados.tse.jus.br/oficial/ele2026/6258/dados/ac/ac-c0001-e006258-u.json

Ambos responderam sem redirecionamento. As identidades foram lidas do conteúdo, não apenas inferidas do nome do arquivo. Ano 2026 é identificado pelo caminho oficial consultado; os códigos e turnos estão no JSON.

## Reprodução

```powershell
python scripts/teste_t2_acre.py
python scripts/teste_t2_acre.py --eleicao 6258 --turno 2
python -m unittest discover -s scripts -p test_validacao_t1.py -v
```

Os dois comandos de coleta terminaram com código 0. Cinco testes passaram, incluindo subcasos que rejeitam eleição, turno, abrangência, UF ou cargo incorretos, raiz inválida, ausência de cargos e falta de data/hora. Os testes utilizam os snapshots locais recebidos; execute as duas coletas antes de reproduzi-los.

## Evidências locais

- [Relatório 6257](../evidencias/validacao_t1_6257.json)
- [Relatório 6258](../evidencias/validacao_t1_6258.json)
- [Resposta bruta 6257](../evidencias/tse_acre_6257.json)
- [Resposta bruta 6258](../evidencias/tse_acre_6258.json)
- [Resultado dos testes](../evidencias/testes_t1.txt)

Cada relatório contém URL, URL final, horário UTC da coleta, status, tipo de conteúdo, identificadores e SHA-256 dos bytes recebidos. O arquivo bruto conserva os bytes da resposta.

## Correção feita no diagnóstico

A resposta real usa `carg`, não `car`. O script anterior não verificava eleição, turno, UF ou cargo e podia retornar sucesso para um objeto vazio. A versão local agora rejeita identidades diferentes das solicitadas e registra evidências. Ela não implementa a extração dos cinco indicadores de T2.

## Limitações e próximo passo

O segundo turno respondeu com data de geração de 13/10/2026, anterior à coleta de 25/10/2026. Portanto, disponibilidade do endpoint e identidade estão confirmadas, mas não se deve chamar esta resposta de apuração atual de hoje. A mesma distinção vale para o primeiro turno, com data de geração de 05/10/2026. O fuso dos campos de geração não foi inferido.

Próximo passo: T2, mapear e conferir os cinco indicadores do Acre, usando o turno correto e a mesma versão dos dados na comparação com o TSE. Acrescentar a conferência de atualização e cobertura antes de apresentar valores como atuais.

Registro e alterações desta execução permanecem locais. Nenhuma issue foi fechada e nenhuma alteração foi publicada no GitHub nesta execução.
