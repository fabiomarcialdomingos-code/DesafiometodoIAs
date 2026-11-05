# M2-A "Ação atrasada": como aumentar o volume (agenteE, 04/11/2026)

## Resumo e veredito

**Não dá para aumentar MUITO o volume do M2-A nas 50 small caps sem perder a vantagem.** O teto honesto fica entre ~9 e ~15 operações por semana, contra 6,7 na base. Acima de ~15 por semana, todas as variantes reprovam. O caminho para volume grande é **mais papéis na faixa de liquidez de R$5–300 milhões por dia**, e não um limiar menor. O pipeline para isso está pronto (`rodar_universo.py`).

| | config | n | op/sem | PF | PF bruto | R$ | DD | 2022 | 2023 | 2024 | 2025 | 2026 | atraso 5 min | +1 tick | grade ±20% | 2024–26 | últimos 16 meses |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C0 | base do agente C: lo 0,25, wmin 0,5, leilão às 10:00 | 1.629 | 6,7 | 1,34 | 1,58 | 8.531 | −1.051 | 1,51 | 1,27 | 1,25 | 1,32 | 1,43 | 1,15 | 1,13 | 79/81 | 1,32 | 1,26 |
| **V6** | **lo 0,25, wmin 0 (sem filtro de força do WIN)** | **2.181** | **9,0** | **1,31** | **1,54** | **10.834** | **−996** | **1,38** | **1,37** | **1,30** | **1,23** | **1,34** | **1,16** | **1,11** | **81/81** | **1,29** | **1,21** |
| V2 | lo 0,20 + leilões tardios (entrada 10:10) | 3.595 | 14,8 | 1,31 | 1,53 | 16.989 | −1.783 | 1,60 | 1,32 | 1,42 | 1,21 | **1,08** | 1,14 | 1,12 | 74/81 | 1,24 | **1,03** |
| – | lo 0,15 + tardios | 5.815 | 23,9 | 1,21 | 1,42 | 19.163 | −2.619 | 1,52 | 1,16 | 1,25 | 1,14 | 1,09 | **1,08** | 1,04 | – | 1,16 | 1,00 |
| – | lo 0,10 | 7.529 | 30,9 | **1,14** | 1,35 | 16.791 | −2.669 | 1,26 | 1,06 | 1,19 | 1,18 | 1,07 | 1,04 | 0,97 | – | 1,15 | – |

A tabela mostra o período de 2022-03 a 2026-10, com small caps, hedge em WIN, stop de 1,0 ATRd e R$80 de risco por operação. O custo é de 0,10% ida e volta mais 15 pts por WIN. "Grade ±20%" conta quantos dos 81 pontos têm PF ≥ 1,2 e nenhum ano abaixo de 1,0.

**Melhor configuração com volume alto: V6.** É o M2-A com lo 0,25 e **sem o filtro de força do WIN 9–10h** (wmin = 0).
- Volume: 9,0 operações por semana, ou 10,2 em 2024–26 (+34%).
- Resultado: PF 1,31 (bruto 1,54) e R$10,8 mil, com DD de −996 (menor que o da base). Todos os anos ≥ 1,23.
- Estresse de atraso: 1,16, com pior ano 1,07.
- Grade ±20% (lo, hi, wmin e stop): passam 81 de 81 pontos. No atraso, o PF fica ≥ 1,1 em 27 de 27.
- Walk-forward: escolhida em 2022–23 (PF 1,38), dá PF 1,29 em 2024–26. Nos últimos 16 meses, PF 1,21.
- **APROVA** em todos os critérios. É um ganho real, mas modesto: +34% de volume e +27% de R$.

**Maior volume que passa no critério formal: V2** (lo 0,20 + tardios), com 14,8 operações por semana, PF 1,31 e R$17,0 mil.
- No papel, passa: anos ≥ 1,08, atraso 1,14, grade 74/81.
- **Não recomendo.** As 1.966 operações que ela acrescenta à base têm PF 0,87 em 2026 e 0,85 nos últimos 16 meses. Com atraso, o PF do incremento em 2026 é 0,93.
- Nos últimos 16 meses, a V2 inteira tem PF 1,03 (R$552), contra 1,26 (R$2.327) da base. O volume extra está sendo pago com a vantagem.
- Na grade, o atraso só fica ≥ 1,1 em 18 de 27 pontos (mínimo 1,06).

**Veredito honesto:**
1. A **V6 é aprovada** e pode substituir a C0. Ela só remove um filtro, não muda nada na execução.
2. A **V2 é "aprovada com ressalva grave"**: passa no critério de 2022–26, mas reprova no teste de recência. Não a adoto.
3. **Nada acima de ~15 operações por semana passa.**
4. **ETFs reprovam.** O SMAL11 não atrasa e o BOVA11 com hedge é só a base entre o ETF e o futuro.
5. **Blue chips com mais de R$300 milhões por dia reprovam**: a vantagem bruta é de ~2–6 bps, contra 26–47 bps nas small caps.
6. **A fragilidade de execução continua e é o que decide.** Em todas as configurações:
   - +1 tick na entrada **e** na saída derruba o PF para menos de 1 (0,89–0,99);
   - 5 minutos de atraso **mais** 1 tick também (0,94–1,00).
   - O forward test em papel, medindo o preço real às 10:05, continua indispensável antes de pôr dinheiro.
7. Com R$80 por operação, o hedge em WIN inteiro arredonda para 0 contratos em 87% dos dias. Para o hedge funcionar de verdade é preciso arriscar ~R$300 ou mais por operação (ver as ressalvas).
8. O sinal está se concentrando nos atrasos maiores: com lo 0,30, o PF de 2026 é 1,85. Já as faixas de 0,15–0,25 ficaram abaixo de 1 em 2026. Isso é coerente com o enfraquecimento do lead-lag que o agente C mediu (coeficiente de 0,04 em 2026).

---

## Convenções (diferenças em relação ao agente C)

O motor (`motor.py`) é novo e roda papel a papel, com memória constante. O sinal é o do agente C: das 1.659 operações dele, 1.629 batem em data, papel e direção.

Diferenças de execução, todas no sentido mais realista, como no `executavel.py` do GPT:
- a entrada exige negócio real na barra de entrada (por isso ficam 1.629 operações, e não 1.659);
- quantidade em ações inteiras;
- stop checado no fechamento da barra sobre o P&L com hedge, e **executado na abertura da próxima barra com negócio**;
- saída às **16:45** (abertura da barra 16:45), o que evita a barra de leilão de fechamento nos dias de horário de verão dos EUA.

Com isso a base fica em PF 1,34 (contra 1,36), atraso 1,15 (contra 1,18) e tick 1,13 (contra 1,16). O motor reproduz o agente C.

Outras convenções:
- **PF por operação:** com hedge fracionário (β × nocional em WIN) e custo de 15 pts proporcional. **Hedge inteiro:** agregado por dia em contratos inteiros, rebalanceado a cada barra conforme as pernas entram e saem (`motor.hedge_inteiro`). O PF desse caso é **diário**, como no GPT, e não é comparável com o PF por operação (somar operações do dia sobe o PF mecanicamente).
- **Coortes:** "cedo" significa leilão na barra 10:00 e entrada às 10:05. "Tarde" significa que o primeiro negócio saiu na barra 10:05; a entrada é às 10:10 e o sinal usa o mesmo WIN até as 10:00.
- **Estresses nas mesmas operações:**
  - atraso de 5 minutos: entrada às 10:10 (cedo) ou 10:15 (tarde);
  - +1 tick: R$0,01 adverso na entrada;
  - "tick2": +1 tick na entrada e na saída;
  - custo ×1,5 e ×2.
- **Op/sem** = n / semanas de 2022-03-01 a 2026-10-31 (243,6 semanas).
- **DD** = drawdown da curva diária de R$, com risco de R$80 por operação.
- **Liquidez** = média de 60 dias de volume × fechamento até ontem (`shift(1)`), sem look-ahead.

## 1. Limiar menor (`e1_limiar.py`, `e1_out.txt`, `e1_grade.csv`, `e1_curva.png`)

Grade: lo ∈ {0,10; 0,15; 0,20; 0,25} × teto hi ∈ {1,2; 1,4; 1,6; 1,8; 2,0} × wmin ∈ {0; 0,5} × coortes × universo (160 pontos).

**O teto não importa.** De hi 1,2 para 2,0 entram ~5 operações, porque quase nenhum atraso passa de 1,2 ATRd. A alavanca é o `lo`.

Small caps, hi = 1,2:

| coortes | wmin | lo | n | op/sem | PF | PF bruto | R$ | DD | pior ano | 2024–26 | atraso 5 min | +1 tick | aprova |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cedo | 0,5 | 0,25 | 1.629 | 6,7 | 1,34 | 1,58 | 8.531 | −1.051 | 1,25 | 1,32 | 1,15 | 1,13 | sim |
| cedo | 0,5 | 0,20 | 2.725 | 11,2 | 1,30 | 1,53 | 12.255 | −1.316 | 1,17 | 1,25 | 1,13 | 1,10 | sim |
| cedo | 0,5 | 0,15 | 4.631 | 19,0 | 1,21 | 1,42 | 14.755 | −1.906 | 1,14 | 1,18 | **1,08** | 1,02 | não |
| cedo | 0,5 | 0,10 | 7.529 | 30,9 | **1,14** | 1,35 | 16.791 | −2.669 | 1,06 | 1,15 | 1,04 | 0,97 | não |
| cedo | 0 | 0,25 | 2.181 | 9,0 | 1,31 | 1,54 | 10.834 | −996 | 1,23 | 1,29 | 1,16 | 1,11 | sim |
| cedo | 0 | 0,20 | 3.719 | 15,3 | 1,24 | 1,46 | 13.927 | −1.066 | 1,08 | 1,20 | 1,11 | 1,05 | sim (limite) |
| cedo | 0 | 0,15 | 6.386 | 26,2 | 1,15 | 1,35 | 15.404 | −1.963 | 1,08 | 1,13 | 1,05 | 0,98 | não |
| cedo+tarde | 0,5 | 0,25 | 2.256 | 9,3 | 1,34 | 1,55 | 12.176 | −1.268 | 1,21 | 1,29 | 1,15 | 1,15 | sim* |
| cedo+tarde | 0,5 | 0,20 | 3.595 | 14,8 | 1,31 | 1,53 | 16.989 | −1.783 | 1,08 | 1,24 | 1,14 | 1,12 | sim |
| cedo+tarde | 0,5 | 0,15 | 5.815 | 23,9 | 1,21 | 1,42 | 19.163 | −2.619 | 1,09 | 1,16 | **1,08** | 1,04 | não |
| cedo+tarde | 0 | 0,20 | 5.138 | 21,1 | 1,21 | 1,41 | 17.754 | −2.117 | **0,95** | 1,16 | 1,09 | 1,04 | não |

\* No atraso, 2023 fica em 0,98.

- A curva volume × PF é monotônica. Cada passo de 0,05 no `lo` dobra o volume e tira ~0,05–0,09 do PF. Já o PF com atraso cai abaixo de 1,1 a partir de ~19 operações por semana.
- O **R$ total** sobe até lo 0,10–0,15 (R$19–21 mil com os tardios), porque o risco por operação é fixo. Mas essas versões reprovam no atraso e no tick. Ou seja, é R$ "de papel", que a execução real come.
- **Incluir as 11 blue chips** (small+blue) piora tudo: com lo 0,25, PF 1,23 e 2023 em 1,07; no atraso, 1,07.

## 2. Várias ações por dia e limite diário de risco (`e2_concentracao.py`, `e2_out.txt`)

A regra do agente C **já opera todas as ações que se qualificam**: em média 3,0 por dia (máximo 15) na C0 e 5,1 por dia (máximo 26) na V2. Testei limitar por dia, escolhendo pelo maior |lag| ou pela maior liquidez, e limitar o risco diário, escalando o risco de cada perna para min(R$80, limite / n do dia).

| V2 (lo 0,20 + tardios) | n | op/sem | PF | R$ | DD | R$/DD | pior dia | atraso 5 min | ICC com hedge | ICC sem hedge | risco/dia máximo |
|---|---|---|---|---|---|---|---|---|---|---|---|
| todas | 3.595 | 14,8 | 1,31 | 16.989 | −1.783 | 9,5 | −579 | 1,14 | 0,118 | 0,315 | 2.074 |
| top 1 por \|lag\| | 706 | 2,9 | 1,40 | 4.752 | −740 | 6,4 | −118 | 1,26 | – | – | 80 |
| top 3 por \|lag\| | 1.818 | 7,5 | 1,24 | 7.333 | −959 | 7,6 | −219 | 1,09 | 0,101 | 0,255 | 240 |
| top 5 por \|lag\| | 2.585 | 10,6 | 1,27 | 11.448 | −1.257 | 9,1 | −281 | 1,11 | 0,099 | 0,273 | 400 |
| risco do dia ≤ R$400 | 3.595 | 14,8 | 1,28 | 11.436 | −1.322 | 8,7 | −253 | 1,12 | 0,060 | 0,175 | 400 |
| **risco do dia ≤ R$640 (8 R)** | 3.595 | 14,8 | 1,31 | 15.112 | **−1.410** | **10,7** | −355 | 1,14 | 0,083 | 0,231 | 639 |

- **Correlação entre as pernas do mesmo dia** (correlação intraclasse dos resultados em R): **0,10–0,12 com hedge** e **0,29–0,32 sem hedge**. O hedge em WIN tira 2/3 da correlação. O número efetivo de apostas independentes por dia é 2,25 (de 2,97) na C0 e 3,06 (de 5,09) na V2.
- **Escolher "top N" não melhora o PF por operação.** O top 1 tem PF maior, mas com um terço do volume; o top 2 ou 3 tem PF menor que "todas". O |lag| maior não ordena bem dentro do dia.
- **O limite de R$640 por dia é o melhor uso do risco.** Na V2, ele mantém o PF, reduz o DD de −1.783 para −1.410 e corta o pior dia de −579 para −355. Na V6 e na C0 quase não muda nada (o DD é o mesmo), porque esses dias raramente passam de 8 pernas.
- Dias com 5 ou mais pernas têm PF **maior** (1,34–1,49 na V2). Dias com só 1 perna têm PF 0,82. A concentração não é o risco principal; os dias "de massa" são os bons.
- As vendas são melhores que as compras em todas as versões: venda 1,32–1,41, compra 1,13–1,25. Nas compras, 2024 ficou em 0,87–0,99.

## 3. ETFs: SMAL11 e BOVA11 (`e3_etf.py`, `e3_out.txt`)

**Fato de dados:** os dois ETFs **nunca** negociam na barra 10:00. O primeiro preço sai na barra 10:05, então eles só entram como "tardios", com entrada às 10:10.

**(a) O SMAL11 atrasa em relação ao WIN da 1ª hora? Não.** A regressão é y = retorno com hedge de 10:10 a 11:00, contra gap, β×WIN da noite, β×WIN 9–10h e β×WIN 10:00–10:05, com erros-padrão agrupados por dia, de 2023-03 a 2026-10:

| | n | coeficiente do WIN 9–10h (t) |
|---|---|---|
| SMAL11 | 856 | **+0,019 (0,3)**; por ano: −0,02 / +0,05 / +0,09 / −0,04 |
| BOVA11 | 839 | +0,081 (1,6) |
| 50 small caps, coorte cedo, 10:05 → 11:00 | 33.649 | **+0,181 (2,8)** |

O SMAL11 é precificado pelos formadores de mercado contra o futuro. Não sobra atraso para explorar.

**(b) O M2-A aplicado ao próprio ETF reprova.**
- SMAL11: PF 0,67–0,95 com custo de 0,06%. Mesmo com 0,03%, fica entre 0,75 e 1,07, com 2023 entre 0,29 e 0,65. São só 0,3–1,4 operações por semana.
- BOVA11: PF 0,13–0,30, embora o PF bruto fique entre 1,5 e 3,8. Com hedge em WIN, o BOVA11 é só a base entre ETF e futuro: o retorno é minúsculo e o custo come tudo.

**(c) ETF como veículo único:** operar o SMAL11 na direção do WIN quando ≥ N small caps estão atrasadas às 10:00.
- Entrando no **primeiro preço** do SMAL11 (barra 10:05), o PF fica entre 1,17 e 1,63 (3,05 com N ≥ 8, mas n = 23). Em 2023 fica abaixo de 1 em todas as variantes, menos essa.
- Entrando às **10:10**, o PF cai para 0,84–1,05 (1,55 com N ≥ 8, n = 24). A informação está no primeiro preço do ETF e some em 5 minutos.
- Entrar no primeiro preço exigiria participar do leilão de abertura do ETF, sem saber o preço. Isso não é executável com os dados que temos, e o volume (1–3 operações por semana) seria baixo de qualquer jeito.
- **Reprovado.** Um ETF único não substitui a cesta.

## 4. Tiers de liquidez, só com o passado (`e4_tiers.py`, `e4_out.txt`)

Small + blue, com o custo de cada grupo e liquidez de 60 dias até ontem.

| tier (R$/dia) | lo 0,25 cedo: n | PF | PF bruto | bps brutos | atraso 5 min | lo 0,20 + tardios: n | PF | bps brutos | atraso 5 min |
|---|---|---|---|---|---|---|---|---|---|
| < 15M | 202 | 1,37 | 1,55 | 36,7 | 1,11 | 374 | 1,33 | 33,8 | 1,07 |
| 15–40M | 530 | 1,28 | 1,50 | 28,0 | 1,11 | 1.086 | 1,34 | 31,9 | 1,18 |
| 40–100M | 589 | 1,50 | 1,80 | 36,0 | 1,32 | 1.334 | 1,29 | 28,1 | 1,15 |
| 100–300M | 311 | 1,16 | 1,37 | 21,0 | 1,01 | 785 | 1,32 | 31,0 | 1,17 |
| **≥ 300M** | 487 | **0,92** | 1,09 | **3,6** | 0,82 | 921 | **0,96** | **5,6** | 0,83 |

- **A vantagem bruta fica estável (~28–36 bps) em toda a faixa abaixo de R$300 milhões por dia, e cai para 4–6 bps acima disso.** Não é efeito de custo: com custo uniforme de 0,10%, o tier ≥ 300M fica em 0,84–0,88. Em 2023 e 2026 os anos ficam abaixo de 1.
- Abaixo de R$15 milhões a vantagem bruta é boa, mas o atraso pesa mais (1,07–1,11) e o custo real deve ser maior que 0,10%. Com custo de 0,15% abaixo de R$10 milhões (pipeline), o tier < 5M fica em 0,99 (3 papéis, n = 82), enquanto o de 5–15M fica em 1,54.
- **Conclusão para expandir o universo:** a faixa útil é de **R$5–300 milhões por dia**. Os ≥ 300M devem ficar de fora, e os < 5M também, ou entrar com custo maior e só depois de medir o spread real. Dentro da faixa, o PF não depende da liquidez de forma estável (os tiers alternam entre anos). Não há um "tier ótimo" a escolher, o que favorece expandir o universo inteiro de 5–300M.

## 5. Candidatas: robustez, estresse e walk-forward (`e5_candidata.py`, `e5_out.txt`, `e5_candidatas.csv`, `e5_grade.csv`, `e5_walkforward.csv`)

| | C0 | V1 lo 0,20 | V2 lo 0,20 + tarde | V3 lo 0,20 wmin 0 | **V6 lo 0,25 wmin 0** | V5 = V2 com 15–300M |
|---|---|---|---|---|---|---|
| n (op/sem) | 1.629 (6,7) | 2.725 (11,2) | 3.595 (14,8) | 3.719 (15,3) | **2.181 (9,0)** | 3.205 (13,2) |
| PF (bruto) | 1,34 (1,58) | 1,30 (1,53) | 1,31 (1,53) | 1,24 (1,46) | **1,31 (1,54)** | 1,31 (1,54) |
| R$ / DD | 8.531 / −1.051 | 12.255 / −1.316 | 16.989 / −1.783 | 13.927 / −1.066 | **10.834 / −996** | 15.326 / −2.138 |
| PF por ano, 22 / 23 / 24 / 25 / 26 | 1,51 / 1,27 / 1,25 / 1,32 / 1,43 | 1,54 / 1,32 / 1,33 / 1,23 / 1,17 | 1,60 / 1,32 / 1,42 / 1,21 / 1,08 | 1,37 / 1,29 / 1,27 / 1,21 / 1,08 | **1,38 / 1,37 / 1,30 / 1,23 / 1,34** | 1,62 / 1,36 / 1,46 / 1,18 / 1,09 |
| atraso 5 min (pior ano) | 1,15 (1,05) | 1,13 (1,05) | 1,14 (1,07) | 1,11 (1,08) | **1,16 (1,07)** | 1,16 (1,06) |
| +1 tick na entrada | 1,13 | 1,10 | 1,12 | 1,05 | 1,11 | 1,14 |
| +1 tick na entrada e na saída | 0,96 | 0,93 | 0,96 | 0,89 | 0,94 | 0,99 |
| atraso + 1 tick | 0,97 | 0,95 | 0,97 | 0,94 | 0,98 | 1,00 |
| custo ×1,5 / ×2 | 1,24 / 1,14 | 1,20 / 1,10 | 1,21 / 1,12 | 1,14 / 1,05 | 1,21 / 1,12 | 1,21 / 1,12 |
| grade ±20% (81 pontos: lo, hi, wmin, stop) | 79/81 | 72/81 | 74/81 | 54/81 | **81/81** | 68/81 |
| grade: atraso ≥ 1,1 | 27/27 | 18/27 | 18/27 | 18/27 | **27/27** | 18/27 |
| beta 48 / 72 dias | 1,29 / 1,29 | 1,31 / 1,30 | 1,33 / 1,29 | 1,24 / 1,25 | 1,26 / 1,28 | – |
| PF diário com hedge inteiro (R$) | 1,50 (8.873) | 1,55 (13.791) | 1,68 (20.088) | 1,48 (17.480) | 1,45 (11.367) | 1,60 (16.464) |
| sem os 5 melhores papéis | 1,22 | 1,20 | 1,23 | 1,17 | 1,21 | 1,24 |
| trimestres positivos | 16/20 | 18/20 | 19/20 | 17/20 | 18/20 | 19/20 |
| 2024–26 | 1,32 | 1,25 | 1,24 | 1,20 | 1,29 | 1,24 |
| **últimos 16 meses (2025-07 a 2026-10)** | 1,26 | 1,10 | **1,03** | 1,07 | **1,21** | 1,02 |

**Walk-forward** (180 combinações de universo, coortes, lo, wmin e stop):
- O critério foi fixado antes de rodar: no treino 2022–23, n ≥ 200, PF ≥ 1,2, todos os anos ≥ 1 e atraso ≥ 1,1. Entre as que passam, vence o maior R$ no treino.
- Ele escolheu **lo 0,15 + tardios, stop 0,8**. No teste 2024–26: 26 operações por semana, mas **PF 1,15** e atraso 1,07. **Reprova fora da amostra.** Escolher por R$ empurra para volume, e o volume não se sustenta.
- Das 36 combinações que passam no treino, 61% passam em tudo no teste, e o PF mediano no teste é 1,23. A correlação entre o PF de treino e o de teste é 0,74, mas o PF **cai ~0,10–0,15** do treino para o teste.
- A V6 passa no treino (PF 1,38, pior ano 1,37, atraso 1,15) e no teste (PF 1,29, pior ano 1,23, atraso 1,17).
- A V2 passa no treino (1,46) e no teste (1,24, pior ano 1,08, atraso 1,13).

## 6. Recência: a vantagem está migrando para os atrasos grandes (`e6_recencia.py`, `e6_out.txt`)

O teste que separa a V6 da V2 é o **PF das operações acrescentadas à base**, medido nos últimos 16 meses:

| alavanca | operações acrescentadas | PF do incremento (2022–26) | atraso | **PF do incremento nos últimos 16 meses** |
|---|---|---|---|---|
| lo 0,25 → 0,20 | 1.096 | 1,23 | 1,09 | **0,88** |
| lo 0,25 → 0,15 | 3.002 | 1,14 | 1,03 | 0,94 |
| + tardios, com lo 0,25 | 627 | 1,33 | 1,14 | **0,85** |
| + tardios, com lo 0,20 (= V2) | 1.966 | 1,28 | 1,12 | **0,85** (2026: 0,87) |
| **wmin 0,5 → 0, com lo 0,25 (= V6)** | 552 | 1,24 | 1,20 | **1,05** |
| wmin 0,5 → 0, com lo 0,30 | 328 | 1,25 | 1,23 | 1,20 |

Por faixa de |lag| (coorte cedo, wmin 0,5), em 2026: 0,10–0,15 deu 0,97; 0,15–0,20 deu 1,11; **0,20–0,25 deu 0,85**; 0,25–0,35 deu 1,35; 0,50–1,20 deu 2,24. A coorte tardia em 2026 ficou entre 0,63 e 0,88 nas faixas de 0,20 a 0,50.

Na leitura econômica, o lead-lag existe mas está ficando mais "raso": só os atrasos grandes ainda pagam o custo. Por isso **a única alavanca de volume que resiste à recência é tirar o filtro de força do WIN**. Ela traz mais dias, sem descer o limiar. Baixar o limiar e incluir os tardios funcionou até 2024 e parou de funcionar.

## 7. Pipeline para um universo maior (`rodar_universo.py`)

```
python3 -I /home/claude/win/m2vol/agenteE/rodar_universo.py --pasta /caminho/acoes --saida /caminho/saida \
    [--jobs 2] [--treino_fim 2024-01-01] [--pf_min_treino 1.35] [--excluir BOVA11,SMAL11,...] [--reusar]
```

- **Entrada:** uma pasta com `{TICKER}_M5.csv` e `{TICKER}_D1.csv` (separador `;`, colunas time, open, high, low, close, tick_volume e real_volume), mais o WIN M5 contínuo. Lê papel a papel (memória constante, multiprocessado). Nos 59 papéis levou ~4 s para gerar as operações e ~40 s no total; 600 papéis devem levar alguns minutos.
- **Sem look-ahead:**
  - liquidez, ATR e beta só até ontem;
  - o filtro e os tiers de liquidez usam a média de 60 dias até ontem;
  - **o custo é dado pela liquidez histórica**: ≥ R$150M, 0,06%; R$10–150M, 0,10%; < R$10M, 0,15%;
  - checa a coerência entre a abertura D1 e o leilão M5;
  - descarta |gap| ≥ 15% (eventos societários);
  - exclui ETFs de índice (lista editável).
- **Walk-forward:** grade de lo × wmin × coortes × stop × piso e teto de liquidez (288 pontos), escolhida **só no treino**.
  - Critério: n ≥ 200, PF ≥ `--pf_min_treino`, todos os anos ≥ 1, atraso ≥ 1,1.
  - Além disso, os vizinhos com lo ×0,8 e ×1,2 precisam ter PF ≥ 1,15 e atraso ≥ 1,05.
  - Entre as que passam, vence o maior R$ no treino, e o resultado é medido no teste.
  - Também mede a **configuração congelada V6** (lo 0,25, wmin 0, cedo, stop 1,0, **liquidez de R$5–300M**).
- **Saídas** em `--saida`:
  - `resumo.md`;
  - `wf_grade.csv`;
  - `tier_ano_<cfg>.csv` (tier × ano: n, PF, PF bruto, bps, atraso, R$);
  - `ano_<cfg>.csv`;
  - `papeis_<cfg>.csv`;
  - `hedge_inteiro_<cfg>.csv`;
  - `papeis_info.csv`;
  - `superconjunto.pkl`, para rodar de novo com `--reusar`.

**Teste nos 61 papéis atuais** (pasta de links simbólicos; os ETFs ficam excluídos; `universo61/` e `universo61_pf135/`):

| | n (op/sem) | PF | pior ano | atraso | +1 tick | R$ | DD | teste 2024+: PF / pior ano / atraso |
|---|---|---|---|---|---|---|---|---|
| congelada V6, R$5–300M, custo por liquidez | 2.108 (8,7) | 1,32 | 1,21 | 1,17 | 1,12 | 10.667 | −1.271 | 1,28 / 1,21 / 1,17 (10,0 por semana) |
| escolhida no treino, `--pf_min_treino 1.2` (lo 0,15 + tarde, k 0,8, ≤ 300M) | 5.762 (23,7) | 1,20 | 1,10 | 1,09 | – | 22.910 | −3.820 | **1,15** / 1,10 / 1,07: reprova |
| escolhida no treino, `--pf_min_treino 1.35` (lo 0,20 + tarde, k 0,8, ≤ 300M) | 3.579 (14,7) | 1,29 | 1,10 | 1,15 | – | 20.057 | −2.675 | 1,21 / 1,10 / 1,13 (16,4 por semana) |

**Recomendação para quando chegar a pasta com centenas de ações:**
1. Rode com `--pf_min_treino 1.35`.
2. Olhe primeiro a **configuração congelada V6**. Para os papéis novos ela é fora da amostra de verdade, porque nenhum parâmetro foi escolhido com eles.
3. Se a V6 mantiver PF ≥ 1,2 e atraso ≥ 1,1 nos papéis novos, o volume escala com o número de papéis. Conta grosseira: ~0,18 operação por semana por small cap; 200 papéis na faixa de 5–300M dariam ~35 operações por semana.
4. Confira `tier_ano_congelada_V6.csv` para ver se algum tier novo (por exemplo, os papéis de < R$5M) quebra.

## Ressalvas

1. **Execução.** Todas as versões dependem de entrar às 10:05 a um preço próximo da abertura da barra.
   - +1 tick nas duas pontas, ou atraso mais 1 tick, levam o PF para menos de 1. O custo de 0,10% precisa de fato cobrir spread e derrapagem, e o spread na abertura das small caps é maior.
   - O tick pesa mais em papel barato: R$0,01 num papel de R$3 equivale a 33 bps.
   - **Forward test em papel por 2–3 meses antes de qualquer dinheiro**, medindo o preço real obtido às 10:05.
2. **Enfraquecimento do sinal.** As faixas marginais já não pagam em 2026. A própria V6 tem 2025 em 1,23 e os últimos 16 meses em 1,21. O pior cenário é que até a faixa ≥ 0,25 se arbitre. Monitore o PF móvel de 6 meses: abaixo de 1,1, pare.
3. **Viés de sobrevivência.** A lista das 50 small caps é a de hoje. O pipeline aceita papéis extintos, se os arquivos existirem; vale incluí-los na pasta grande.
4. **Seleção.** V6 e V2 foram escolhidas olhando 2022–26 inteiro, inclusive a recência. O walk-forward mitiga isso (a V6 é aprovada só com o treino de 2022–23), mas não substitui dados novos. Os papéis novos do universo grande serão o primeiro teste limpo.
5. **Hedge inteiro: com R$80 por operação, ele quase não existe.**
   - Na V6, o hedge agregado arredonda para **0 contratos em 87% dos dias** (84% na C0, 64% na V2). O "PF 1,45 diário com lotes inteiros" é, na prática, a cesta **sem hedge** na maioria dos dias.
   - Sem hedge, a V6 tem PF 1,30 por operação, com 2025 em 1,07 e DD de −2.259.
   - Com **R$320 por operação** (4×), o hedge inteiro fica ativo em 63% dos dias. Na escala de R$80: PF diário 1,46 e **DD de −829**, contra −1.680 com R$80.
   - **Ou se opera com pelo menos ~R$300 de risco por operação (nocional de ~R$9 mil por perna), ou se aceita o DD sem hedge, cerca de 2× maior.**
6. **O limite de R$640 por dia** não muda a V6, mas protege em dias de muitas pernas. Recomendo usá-lo como trava operacional.

## Arquivos (`/home/claude/win/m2vol/agenteE/`)

Para reproduzir, rode nesta ordem: `python3 -I e0_cache.py`, depois `e1_limiar.py`, `e2_concentracao.py`, `e3_etf.py`, `e4_tiers.py`, `e5_candidata.py` e `e6_recencia.py`. Tudo leva menos de 5 minutos.

- `motor.py`: carga papel a papel, sinal, simulador executável, P&L, hedge inteiro, ICC e resumos.
- `comum.py`: avaliação padrão de uma configuração, com estresses e hedge inteiro.
- `e0_cache.py`: gera `super.pkl` (superconjunto dos 61 papéis) e valida contra o agente C. Saída em `e0_out.txt`.
- `e1_limiar.py`: grade de limiares. Saídas em `e1_out.txt`, `e1_grade.csv` e `e1_curva.png` (curva volume × PF × R$).
- `e2_concentracao.py`: concentração diária. Saídas em `e2_out.txt` e `e2_concentracao.csv`.
- `e3_etf.py`: ETFs. Saídas em `e3_out.txt` e `e3_etf.csv`.
- `e4_tiers.py`: tiers de liquidez. Saídas em `e4_out.txt` e `e4_tiers.csv`.
- `e5_candidata.py`: candidatas, grade ±20%, beta, estresses e walk-forward. Saídas em `e5_out.txt`, `e5_candidatas.csv`, `e5_grade.csv`, `e5_walkforward.csv` e `trades_C0.csv` … `trades_V7.csv`.
- `e6_recencia.py`: recência e incremento sobre a base. Saídas em `e6_out.txt` e `e6_recencia.csv`.
- `rodar_universo.py`: pipeline. Testes em `universo61/` e `universo61_pf135/`.
