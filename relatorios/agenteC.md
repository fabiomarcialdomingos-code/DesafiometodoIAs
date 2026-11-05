# Ações: gap idiossincrático e lead-lag do WIN (agenteC, 04/11/2026)

## Resumo e veredito

**Uma regra passa no critério: a "AÇÃO ATRASADA".** Ela nasceu da parte 2 (lead-lag). Nas **small caps**, o leilão das 10:00 incorpora só parte do que o WIN andou entre 9:00 e 10:00, e a ação continua andando na direção do WIN depois da abertura. O fade do gap residual só tem vantagem nesse caso, quando a ação ficou "atrás" do índice **na direção do WIN da 1ª hora**. Na metade oposta (a ação "adiantada") o fade perde dinheiro, e é por isso que o fade residual simples (parte 1) não chega a PF 1,2.

Regra final, `final.py`:

| | n | op/sem | PF | PF bruto | R$ (R$80 por operação) | DD | 2022 | 2023 | 2024 | 2025 | 2026 | corr. com o M2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **ATRASADA** (small, 10:05→16:55, hedge WIN, stop 1,0 ATRd) | 1.659 | 6,8 | **1,36** | 1,60 | 9.428 | −991 | 1,52 | 1,31 | 1,21 | 1,37 | 1,52 | 0,01 |
| mesma, sem hedge | 1.659 | 6,8 | 1,25 | 1,42 | 7.540 | −1.979 | 1,75 | 1,46 | 1,06 | 1,14 | 1,20 | −0,06 |

- **Grade ±20%:** passam todos os 10 pontos (lo, hi, wmin, stop e janela do beta), com PF entre 1,31 e 1,42 e nenhum ano abaixo de 1,07.
- **Walk-forward:** escolhendo os parâmetros só com 2022–23, o PF de 2024–26 fica em 1,26–1,43. Entre as 45 combinações, a mediana fora da amostra é 1,30, e 98% delas ficam acima de 1.
- **Correlação diária com o M2 do WIN:** 0,01. Somadas, as duas dão R$35,8 mil, com DD de −2.163 (o M2 sozinho tem DD de −2.108).

**Mas há uma fragilidade séria de execução, e é ela que decide.** Toda a vantagem depende de entrar **na abertura da barra 10:05**, logo depois do leilão:

| Estresse (mesmas 1.659 operações) | PF | anos |
|---|---|---|
| base, entrada às 10:05 | 1,36 | todos ≥ 1,21 |
| entrada às 10:10 | **1,18** | 1,07–1,51 |
| entrada às 10:15 | 1,13 | 1,04–1,44 |
| +1 tick de derrapagem na entrada, além do custo | **1,16** | 1,03–1,31 |
| custo ×1,5 (0,15%) | 1,27 | ≥ 1,13 |
| custo ×2 (0,20%) | 1,18 | ≥ 1,04 |

**Veredito honesto:** pelo critério formal, **APROVA**: PF 1,36, todos os anos acima de 1,2, n = 1.659 e robusta na grade de ±20%. O volume é modesto (6,8 operações por semana; ~11 por semana com lo = 0,20, também aprovado) e o dinheiro é pequeno (~R$2 mil por ano arriscando R$80 por operação). A vantagem some com 5 minutos de atraso ou 1 tick de derrapagem. **Recomendo paper trading / forward test de 2–3 meses**, medindo o preço real que se consegue às 10:05 nas small caps, antes de pôr dinheiro. O coeficiente do lead-lag também está caindo com o tempo (ver a parte 2). Nada nas blue chips passa, e as ideias de volume (parte 4) reprovam.

---

## Dados e convenções (sem look-ahead)

- **Painel** (`core.py`): dias × barras M5. Para o WIN são as barras 9:00–18:25. Para as ações são as barras 10:00–17:55, descartando as barras ≥ 18:00 e as barras ≥ 17:00 nos dias de horário de verão dos EUA (`horarios.us_dst`). Barra sem negócio = último fechamento. O preço de abertura da 1ª barra é igual à abertura do D1 em 100% dos casos (conferido).
- **Gap da ação:** abertura oficial (D1) / fechamento oficial anterior − 1. Descarto |gap| ≥ 15%, que são eventos societários.
- **r_WIN até as 10:00:** fechamento da barra 9:55 / fechamento da barra 16:55 ou 17:55 do dia anterior (o horário do fechamento do à vista). Decomposto em *noite* (fechamento do à vista → 9:00) e *1ª hora* (9:00 → 10:00). Excluo os dias de vencimento do WIN, onde a série contN salta.
- **beta:** cov/var de 60 pregões do gap da ação contra r_WIN até as 10:00, com `shift(1)`, ou seja, só com o passado (mínimo de 40 dias). **ATRd:** média de 14 dias de (máx − mín) até ontem.
- **gap_resid** = gap − beta × r_WIN até as 10:00, em unidades de ATRd. **lag** = −gap_resid.
- **Entrada:** abertura da barra (10:05, 10:10, 10:15 ou 10:30). Às 10:05 exijo que o leilão tenha saído na barra 10:00. Em ~25–40% dos dias o leilão das small caps só termina na barra 10:05 ou depois, e esses dias ficam de fora; a variante "tardios" entra às 10:10. **Saída:** fechamento da barra 10:55 (11:00), da 12:55 (13:00) ou da 16:50 (16:55).
- **Tamanho:** R$80 / (k × ATRd) de nocional. O stop é checado barra a barra (máx/mín sem hedge; fechamento do P&L combinado com hedge). "k = None" significa sem stop, com o tamanho calculado como se k = 0,3. Isso **não** limita o risco a R$80: 23% das operações perdem mais que isso. Por isso a regra final usa stop real de 1,0 ATRd.
- **Custo:** 0,06% (blue chips) / 0,10% (small caps) do nocional, ida e volta. No hedge, 15 pts por contrato de WIN, proporcional ao tamanho do hedge. **Hedge:** vende beta × nocional em WIN no mesmo horário. Por operação ele é fracionário (~0,3 contrato). Por isso também testei o hedge agregado por dia com **contratos inteiros** (média de 0,95 contrato por dia; 37% dos dias arredondam para 0). Nesse teste, a ATRASADA sem stop faz R$29,5 mil, contra R$32,0 mil com o hedge fracionário. Logo, o hedge é executável.
- **Correlação com o M2:** R$ diário contra `agenteA/trades_win.csv`, com os dias sem operação valendo 0.

## Parte 1: fade do gap idiossincrático (`p1_resid.py`, `p1_out.txt`)

Mesmos filtros nas linhas abaixo: |resid| entre 0,3 e 1,2 ATRd, small caps, R$80 por operação.

| Teste | n | PF | PF bruto | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|
| **gap bruto** (controle, sem tirar o WIN), 10:05→16:55 | 4.163 | 0,99 | 1,13 | 0,96 | 1,17 | 0,96 | 0,94 | 0,93 |
| **gap residual**, 10:05→16:55, sem stop | 2.261 | 1,17 | 1,33 | 1,61 | 1,42 | 0,99 | 0,98 | 1,32 |
| idem, com hedge | 2.261 | 1,15 | 1,34 | 1,25 | 1,22 | 0,96 | 1,17 | 1,36 |
| idem, stop 0,3 ATRd, sem hedge | 2.261 | 1,13 | 1,34 | 1,44 | 1,18 | 1,08 | 0,97 | 1,24 |
| residual, 10:05→13:00, sem stop | 2.261 | 1,17 | 1,37 | 1,64 | 1,38 | 1,12 | 0,96 | 1,11 |
| residual, entrada 10:15→16:55 | 4.794 | 1,09 | 1,23 | 1,02 | 1,18 | 1,06 | 0,98 | 1,27 |
| residual, entrada 10:30→16:55 | 4.875 | 1,05 | 1,19 | 1,10 | 1,10 | 0,95 | 0,92 | 1,25 |
| residual, +1 tick na entrada | 2.261 | 1,02 | 1,33 | 1,39 | 1,21 | 0,86 | 0,85 | 1,18 |
| blue chips, melhor linha (10:05→16:55, \|r\| ≥ 0,15) | 2.439 | 0,92 | 1,08 | – | 1,11 | 0,94 | 0,81 | 0,89 |

- **Tirar o WIN do gap funciona.** O PF bruto sobe de 1,13 para 1,33 nas small caps. A parte do gap que veio do índice não volta; a parte idiossincrática volta.
- **Não basta, porém.** Depois do custo o PF fica em 1,15–1,17, com 2024 e 2025 em torno de 1,0. A única linha que passa no papel é a faixa estreita 0,5–1,2 com hedge (n = 329, PF 1,29), no limite do n mínimo, e não a adoto. A parte 2 explica por quê.
- **A reversão é rápida.** Metade do movimento acontece entre 10:05 e 10:15. Entrar às 10:30, como no fade antigo, perde quase tudo.
- **Blue chips:** o gap residual é pequeno (mediana de ~0,11 ATRd), a vantagem bruta é de 1–3 bps e o custo de 6 bps acaba com ela. Reprovado em todas as combinações.

## Parte 2: lead-lag do WIN (`p2_leadlag.py`, `p2_out.txt`, `p2b_regra.py`, `p2b_out.txt`)

Regressão empilhada (ação × dia), com erros-padrão agrupados por dia. y = retorno da ação de 10:05 a 11:00 com hedge, em fração. As células trazem coeficiente (t).

| | gap da ação | beta × WIN da noite | beta × WIN 9–10h |
|---|---|---|---|
| small caps (n = 42.403) | −0,089 (t −3,6) | +0,030 (t 0,7) | **+0,228 (t 4,1)** |
| blue chips (n = 6.108) | −0,068 (t −2,6) | +0,083 (t 2,2) | +0,074 (t 2,1) |

O coeficiente do beta × WIN 9–10h nas small caps, ano a ano:

| | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|
| coeficiente (t) | +0,45 (t 4,8) | +0,29 (t 2,5) | +0,26 (t 2,9) | +0,21 (t 1,6) | **+0,04 (t 0,6)** |

- **Sim, as small caps sub-reagem ao WIN, e só ao WIN da 1ª hora.** O que o WIN andou durante a noite já está no preço do leilão. O que andou entre 9:00 e 10:00, quando o à vista está fechado, entra só em parte: cerca de 20% ainda aparece de 10:05 a 11:00.
- O mecanismo faz sentido. O leilão de uma small cap ilíquida não absorve toda a informação de mercado acumulada na hora em que só o futuro negocia (é o lead-lag clássico, em que o futuro lidera e o papel pequeno segue).
- **O coeficiente cai ano a ano** e não é significativo em 2026. A regra de negociação ainda funciona em 2026 (PF 1,52), mas o sinal estatístico enfraquece. Isso é compatível com arbitragem crescente e é o principal risco de futuro.
- Nas blue chips a sub-reação existe, mas é pequena demais para o custo.

**A regra (ATRASADA):** opera quando 0,25 ≤ |lag| ≤ 1,2 ATRd e **sinal(lag) = sinal(WIN 9–10h)**, com |WIN 9–10h| ≥ 0,5 × a média dos 60 pregões anteriores. Entra às 10:05 na direção do lag e sai às 16:55. Linhas abaixo sem stop, para comparar com a parte 1:

| Regra | n | PF | PF bruto | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|
| ATRASADA, com hedge | 1.659 | 1,37 | 1,61 | 1,61 | 1,39 | 1,19 | 1,30 | 1,58 |
| ADIANTADA (complemento: fade contra o WIN 9–10h) | 962 | **0,95** | 1,11 | 0,95 | 1,10 | 0,84 | 0,93 | 1,04 |
| ATRASADA, sem filtro de força do WIN (wmin = 0) | 2.224 | 1,33 | 1,55 | 1,43 | 1,49 | 1,27 | 1,20 | 1,42 |
| blue chips, ATRASADA (lo 0,15) | 984 | 0,99 | 1,18 | – | 0,93 | 1,20 | 1,05 | 0,71 |

O complemento perde dinheiro. Isso confirma que a vantagem é o **lead-lag**, e não uma reversão genérica do gap.

## Parte 3: varredura por ação e grupo (`p3_varredura.py`, `p3_out.txt`, `p3_varredura.csv`)

Métrica: PF líquido por papel e grupo, e por ano.

- **Por papel:** 39 das 50 small caps têm PF > 1 na ATRASADA, e só 6 têm todos os anos ≥ 1 (n pequeno, ~20–70 por papel). Sem os 5 melhores papéis o PF ainda é 1,24 (todos os anos ≥ 1,05). A vantagem é **ampla**, não concentrada.
- **Por liquidez** (tercil do volume financeiro de 60 dias até ontem): baixa 1,42, média 1,47, alta 1,23. Os três passam em todos os anos, então a liquidez não filtra nada; a vantagem é menor no tercil mais líquido, como a hipótese prevê.
- **Por setor:** indústria, varejo e mineração/siderurgia passam em todos os anos. Petróleo (0,92), agro (1,00), bancos (0,74), utilidades (1,04) e tecnologia (0,46) não passam. Há uma leitura econômica possível (o gap de petróleo e agro vem da commodity, não de exagero). Mas mineração contradiz essa leitura, o n por setor é de 80–280 e no fade simples a ordem dos setores muda. **Não aceito** filtro por setor.
- **Por preço/tick:** não é monotônico (tick > 20 bps: 1,96; tick de 5–10 bps: 1,06; tick < 5 bps: 1,46). Logo, não é bid-ask bounce de papel barato, mas também não dá um filtro estável. Só com preço ≥ R$10 o PF é 1,21, com 2025 em 0,92.
- **Compra × venda:** venda 1,44 (todos os anos ≥ 1,25); compra 1,28 (2024 em 0,92).
- **ADR × demais** (PETR4, VALE3, ITUB4, BBDC4, ABEV3 contra as outras blue chips): nenhum dos dois grupos passa, nem no fade residual (0,94 × 0,92) nem na ATRASADA (0,98 × 1,01). Não há diferença.
- **Conclusão da parte 3:** nenhum padrão de grupo estável que acrescente algo à regra.

## Parte 4: ideia própria para volume (`p4_intraday.py`, `p4_out.txt`, `p5_volume.py`, `p5_out.txt`)

**Ideia: catch-up intradiário.** Se as small caps andam atrás do WIN, isso deveria valer o dia todo. A regra: em cada checkpoint (10:30, 11:00, …, 15:30), comprar ou vender as ações que ficaram atrás de beta × WIN nos últimos 30 ou 60 minutos, na direção do WIN, saindo em 30 minutos, 60 minutos ou às 16:55.

- **Regressão:** o coeficiente do WIN dos últimos 30 minutos varia entre −0,04 e +0,17, quase sempre com t < 2 (só às 14:00 e às 15:00 chega a t ≈ 3), e é pequeno.
- **Regra:** 20 a 370 operações por semana, PF bruto de 0,94 a 1,15 e **PF líquido de 0,60 a 0,88 em todas as variantes**. **Reprovada.**
- A sub-reação existe **só** na janela 9:00–10:00, quando o à vista está fechado. Em pregão contínuo as small caps acompanham o índice rápido o bastante para o custo de 0,10% comer tudo.

**Alavancas de volume dentro da própria ATRASADA** (16:55, com hedge, sem stop):

| Variante | n | op/sem | PF | ano mais fraco |
|---|---|---|---|---|
| lo 0,25, wmin 0,5 (candidata) | 1.659 | 6,8 | 1,37 | 1,19 |
| lo 0,25 + tardios (leilão na barra 10:05, entra às 10:10) | 2.317 | 9,6 | 1,35 | 1,24 |
| lo 0,20, wmin 0,5 | 2.768 | 11,4 | 1,32 | 1,13 |
| lo 0,20 + tardios (versão VOLUME) | 3.671 | 15,1 | 1,32 | **1,03 (2026)** |
| lo 0,15 + tardios | 5.910 | 24,4 | 1,22 | 1,04 |
| lo 0,10 | 7.615 | 31,4 | 1,15 | – (reprova) |

A versão VOLUME (15 operações por semana) passa no ponto base, mas **não é robusta**: com wmin = 0,6 o pior ano cai para 0,99, com custo ×1,5 para 0,97 e com +1 tick o PF total é 1,14. Fico com a candidata de 6,8 a ~11 operações por semana.

## Regra final em detalhe (`final.py`, `final_out.txt`, `trades_final.csv`)

**Regra:**
- **Universo:** as 50 small caps.
- **Às 10:00, para cada ação:**
  - lag = beta(60d) × r_WIN(fechamento do à vista anterior → 10:00) − gap, dividido pelo ATRd da ação.
  - Condições: o leilão saiu na barra 10:00; 0,25 ≤ |lag| ≤ 1,2; sinal(lag) = sinal(WIN 9:00→10:00); |WIN 9–10h| ≥ 0,5 × a média dos 60 pregões anteriores. Excluo os dias de vencimento do WIN.
- **Entrada:** a mercado na abertura da barra 10:05, na direção do lag.
- **Hedge:** vender ou comprar beta × nocional em WIN, agregado no dia em contratos inteiros.
- **Stop:** 1,0 ATRd no P&L combinado.
- **Saída:** às 16:55.
- **Tamanho:** R$80 / (1,0 × ATRd) de nocional, ~R$2,3 mil por operação.

**Exposição:**
- Opera em ~550 dias de ~1.200, com 3,0 operações por dia em média e no máximo 15 no mesmo dia.
- Na versão dimensionada como "0,3 ATRd" (sem stop), o nocional médio é de R$26 mil por dia, com máximo de R$130 mil.

**Robustez:**
- 16 de 20 trimestres têm resultado positivo.
- A saída às 13:00 dá PF 1,34 e a das 11:00 dá 1,29; as duas também passam.
- O stop de 0,3 ATRd (como no M2) dá PF 1,25, com R$20,9 mil, porque o tamanho é maior.

**Carteira com o M2 v2 do WIN (2022-02 a 2026-10):**

| | R$ | DD |
|---|---|---|
| M2 | 26.744 | −2.108 |
| ATRASADA | 9.092 | −991 |
| Soma | 35.836 | −2.163 |

A correlação diária é de 0,01 no total e de 0,03 nos dias em que os dois operam. Por ano, a ATRASADA dá R$1,8 mil / 1,3 mil / 1,5 mil / 2,4 mil / 2,0 mil.

## Ressalvas

1. **Execução às 10:05 é o ponto crítico.** Com 5 minutos de atraso nas mesmas operações o PF cai para 1,18; com +1 tick, para 1,16. O custo de 0,10% precisa incluir de fato spread e derrapagem. Na abertura das small caps o spread costuma ser maior que no resto do dia. Um forward test é indispensável.
2. **O sinal está enfraquecendo.** A regressão perde força a cada ano e em 2026 não é significativa (t 0,6), embora a regra ainda lucre em 2026.
3. **Viés de sobrevivência:** a lista das 50 small caps é a de hoje (por liquidez atual). Papéis que deixaram de existir não estão no teste. O efeito sobre uma regra intradiária de reversão deve ser pequeno, mas não é zero.
4. **Seleção de parâmetros:** a forma da regra saiu da regressão sobre a amostra inteira. O walk-forward (parâmetros só de 2022–23) mitiga isso, mas não substitui dados realmente novos.
5. **O hedge fracionário por operação é aproximado.** O hedge inteiro agregado por dia foi testado e funciona (R$29,5 mil contra 32,0 mil, na versão sem stop).
6. **Concentração de risco por dia:** até 15 operações no mesmo dia, todas na mesma direção (a do WIN). Com hedge isso fica neutro ao mercado; sem hedge, o DD dobra (−1.979 contra −991).

## Arquivos

Todos em `/home/claude/win/m2vol/agenteC/`. Para reproduzir, rode nesta ordem: `python3 -I events.py`, depois `p1_resid.py`, `p2_leadlag.py`, `p2b_regra.py`, `p3_varredura.py`, `p4_intraday.py`, `p5_volume.py` e `final.py`.

- `core.py`: painel, beta, simulador vetorizado, `resumo`.
- `painel.pkl`: cache. `events.pkl` / `events.py`: tabela ação × dia para diagnóstico.
- Parte 1: `p1_resid.py`, `p1_out.txt`, `p1_tabela.csv`.
- Parte 2: `p2_leadlag.py`, `p2_out.txt`, `p2_regressoes.csv`, `p2_regra.csv`, `p2b_regra.py`, `p2b_out.txt`, `p2b_tabela.csv`, `p2b_grade.csv`, `trades_atrasada_*.csv`.
- Parte 3: `p3_varredura.py`, `p3_out.txt`, `p3_varredura.csv`.
- Parte 4: `p4_intraday.py`, `p4_out.txt`, `p4_regressoes.csv`, `p4_regra.csv`, `p5_volume.py`, `p5_out.txt`, `p5_volume.csv`, `p5_grade_volume.csv`, `trades_volume.csv`.
- Final: `final.py`, `final_out.txt`, `final_atraso_out.txt`, `final_grade.csv`, `final_walkforward.csv`, `trades_final.csv`.
