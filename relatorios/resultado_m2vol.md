# M2: aumento de volume (04/11/2026)

**Dados e período:** WIN M5 de 2022 a 2026, custo de 15 pts, 1 contrato. Scripts em `m2vol/lab*.py` e `r1..r6.py`. Ideias de Opus e Sonnet em `ideias_*.md`.

**Base:** 616 entradas (2,45 por semana), PF 1,35, R$13.420, DD −1.414. Pior ano: PF 1,14.

## Reprovados (mais entradas, mas pioram)
- **Faixa de gap mais larga (0–2,0 ATR):** +31% de entradas, PF 1,29, 2024 com PF 1,02.
- **Teto de R$300, sem teto ou stop limitado:** as operações de dias de vol alta perdem.
- **Outro stop (0,2/0,25/0,4/0,5 ATR) e stop estrutural (extremo da 1ª hora):** todos piores.
- **Outro horário único (9:05–11:00):** todos piores. O das 10h é o melhor.
- **Várias entradas por dia** (10h + 11h, checkpoints, a cada 15 min): PF cai para 1,11–1,26.
- **Re-entrada depois do stop:** as re-entradas perdem (PF 0,76–1,08).
- **Gap pequeno com extensão na 1ª hora:** perde (PF 0,8).
- **Filtro de volume da 1ª hora; só depois de fim de semana; só gap dentro do range anterior:** nenhum melhora.
- **Escalonar +1 contrato contra a posição:** equivale a dobrar o tamanho, sem ganho de qualidade.

## Aprovados como candidatos (falta o Testador)
1. **Tamanho pelo preenchimento do gap às 9:55**
   - f = (abertura − preço 9:55)/gap.
   - f ≥ 0 (o gap já começou a voltar): 2 contratos. PF dessas operações ~1,7.
   - f < 0 (o gap esticou): 1 contrato. PF 1,17.
   - Resultado: 856 contratos, PF 1,43, R$22.583, DD −2.071. Todos os anos melhoram: 1,16 / 1,31 / 1,26 / 1,96 / 1,94.
2. **M2 Tarde, só nos dias sem M2 de manhã**
   - Regra: às 13:10, se 0,2 ≤ |preço − fechamento anterior|/ATRd ≤ 1,0, entra contra o desvio. Stop de 0,3 ATRd (teto de R$200), saída às 17:05.
   - Sozinho: 289 operações, PF 1,36, R$4.075. 2023 dá PF 0,93.
   - Grade de 40 pontos: soma lucro em 39 deles, mas a tarde sozinha tem algum ano abaixo de 1 em quase todos.
   - Região estável: 13:10–13:30, desvio de 0,2–0,3.
3. **Juntos (M2 v2):**
   - 905 entradas (3,6 por semana, +47%) e 1.145 contratos.
   - PF 1,42, R$26.658 (×2,0), DD −2.108, 66% dos meses positivos.
   - PF por ano: 1,18 / 1,25 / 1,26 / 1,86 / 1,98.
   - Comparação: dobrar o M2 base dá o mesmo lucro com DD −2.827.

**Atenção:** as regras novas foram escolhidas olhando 2022–26, então não há validação fora da amostra. Próximo passo: testar no Testador e depois rodar pequeno.

O bloqueio na vol alta continua. Nenhuma variante ganha dinheiro com ATRd acima de ~3.300.

## Rodada 2 (04/11, 22h), M2 v2 congelado
- **Vol alta, liberando o teto só quando o gap já voltou:** os 16 dias extras perdem (PF 0,24). Continua bloqueado.
- **Cruzamento do tamanho do gap (z) com o preenchimento:** buckets pequenos e instáveis entre si. Não refinar, porque é risco de overfitting.
- **Stop e saída só para o gap que já voltou:** k=0,35 e saída às 15h parecem melhores, mas são variações pequenas. Não mudar.
- **Entrada às 9:30 ou 9:45 no gap que já voltou:** pior.
- **M2 Tarde nos dias em que a manhã foi estopada:** PF 0,77, perde. Confirma a regra "só nos dias sem M2 de manhã".
- **Ações:** o fade não tem vantagem nem antes do custo (`grade/resultado_acoes.md`). O mecanismo do M2 é o WIN abrir 1h antes do à vista.
- **Próximos passos:**
  - histórico antigo do WIN (`out/PROMPT_CLAUDE_CODE_21_HISTORICO.md`) para validação fora da amostra;
  - revisão do GPT (`out/BRIEF_GPT_M2.md`).

## Rodada 3 (04/11, 22h): críticas e ideias do GPT (`gpt1.py`, `gpt2.py`, `gpt3.py`)
**De onde vem o ganho do v2 (R$26.658 no total):**
- base: R$13.420;
- dobra: +R$9.163;
- tarde: +R$4.075.

**Dobra (2 contratos quando f ≥ 0):**
- Controle com o 2º contrato em dias sorteados (5.000 sorteios com o mesmo número de dias): média de R$5.205; o p95 fica em R$8.891, abaixo do real. p = 0,038.
- Deslocar o corte em ±5, ±25 ou ±50 pts quase não muda nada (R$21,8–23,0 mil).
- Bootstrap em blocos de 10 pregões: IC95 de +2,9 a +12,7 R$/pregão.
- **Validado dentro da amostra.**

**Tarde:**
- Bootstrap: IC95 de +0,2 a +7,3 R$/pregão. Positivo, mas por pouco.
- Por motivo de ficar fora de manhã: "gap pequeno" 222 operações, PF 1,26; "gap já fechou" 64 operações, PF 2,08; "gap grande" 3 operações, perde.

**Ganho total do v2 sobre a base (bootstrap):** IC95 de +5,4 a +17,0 R$/pregão, com blocos de 5, 10 ou 20.

**Custo estressado:**

| Custo | PF base | PF v2 |
|---|---|---|
| 30 pts | 1,29 | 1,36 |
| 45 pts | 1,24 | 1,30 |

**Hipóteses do GPT:**

| Hipótese | Resultado |
|---|---|
| H1: âncora às 16:50 | 152 operações, PF 0,74. Reprovada. |
| H2: excesso do WIN sobre o BOVA11 | Nenhum sinal. O excesso fica em 0,03 ATR na mediana e 0,12 no p99, nunca chega a 0,2. O futuro não descola do à vista. |
| H3: gap fecha e reabre | 8 operações, insuficiente. |
| H4: impulso do almoço | 2 operações, insuficiente. |
| H5: sair quando o gap fecha | Já testado: PF 1,21, pior. |
| H6: amplitude dos papéis do índice | Precisa de dados que não temos. |
| H7: ordem passiva | Precisa do book. |
| H8: esticou e devolveu até a metade | 104 operações, PF 1,16, igual aos outros f < 0. Reprovada. |

**Volatilidade relativa (ATR/preço):** um teto em ATR% de 2,2–2,5% equivale ao teto de R$200. O ATR% de hoje é ~2,56%, acima do p95 histórico (2,33%). É regime extremo: ficar fora.

## Rodada 4 (04/11, 22h30): novos caminhos (`m2vol/eu/c1.py`)
- **Vol alta (dias bloqueados pelo teto):**
  - fade: PF 0,97 (47 operações, 43 delas em 2026), quase zero a zero;
  - a favor do gap: PF 0,58, perde;
  - ATR% acima de 2,2%: fade PF 0,81, a favor PF 1,14 (65 operações, instável).
  - Nada aproveitável.
- **Gap maior que 1 ATR:** só 12 casos. O fade dá PF 3,3, amostra pequena demais.
- **Gap esticado (f < 0) operado a favor:** PF 0,96. Reprovado.
- **Em paralelo:**
  - agente A: M2 v2 em WDO, ações, IND e IVVB11 (`m2vol/agenteA/`);
  - agente B: "gap residual" explicado por WDO e IVVB11 (`m2vol/agenteB/`).
- **Agente A (outros ativos):** só o IND passa, e é o mesmo WIN.
  - Reprovados: WDO, cesta de ações, BOVA11, IVVB11 e o sinal do WIN executado em ações.
  - Nas ações, o filtro f ≥ 0 cria vantagem bruta (PF 1,12 antes do custo), mas o custo de 0,06% consome. Detalhes em `agenteA/relatorio.md`.
- **BIT futuro × spot (base na abertura das 9:00)** (`cripto_b3/bit_basis.py`):
  - o desvio da abertura tem desvio-padrão de ~40 bps;
  - o fade do desvio tem PF ~1,0 ANTES do custo e 0,5 depois. Sem vantagem.
  - Contrato BIT = 0,01 BTC (tick de 20 = R$0,20). ETR e SOL são cotados em US$ e quase não têm negócios (1 contrato por barra).
- **Small caps:** pedidas ao Code (`out/PROMPT_CLAUDE_CODE_22_SMALLCAPS.md`). Custo a usar: 0,10% ida e volta.
- **Agente B (gap residual WDO/IVVB11):** nada aprovado.
  - O gap pouco explicado pelo dólar reverte mais, mas só quando f < 0.
  - R_A (2 contratos quando f < 0 e resíduo/gap ≥ 0,5): R$32.150, PF 1,42, placebo p = 0,03, mas só 7 de 15 pontos da grade passam. Candidato fraco, guardado.
  - Com o IVVB11, a entrada só pode ser às 10:10, e o M2 perde força nesse horário.
  - Detalhes em `agenteB/relatorio.md`.
- **Small caps** (50 papéis com volume ≥ R$15 mi/dia, M5 2022–26, `small/sc.py`):

| Variante | Operações | PF bruto | PF a 0,10% de custo | PF a 0,06% de custo |
|---|---|---|---|---|
| Original às 11:00 | 22.987 | 1,03 | 0,87 | — |
| v2 às 10:30 com f ≥ 0 | 9.549 | 1,13 | 0,96 | 1,03 |
| v2 às 11:00 com f ≥ 0 | — | 1,04 | 0,87 | — |
| f < 0 | — | 1,04 | 0,89 | — |
| Tarde | — | 1,03 | 0,84 | — |

  - v2 às 10:30 com f ≥ 0, a 0,06% de custo, por ano: 2022 1,16, 2023 1,06, 2024 1,08, 2025 0,96, 2026 0,88. A vantagem está caindo nos anos recentes.
  - Nenhum papel passa sozinho: todos têm algum ano abaixo de 1.
  - **Reprovado.** A vantagem bruta existe, mas é pequena e o custo come.

## Rodada 5 (04/11, 22h45)
- **Calendário** (`eu/c2.py`): dia da semana, 1ª sexta, dia seguinte ao vencimento, dia do mês e mês. As diferenças são ruído, com amostras pequenas e sem padrão econômico claro.
- **Dia seguinte a Copom/FOMC** (2022–25): f < 0 dá PF 0,63 (15 operações); f ≥ 0 dá PF 3,90 (13 operações). Faz sentido (o gap traz informação), mas a amostra é pequena. Fica em observação.
- **Em paralelo:**
  - agente C: gap idiossincrático e lead-lag nas ações (`agenteC/`);
  - agente D: precisão de minuto em M1, curva intradiária, janela do fim do dia e gestão (`agenteD/`);
  - GPT: dados reais (`gpt_pack_M2.zip`);
  - Code: rodada 20 com ticks reais.

## Consolidado da rodada 5 (04/11, 23h30)
- **Agente D (M1, minuto a minuto):** nenhuma mudança no M2 v2.
  - A vantagem está no leilão das 10:00 e nos ~5 minutos seguintes.
  - Do lucro, 43% sai até 11h e 86% até 13h. Sair cedo piora.
  - Manhã curta + tarde em todos os dias: PF 1,12–1,31. Reprovado.
  - Gestão (parcial, break-even, trailing): piora.
  - Candidato fraco **"M2 Noturno"**: fade do movimento do WIN entre o fechamento do à vista e 18:19, com entrada às 18:20 e saída no 1º negócio do dia seguinte.
    - Sozinho: PF 2,30, R$6.350, 0,63 entrada por semana.
    - Somado ao v2: +5,3 R$/pregão (IC95 [2,7; 8,0]).
    - Só 28% da grade passa, por causa da eleição (02→05/10/2026, −R$3.558). Só em papel, com filtro de eventos.
- **Agente C (ações):** **"Ação atrasada"** APROVADA no critério formal.
  - Regra: às 10:05, opera a small cap que ficou para trás do WIN da 1ª hora, na direção do WIN. Gap residual entre 0,25 e 1,2 ATRd, hedge no WIN, stop de 1,0 ATRd, saída às 16:55.
  - 1.659 operações, 6,8 por semana, PF 1,36 depois do custo, todos os anos ≥ 1,21, DD −991, correlação 0 com o M2.
  - Walk-forward 2024–26: PF 1,26–1,43.
  - Ressalvas: muito sensível à execução (10:10 → PF 1,18; +1 tick → 1,16); sinal enfraquecendo; viés de sobrevivência na lista de 50.
  - Detalhes em `agenteC/relatorio.md`.
- **GPT, rodada 2, com os dados reais** (`m2vol/gpt_r2/`):
  - Replicou o M2 v2 de forma independente: 905 entradas, R$26.657,77, PF 1,421, DD −2.108. PF por ano: 1,18 / 1,25 / 1,26 / 1,86 / 1,98.
  - Atribuição do ganho por pregão (IC95):
    - manhã: R$11,12 [4,40; 18,31];
    - 2º contrato: R$7,59 [2,92; 12,62];
    - tarde: R$3,38 [−0,02; 7,06], com perda de R$164 em 2023.
  - Estresse (entrada 5 min atrasada, stop no tick, preenchimento pior no gap): R$22.977, PF 1,35, todos os anos positivos.
  - 30 hipóteses e 264 configurações: todas reprovadas.
  - Decisão do GPT: manter o v2 como referência.

## Inventário do MT5 (04/11, 23h30), em `m2vol/doc/Doc/inventario_mt5/`
- **Ticks do WIN$ desde 03/2023** (~3,4 GB, preço real) e do WIN$N desde 01/2026. Com eles dá para medir a execução real às 10:00/10:05 (rodada 23).
- **Calendário econômico:** 56 mil eventos de 2019 a 2027 (`apex_calendario_economico.csv`).
  - Dia seguinte ao Copom: esticado PF 0,74 (13 operações), tarde PF 0,49 (6 operações), voltando PF 3,2 (8 operações).
  - Amostras pequenas. Só observação.
- **Já existe um coletor de book** (service ApexColetorBook), de outro projeto, com poucos dados.
- Não há opções no disco.

## GPT, rodada 3 (04/11, 23h30), em `m2vol/gpt_r3/`
- Nenhuma alteração passou em todos os critérios. O M2 v2 segue como referência; o Noturno ficou fora (13 de 54 pontos da grade; o gap de 23→26/10 perde até R$6.215 por WIN).
- **M2-A com lotes inteiros e hedge em WIN inteiro, 2024–26:**

| Versão | PF |
|---|---|
| Saída às 16:50 | 1,54 |
| Saída às 16:45 | 1,52 |
| Entrada 5 min atrasada | 1,25 |
| 1 tick adverso na entrada | 1,19 |
| Universo de 61 ativos | 1,49 |
| Melhor configuração escolhida só com 2022–23, testada em 2024–26 | 1,23 (1,05 com atraso e custo +50%) |

  - P&L de R$6.359 a R$6.478.
  - O GPT recomenda a saída às 16:45 no simulador.
- **Carteira 2024–26:**

| Carteira | P&L | DD |
|---|---|---|
| M2 v2 | R$19.676 | −R$1.893 |
| + M2-A | R$26.154 | −R$1.909 |
| + Noturno | R$30.207 | −R$1.945 |

- **Tamanho:**
  - 2º contrato com placebo pareado: p = 0,070. Começar com 1 lote.
  - ¼ de Kelly do v2: 3,4% (central) e 1,5% (limite inferior).
  - 1 WIN pede orçamento de R$203 por operação; com 2% de risco, uma banca de R$10.150.
  - v2 + M2-A na escala testada: risco somado de R$1.298 num pregão, o que pede ~R$65 mil com limite diário de 2%.
  - Garantia alocada no day trade de mais de R$290 por WIN, por causa da regra dos 70%.

## Agente E: volume do M2-A (05/11, madrugada), em `m2vol/agenteE/`
- **V6 aprovada:** M2-A com limiar de 0,25, sem o filtro de força do WIN (wmin = 0).
  - Volume: 9,0 operações por semana (10,2 em 2024–26), n = 2.181.
  - Resultado: PF 1,31 (1,54 antes do custo), R$10.834 com risco de R$80, DD −996.
  - PF por ano: 1,38 / 1,37 / 1,30 / 1,23 / 1,34.
  - Estresse: entrada atrasada 1,16; +1 tick 1,11.
  - Grade: 81 de 81 pontos passam. Walk-forward 2024–26: 1,29.
- **Reprovados:**
  - limiar 0,20: as operações acrescentadas perdem em 2026;
  - limiar 0,15 ou 0,10;
  - ETFs: o SMAL11 não atrasa;
  - escolher só as melhores ações do dia.
- **Liquidez:** a vantagem bruta é estável em R$5–300 mi/dia e some acima de R$300 mi. Isso define o universo para expandir.
- **Hedge com WIN inteiro:** com R$80 de risco por operação, arredonda para zero em 87% dos dias. Precisa de risco ≥ R$300 por operação.
- **Pipeline:** `rodar_universo.py`, usar com `--pf_min_treino 1.35`. Com ~200 papéis, a estimativa é de ~35 operações por semana.

## GPT, rodada 4: "M2 Duas Janelas" (05/11), em `m2vol/gpt_r4/`
- **Regras:**
  - manhã: rompimento de faixa comprimida de 6 barras M5 com volume, saída em até 30 minutos;
  - tarde: modelo de ML treinado em 2022–23 que prevê compra ou venda, saída em até 1h;
  - stop de até 1.000 pts.
- **Resultado 2024–26:** +420 entradas (de 3,3 para 6,2 por semana), +R$3.742, PF 1,40.
  - Por ano: 2024 +R$412, 2025 +R$70, 2026 +R$3.260.
- **Contra:**
  - incremento por pregão com IC95 de −R$0,28 a +R$12,03, ou seja, cruza zero;
  - grade com 13 de 27 pontos passando, abaixo da maioria;
  - com atraso de 5 min, PF de 1,05 a 1,11;
  - montado depois de olhar os dados.
- **Veredito:** candidato fraco. Não adotar; no máximo, acompanhar em papel. O caminho mais forte para volume continua sendo o M2-A V6 com o universo expandido.

## GPT, rodada 6: "Retomada + redistribuição do 2º lote" (05/11), em `m2vol/gpt_r6/`
- **Combinado em 2024–25:** +96 entradas (+24%), com incremento de +R$726 a +R$885. IC95 de −R$3,1 a +R$6,9 por pregão (cruza zero). 2024 em −R$17 sem estresse.
- **Retomada sozinha:** p = 0,724 no ajuste max-t. Sem significância.
- **Auditoria das Duas Janelas:** 77% do lucro incremental veio dos 78 dias de 2026 em que o v2 estava bloqueado por risco. Nos dias normais, perdeu em 2024 e 2025.
- **Veredito do próprio GPT:** não promover. Confirma que o Duas Janelas também era fraco.

## GPT, rodada 8: "Liderança diária das ações" (05/11), em `m2vol/gpt_r8/`
- **Hipótese:** a força relativa de small caps contra blue chips prevê o WIN no dia seguinte. Foram 1.536 configurações.
- **Resultado:** nenhuma regra selecionada no treino supera o M2 v2 unitário.
  - "Espelho das árvores": +R$1.431 em 2024–25, IC95 de −R$10,4 a +R$15,9 por pregão, e cai pela metade em 2026.
  - Descolamento contrário: −R$7 em 2026.
- **Veredito:** reprovado.

## M2-A V6 no universo expandido, rodada 24 (05/11, 6h), em `m2vol/universo/`
- **Teste fora da amostra:** 117 papéis novos com R$5–300 mi/dia, que o M2-A nunca tinha visto, com a V6 congelada.
  - 4.152 operações (17 por semana).
  - PF 1,05 depois do custo, 1,31 antes; atraso de 5 min: 0,98.
  - PF por ano: 1,07 / 1,17 / 1,11 / 0,94 / 1,05.
  - **REPROVADO.** A vantagem bruta existe (~14 bps), mas não sobra nada depois do custo.
- **Por tier de liquidez:** instável. Por exemplo, 40–100 mi/dia dá 0,74 em 2024 e 0,56 em 2025.
- **Todos juntos (173 papéis):** 25,7 operações por semana, PF 1,14, pior ano 1,03, atraso 1,04, R$14,6 mil.
- **Conclusão:** parte do resultado do M2-A nas 50 small caps veio da seleção da lista. A vantagem real é menor, PF ~1,05–1,15. O M2-A cai para "observação em papel" e não tem expansão.

## Liderança diária do GPT refeita com o universo expandido (05/11, 6h), em `m2vol/gpt_r8x/`
- **Reprodução do original (57 ações):** bate. O espelho das árvores dá R$6.792 sem estresse, igual ao do GPT.
- **Com 167 small/mid + 11 blue chips:**
  - todas as regras diretas perdem (árvore: −R$3.004, PF 0,85; ridge: −R$2.696, PF 0,83);
  - a melhor contrária escolhida no treino continua sendo o "descolamento": +R$2.577 em 2024–25 sob estresse, PF 1,30, abaixo do M2 v2 unitário (+R$3.945);
  - "liquidez contrária": +R$982 sob estresse.
- **Veredito:** mais ações não melhoram o sinal. Continua reprovado.
