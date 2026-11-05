# M2 v2 em outros ativos (agenteA, 04/11/2026)

**Resumo: nenhum ativo novo passa.** Só o IND passa, e ele é o próprio WIN em outro tamanho de contrato, então não traz volume novo. WDO, ações, cesta, BOVA11, IVVB11 e a ideia extra (sinal do WIN executado nas ações) reprovam todos. Nenhum chega a PF 1,2 depois do custo, e todos têm pelo menos um ano abaixo de 1,0. Achado útil: o filtro f ≥ 0 cria uma **vantagem bruta pequena** em ações e no BOVA11, que o M2 original não tinha. O custo de 0,06% consome essa vantagem.

Para reproduzir: `python3 -I /home/claude/win/m2vol/agenteA/rodar.py`. O núcleo fica em `m2core.py`; as saídas são `tabela.csv` (todas as linhas), `grade.csv` (±20%), `ind_vs_win.csv`, `trades_*.csv` e `log.txt`.

**Critério de aprovação:** PF ≥ 1,2 no total, nenhum ano com PF < 1,0, n ≥ 100, e R$ positivo antes e depois do custo. Os parâmetros são os do WIN em todos os ativos. A única variação é a grade de ±20%, um parâmetro por vez.

## 0. Controle: o núcleo reproduz o WIN

O `m2core.m2v2_fut` é genérico. Rodado no WIN (`hist21`), ele reproduz exatamente os números do lab:

| Teste (WIN, 2022–26, custo 15 pts) | n | PF | PF bruto | R$ | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|
| M2 base | 616 | 1,35 | 1,41 | 13.420 | 1,15 | 1,26 | 1,14 | 1,71 | 1,80 |
| **M2 v2** (1.145 contratos) | 905 | **1,42** | 1,49 | 26.658 | 1,18 | 1,25 | 1,26 | 1,86 | 1,98 |
| manhã com f ≥ 0 (1 contrato) | 240 | 1,67 | 1,75 | 9.163 | 1,19 | 1,44 | 1,64 | 2,78 | 2,43 |
| manhã com f < 0 | 376 | 1,17 | 1,22 | 4.256 | 1,11 | 1,17 | 0,92 | 1,23 | 1,55 |
| tarde | 289 | 1,36 | 1,46 | 4.075 | 1,30 | 0,93 | 1,24 | 1,57 | 2,18 |

## 1. WDO: reprovado (não há vantagem nem antes do custo)

Adaptação: ATRd do próprio WDO, R$10/pt, custo de 1,2 pt, e pula o 1º pregão de cada mês. O resto é idêntico, inclusive f, a dobra e a tarde.

Testei o teto de risco de quatro formas, porque não existe um equivalente único:
- **R$400 por contrato.** É a mesma fração do nocional do WIN (R$200 / (0,20 × ~130 mil) ≈ 0,77%; o WDO tem nocional de ~R$53 mil). Na prática não bloqueia nada.
- **R$200, o mesmo valor em reais.** Bloqueia 41% dos dias e 98% de 2022.
- **Sem teto.**
- **Teto por regime.** Pula os dias com ATRd acima do percentil 92,6 do passado (só dados anteriores). É a mesma fração de dias que o teto bloqueia no WIN (7,4%).

| WDO 2022–26 | n | PF | PF bruto | R$ | R$ bruto | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|---|
| v2, teto R$400 | 934 | **0,87** | 0,98 | −15.879 | −1.911 | 0,78 | 0,78 | 0,92 | 1,16 | 0,75 |
| v2, teto R$200 | 562 | 0,91 | 1,06 | −5.323 | +2.921 | 0,84 | 0,82 | 1,01 | 1,12 | 0,73 |
| v2, sem teto | 935 | 0,87 | 0,99 | −15.466 | −1.486 | 0,79 | 0,78 | 0,92 | 1,16 | 0,75 |
| v2, teto por regime | 880 | 0,89 | 1,01 | −12.006 | +1.146 | 0,81 | 0,78 | 0,99 | 1,17 | 0,75 |
| manhã com f ≥ 0 (1 contrato) | 230 | 0,82 | 0,92 | −4.970 | −2.210 | 0,51 | 0,74 | 1,26 | 1,30 | 0,56 |
| manhã com f < 0 | 363 | 0,98 | 1,10 | −678 | +3.678 | 1,20 | 0,80 | 0,75 | 1,18 | 0,83 |
| tarde | 341 | 0,80 | 0,95 | −5.261 | −1.169 | 0,82 | 0,83 | 0,57 | 0,82 | 1,15 |

O dado que mais pesa: no WDO o grupo **f ≥ 0 é o pior** (PF bruto 0,92), o contrário do WIN (1,75). Ou seja, o mecanismo não existe no dólar. É coerente com a hipótese: o dólar à vista (interbancário) já negocia às 9:00, então o WDO não abre antes do seu à vista. Na grade de ±20%, o PF fica entre 0,85 e 0,88 em todos os pontos.

## 2. Ações e BOVA11: reprovado (o f ≥ 0 cria vantagem bruta, mas o custo a consome)

Regras:
- **Gap** = abertura oficial do leilão das 10:00 (D1) − fechamento oficial anterior (D1). ATRd de 14 dias do D1, até ontem.
- **Entrada** às 10:30 ou às 11:00, se 0,10 ≤ |gap|/ATRd ≤ 1,0, o gap ainda está aberto na barra anterior e **f ≥ 0**.
- **Saída e custo:** stop de 0,3 ATRd, saída às 16:55 (fechamento da barra 16:50, antes do call), custo de 0,06% ida e volta.
- **Tamanho:** R$100 de risco por operação. Nocional mediano de ~R$16 mil (R$27,5 mil no BOVA11). Ações não têm teto.
- **Período:** 2023–2026.

**Cesta (11 papéis):**

| Variante | n | PF | PF bruto | R$ | R$ bruto | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|
| 10:30, f ≥ 0 | 2.360 | **0,95** | **1,12** | −8.011 | +16.360 | 0,82 | 1,00 | 1,11 | 0,83 |
| 11:00, f ≥ 0 | 2.022 | 0,93 | 1,12 | −8.568 | +12.115 | 0,96 | 0,99 | 0,91 | 0,84 |
| 11:00 sem f (M2 original, referência) | 5.255 | 0,81 | 0,97 | −62.272 | −8.813 | 0,77 | 0,81 | 0,87 | 0,78 |
| tarde 13:10 (dias sem entrada às 10:30) | 4.844 | 0,79 | 1,01 | −45.578 | +2.591 | 0,75 | 0,66 | 0,89 | 0,93 |
| tarde 13:10 (dias sem entrada às 11:00) | 5.121 | 0,80 | 1,02 | −46.347 | +4.768 | 0,76 | 0,70 | 0,89 | 0,90 |
| 10:30 f ≥ 0 + tarde | 7.204 | 0,85 | 1,06 | −53.589 | +18.951 | 0,78 | 0,79 | 0,98 | 0,88 |
| *diagnóstico: 10:30 f ≥ 0 com custo de 0,03%* | 2.360 | 1,03 | — | +4.174 | — | 0,90 | 1,10 | 1,22 | 0,89 |

**Por ação, 10:30 com f ≥ 0** (11:00 entre colchetes):

| Ação | n | PF | PF bruto | R$ | 2023 | 2024 | 2025 | 2026 | PF 11:00 [bruto] |
|---|---|---|---|---|---|---|---|---|---|
| PETR4 | 226 | 1,25 | 1,47 | 3.202 | 0,56 | 3,10 | 1,11 | 1,10 | 1,13 [1,36] |
| VALE3 | 274 | 0,87 | 1,05 | −2.367 | 1,25 | 0,96 | 0,45 | 0,96 | 0,79 [0,97] |
| ITUB4 | 223 | 0,75 | 0,90 | −3.652 | 0,57 | 0,70 | 1,03 | 0,71 | 0,90 [1,11] |
| BBDC4 | 192 | 0,75 | 0,88 | −3.042 | 0,67 | 0,81 | 0,84 | 0,70 | 1,01 [1,20] |
| BBAS3 | 144 | 1,05 | 1,23 | 509 | 0,70 | 0,75 | 2,35 | 1,02 | 1,19 [1,41] |
| B3SA3 | 218 | 0,81 | 0,91 | −2.651 | 0,70 | 0,65 | 1,26 | 0,67 | 1,03 [1,18] |
| PRIO3 | 222 | 1,07 | 1,22 | 934 | 1,27 | 0,95 | 1,08 | 1,05 | 0,90 [1,02] |
| **BOVA11** | 249 | 1,12 | **1,45** | 1.949 | 1,00 | 1,15 | 1,44 | **0,86** | 0,92 [1,23] |
| SMAL11 | 208 | 1,15 | 1,37 | 1.764 | 0,93 | 1,42 | 1,69 | 0,70 | 0,78 [0,94] |
| WEGE3 | 183 | 0,68 | 0,80 | −3.873 | 0,79 | 0,62 | 0,76 | 0,56 | 0,90 [1,07] |
| ABEV3 | 221 | 0,94 | 1,13 | −783 | 0,56 | 0,95 | 1,33 | 0,90 | 0,76 [0,93] |

Nenhuma ação passa, em nenhum dos dois horários.
- **PETR4 (PF 1,25):** 2023 dá 0,56, e todo o resultado vem de 2024 (3,10).
- **BOVA11:** é o caso mais próximo do WIN, com PF bruto de 1,45 às 10:30, mas 2026 fica em 0,86.
  - Com custo de 0,03% ida e volta, o PF iria a 1,27, e 2026 ainda ficaria em 0,95. Não passa nem com metade do custo.
  - Às 11:00 o PF cai para 0,92.
  - Somar a tarde ao BOVA11 piora: PF 0,94.
  - Escolher o BOVA11 entre 11 papéis já seria seleção depois de ver o resultado.
- **Leitura:** o f ≥ 0 sobe o PF bruto da cesta de 0,97 (M2 original) para 1,12, então há um resíduo do mecanismo. Mas o stop de 0,3 ATRd equivale a ~0,63% do preço, e o custo de 0,06% custa ~0,1R por operação, contra ~0,03R no WIN.
- **Tarde nas ações:** não tem vantagem bruta (PF 1,01).
- **Grade de ±20%:** a cesta fica entre 0,85 e 0,86 em todos os pontos. O BOVA11 só de manhã fica entre 1,06 e 1,16, com pior ano entre 0,78 e 0,93, e nunca passa.

## 3. IND: confere com o WIN (sanity check ok)

Fonte: zip `historico_longo`, extraído em `agenteA/dados_ind/`. O WIN desse zip dá resultado idêntico ao do `hist21`: 905 operações, PF 1,42, R$26.658. O teto do IND é de 1.000 pts (= R$200 por WIN equivalente), e o vencimento cai nas mesmas datas.

| 2022–26 | n | PF | PF bruto | R$ por contrato | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|
| WIN v2 (R$0,20/pt, custo 15) | 905 | 1,42 | 1,49 | 26.658 (= 133.289 pts líq.) | 1,18 | 1,25 | 1,26 | 1,86 | 1,98 |
| IND v2 (R$1/pt, custo 5) | 885 | 1,42 | 1,44 | **126.241** | 1,40 | 1,24 | 1,05 | 1,56 | 2,13 |
| IND v2 com custo de 15 pts (igual ao WIN) | 885 | 1,37 | 1,44 | 115.031 pts | 1,36 | 1,20 | 1,01 | 1,51 | 2,09 |

- **Operações em comum:** 794. Há 111 só no WIN e 91 só no IND.
- **Nas comuns:** direção igual em 99,9%, contratos iguais em 94%, correlação de 0,98 nos pontos brutos. Os pontos brutos somam 126.276 no WIN e 124.097 no IND (−1,7%).
- **Origem da diferença:** a abertura das 9:00 do IND é pouco líquida e difere da do WIN em ±65 pts (intervalo interquartil). Com isso, alguns dias cruzam os limiares de gap/ATR ou de f. Por isso o PF de 2024 cai para 1,05.
- **Em R$:** 1 IND equivale a 5 WIN em exposição (R$126 mil contra 5 × R$26,7 mil = R$133 mil). Com custo de 5 pts, o IND sai mais barato por exposição: R$5 contra R$15 de 5 WIN.
- **Conclusão:** o mecanismo se confirma no índice cheio. Mas o IND é a **mesma aposta** do WIN e não soma volume independente. Serve só como forma de executar lotes grandes, com o cuidado de que a abertura dele é menos líquida.

## 4. IVVB11: reprovado

Não há D1 do IVVB11. O diário foi montado do M5: abertura = open da 1ª barra (10:05, depois do leilão) e fechamento anterior = close da última barra (sem o call). As regras são as mesmas das ações.

| IVVB11 2023–26 | n | PF | PF bruto | R$ | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|
| 10:30, f ≥ 0 | 225 | 0,86 | 1,15 | −2.145 | 0,55 | 1,25 | 0,92 | 0,70 |
| 11:00, f ≥ 0 | 163 | 1,01 | 1,37 | +116 | 0,51 | 1,09 | 1,60 | 0,80 |
| 10:30 sem f | 581 | 0,69 | 0,93 | −12.848 | 0,56 | 0,64 | 0,94 | 0,65 |
| tarde 13:10 | 429 | 0,59 | 0,88 | −10.201 | 0,65 | 0,53 | 0,61 | 0,60 |
| 10:30 f ≥ 0 + tarde | 654 | 0,69 | 0,98 | −12.346 | 0,62 | 0,77 | 0,73 | 0,64 |
| 10:30 f ≥ 0, EUA no verão (NY abre 10:30) | 167 | 0,77 | 1,05 | −2.566 | 0,41 | 1,01 | 0,88 | 0,79 |
| 10:30 f ≥ 0, EUA no inverno (NY abre 11:30) | 58 | 1,11 | 1,43 | +421 | 0,96 | 1,87 | 1,03 | 0,36 |

O IVVB11 abre antes da bolsa de NY, mas o S&P tem futuro líquido a noite toda. O "gap" dele é informação, não excesso. Na janela em que o IVVB11 negocia 1h30 antes de NY (inverno americano), o PF bruto chega a 1,43, mas com só 58 operações. É insuficiente e não deve ser perseguido. Na grade, o PF fica entre 0,67 e 0,72.

## 5. Ideia extra: o sinal do WIN executado no BOVA11 e nas ações (reprovada)

**Hipótese:** o leilão das 10:00 das ações forma preço olhando o WIN, que já negociou 1h. Nos dias de M2, o leilão herdaria o excesso do gap noturno.

**Regra:** nos dias em que o M2 do WIN entra de manhã, entra no papel contra o gap do WIN, se o gap do papel tiver o mesmo sinal. Entrada às 10:05 (1ª barra contínua) ou às 10:30. Stop de 0,3 ATRd do papel, saída às 16:55, custo de 0,06%.

| 2023–26 | n | PF | PF bruto | R$ | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|
| BOVA11, todos os dias de M2, 10:05 | 407 | 0,83 | 1,07 | −5.130 | 0,87 | 0,73 | 0,90 | 0,84 |
| BOVA11, todos os dias de M2, 10:30 | 407 | 0,92 | 1,21 | −2.161 | 0,80 | 0,91 | 0,95 | 1,18 |
| BOVA11, só f ≥ 0 no WIN, 10:30 | 126 | 1,06 | 1,39 | +478 | 0,53 | 1,00 | 1,55 | 1,65 |
| Cesta, só f ≥ 0 no WIN, 10:05 | 1.125 | 1,04 | 1,22 | +2.639 | 0,70 | 1,19 | 1,30 | 0,93 |
| Cesta, só f ≥ 0 no WIN, 10:30 | 1.125 | 1,05 | 1,24 | +3.218 | 0,74 | 1,10 | 1,40 | 0,91 |
| *referência: WIN M2 manhã, 2023–26* | 471 | 1,55 | 1,62 | 20.146 | 1,31 | 1,26 | 1,96 | 1,94 |

- **Vantagem bruta:** existe (PF bruto de 1,22–1,39 nos dias com f ≥ 0), mas é menor que no próprio WIN.
- **Depois do custo:** fica em ~1,05, com 2023 abaixo de 1.
- **Correlação:** a correlação diária com o WIN v2 é de 0,72. Não diversifica; é a mesma aposta, executada num instrumento mais caro.

## Veredito por ativo

| Ativo / variante | n | PF líquido | PF bruto | Pior ano | Veredito |
|---|---|---|---|---|---|
| WIN M2 v2 (referência) | 905 | 1,42 | 1,49 | 1,18 | aprovado (já validado) |
| IND M2 v2 | 885 | 1,42 | 1,44 | 1,05 | **aprovado como sanity check**: é o mesmo sinal do WIN, sem volume novo |
| WDO M2 v2 (qualquer teto) | 562–935 | 0,87–0,91 | 0,98–1,06 | 0,73 | **reprovado**: sem vantagem bruta; no WDO o f ≥ 0 é o pior grupo |
| Cesta de ações, 10:30 f ≥ 0 | 2.360 | 0,95 | 1,12 | 0,82 | **reprovado**: há vantagem bruta, mas o custo a consome |
| Cesta de ações, 11:00 f ≥ 0 | 2.022 | 0,93 | 1,12 | 0,84 | **reprovado** |
| Ações, tarde 13:10 | 4.844 | 0,79 | 1,01 | 0,66 | **reprovado**: sem vantagem bruta |
| BOVA11, 10:30 f ≥ 0 | 249 | 1,12 | 1,45 | 0,86 | **reprovado**: o melhor caso, mas PF < 1,2 e 2026 < 1, mesmo com metade do custo |
| Qualquer ação isolada | 140–274 | 0,68–1,25 | 0,80–1,47 | ≤ 0,70 | **reprovado**: 0 de 11 passam |
| IVVB11 (todas as variantes) | 58–654 | 0,59–1,11 | 0,88–1,43 | ≤ 0,51 | **reprovado** |
| Ideia 5: sinal do WIN em ações/BOVA11 | 126–3.761 | 0,83–1,06 | 1,07–1,39 | ≤ 0,87 | **reprovado**: é a mesma aposta do WIN (corr 0,72), só mais cara |

**Conclusão.** A vantagem do M2 v2 está no WIN e no IND, que abrem 1h antes do à vista e custam pouco em relação ao stop (~0,03R). O filtro f ≥ 0 carrega um resíduo dessa vantagem para as ações e o BOVA11 (PF bruto de 1,12 a 1,45), mas com 0,06% de custo (~0,1R) nada sobrevive. Para ganhar volume, o caminho continua no próprio WIN (ou no IND para lotes grandes), não em outros ativos. Se um dia o custo efetivo no BOVA11 cair para perto de 0,02% ida e volta, vale reavaliar o BOVA11 às 10:30 com f ≥ 0. Mesmo assim, 2026 ficou abaixo de 1 com metade do custo.

**Ressalvas:**
- Os preços das ações são ajustados por proventos. Todo o cálculo é feito em %, então isso não afeta o resultado.
- O IVVB11 não tem o preço do call de fechamento.
- Não há dados de 2022 para as ações.
- A grade de ±20% muda um parâmetro por vez (`grade.csv`).
