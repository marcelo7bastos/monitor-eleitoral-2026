# Identidade visual — Monitor Eleitoral 2026

**Versão:** 1.0 (proposta para avaliação)  
**Data:** 25/10/2026  
**Status:** especificação visual, sem implementação ou homologação.  
**Referências:** [MDA](https://www.gov.br/mda/pt-br), [Padrão Digital de Governo](https://www.gov.br/ds/home), [Mobbin](https://mobbin.com/explore/web/screens/best-dashboards), Refero, Page Flows e SaaSFrame.

## 1. Princípio e limites de marca

**Conceito:** “Institucional contemporâneo”: clareza governamental, estética sóbria, dados como protagonistas, ritmo visual leve e acabamento analítico moderno.

O MDA e o gov.br são **referências de linguagem visual**, não endosso institucional do monitor eleitoral. Repositório público independente não deve usar logotipos, assinaturas institucionais ou selos que impliquem publicação oficial sem autorização formal. Mostrar no produto: **“Projeto experimental independente. Fonte dos dados: TSE. Estimativas não são resultados oficiais.”** Se o dashboard se tornar produto formal do MDA, submeter a identidade e as peças à área institucional competente.

**Regras de neutralidade:** nunca atribuir as cores do MDA ou do governo a um candidato. Usar cores analíticas próprias, labels sempre visíveis, escala idêntica e linguagem neutra; não usar fotos de candidatos, slogans, número de urna, símbolos partidários ou cores partidárias na identidade do painel.

## 2. Paleta cromática proposta (não oficial)

| Token | Valor | Uso |
|---|---|---|
| brand-600 | #246B45 | Cabeçalhos, links de navegação e elementos de identidade |
| brand-800 | #174B34 | Títulos destacados, hover do verde |
| brand-100 | #E8F3EB | Superfícies brand suaves, seleção discreta |
| accent-ochre | #D19C31 | Pequenos destaques e elementos auxiliares |
| accent-earth | #765A42 | Acentos secundários e separadores de seções |
| analytical-blue | #2165A3 | Série analítica A, distinta do verde institucional |
| analytical-amber | #9B5C18 | Série analítica B, distinta do verde institucional |
| bg | #F7F9F8 | Fundo geral |
| surface | #FFFFFF | Cartões e tabelas |
| text | #172B25 | Texto principal |
| text-muted | #50615A | Descrição, metadados e legendas |
| border | #D9E2DB | Separadores e contornos discretos |
| error | #B42318 | Erros técnicos, com texto e ícone |
| warning | #8A5A12 | Dados atrasados/incompletos, com texto |
| success | #246B45 | Estado válido, com texto e ícone |

Não usar só cores para comunicar diferenças: sempre nome, símbolo, legenda ou valor numérico. Validar contraste WCAG AA nos pares efetivamente usados (4,5:1 para texto normal, 3:1 para texto grande e componentes).

## 3. Tipografia, iconografia e ritmo

- Família preferencial: **Rawline**, em consonância com o Padrão Digital de Governo; fallback: Arial, Helvetica, sans-serif. Não armazenar/distribuir arquivos de fontes sem examinar licença.
- Título da página: 28–32 px, peso 700; título de seção: 18–20 px, 600; KPI: 26–36 px, 700; texto: 14–16 px; rótulos/metadados: 12–13 px quando legíveis.
- Números tabulares para rankings e comparações; percentuais sempre com padrão único, ex.: 52,37%; quantidades com separador de milhar.
- Ícones lineares discretos de 18–20 px, sempre acompanhados de texto nas ações relevantes.
- Escala de espaço: 4, 8, 12, 16, 24, 32 px. Raio de 8–12 px; borda 1 px; sombra mínima ou ausente.

## 4. Estrutura da tela principal (wireframe)

### Desktop (> 1024 px)
1. **Cabeçalho discreto:** marca textual “Monitor Eleitoral 2026”, identificação de protótipo independente; à direita, fonte TSE, status e última coleta válida.
2. **Barra de filtros:** turno (1º/2º), abrangência (Brasil/UF/exterior), tipo de medida (resultado oficial/estimativa) e horário de referência. Filtros persistentes na página, com indicação clara da seleção.
3. **Linha de indicadores de participação:** eleitorado apto, comparecimento, abstenção, cobertura da apuração. Cobertura só aparece se a fonte fornecer indicador validado.
4. **Área principal de comparação:** dois resultados lado a lado e gráfico horizontal com escala e denominador comuns. Distinguir se são percentuais oficiais apurados ou estimados.
5. **Detalhamento territorial:** gráfico de barras horizontais por UF e tabela analítica de 28 abrangências (colunas definidas abaixo). Mapa não é requisito da primeira versão.
6. **Rodapé de transparência:** fonte, metodologia, status de atualização, download CSV, hora da coleta, hora de referência dos dados e aviso de independência.

### Tabela principal
UF | Lula (%) | Flávio Bolsonaro (%) | Aptos | Comparecimento | Abstenção | Cobertura/status. Colunas de quantidade e percentual alinhadas à direita, UF fixa, busca, ordenação e exportação CSV. Explicitar se a linha exterior ZZ integra a consolidação nacional.

### Mobile (até 640 px)
Sem menu lateral fixo. Cabeçalho compacto, filtros recolhíveis, KPIs em grade de 2 colunas, comparação em linhas empilhadas, gráfico com rolagem/seleção, tabela adaptada por linhas ou rolagem horizontal identificada. Os botões devem ser acionáveis ao toque (alvo recomendado >= 44×44 px).

## 5. Componentes e regras

- **Cabeçalho:** altura aproximada 64–72 px; sem grandes banners, sem imagens decorativas.
- **Cards:** superfície branca, borda #D9E2DB, padding 16–20 px, rótulo acima, valor grande, nota metodológica abaixo.
- **Filtros:** select e segmented control com foco visível, indicação de valor padrão e botão de limpar quando necessário.
- **Gráficos:** eixos legíveis, sem 3D, sem gradientes dramáticos, tooltips também acessíveis por teclado. Representar diferença entre dois candidatos por valor e barra de mesma escala; evitar gráficos pizza para comparações repetidas.
- **Tabela:** zebra opcional muito sutil, cabeçalhos nítidos, colunas numéricas à direita e ordenação explícita; não esconder dados atrás de hover.
- **Estados de sistema:** carregando (texto + indicador), sem dado, desatualizado, parcial, válido e falha; mostrar explicitamente a última coleta validada.
- **Links e botões:** verde institucional nos comandos; botões secundários de contorno; não usar amarelo como botão primário.

## 6. Hierarquia e tratamento de dados

**Separar visualmente:** “Dados oficiais do TSE” de “Estimativas do modelo”. Não misturar séries oficiais e estimadas no mesmo KPI sem um identificador permanente. Exibir sempre o **turno**, a **base de cálculo**, a **fonte**, a **hora de referência** e a **última coleta válida**.

Nunca inventar porcentagens em protótipos publicados; usar traços (—) ou dados sintéticos expressamente identificados. Não supor que os campos aptos/comparecimento/votos válidos tenham o mesmo denominador nem que a cobertura da apuração esteja disponível. Total nacional deve ser calculado com ponderação e metodologia homologada, não média simples entre UFs.

## 7. Exemplo de tokens CSS

~~~css
:root {
  --brand: #246B45; --brand-dark: #174B34;
  --brand-soft: #E8F3EB; --accent: #D19C31;
  --candidate-a: #2165A3; --candidate-b: #9B5C18;
  --background: #F7F9F8; --surface: #FFFFFF;
  --text: #172B25; --muted: #50615A;
  --border: #D9E2DB; --danger: #B42318;
  --radius: 10px; --space-unit: 4px;
  --font-ui: Rawline, Arial, Helvetica, sans-serif;
}
~~~

Os valores são propostos para prototipagem; ajustar após validação visual e testes de contraste.

## 8. Implementação planejada e critérios de aceite visual

**Fase visual V1 — especificação:** aprovar paleta, hierarquia, linguagem de neutralidade e wireframe. Evidência: revisão deste documento.

**V2 — HTML estático sem dados reais:** implementar cabeçalho, filtros, KPIs, comparação, tabela e estados vazios usando tokens; validar desktop e mobile. Evidência: HTML e capturas ou link de preview.

**V3 — integração:** consumir CSV/JSON validados após testes da API e cálculos, exibir horário e status corretamente. Evidência: verificação de igualdade entre valores exibidos e artefatos de dados.

**V4 — homologação visual e acessibilidade:** contraste, teclado, foco, rótulos, leitura móvel, proteção contra informações eleitorais ambíguas. Evidência: checklist de revisão e testes automatizados/manuais.

**Regra de dependência:** as tarefas V1 e V2 podem evoluir sem a API; V3/V4 só podem publicar resultados eleitorais como dados reais depois da aprovação de T1–T4 do Projeto Master.

## 9. Referências e inspiração

- MDA: https://www.gov.br/mda/pt-br
- Padrão Digital de Governo: https://www.gov.br/ds/home
- Fundamentos de tipografia e acessibilidade: https://www.gov.br/ds/fundamentos-visuais/visao-geral
- Mobbin: https://mobbin.com/explore/web/screens/best-dashboards
- Refero: https://refero.design/
- Page Flows: https://pageflows.com/
- SaaSFrame: https://www.saasframe.io/

**Observação:** não se trata de manual oficial de marca do MDA; é uma proposta de design inspirada na linguagem pública brasileira e adaptada à visualização eleitoral.
