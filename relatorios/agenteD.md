# Agente D: M2 v2 no M1 (precisão de minuto, janelas e gestão)

**Dados:** `hist21/WIN_contN_M1.csv`, 2022-01 a 2026-10, 1.182 pregões. Custo de 15 pts ida e volta por contrato, R$0,20/pt. Sem look-ahead: o sinal usa o close da barra anterior e a entrada é na abertura da barra seguinte.

**Incremento:** sempre medido contra o M2 v2 nos mesmos pregões, em R$/pregão. O IC95 vem de bootstrap em blocos móveis de 10 pregões (5.000 reamostragens).

**Critério para aprovar:**
- IC95 do incremento > 0;
- nenhum ano com PF < 1,0;
- robusto numa grade de ±20%.

Só backtest em CSV local. Nenhuma ordem foi enviada.

## Veredito curto

**Nenhuma mudança aprovada.** O M2 v2 fica como está.

| Tarefa | Resultado |
|---|---|
| 0. M1 reproduz o M5? | **Sim, exato**: 905 entradas, PF 1,42, R$26.658, DD −2.108. Os 616 trades da manhã e os 289 da tarde casam dia a dia, com o mesmo sentido, o mesmo número de contratos e o mesmo P&L. |
| 1. Minuto da entrada | A vantagem está **no leilão das 10:00 e nos ~5 min seguintes**. Antes piora; depois de 10:05 piora. 10:01–10:03 empatam com 10:00 (IC inclui 0). **Manter 10:00.** |
| 2. Curva intradiária | Só 23% do lucro sai até 10:30, 43% até 11:00 e 86% até 13:00. A saída cedo destrói valor, e a tarde nos dias com manhã tem PF 1,00. **Reprovado.** |
| 3a. Fade 17:55→18:15 | Saindo no mesmo dia: PF 0,51–0,83, perde. Segurando até a abertura do dia seguinte: PF ~1,0. **Reprovado.** |
| 3b. Âncora no fechamento do à vista | PF 1,31 (contra 1,42) e incremento de −5,8 R$/pregão. **Reprovado.** O fechamento das 18:25 é a âncora melhor. |
| 4. Parcial, break-even e trailing | Nenhuma melhora. Parcial no fechamento do gap: −6 R$/pregão (IC < 0). BE e trailing apertados pioram; os folgados empatam. **Reprovado.** |
| 5. Ideia: fade de fim de pregão até o leilão das 9:00 | +0,63 operação/semana, leg com PF 2,30, +5,3 R$/pregão (IC [2,7; 8,0]), placebo p < 0,001. **Mas falha na grade ±20%:** só 28% das células passam, porque um único fim de semana (eleição, 02→05/10/2026, gap de 9%) custa R$3.558 por contrato. **Não aprovado.** É o melhor candidato para validar fora da amostra. |

---

## 0. Reprodução (`rep.py`)
O núcleo `core.py` monta matrizes dia × minuto e segue as convenções de `engine.py` e `lab*.py`:
- abertura das 9:00 = open da 1ª barra entre 9:00 e 9:04;
- saída às 17:05 = close da barra de 17:04;
- stop checado barra a barra, preenchido na abertura se houver gap.

O M1 reproduz o M5 **exatamente**: manhã com 616 trades, PF 1,43 e R$22.583; tarde com 289 trades, PF 1,36 e R$4.075. Correlação de 1,000 por trade.

## 1. Minuto da entrada (`t1_minuto.py`, saída em `t1_minuto_out.txt`)

**(a) Sinal e entrada deslocados juntos.** Gap aberto e f são lidos no close da barra m−1; entra na abertura de m.

| Entrada | PF total | R$ | Pior ano | Incremento R$/pregão [IC95] |
|---|---|---|---|---|
| 9:50 | 1,28 | 18.807 | 1,04 | −6,5 [−11,9; −1,3] |
| 9:55 | 1,29 | 19.353 | 1,01 | −6,1 [−11,1; −1,1] |
| 9:58 | 1,37 | 23.633 | 1,10 | −2,5 [−6,9; 1,6] |
| 9:59 | 1,40 | 25.438 | 1,13 | −1,0 [−4,5; 2,4] |
| **10:00 (v2)** | **1,42** | **26.658** | **1,18** | — |
| 10:01 | 1,44 | 27.141 | 1,18 | +0,4 [−4,9; 5,6] |
| 10:02 | 1,47 | 29.091 | 1,18 | +2,0 [−3,2; 7,4] |
| 10:03 | 1,39 | 24.700 | 1,19 | −1,6 [−7,8; 4,1] |
| 10:05 | 1,32 | 21.337 | 1,17 | −4,4 [−11,0; 1,5] |
| 10:07 | 1,21 | 14.408 | 1,02 | −10,2 [−17,5; −4,2] |
| 10:10 | 1,24 | 15.873 | 1,12 | −8,9 [−17,0; −2,2] |

**(b) Sinal fixo às 10:00, só a entrada atrasa.**
- 10:01: PF 1,41.
- 10:02: PF 1,45, +1,2 R$/pregão, IC [−1,9; 4,4].
- 10:03: PF 1,41.
- 10:05: PF 1,35.
- 10:07–10:10: PF 1,30–1,32 (IC < 0).

**(d) Movimento minuto a minuto nos 616 dias, a favor do trade:**
- 9:53–9:56: o gap ainda estica (−19 pts acumulados).
- 10:00–10:06: o preço volta **+25 pts em média**. Há um repique de −11 pts na barra de 10:01. O volume triplica às 10:00.
- Depois de 10:06: fica de lado até ~10:30.

**Conclusão:** a correção acontece **durante e logo depois do leilão do à vista**. Entrar antes paga o último esticão. Entrar depois de 10:05 perde a correção.

O ponto ótimo aparente (10:02) está dentro do ruído. Minutos vizinhos variam ±0,07 de PF, e esse é o nível de ruído do método. **Não mudar.**

## 2. Curva de lucro intradiária (`t2_curva.py`, `t2_curva.csv`)
P&L médio acumulado dos 616 trades da manhã, bruto por contrato (resultado final: 123,9 pts = 0,20 R bruto):

| Até | 10:05 | 10:15 | 10:30 | 11:00 | 11:30 | 12:00 | 13:00 | 14:00 | 15:00 | 17:04 |
|---|---|---|---|---|---|---|---|---|---|---|
| pts | 29,8 | 34,5 | 28,4 | 53,0 | 68,1 | 73,2 | 107,2 | 118,3 | 119,1 | 123,9 |
| % do final | 24 | 28 | 23 | 43 | 55 | 59 | 86 | 95 | 96 | 100 |
| R | 0,05 | 0,06 | 0,04 | 0,09 | 0,12 | 0,12 | 0,18 | 0,20 | 0,20 | 0,20 |

- Nos trades com f ≥ 0, o lucro continua até 17:05 (205 pts).
- 2025 e 2026 ganham a maior parte depois das 11:00.

**Saída cedo, com a tarde do v2 (só nos dias sem manhã):**

| Saída | PF | Pior ano |
|---|---|---|
| 10:30 | 1,18 | 0,81 |
| 11:00 | 1,23 | 0,96 |
| 12:00 | 1,29 | — |
| 13:00 | 1,39 | — |
| 15:00 | 1,43 | — |

O incremento é negativo em todas as saídas. Até 12:00, o IC fica abaixo de 0.

**Manhã curta + tarde (13:10) em todos os dias:** 5,15 operações/semana (+43%), mas o PF cai para 1,12–1,31 e o incremento vai de −2,97 a −16,6 R$/pregão.

A tarde nos 391 dias com manhã tem **PF 1,00**:
- quando a manhã foi estopada: PF 0,91;
- quando não foi: PF 1,03.

Outros horários para a 2ª operação (11:10–14:10) dão PF total de 1,03–1,17. **Reprovado.** O lucro do M2 é um movimento de dia inteiro, não um scalp da abertura.

## 3. Janela do fim do dia (`t3_fimdia.py`, `t3_fimdia_out.txt`)

**Fechamento do à vista (cc):** 17:55 com call até 18:00 no inverno dos EUA; 16:55 com call até 17:00 no horário de verão dos EUA. O WIN fecha às 18:25 (17:55 no verão de 2022–23).

**Descritivo (1.133 pregões).** O movimento do WIN entre cc e o seu fechamento (`x`):
- **Reverte no dia seguinte:**
  - contra o gap das 9:00: β = −0,35, Spearman −0,20;
  - até as 10:00: β = −0,57.
- **Não reverte na mesma noite:** β = +0,04.
- Depois das 10:00 não há mais nada: β = +0,16.

Ou seja, existe exagero do WIN com o à vista fechado, mas ele só é corrigido **na abertura seguinte**.

**3a. Fade de cc→cc+X:**

| Saída | PF da leg | Incremento |
|---|---|---|
| Mesmo dia (18:25) | 0,51–0,83 | negativo em todas as 9 células |
| Abertura do dia seguinte | ~0,6–1,0 | — |
| 10:00 do dia seguinte | 0,65–1,16 | — |

O literal "17:55→18:15, sai na abertura" dá PF 1,03, e o placebo de direção dá p = 0,49. **Reprovado.**

> **Bug corrigido no caminho:** numa primeira versão, essa variante deu PF 1,65. O motivo era que, nos dias em que o leilão de abertura é prorrogado (sem barra das 9:00, 25 casos), a simulação saía no fechamento anterior e evitava o gap. Agora a saída é no 1º negócio do dia seguinte, e a vantagem some.

**3b. Âncora = WIN no fechamento do à vista do dia anterior** (diferença mediana para o fechamento das 18:25: 0,08 ATR):

| Versão | PF | R$ | Pior ano | Incremento [IC95] |
|---|---|---|---|---|
| Só na manhã | 1,31 | 19.655 | 1,06 | −5,8 [−14,2; 1,8] |
| Manhã + tarde | 1,28 | — | 0,99 | — |
| Âncora 17:55/16:55 | 1,21–1,24 | — | — | — |

Os 113 dias que a âncora nova inclui têm PF 0,91. **Reprovado.**

## 4. Gestão (`t4_gestao.py`)
Gestão só na manhã. A tarde do v2 fica inalterada. R = 0,3 ATRd.

| Variante | PF | R$ | Pior ano | Incremento [IC95] |
|---|---|---|---|---|
| **v2 sem gestão** | **1,42** | **26.658** | **1,18** | — |
| 1 de 2 contratos sai no fechamento do gap | 1,35 | 19.356 | 1,09 | −6,1 [−10,6; −2,0] |
| Idem, e os de 1 contrato saem inteiros | 1,37 | 19.434 | 1,17 | −6,0 [−11,2; −0,8] |
| Alvo cheio no fechamento do gap | 1,25 | 12.132 | 1,07 | −12,0 [−21,2; −3,4] |
| BE após +0,5R | 1,40 | 17.628 | 1,11 | −7,5 [−14,6; −1,2] |
| BE após +1R | 1,42 | 23.513 | 1,09 | −2,6 [−6,3; 0,6] |
| BE após +1,5R | 1,43 | 26.473 | 1,19 | −0,2 [−1,6; 1,2] |
| BE após +2R | 1,43 | 26.670 | 1,21 | 0,0 [−0,7; 0,8] |
| Trailing de 1R desde a entrada | 1,20 | 9.194 | 0,91 | −14,5 [−22,8; −7,2] |
| Trailing de 2R, ativo após +1R | 1,37 | 23.008 | 1,08 | −3,0 [−7,0; 0,4] |
| Trailing de 3R, ativo após +2R | 1,42 | 26.411 | 1,19 | −0,2 [−0,7; 0,3] |
| Parcial + BE após +1R | 1,34 | 17.247 | 1,04 | −7,8 [−13,5; −2,8] |

Toda gestão que encurta o trade corta a cauda direita, e é nela que está o lucro (f ≥ 0 vai até 205 pts). As versões folgadas (BE ≥ 1,5R, trailing de 3R) quase nunca disparam e empatam. Aplicar nas duas pernas também não ajuda. **Reprovado.**

## 5. Ideia: fade de fim de pregão até o leilão de abertura (`t5d_ultima.py`, `t5e_robustez.py`, `t5f_fds.py`)

**Ideia:** levar o descritivo do item 3 para uma regra operável.

**Regra:**
- Sinal: x = WIN no close da barra fim−6 min menos o WIN no fechamento do à vista (18:00 ou 17:00), dividido pelo ATRd.
- Se |x| ≥ 0,15, entra contra x na abertura da barra fim−5 min (18:20).
- Stop de 0,3 ATRd, com o mesmo teto de R$200.
- Sai no 1º negócio do pregão seguinte (o leilão das 9:00, mesmo se prorrogado).
- Pula a véspera de vencimento. 1 contrato.

| | n | Por semana | PF | R$ | DD | PF 22/23/24/25/26 |
|---|---|---|---|---|---|---|
| Só a leg | 159 | 0,63 | 2,30 | 6.350 | — | 2,31 / 1,03 / 2,65 / 2,85 / 5,34 |
| M2 v2 | 905 | 3,60 | 1,42 | 26.658 | −2.108 | 1,18 / 1,25 / 1,26 / 1,86 / 1,98 |
| **v2 + leg** | **1.064** | **4,23** | **1,48** | **33.008** | **−2.222** | 1,27 / 1,23 / 1,35 / 1,93 / 2,13 |

**A favor:**
- Incremento de +5,26 R$/pregão, IC95 [2,74; 8,01].
- Placebo com direção sorteada (2.000×): média de −R$628, p95 de R$2.324, real de R$6.350, p < 0,0005.
- O espelho (a favor do movimento) dá PF 0,38.
- Custo de 25/35/45 pts: PF 2,20 / 2,11 / 2,03.
- Funciona nos dois sentidos (PF 2,39 e 2,20) e nas duas metades da amostra (1,77 e 3,24).
- Não é artefato do preço do leilão: sem stop, sair às 9:05, 9:15 ou 10:00 dá PF ~2,5–3,2.

**Contra (motivos da reprovação):**
- **Grade ±20%** (fim−4/5/6, limiar 0,12/0,15/0,18, stop 0,24/0,30/0,36, âncora cc ou cc−5; 54 células):
  - incremento > 0 em 100%;
  - IC > 0 em só 33%;
  - todos os anos ≥ 1 em só 28%.
- **A reprovação vem toda de um evento.** Em 67% das células entra o trade de sexta 02/10/2026 → segunda 05/10/2026 (eleição, gap de +9%, 5,1 ATR), que perde **R$3.558 por contrato** passando direto pelo stop. Nenhuma das células que têm esse trade passa.
- Sem carregar posição em fim de semana ou feriado, 61% das células passam. Mas essa regra é **pós-hoc**. E o centro, sem fim de semana, tem 2023 com PF 0,78, porque os fins de semana, fora o da eleição, são justamente os melhores (PF 3,3).
- **Risco de natureza diferente:** posição overnight, e o stop não protege de gap. Um único evento come mais da metade do lucro da leg.
- **Seleção:** o limiar de 0,15 e a entrada no fim do pregão foram escolhidos depois do descritivo e da grade inicial (`t5d_grade.csv`, 24 células). Não existe histórico M1 do WIN anterior a 2021-11 para validar fora da amostra (`hist/` começa em 2023).
- **Volume pequeno:** +0,63 entrada/semana.

**Status:** candidato fraco. Se for adiante, rodar só em papel ou com 1 contrato, com regra de evento definida **antes** (não carregar em fim de semana com eleição/Copom/feriado longo, por exemplo), e reavaliar com 6–12 meses novos.

Outras ideias com M1 testadas rapidamente e descartadas:
- Fade às 10:00 nos dias em que o gap já fechou: PF 0,58–0,75.
- Seguir o preenchimento nesses mesmos dias: PF ~1,0.
- Tarde com gatilho contínuo de 13:10 até 13:30, 14:00 ou 15:00: PF 1,27 → 1,16, incremento negativo.
- Gap de 0,03–0,10 com f ≥ 0: 29 casos, PF 1,14.

## Arquivos
- `core.py`: núcleo M1 (matrizes, simulação com parcial, BE e trailing, M2 v2, estatísticas, bootstrap).
- `rep.py`: reprodução M1 × M5.
- `t1_minuto.py`, `t2_curva.py`, `t3_fimdia.py`, `t4_gestao.py`: tarefas 1 a 4. As saídas `*_out.txt` ficam ao lado de cada script.
- `t5_noturno.py`, `t5b_robustez.py`, `t5c_leilao.py`: fade 18:15 → abertura e o diagnóstico do bug do leilão prorrogado.
- `t5d_ultima.py`, `t5e_robustez.py`, `t5f_fds.py`: ideia 5, com grade, placebo, custo e sensibilidade ao evento. CSVs `t5*_grade*.csv`, `t5f_fds.csv`.
