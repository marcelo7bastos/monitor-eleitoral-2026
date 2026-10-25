# Metodologia aceita, falhas e Actions manual

## Decisão do usuário — 25/10/2026

A metodologia da planilha foi aceita. As fórmulas, os denominadores, os pesos e os arredondamentos foram preservados. A única correção metodológica de apresentação é o rótulo **PRESENTES ESTIMADOS** para a saída L. O XLSX de referência permanece intacto; os rótulos corrigidos estão nos JSON/CSV produzidos pelo monitor.

## Preservação e desatualização

`python -m monitor.pipeline --eleicao 6258` coleta as 27 UFs e o exterior (ZZ), valida a identidade de cada resposta e executa os mesmos cálculos da planilha.

- `dados/conjunto_<eleicao>.json` é o conjunto autoritativo aceito, contendo exatamente as 28 abrangências. O CSV de mesmo nome é sua exportação derivada.
- Se uma abrangência falhar, o conjunto JSON e o CSV anteriores permanecem inalterados. As coletas individuais e o log da tentativa são preservados para diagnóstico.
- `dados/estado_conjunto_<eleicao>.json` informa sucesso/falha, abrangências com erro, última tentativa, última coleta válida, disponibilidade do conjunto, preservação e aviso de desatualização.
- Os estados individuais ficam em `dados/abrangencias/estado_<uf>_<eleicao>.json`.
- O log cumulativo fica em `dados/abrangencias/logs/atualizacoes.csv`, com data, hora, minuto, fuso, identificadores, fonte, hash e erro. Cada execução completa acrescenta 28 linhas, inclusive em falha.
- Sem conjunto anterior válido, o sistema informa indisponibilidade. Não fabrica um conjunto nacional de zeros.
- Fonte com mais de 30 minutos gera aviso operacional de idade. O horário bruto da fonte é preservado; para esse aviso assume-se UTC-03:00. Um resultado histórico finalizado pode naturalmente ter horário antigo.

Os testes controlados usam dados fictícios derivados de fixtures em diretórios temporários. Cobrem timeout, DNS, HTTP 503, JSON inválido, campo obrigatório ausente, identidade incorreta, resposta regressiva, fonte antiga, falha parcial com preservação byte a byte de JSON/CSV e primeira execução sem fonte disponível. Evidência local: [testes_resiliencia.txt](../evidencias/testes_resiliencia.txt). A metodologia matemática não foi alterada para contornar qualquer falha.

## Workflow manual

[Monitor eleitoral - manual](https://github.com/marcelo7bastos/monitor-eleitoral-2026/actions/workflows/monitor-manual.yml) tem apenas `workflow_dispatch`. Não há cron, deploy de Pages nem publicação de painel.

Entrada: eleição `6257` ou `6258`. O job executa os testes, recupera o último artefato `monitor-estado`, coleta as 28 abrangências, calcula, gera JSON/CSV e grava estado/logs. O resumo mostra avisos de desatualização e o estado da consolidação. Fonte zerada válida pode concluir a coleta com consolidação indisponível; isso é explicitado no resumo.

O artefato `monitor-estado` é reenviado inclusive quando a coleta falha; contém os últimos dados aceitos, o estado atual e o histórico. O artefato `monitor-testes` guarda o log dos testes. A retenção configurada é de 90 dias, sujeita ao limite do GitHub; não é um backup permanente. Se o download de um artefato existente falhar, o job interrompe sem publicar um estado vazio substituto.

O grupo de concorrência único impede duas coletas remotas simultâneas. A restauração em uma segunda execução deve ser verificada nos logs e no crescimento da tabela de histórico. O primeiro artefato remoto inicia um histórico novo: os logs locais antigos continuam arquivados nas evidências e não são apresentados como coletas do runner.

Para disparar: Actions → Monitor eleitoral - manual → Run workflow → escolher eleição → Run workflow. As execuções e os artefatos reais serão registrados abaixo após conferência.

## Evidências de execução remota

Em validação. Não considerar a existência do YAML como aprovação da execução.
