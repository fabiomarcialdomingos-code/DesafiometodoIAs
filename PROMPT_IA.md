# Missão: criar um método para a B3 que tenha MAIS VOLUME e MAIS LUCRO que o M2 v2, e que se sustente

Você é um pesquisador quantitativo sênior. Use TODOS os dados e relatórios deste pacote. Responda em português.

## O que há no pacote
**dados/** (todos os CSV com separador `;`, colunas time, open, high, low, close, tick_volume e real_volume, horário de Brasília, timestamp na abertura da barra):

| Pasta | Conteúdo | Período |
|---|---|---|
| `win/` | mini índice em M1, M5 e D1 (R$0,20/pt, custo 15 pts ida e volta, pregão das 9:00 às 18:25) | 2021-11 a 2026-10 |
| `ind/` | índice cheio (R$1/pt) | 2021-11 a 2026-11 |
| `wdo/` | mini dólar (R$10/pt, custo 1,2 pt) | — |
| `smallcaps/` | 50 small caps em M5 e D1 | 2022–26 |
| `bluechips/` | 11 blue chips e ETFs em M5 e D1 | 2023–26 |
| `acoes_universo/` | 117 ações a mais, com R$5–300 mi/dia, em M5 e D1, e a lista com o volume médio | 2022–26 |
| `cripto_b3/` | futuros BIT, ETR e SOL da B3 (BIT = 0,01 BTC; ETR e SOL quase sem liquidez) | — |
| `calendario/` | calendário econômico com 56 mil eventos (encoding latin1) | 2019–2027 |

Custo das ações: 0,06% ida e volta nas blue chips, 0,10% nas small caps. As ações abrem às 10:00 em leilão.

**codigo/:**
- `engine.py` (simulate) e `horarios.py` (calendário, vencimentos);
- `lab.py`, `lab2.py` e `gpt1.py`, que reproduzem o M2 v2;
- `motor.py` e `rodar_universo.py`, do M2-A;
- `agente*_*.py`.

**relatorios/:** LEIA PRIMEIRO `resultado_m2vol.md`, que lista TUDO o que já foi testado e reprovado, e o `CARTEIRA.md`. Também estão aqui os relatórios de 5 agentes (A a E), de 5 rodadas do GPT e do M2-A no universo expandido.

## A referência a bater: M2 v2 (WIN)
**Manhã:**
- às 10:00, se 0,10 ≤ |gap|/ATRd ≤ 1,0, onde gap = abertura das 9:00 − fechamento anterior e ATRd = média de 14 dias de (máx−mín) até ontem, e o gap ainda está aberto às 9:55, entra contra o gap;
- stop de 0,3 ATRd, saída às 17:05, não entra se o stop passar de R$200 por contrato;
- 2 contratos se f = (abertura − preço 9:55)/gap ≥ 0, 1 contrato se não. Pula o vencimento.

**Tarde:** nos dias sem manhã, às 13:10, fade do desvio vs fechamento anterior entre 0,2 e 1,0 ATRd, com stop de 0,3 ATRd e saída às 17:05.

**Resultado em 2022–26:**
- 905 entradas (3,6 por semana), R$26.658, PF 1,42, DD −R$2.108;
- PF por ano: 1,18 / 1,25 / 1,26 / 1,86 / 1,98;
- com entrada 5 minutos atrasada e custo pior: R$22.977, PF 1,35.

**Mecanismo:** o WIN negocia das 9h às 10h com o à vista fechado, e o leilão das 10:00 corrige o exagero do gap noturno.

**Limitação atual:** com o mercado agitado depois da eleição (ATRd ~4.300 pts), o teto bloqueia o M2 v2.

## Já reprovado (NÃO repita sem uma ideia nova)
- **Variações do M2:** mais faixas de gap, outros horários, várias entradas por dia, re-entrada, gestão (parcial, break-even, trailing), operar com vol alta, gap residual pelo WDO ou S&P.
- **Outros ativos:** M2 no WDO, ações, small caps, ETFs e BIT.
- **M2-A** (small caps × WIN da 1ª hora): passou nas 50 small caps, mas falhou fora da amostra nas 117 ações novas (PF 1,05).
- **Métodos do GPT:** Duas Janelas (77% do lucro veio de dias de vol alta), Retomada, Liderança diária e Noturno (frágil por causa da eleição).
- **Calendário:** diferenças pequenas que parecem ruído.

## O que eu quero
1. Um método NOVO (ou uma combinação) com **mais operações por semana que o M2 v2** e **lucro total maior** no mesmo período. Ele pode usar o M2 v2 como base, por exemplo com filtros ou módulos complementares.
2. **Protocolo obrigatório:**
   - escolha as regras com 2022–23 e teste em 2024–26, sem mexer depois;
   - não use informação do futuro;
   - aplique o custo real: 15 pts no WIN, 0,06–0,10% nas ações;
   - faça estresse com entrada 5 min atrasada e custo de 30 pts.
3. **Critério para aprovar:**
   - PF ≥ 1,2 depois do custo e nenhum ano abaixo de 1,0;
   - grade ±20% com a maioria dos pontos passando;
   - ganho incremental sobre o M2 v2 com IC95 > 0 (bootstrap em blocos de 10 pregões);
   - placebo quando o ganho vier de tamanho;
   - teste fora da amostra em ativos ou anos que não foram usados para escolher.
4. Pense fora da caixa, mas com **mecanismo econômico**: por que a vantagem existe e quem perde do outro lado.
5. **Entregue:**
   - código reproduzível;
   - tabela por ano;
   - comparação lado a lado com o M2 v2;
   - estresse;
   - veredito honesto: se nada passar, diga.
