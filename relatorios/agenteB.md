# Agente B: "gap residual" no M2 v2 (04/11/2026)

Tudo foi rodado só em backtest, com os CSVs locais. Nenhuma ordem foi enviada.

- **Configuração:** WIN M5, custo de 15 pts por contrato, R$0,20/pt.
- **Período:** 2022-01 a 2026-10. O IVVB11 só tem dados a partir de 2023-03, porque o beta precisa de histórico.
- **Bootstrap:** estacionário, em blocos de 10 pregões, sobre a diferença diária de R$ contra o M2 v2 em todos os pregões do período.
- **Como ler as tabelas:**
  - `n` conta as entradas.
  - `ctr` conta os contratos.
  - O PF considera os contratos.
  - O DD é calculado sobre o P&L diário.

## Referência: M2 v2, reproduzido exatamente (`core.m2v2`)

| | n | /sem | ctr | PF | R$ | DD | PF por ano (22/23/24/25/26) |
|---|---|---|---|---|---|---|---|
| M2 v2 (manhã + tarde) | 905 | 3,60 | 1145 | 1,42 | 26.658 | −2.108 | 1,18 / 1,25 / 1,26 / 1,86 / 1,98 |
| M2 v2, só 2023-03+ (para comparar com o IVVB11) | 669 | 3,50 | 832 | 1,53 | 22.178 | −1.971 | – / 1,21 / 1,26 / 1,86 / 1,98 |

## Controle de look-ahead
- **Beta:** OLS numa janela móvel dos 60 pregões válidos anteriores, com `shift(1)`. O dia da decisão nunca entra na estimativa. Dia sem dado usa o último beta conhecido.
- **WDO:**
  - O gap usa a abertura das 9:00 (conhecida às 9:00).
  - A checagem de "ainda aberto" usa o fechamento da barra das 9:55, como o M2.
  - No 1º pregão do mês o WDO rola e o contN salta. Nesses dias o resíduo cai para o gap bruto.
- **IVVB11:**
  - A primeira barra do arquivo é a das **10:05**. O leilão das 10:00 não aparece como barra própria. Isso foi conferido em 948 de 957 dias, e o BOVA11 tem o mesmo padrão.
  - Por isso o primeiro preço do IVVB11 só existe às 10:05.
  - No teste principal a entrada é na abertura das **10:10**, usando a abertura do IVVB11 das 10:05 e o fechamento das 10:05 do WIN e do WDO.
  - Um teste otimista com entrada às 10:05 (`t2b`) fica no limite do look-ahead. Serve só como teto.
- **Outliers fora da estimação:** |gap WIN| > 5%, |WDO| > 3% e |IVVB11| > 5%. Ex.: o dado quebrado de 26/10/2026.

## 1. Quanto do gap é "explicado" e se o resíduo reverte mais (`diag.py`)

**Quanto cada fator explica do gap do WIN (R² fora da amostra):**

| Fator | Beta mediano | R² |
|---|---|---|
| Gap do WDO das 9:00 | −0,81 | **0,45** |
| IVVB11 bruto (S&P em R$) | – | 0,04 |
| S&P em US$ (IVVB11 ÷ WDO) | – | 0,38 |
| WDO + S&P em US$ | – | 0,47 |

O IVVB11 bruto quase não explica nada porque o dólar dentro dele anula o efeito do S&P.

**Regressão do retorno das 10:00 às 17:05 (em ATRd) no gap decomposto (t de Newey-West):**

| Recorte | Parte explicada pelo WDO | Resíduo |
|---|---|---|
| Todos os dias | −0,16 (t −1,7) | **−0,24 (t −3,1)** |
| \|gap\| entre 0,1 e 1,0 ATR | −0,12 (t −1,3) | **−0,26 (t −3,0)** |

- **Leitura:** a hipótese tem sustentação qualitativa. O resíduo reverte com o dobro da intensidade e de forma significativa; a parte explicada pelo dólar reverte pouco e sem significância.
- **Ressalva:** a diferença entre os dois coeficientes não é significativa (t ≈ 1).
- **Pelo IVVB11 (às 10:05, 2023+), o efeito é o inverso:** a parte explicada reverte −0,28 (t −2,2) e o resíduo só −0,05.

## 2. Gap residual pelo WDO (`t1_wdo.py`, `t3_wdo_grade.py`, `t4_q.py`, `t5_fneg.py`)

### Trades do M2 v2 da manhã por q = resíduo/gap (1 contrato)

| q | n | PF |
|---|---|---|
| < 0 | 87 | 1,10 |
| 0 a 0,5 | 168 | 1,15 |
| 0,5 a 1 | 221 | 1,53 |
| 1 a 1,5 | 98 | 1,30 |
| > 1,5 | 42 | 2,01 |

O fade funciona pior quando o dólar explica a maior parte do gap, como a hipótese previa.

O efeito aparece **só no grupo f < 0** (o gap esticou até 9:55). Nesse grupo:
- **q ≥ 0,5:** PF 1,43 com N=60. Na grade toda vai de 1,29 a 1,47.
- **q < 0,5:** PF 0,90, de 0,76 a 1,06 na grade.
- O PF de q alto fica acima do de q baixo em **15 de 15 pontos da grade**.
- No grupo f ≥ 0 o resíduo não discrimina nada.

### Variantes testadas

| Variante | n | /sem | ctr | PF | R$ | DD | PF mín. no ano | Incremento R$/pregão (IC95) |
|---|---|---|---|---|---|---|---|---|
| (a/b) Resíduo **no lugar** do gap + tarde | 855 | 3,40 | 1050 | 1,36 | 20.686 | −2.224 | 1,05 | −4,95 (−14,2; +3,9) |
| (a) v2 + entradas novas do resíduo nos dias sem M2 + tarde | 944 | 3,75 | 1237 | 1,40 | 28.533 | −2.704 | **1,01** | +1,55 (−3,7; +6,7) |
| Idem, com a entrada nova de 1 contrato | 944 | 3,75 | 1184 | 1,42 | 28.648 | −2.511 | 1,07 | +1,65 (−2,4; +5,5) |
| Catch-up: gap bruto < 0,10, resíduo ≥ 0,10, só as entradas novas | 84 | 0,33 | 84 | 1,48 | 2.363 | −1.022 | **0,68** | +2,44 (−0,9; +5,8) |
| (c) Filtro: v2 só se o resíduo tem o mesmo sinal do gap | 867 | 3,45 | 1078 | 1,42 | 24.666 | −2.066 | 1,17 | −1,65 (−5,6; +2,1) |
| (c) Tamanho: +1 contrato se \|res\| ≥ 0,3 ATR com o mesmo sinal | 905 | 3,60 | 1254 | 1,44 | 30.855 | −2.307 | 1,17 | **+3,48 (+0,5; +6,7)** |
| (c) **R_A:** f < 0 e q ≥ 0,5 passa a 2 contratos | 905 | 3,60 | 1350 | 1,42 | 32.150 | −2.682 | 1,21 | **+4,55 (+0,35; +8,95)** |
| (c) R_B: f < 0 e q < 0,5 não opera (o dia vai para a tarde) | 846 | 3,36 | – | 1,50 | 27.960 | −2.159 | 1,19 | +1,08 (−2,4; +4,3) |

Os anos do R_A ficam em 1,21 / 1,26 / 1,24 / 1,81 / 1,94.

### Robustez das duas linhas com IC95 > 0 (grade de ±20% em N, limiar, k e faixa do gap)

**Tamanho por |res| ≥ 0,3:**
- **Grade:** o IC95 fica acima de 0 com limiar de 0,24 a 0,30, mas **cruza 0 com limiar de 0,33 e 0,36**, nos três N testados.
- **Placebo** (+1 contrato em trades do M2 sorteados, mesmo número): p = 0,14 no ponto central e de 0,05 a 0,76 na grade.
- **Leitura:** o ganho vem quase todo de colocar mais contratos numa estratégia que já tem expectativa positiva. Não há seleção real.

**R_A:**
- **Placebo:** p = 0,03 no ponto central, contra o sorteio dentro do grupo f < 0.
- **Grade:** só **7 de 15 pontos** têm IC95 > 0. Com N=48, q0 = 0,4 ou 0,6 e k = 0,36, o IC inclui 0.
- **Leitura:** o ponto central é um pico local. A direção do efeito é robusta; o tamanho, não.
- **Custo estressado:** o PF fica igual ao do v2 (1,36 com 30 pts, 1,30 com 45 pts), com mais R$.

## 3. Gap explicado pelo exterior (IVVB11, 2023-03+) (`t2_ivv.py`, `t2b_ivv1005.py`)

**O problema é o horário.** O mesmo M2 v2 da manhã cai de PF 1,56 com entrada às 10:00 para 1,38 às 10:05 e **1,28 às 10:10**. Os primeiros 10 minutos do pregão à vista são parte da vantagem, e a informação do IVVB11 chega tarde demais.

**Substituir o gap pelo resíduo (10:10):** pior em todas as versões, com PF de 0,93 a 1,26 e incremento de −10 a −28 R$/pregão.

**Entradas novas do resíduo nos dias sem M2:**
- Ficam entre 55 e 77 operações (0,3 a 0,4 por semana).
- O incremento não é significativo: +1,1 a +2,4, com IC cruzando 0.
- No modo otimista das 10:05, com WDO + S&P, chega a +3,4 (IC de −0,6 a +7,9).

**+1 contrato às 10:10 quando |res| ≥ 0,2 (WDO + S&P):**
- Incremento de +5,0 (IC de +0,9 a +9,5), placebo p = 0,045.
- **Com limiar de 0,3, cai para +0,2 e p = 0,65**, então não é robusto.
- As outras versões dão p de 0,27 a 0,92.

**Filtro:** em todas as versões reduz o R$.

## 4. Ideias próprias, por outros caminhos (`t6_ideias.py`, `t6b_run4b.py`, `t7_1hora.py`)

| Ideia | Resultado |
|---|---|
| **4a. Tarde ajustada pelo dólar:** desvio das 13:10 menos beta × WDO no mesmo intervalo (beta −0,77) | No lugar da tarde bruta: PF 1,14 (pior que 1,36). Entradas novas nos dias sem v2: PF 0,61. Na grade de 27 pontos, o incremento é negativo em todos. Como filtro, piora. **Reprovada.** |
| **4b. Excesso intradiário contra o S&P:** retorno do WIN desde 10:10 menos beta × S&P em US$, às 11:00, 12:00 ou 13:10, nos dias sem v2 | PF de 0,57 a 0,74 em todos os 9 pontos. **Reprovada.** O WIN não reverte o descolamento do S&P dentro do dia. |
| **4c. Excesso da 1ª hora contra o dólar:** movimento do WIN de 9:00 a 9:55 menos beta × WDO, fade às 10:00 nos dias sem M2 | Com o resíduo, PF de 0,82 a 0,96; com o movimento bruto, 0,76 a 0,79. Ajustar pelo dólar melhora, mas continua perdendo. **Reprovada.** |

## Veredito

Pelo critério combinado (PF ≥ 1,2, nenhum ano < 1,0, incremento com IC95 > 0 e robustez na grade de ±20%), **nada foi aprovado**.

**A hipótese do "gap residual" se confirma qualitativamente.** O gap que o dólar não explica reverte mais. Os trades do M2 com gap esticado (f < 0) e bem explicado pelo WDO ficam no zero a zero (PF ~0,9) em toda a grade.

**Ela não gera volume novo:**
- O resíduo não cria entradas boas fora dos dias do M2.
- Os dias de "gap bruto pequeno e resíduo grande" são poucos (0,3 por semana) e instáveis: 2022 tem PF 0,6.

**O único uso com sinal estatístico é dimensionar o grupo f < 0 (R_A):** +R$5,5 mil, PF 1,42, IC95 > 0 e placebo p = 0,03. Mas o efeito some em metade da grade. Isso é **candidato fraco, não aprovado**. Sugestão: acompanhar fora da amostra (no histórico antigo do WIN, se ele for montado) antes de qualquer uso.

**Se o objetivo for qualidade e não volume,** a versão R_B (não operar f < 0 com q < 0,5) sobe o PF de 1,42 para ~1,50 com o mesmo R$. É uma melhoria de eficiência, não de volume, e tampouco foi provada (IC cruza 0).

**IVVB11:** descartado como fonte de sinal para o M2, porque chega depois da janela que tem a vantagem.

**Observação metodológica:** num método de expectativa positiva, qualquer aumento de tamanho dá "incremento com IC95 > 0". Por isso usei o **placebo** (contrato extra em dias sorteados) como teste de seleção. Sem ele, as variantes de tamanho pareceriam aprovadas.

## Arquivos

Ficam em `/home/claude/win/m2vol/agenteB/`.

**Base:** `core.py` (dados, beta móvel, gerador do M2, simulação, bootstrap, placebo).

**Scripts e saídas:**

| Script | Saída |
|---|---|
| `diag.py` | `diag_out.txt` |
| `t1_wdo.py` | `t1_wdo_out.txt` |
| `t3_wdo_grade.py` | `t3_wdo_grade_out.txt`, `t3_grade_S.csv`, `t3_grade_C.csv` |
| `t4_q.py` | `t4_q_out.txt` |
| `t5_fneg.py` | `t5_fneg_out.txt`, `t5_grade_A.csv`, `t5_grade_B.csv` |
| `t2_ivv.py` | `t2_ivv_out.txt` |
| `t2b_ivv1005.py` | `t2b_ivv1005_out.txt` |
| `t6_ideias.py` | `t6_ideias_out.txt`, `t6_grade_4a.csv` |
| `t6b_run4b.py` | `t6b_4b_out.txt` |
| `t7_1hora.py` | `t7_1hora_out.txt` |

**Ressalva:** os refinamentos R_A e R_B foram definidos depois de olhar os buckets do t4 (pós-hoc). Todos os resultados são dentro da amostra de 2022 a 2026.
