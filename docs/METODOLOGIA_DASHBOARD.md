# Metodologia do dashboard — protótipo simulado

**Versão:** 3.0 · **Data:** 25/10/2026 · **Natureza:** demonstração, não apuração ou projeção real.

## 1. Objetivo

Este documento registra as regras de geração dos **dados inteiramente fictícios** usados em `site/prototipo-simulacao.html`. O arquivo HTML apresenta o ícone **i** junto aos campos calculados; cada ícone abre uma janela com fórmula, interpretação e limitação correspondente.

**Atenção:** estas fórmulas reproduzem a simulação visual da interface, **não** as fórmulas da planilha original `estimativa voto 2T.xlsx`, cuja homologação matemática permanece na issue #3.

## 2. Parâmetros e dados sintéticos

O protótipo contém uma tabela no JavaScript com 28 abrangências: 27 UFs e exterior (ZZ). Cada linha define:

- `peso` sintético em milhões para o eleitorado;
- `inclinação` sintética inicial para Lula;
- `taxa_presença` sintética.

Esses parâmetros foram inventados para testar a navegação e os gráficos.

### Quantidades por UF

```text
eleitorado_apto_UF = arredondar(peso_UF * 1.000.000)
comparecimento_UF = arredondar(eleitorado_apto_UF * taxa_presença_UF)
abstenção_UF = eleitorado_apto_UF - comparecimento_UF
fator_válidos_UF = 0,946 + (índice_UF % 6) * 0,004
votos_válidos_UF = arredondar(comparecimento_UF * fator_válidos_UF)
```

O índice é a posição iniciada em 0 na lista sintética de UFs.

## 3. Votos por candidato e agregação

O cenário fictício foi calibrado para uma disputa nacional próxima de 50,64% versus 49,36%:

```text
base_ponderada = soma(válidos_UF * inclinação_UF) / soma(válidos_UF)
ajuste = 0,5064 - base_ponderada
votos_Lula_UF = arredondar(válidos_UF * (inclinação_UF + ajuste))
votos_Flávio_UF = válidos_UF - votos_Lula_UF

% Lula_UF = 100 * votos_Lula_UF / válidos_UF
% Flávio_UF = 100 * votos_Flávio_UF / válidos_UF
```

**Brasil e regiões**: primeiro somam-se votos por candidato e válidos, depois calcula-se o percentual. Nunca se faz a média simples dos percentuais das UFs.

```text
% candidato_abrangência = 100 * soma(votos_candidato_UFs) / soma(válidos_UFs)
```

O exterior integra o agregado Brasil; na contagem de UFs em que cada candidato lidera, ZZ é excluído.

## 4. Histórico sintético

O eixo começa em **25/10/2026 às 17h**. Inicialmente há 42 pontos: 17h00, 17h10, …, 23h50. O gráfico mostra por padrão o intervalo até **00h**, estendendo-o ao adicionar pontos após a meia-noite.

Definições:

```text
base_end = 23h50 = 1430 minutos
start = 17h00 = 1020 minutos
restante = (base_end - minuto) / (base_end - start)
t = (minuto - start) / 60
drift = restante * (-1,18 + 0,55*sen(2,25*t+0,4) + 0,27*sen(5,3*t))
% Lula(t) = % Lula_base + drift
```

Após 23h50:

```text
k = (minuto - base_end) / 10
% Lula(t) = % Lula_base + 0,12*sen(0,75*k) + 0,045*sen(1,83*k)
% Flávio(t) = 100 - % Lula(t)
```

Os percentuais são limitados por código ao intervalo [0,5%; 99,5%] para evitar curvas impossíveis. A base de votos válidos permanece fixa na animação. Cada clique em `+10 min` simula um novo ponto. `Reproduzir` avança rapidamente e **não consulta o TSE**.

```text
votos_Lula(t) = arredondar(válidos_base * % Lula(t) / 100)
votos_Flávio(t) = válidos_base - votos_Lula(t)
diferença_pontos_percentuais(t) = |% Lula(t) - % Flávio(t)|
diferença_votos(t) = |votos_Lula(t) - votos_Flávio(t)|
taxa_comparecimento = 100 * comparecimento / aptos
taxa_abstenção = 100 * abstenção / aptos
```

A escala vertical se ajusta aos valores da série e **não começa obrigatoriamente em zero**; eixos indicam os limites usados.

## 5. Regras de leitura

- Os cartões de percentual nacional/UF e gráfico usam o **último ponto do histórico**.
- Os indicadores de participação e a tabela territorial exibem o **cenário-base**.
- O gráfico regional também apresenta o **cenário-base**, não a série temporal.
- Percentuais exibidos têm em geral duas casas decimais; taxas de participação e regiões têm uma. Quantidades podem aparecer abreviadas em mil/mi.
- Símbolos e cores não constituem endosso institucional ou identificação partidária.

## 6. Próxima integração

A metodologia fictícia será substituída/adequada conforme contrato de dados oficial, fórmulas homologadas do Excel e testes do Projeto Master. Em especial, no mundo real os votos válidos e eleitorado apto não podem ser tratados como fixos no processo de apuração sem evidência compatível.

## 7. Colaboradores e natureza do projeto

A barra lateral, acima de **Modo de demonstração**, identifica **Marcelo Cabreira Bastos** (desenvolvimento e análise) e **Ernesto Galindo** (colaborador). Os links ORCID, LinkedIn, site pessoal e GitHub são apresentados somente para Marcelo. ORCID confirmado pelo próprio usuário: https://orcid.org/0009-0002-4215-3446.

**Privacidade:** não exibir e-mail, telefone ou outros dados pessoais/profissionais de Ernesto. O projeto é pessoal e independente; a referência estética ao MDA não significa endosso institucional. Aviso solicitado no painel: **“Este não é um sistema oficial do TSE”**.

## 8. Selo de margem de cenário (produção)

Exibido no cabeçalho da coluna "Nossa estimativa" do placar, ao lado do selo de estado. Calculado no navegador (`margemCenario`, em `site/dashboard.js`) a partir da `cobertura` já publicada (seções totalizadas ÷ total de seções). Não altera dados, fórmulas da planilha nem valores oficiais.

| Seções apuradas | Selo | Margem (δ = 10 p.p.) |
|---|---|---|
| menos de 25% | Apuração inicial · sem margem | — |
| 25% a 50% | faixa ampla | ± 7,5 p.p. |
| 50% a 75% | moderada | ± 5,0 p.p. |
| 75% a 99,99% | estreita | ± 2,5 p.p. |
| 100% | Apuração completa | — |

Regra: margem = (1 − piso da faixa) × δ. Usar o piso da faixa dá o pior caso dentro dela e evita que o número oscile a cada coleta. Estimativa parcial do Brasil (nem todas as UFs com dados): "Sem margem". Sem estimativa ou sem cobertura: o selo não aparece.

Limites: δ é uma suposição explícita (quanto o restante a apurar pode divergir do já apurado), não um valor medido; não é intervalo de confiança estatístico; a fração por seções ignora que elas têm eleitorados diferentes; não corrige o viés da fórmula da planilha. A calibração de δ e das faixas com o histórico de coletas fica para depois da apuração (issue #21).
