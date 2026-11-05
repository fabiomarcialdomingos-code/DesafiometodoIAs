# CARTEIRA DO PROJETO: índice mestre (congelada em 03/11/2026, 11:50)

> **Decisão do Fabio:** a busca por métodos novos está encerrada. A carteira são os métodos abaixo. Daqui em diante, quando houver material suficiente (operações reais e testes), o trabalho é só melhorar esses métodos.
> **Para retomar:** abra este arquivo. Cada método tem código, regra, números, arquivos e próximo passo.

## Visão geral

| Código | Nome | Mercado | Status em 03/11 | Frequência |
|---|---|---|---|---|
| **G-M1** | Zona de Ruído | WIN intraday (MT5 Clear) | **LIGADO** na conta real (WIN_Grade) | ~1,3/sem |
| **G-M2** | Fade do Gap | WIN intraday (MT5 Clear) | **LIGADO** na conta real (WIN_Grade) | ~1/sem |
| G-M3 | Continuação da 1ª hora | WIN intraday | **DESLIGADO**: reprovado fora da amostra. Fica no código com `InpM3On=false` | — |
| **G-M4** | Drift Noturno WIN | WIN de um dia para o outro | **APROVADO**, falta implantar (WIN_Grade v1.04) | ~0,5/sem |
| **A-M5** | Drift Noturno Ações | 11 ações/ETFs à vista, de um dia para o outro | **APROVADO**, falta robô próprio | ~5/sem |
| **C-M6** | Binance Maré 50 | Cripto spot BRL (BTC/ETH/SOL) | **APROVADO**, automação marcada para hoje às 19:00 | ~0,6/sem |

**Volume total previsto:** ~9 operações por semana.

**Correlações:**
- M1 × M2: baixa;
- M4 × M1: −0,02;
- M4 × M2: −0,10;
- M4 × M5 (mensal): 0,47;
- M6 é independente da bolsa.

**Custos usados nos testes:**
- WIN: 15 pts por ida e volta por contrato. No Testador: R$0,25 por lado + 5 pts de slippage por lado.
- Ações: 0,06% ida e volta.
- Cripto: 0,10% por ordem.

---

## G-M1: Zona de Ruído (WIN, intraday) · LIGADO
- **Origem:** "noise area" de Zarattini/Aziz/Barbon.
- **Sinais:** no fechamento das velas H1 das 11h, 12h e 13h. Referência: abertura das 10:00.
- **Sigma:** média de 14 dias de |close/open10 − 1| em cada horário.
- **Bandas:** 0,8·sigma em torno de máx/mín(open10, fechamento de ontem), com filtro de VWAP.
- **Stop:** max(banda, VWAP), entre 0,10% e 0,35%. Risco de R$80.
- **Gestão:** até 2 piramidações no fechamento da hora; trailing no fechamento da hora; zera às 17:30; 1 operação por dia.
- **PF de laboratório:**

| 2022 (fora da amostra) | 2023 (fora da amostra) | 2024 | 2025 | 2026 |
|---|---|---|---|---|
| 1,84 | 1,45 | 1,46 | 1,36 | 1,63 |

- **Testador:**
  - No Model=1 o resultado é pior, porque a saída acontece no extremo do minuto (−39 pts por saída).
  - O Model=4 só é possível a partir de 2026, porque só há ticks locais de jan/2026 em diante.
- **Arquivos:**
  - código: `out/WIN_Grade.mq5`;
  - laboratório: `grade/noise.py` (`run_noise`);
  - operações: `grade/trades_metodo1_N.csv`.
- **A melhorar:** comparar com as operações reais quando houver de 20 a 30; rodar o T4_2026 com Model=4.

## G-M2: Fade do Gap (WIN, intraday) · LIGADO
- **Entrada:** às 10:00, contra o gap (abertura das 9:00 − fechamento de ontem).
- **Condições:** 0,10 ≤ |gap|/ATRd ≤ 1,0, e o gap ainda aberto às 9:55.
- **Stop:** 0,3·ATRd, com teto de risco de R$200.
- **Saída e exceções:** sai às 17:05; não opera no dia de vencimento.
- **PF de laboratório:**

| 2022 (fora da amostra) | 2023 (fora da amostra) | 2024 | 2025 | 2026 |
|---|---|---|---|---|
| 1,15 | 1,26 | 1,14 | 1,71 | 1,80 |

- **Testador G2b:** PF 1,37 (1,04 / 1,57 / 1,60).
- **Arquivos:** `grade/horarios.py` (`sig_gapfade`); operações em `grade/trades_metodo2_gap.csv`.
- **A melhorar:** acompanhar se o teto de R$200 ainda corta sinais com a volatilidade de 2026.

**Grade M1 + M2 (laboratório):**

| 2022 | 2023 | 2024 | 2025 | 2026 | DD |
|---|---|---|---|---|---|
| R$4.815 | R$4.410 | R$3.008 | R$6.030 | R$6.147 | R$1.867 |

## G-M3: Continuação da 1ª hora · DESLIGADO
- **Por quê:** reprovou fora da amostra (2022 PF 0,65; 2023 PF 0,66).
- **Situação:** desligado na v1.03, que vai para a conta hoje à noite (rodada 13). Não volta sem dado novo que justifique.

## G-M4: Drift Noturno WIN · APROVADO, a implantar
- **Origem:** prêmio noturno depois de dias de queda (Boyarchenko/Larsen/Whelan 2023; Lou/Polk/Skouras 2019).
- **Regra de compra:** no último candle do pregão (decide de 1 a 3 min antes do fim), quando valem as duas condições:
  - retorno do dia desde a abertura das 9h < −1 × desvio-padrão de 20 dias (z < −1);
  - IBS = (fechamento − mínima)/(máxima − mínima) < 0,15, ou seja, fechando colado na mínima.
- **Tamanho:** 1 contrato; 2 contratos se z < −2.
- **Saída:** no dia seguinte, entre 9:30 e 10:00.
- **Não opera:**
  - na véspera de vencimento;
  - na véspera de feriado no meio da semana (2 dias de gap: PF ~0,4 no WIN e no BOVA11);
  - na véspera de eleição ou de evento grande.
- **Sexta-feira:** opera (PF 4,7).
- **Números (WIN 2022–26, 1 contrato):**
  - fechamento exato: n=121, PF 2,68, R$7.476, pior noite −R$448;
    - por ano: 2022 R$1.769 (2,01), 2023 R$1.688 (3,37), 2024 R$791 (1,86), 2025 R$670 (2,63), 2026 R$2.558 (4,92);
  - realista, decidindo 5 min antes: PF 2,16, R$6.162;
  - com 2 contratos se z < −2: R$10.865, PF 3,09.
- **Validação longa (BOVA11 2009–2026):** PF 1,41 em 2009–15 e 2,19 em 2016–26; 83% dos anos positivos.
- **Variante de volume (reserva):** z < −0,75 e IBS < 0,12 → PF 2,40 (realista 2,13).
- **Reprovado:** o lado vendido (espelho, PF 0,85) e a escala 1/2/3 contratos (sobreajuste).
- **Precisa:**
  - conta da Clear habilitada para swing, senão zeragem compulsória e taxa de R$50;
  - margem de ~R$4–5 mil por contrato (confirmar com a Clear).
- **Risco:** gap de madrugada. Na eleição de 26/10/2026, −15% teria custado ≈ −R$6 mil por contrato.
- **Implantação:** construída em 04/11 como `out/WIN_Grade_v104.mq5` (42 inputs; `out/grade_v104_inputs_base.txt`), com M4 desligado por padrão. Teste no Testador na rodada 17.
  - **Decisão:** 2 min antes do último candle típico, a mediana dos 5 dias anteriores (em geral 18:22).
  - **Por que a mediana:** em 2022–23, nos meses de horário de verão dos EUA, o último candle era às 17:54. Desde 2024 é sempre 18:24.
  - **Réplica no laboratório** (`drift/m4_ea_replica.py`): 120 operações. Com 1 ou 2 contratos, PF 2,63 e R$9.398. Com sempre 1 contrato, PF 2,13 e R$5.869. Todos os anos positivos.
  - **Atenção:** decidir no horário fixo de 17:52 nos meses de horário de verão derrubou 2024 para PF 0,58. Por isso a decisão segue o fim real do pregão.
- **Arquivos:** `drift/base.py`, `drift/consolida.py`, `drift/win_real.py`, `drift/ibs_grid.py`, `drift/longo2.py`, `drift/resultado_drift2.md`.

## A-M5: Drift Noturno Ações · APROVADO, a implantar
- **Regra:** a mesma do M4, com z < −0,75 e IBS < 0,12.
- **Execução:** compra no leilão de fechamento e vende na abertura do dia seguinte.
- **Papéis:** PETR4, VALE3, ITUB4, BBDC4, BBAS3, B3SA3, PRIO3, BOVA11, SMAL11, WEGE3, ABEV3. Os fracos (BBDC4 0,68, ABEV3 1,02, VALE3 1,07) ficam na lista para não sobreajustar.
- **Números (D1 2023–26):**
  - fechamento exato: n=972, ~5,2 por semana, PF 1,71, pior ano 1,53, média +0,153%;
  - realista, decidindo 5 min antes: PF 1,42, média +0,104%;
  - decidindo 15 min antes: PF 1,32.
- **Capital:** posições simultâneas — média 2,1, p90 4, máximo 8.
  - R$5 mil por posição: ~R$1,3–2 mil por ano, DD −R$679.
  - R$10 mil por posição: ~R$2,6 mil por ano realista, com ~R$40 mil de capital (até R$80 mil nos extremos).
- **A confirmar:**
  - se o MT5 da Clear negocia ações na mesma conta;
  - como o robô participa do leilão de fechamento;
  - o imposto do swing (15%; vendas de ações até R$20 mil/mês são isentas, ETF não).
- **Implantação:** robô separado, multi-símbolo, magic próprio.
- **Arquivos:** `drift/expandir.py`, `drift/expandir2.py`, `drift/acoes_real.py`; dados em `proj/WIN_WDO/export/acoes/`.

## C-M6: Binance Maré 50 · APROVADO, automação hoje às 19:00
- **Regra completa:** `out/BINANCE_MARE50.md`.
  - BTC/ETH/SOL, 1/3 do capital cada.
  - Comprado se o fechamento diário estiver acima da SMA50.
  - Exposição = mín(1; 0,60/vol20 anual), com faixa de rebalanceamento de 10%.
  - Decisão às 21:00 BRT.
- **Resultados:**

| 2021 | 2022 | 2023 | 2024 | 2025 | 2026 | DD |
|---|---|---|---|---|---|---|
| +127% | −27% | +201% | +37% | +26% | +11% | −41% |

  O número realista é menor, por causa do viés da SOL.
- **Sinal em 31/10:** tudo em caixa.
- **Automação:**
  - GitHub Actions às 00:05 UTC, puxando de data-api.binance.vision;
  - tabela `cripto_sinais` no Neon;
  - alerta no Telegram;
  - página na Vercel.
- **O Fabio traz:**
  - nome do repositório (sugestão: `binance-mare-50`);
  - token do bot do Telegram, já com uma mensagem enviada a ele;
  - decisão sobre o Neon;
  - capital.
- **Arquivos:** `cripto/swing.py`, `cripto/swing2.py`, `cripto/resultado_swing.md`, `cripto/resultado_gestao.md`.

---

## Robô ao vivo e arquivos do MT5
- **Agora:** WIN_Grade v1.02 (M1+M2+M3) em WINZ26 H1, magic 270001, ligado às 07:18.
- **Hoje à noite:** v1.03 com o M3 desligado. Arquivos: `out/WIN_Grade.mq5` e `out/win_grade_live.set` (31 inputs, UTF-16).
- **Backups:** `out/WIN_Grade_v101_backup.mq5`, `out/WIN_Grade_v102_backup.mq5`.
- **No PC do Fabio:**
  - LIGAR_GRADE_WIN.bat (Área de Trabalho);
  - `C:\mt5tests\grade_live.ini`;
  - perfil `Grade`;
  - pasta `C:\Arquivos\Bolsa de Valores\WIN_WDO`.
- **O que o robô grava** em `Common\Files`:
  - diário: `grade_diario_AAAAMMDD.txt`;
  - estado: `grade_estado_270001.csv`.
- **Relatório da noite:** `relatorio/refaz_dia.py`, que refaz as decisões do M1/M2 de um dia.
- **Regras de segurança:**
  - o Claude Code nunca envia ordens; o Fabio liga o robô com dois cliques no .bat;
  - o MT5 só reinicia com o mercado fechado e o robô zerado (antes das 9:00 ou depois das 18:30);
  - no Testador, só WIN$N (o WIN$ é ajustado); nunca deixar input de texto vazio no .ini.

## Diário de bordo
- **03/11:** 0 operações, todas por regra.
  - M2: gap −1.710 pts, mas o stop de R$260 passou do teto de R$200. O laboratório mostra PF ≤1,05 acima de R$200, então o teto fica.
  - M3: bloqueado pelo teto.
  - M1: sem sinal.
  - Houve uma operação manual às 12:23 (magic 0, −R$12) e trocas de período no gráfico às 12:24 e 12:27. Isso revelou um defeito no diário, corrigido na v1.03a (`out/WIN_Grade.mq5`; backup da v1.03 em `out/WIN_Grade_v103_backup.mq5`).

- **Nota Clear de 03/11 (operações manuais do Fabio em outro PC, mesma conta):**
  - 31 contratos de WIN de ida e volta, ajuste de day trade de +R$867;
  - custos de R$15,50 = registro BM&F 9,92 + emolumentos 5,58, ou seja, **R$0,25 por contrato por lado** (1,25 pt);
  - taxa operacional (corretagem) R$0;
  - IRRF 1% = R$8,51; o DARF de 20% sobre o líquido do mês vence no último dia útil do mês seguinte.
  - O custo do laboratório (15 pts ida e volta) e o do Testador (0,25/lado + 5 pts de slippage/lado) estão certos nas taxas. O restante é slippage estimado, a medir com as execuções reais do robô.
- **ATENÇÃO:** a conta é netting. Operação manual no WINZ26, de qualquer computador, mistura com a posição do robô.

- **04/11:** 0 operações, por regra outra vez.
  - M2: stop de R$260, acima do teto de R$200.
  - M1: preço dentro da zona.
  - Diagnóstico na rodada 16.
- **04/11, Testador da v1.04 (rodada 17, WIN$N 2022–26, Model=1):**
  - M4 sozinho: 114 operações, R$10.113, PF 3,02.
  - PF por ano: 2,54 / 3,60 / 1,68 / 3,41 / 5,31.
  - Pior operação: −R$379. DD −R$685. 77% dos meses positivos.
  - Na grade: M1 PF 1,26 e M2 PF 1,23.
  - Achado: em 7 dias a mediana deu decisão às 18:29, e 6 deles ficaram sem decidir porque não havia tick. Corrigido na **v1.04b**, que usa o fim de pregão mais cedo dos 5 dias.
  - Para ligar: `out/PROMPT_CLAUDE_CODE_18_LIGAR_M4.md` + `out/win_grade_v104_live.set`. Só depois de o swing estar liberado na Clear e com ~R$10 mil de margem.
- **04/11, 19h — decisão do Fabio:** o M4 vai ser operado **MANUALMENTE**, no swing do home broker da Clear. O robô só avisa no celular.
  - Robô v1.04d com `InpM4AlertOnly=true` e `InpM4Push=false` (46 inputs), ligado pela rodada 18. O alerta é uma janela com som no próprio MT5 do PC do robô, sem celular.
  - Alerta de compra às 18:20 e alerta de venda às 9:15. Vender até 9:30, antes do M2 das 10h, porque a conta é netting.
  - Laboratório com alerta às 18:20 e saída às 9:30, 1 contrato: 126 operações, PF 2,32, R$6.237. PF por ano: 1,32 / 2,52 / 2,38 / 2,78 / 5,23.
  - Saída às 9:00, na abertura: PF 1,52, com 2022 em 0,78. Evitar.
- **04/11, rodada 18:** v1.04d instalada como WIN_Grade (46 inputs, 0 erros). Backup da v1.03a em `WIN_WDO\backup_r18_20261104\`.
  - T18_m4 (decisão às 18:20, saída às 10:00, 1 ou 2 contratos): 121 operações, R$9.790, PF 2,70.
  - PF por ano: 1,79 / 3,35 / 1,81 / 3,74 / 5,44.
  - Trocar 2 minutos no horário mexe ~0,3 no PF. Para a operação manual, a expectativa realista é **PF 2 a 2,5**.
- **04/11 — margens de swing.** Fonte: tabela da XP de 23/10/2026; a Clear é do grupo XP, mas a margem exata vem do MT5 ou da Clear.
  - Swing: BIT R$600, ETR R$1.230, SOL R$1.564, **WIN R$1.000**, WDO R$1.500 por contrato.
  - Day trade: BIT 45, ETR 70, SOL 85, WIN 155, WDO 140.
  - O M4 com 2 WIN precisa de ~R$2 mil de margem, e não dos R$5 mil por contrato que eu tinha estimado.
  - Maré 50 nos futuros com 1 contrato de cada: margem R$3.394, ou ~R$4,5 mil com folga para o ajuste diário. Isso dá ~2x de alavancagem sobre ~R$10 mil de exposição.
- **04/11, M2 volume:** estudo em `m2vol/resultado_m2vol.md`. Candidato **M2 v2**: 2 contratos quando o gap já começou a voltar às 9:55, mais o M2 Tarde às 13:10 nos dias sem M2.
  - Resultado: +47% de entradas, lucro ×2, PF 1,42, DD −2,1 mil.
  - Ainda falta o Testador.
- **04/11, 22h:** pasta nova no PC do Fabio para o trabalho do M2: `C:\Arquivos\Bolsa de Valores\WIN_M2` (relatórios, zips e resultados vão em `WIN_M2\Doc`). O Code roda a rodada 21 (histórico longo) nela e o GPT revisa o M2 v2 (`out/BRIEF_GPT_M2.md`).
- **04/11, 23h — rodadas 2 a 4 do M2:** o M2 v2 continua congelado.
  - Reprovados: outros ativos (WDO, ações, small caps, BOVA11, IVVB11, BIT), gap residual, vol alta e as hipóteses do GPT.
  - Só o IND replica o WIN, e serve para lotes grandes.
  - Detalhes em `m2vol/resultado_m2vol.md`.
- **04/11, 23h30 — candidatos novos (só em papel, sem dinheiro):**
  - **M2-A "Ação atrasada"** (small caps × WIN da 1ª hora): PF 1,36, 6,8 operações por semana, todos os anos ≥ 1,21. Sensível à execução às 10:05.
  - **M2-N "M2 Noturno"** (fade do WIN depois do fechamento do à vista até as 9:00): PF 2,30 sozinho, mas frágil (eleição).
  - O M2 v2 segue congelado e sem mudanças.
- **05/11, madrugada:** M2-A atualizado para a versão **V6** (sem o filtro de força do WIN): 9 a 10 operações por semana, PF 1,31, todos os anos ≥ 1,23. A expansão para ~200 ações (rodada 24) pode levar a ~35 operações por semana.
- **05/11, 6h — teste do M2-A nas 117 ações novas, fora da amostra:** PF 1,05 depois do custo, 2025 em 0,94. **Reprovado.** O M2-A fica rebaixado para observação em papel. O M2 v2 segue como único método principal do WIN.

## Agenda de hoje (03/11)
1. **18:30:** o Fabio cola `out/PROMPT_CLAUDE_CODE_13_NOITE.md` no Code. Volta o `relatorio_20261103.zip`, o Claude monta o relatório do dia, e a v1.03 é instalada.
2. **19:00:** automação do C-M6 (Binance Maré 50).
3. **Depois:** G-M4 na WIN_Grade v1.04 e teste no Testador. O A-M5 vem depois de confirmar as ações no MT5 da Clear.

## Decisões pendentes do Fabio
- Capital: ~R$10 mil só para o M4 (2 contratos), ou ~R$40–50 mil para M4 + M5.
- Habilitar swing na Clear.
- Capital do M6.

## Lista de melhorias (só com material suficiente)
- **M1/M2:** comparar operações reais com o laboratório (de 20 a 30 operações); Model=4 em 2026.
- **M4:** confirmar com o Testador a decisão no último candle; filtro de eventos (calendário de eleições e feriados).
- **M5:** testar a entrada no leilão com dados reais; avaliar tirar os papéis fracos, mas só com dado fora da amostra.
- **M6:** acompanhar se o sinal real bate com o backtest; fase 2 com ordens automáticas pela API.

## Ideias congeladas (sem pesquisa nova)
- TSMOM 6m no dólar: lento, ~7 operações por ano, precisa de R$25–30 mil.
- Regra do "negócio grande" no volume.
- Drift no WDO, os dois lados: PF 2,16, mas 2024 deu 0,80.

**Tudo o que já foi reprovado** (não retestar): `grade/resultado_*.md`, `garimpo/resultado_*.md`, `cripto/resultado_*.md`.
