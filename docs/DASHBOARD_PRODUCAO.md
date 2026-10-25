# Dashboard de produção — integração e homologação

## Referência visual e limites das alterações
O HTML enviado pelo usuário (`monitor_eleitoral_2026_colaboradores (2).html`) e `site/prototipo-simulacao.html` têm conteúdo textual idêntico após normalização das quebras de linha. O protótipo original foi preservado. A produção reutiliza seus estilos e sidebar, gráfico central, placar à direita, quatro indicadores, resumo por região, tabela e leitura da apuração, três páginas de navegação e autoria.

Adaptações funcionais informadas ao usuário: fonte TSE no lugar do modo fictício; filtros dos dois turnos; consulta de atualização no lugar da geração/reprodução artificial; pontos apenas de snapshots validados; datas de fonte/coleta/publicação; avisos de indisponibilidade, falha e idade. Foram ajustadas larguras dos filtros e rolagem do gráfico em celular para evitar texto cortado. Nenhuma melhoria opcional foi aplicada. As sugestões serão apresentadas somente após disponibilização no Pages.

## Contrato e histórico
`monitor/publicacao.py` transforma os conjuntos já validados em `dist/data/dashboard.json`. Há 29 vistas por eleição: Brasil, 27 UFs e exterior. O Brasil é explicitamente identificado como agregado dos 28 arquivos oficiais; percentuais oficiais usam soma dos votos / soma de v.vvc, não média das UFs. O modelo usa a consolidação existente da planilha; fórmulas e XLSX não foram alterados.

O histórico persistente fica em `dados/historico_dashboard.json`, com eleição, horário da coleta, fonte/hash/IDG por abrangência, valores oficiais e estimados. Uma mesma coleta não é duplicada ao reconstruir o site. Novas coletas válidas geram novos registros, inclusive se a fonte não mudou. Em falha, preserva-se o conjunto anterior e não se fabrica ponto. Antes de 25/10 às 17h, e sem apuração, o gráfico fica vazio. O eixo inicial termina em 26/10 às 00h e se estende após esse horário, sem apagar o início.

O servidor Pages informa a data de publicação via HTTP Last-Modified quando disponível. Ela é exibida separadamente dos horários brutos TSE, da coleta válida e da última tentativa. O cliente sinaliza mais de 30 minutos sem coleta mesmo que nenhuma nova publicação ocorra. Uma falha ao buscar o JSON preserva os dados carregados e mantém o aviso durante mudanças de filtros.

## Evidência visual TSE — Acre
Portal: https://resultados.tse.jus.br/oficial/app/index.html. Navegação observada: eleição 6257/6258, Acre, todos os municípios, Presidente, votação nominal.

| Turno | Lula | Flávio | Comparecimento | Abstenção | Aptos | Referência da tela |
|---|---:|---:|---:|---:|---:|---|
| 1º | 28,73% | 64,56% | 488.330 | 125.412 | 613.742 | 05/10/2026 12:51:05 (totalização) |
| 2º | 0,00% na fonte | 0,00% na fonte | 0 | 0 | 613.715 | 13/10/2026 17:42:47; zero seções totalizadas |

Todos os cinco indicadores coincidiram com os snapshots extraídos. Na produção, os zeros sem apuração se tornam traços/indisponibilidade eleitoral, mantendo aptos e cobertura informativos. A diferença entre hora de geração (`dg/hg`) e totalização (`dt/ht`) é preservada.

Capturas e árvores visíveis: [1º turno](../evidencias/visual/tse_acre_1t.png), [texto observado 1º turno](../evidencias/visual/tse_acre_1t.txt), [2º turno](../evidencias/visual/tse_acre_2t.png), [texto observado 2º turno](../evidencias/visual/tse_acre_2t.txt).

## Testes já executados
- 22 testes Python de implementação, resiliência e publicação, além dos cinco testes T1 existentes.
- Quatro testes JavaScript: ausência versus zero, série sem dados inventados, extensão após meia-noite, falha/indisponibilidade/atraso.
- Desktop 1440 × 1000 e celular 390 × 844: sem overflow horizontal da página. Filtros e busca, ordenação, mudança entre oficial/modelo, metadados e diálogo metodológico conferidos. Escape fecha o diálogo e devolve o foco.
- Falha controlada de API sobre cópia dos dados reais: tela mostrou aviso de falha e manteve 28,73% / 64,56% e 134.770 / 302.807 votos oficiais do Acre. Nenhum valor sintético foi divulgado.
- Falha HTTP 404 da atualização do site: últimos dados carregados preservados; aviso persistiu ao mudar a medida.

Evidências: [testes](../evidencias/testes_dashboard.txt), [desktop](../evidencias/visual/painel_desktop.png), [celular](../evidencias/visual/painel_mobile.png), [falha API](../evidencias/visual/painel_falha.png), [falha de atualização](../evidencias/visual/painel_falha_publicacao.png).

## Publicação e agendamento
Em implementação: o workflow manual existente foi estendido para gerar o dashboard, preservar o histórico por artefatos e publicar o Pages. Em falha da coleta, a versão anterior é publicada com o estado de erro atualizado, e o job termina como falha. Testes inválidos ou restauração incompleta impedem publicação. O agendamento somente será habilitado após comprovar o deploy manual e o acesso público. Não considerar esta seção como comprovação de deploy ou cron.

## Deploy manual e conferência pública — 25/10/2026
- [PR #9](https://github.com/marcelo7bastos/monitor-eleitoral-2026/pull/9) integrado após checks aprovados.
- [Execução manual 40223454439](https://github.com/marcelo7bastos/monitor-eleitoral-2026/actions/runs/40223454439) concluiu testes, restauração, coleta de 28 abrangências, geração e implantação com sucesso.
- [Dashboard público](https://marcelo7bastos.github.io/monitor-eleitoral-2026/): HTTP 200, JSON público conferido, data da publicação informada por Last-Modified.
- Desktop e celular sem overflow da página; alternância de turno/UF/modelo, busca e navegação, metodologia e Escape testados. Nenhum erro JavaScript observado no site público.
- Brasil/1º turno: Lula 45,16% / 53.879.538 votos; Flávio 47,03% / 56.104.503 votos, coincidindo com o portal oficial observado. Acre também conferido. Segundo turno sem totalização é exibido como indisponível eleitoralmente.
- [Captura desktop pública](../evidencias/visual/pages_desktop.png) e [celular público](../evidencias/visual/pages_mobile.png).

Após essa validação, cron de dez minutos preparado em branch da issue #6. As duas execuções automáticas reais e a preservação do histórico ainda precisam ser registradas. O cron do GitHub usa UTC e não garante início pontual; atrasos serão documentados.
