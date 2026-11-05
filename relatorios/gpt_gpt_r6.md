# WIN M2 — rodada 6 — retomada e alocação do segundo lote

A rodada usou quatro agentes em paralelo, além do estudo de trajetória. As tabelas de seleção somam 2.760 configurações. A seleção das regras individuais usou 2022–23. O primeiro recorte de avaliação foi 2024–25 (501 pregões) e 2026 até outubro ficou separado. A combinação foi construída após observar os testes individuais. O histórico já foi explorado em outras rodadas. A combinação permanece em pesquisa.

## Candidato combinado

1. Retomada da manhã. Sem sinal matinal do v2, avalia janelas de 15 minutos a partir de 10h15, usando a trajetória das últimas oito variações M5. Exige deslocamento de pelo menos 1,2 vez a média daquele horário dos 30 pregões anteriores, eficiência direcional de pelo menos 0,60, última variação contra o impulso e posição ainda favorável na faixa. Entra no sentido do impulso, no máximo uma vez por dia, e encerra em 20 minutos, preservando a janela da tarde do v2. A distância planejada de stop usa 0,30 ATR e é limitada a 1.000 pontos. Portanto, em dias de ATR elevado, essa perna pode operar com stop limitado enquanto o v2 abstém. Há diagnóstico separado por esse regime.
2. Redistribuição. Onde há sinal matinal do v2, o primeiro lote permanece. O segundo é transferido entre sinais de manhã, com crédito de risco planejado que só nasce quando o v2 daria dois lotes. O saldo acumula até o fim do ano. O modelo Ridge simples usa informações conhecidas antes das 10h. Foi ajustado em 2022, selecionado em 2023 e reajustado em 2022–23. A soma do risco planejado do segundo lote em 2024–25 foi R$ 10.590 contra R$ 10.714 do v2. Isso mede orçamento de stops, não perdas garantidas.

A auditoria reconstruiu o v2 em M1. Os sinais, lotes, ATR e preços de referência foram reconciliados. Arredondar o stop ao tick e fazer a saída no preço de abertura do minuto de encerramento muda o P&L frente ao cálculo teórico. O benchmark comum de 2024–25 rendeu R$ 11.695 a 15 pontos sem atraso e R$ 7.051 com atraso de cinco minutos e custo de 30 pontos ida e volta. Houve uma entrada estressada ausente por falta de preço na janela. Barras M1/M5 são proxies e não garantem preços de execução.

| Cenário | 2024 incremental | 2025 incremental | 2026 incremental | 2024–25 incremental |
|---|---:|---:|---:|---:|
| Combinado, 15 pontos sem atraso | −17 | +743 | +1.043 | +726 |
| Combinado, 30 pontos e atraso de 5 minutos | +94 | +791 | +1.399 | +885 |

O cenário estressado passa de 397 para 493 entradas em 2024–25 (+96, 24,2%). O drawdown passa de R$ 2.278 para R$ 2.321. O intervalo de 95% incremental é de −R$ 3,11 a +R$ 6,94 por pregão, com bootstrap de blocos de dez pregões em média. No cenário de 15 pontos, o intervalo é de −R$ 3,78 a +R$ 6,93. A combinação perde R$ 17 em 2024 a 15 pontos. Nenhum resultado justifica promover a combinação a produção.

A Retomada sozinha fez +R$ 85 em 2024 e +R$ 241 em 2025 sob estresse. Em 2026 fez −R$ 357. O sinal superou seu espelho em R$ 1.833 nas mesmas 96 entradas de 2024–25, mas o ganho absoluto de R$ 326 teve IC95% de −R$ 0,73 a +R$ 2,10 por pregão. O ajuste max-t exploratório entre as seis vencedoras da família de trajetórias deu p=0,724 frente a zero.

## Auditoria da rodada anterior

O Duas Janelas fez R$ 2.882 e 151 entradas em 2026 nos 78 pregões normais que o v2 bloqueou por risco. Isso representa 77% do lucro histórico incremental da extensão. Em 2024 e 2025 não houve esse bloqueio em pregões normais. Entre os dias elegíveis em que o v2 ficou sem sinal, o Duas Janelas perdeu R$ 368 em 2024 e R$ 72 em 2025. No recorte cru de ATR em 2026 há 81 dias acima do teto. A diferença são dias que a classificação causal da auditoria exclui por outras razões antes de aplicar o teto.

## Arquivos e reprodução

Extraia PACOTE_GPT_M2.zip e este arquivo na mesma raiz. O pacote original fornece dados/ e codigo/. Use Python 3 com NumPy, pandas e scikit-learn. Execute os scripts a partir da raiz, na seguinte ordem para reproduzir a comparação principal:

1. `python round6/auditoria/benchmark_m1.py`
2. `python round6/raiz/trajetoria.py`
3. `python round6/risco/invalidacao.py`
4. `python round6/risco/redistribuicao.py`
5. `python round6/raiz/comparacao.py`
6. `python round6/auditoria/controles_trajetoria.py`

As frentes independentes são `python round6/estrutura/niveis_redondos.py`, `python round6/alternativa/amplitude.py` e `python round6/alternativa/leilao.py`. As tabelas entregues incluem séries por dia, resultados anuais, controles, auditoria de horários e todas as configurações de treino. O CSV comparacao_retomada.csv contém os resultados da estratégia combinada.
