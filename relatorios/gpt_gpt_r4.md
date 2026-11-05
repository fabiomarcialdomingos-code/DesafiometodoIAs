# WIN M2 — rodada 4 — Duas Janelas

## Resultado central

709 pregões em 148 semanas de calendário observadas, de janeiro de 2024 a outubro de 2026. O M2 v2 de referência teve 495 entradas e R$ 19.675,50 líquidos do custo simulado no recorte. O candidato Duas Janelas acrescentou 420 entradas em 257 pregões, R$ 3.742,00, PF líquido diário de 1,403 e drawdown de R$ 1.231 na perna adicional. O v2 somado à perna chega a 915 entradas, R$ 23.417,50 e drawdown de R$ 2.135,08. Com o M2-A executado na versão de saída às 16h45, a soma indicativa passa de R$ 26.034,87 para R$ 29.776,87, sem compensação de posições ou conciliação de garantias entre as pernas.

O IC95% incremental central vai de −R$ 0,28 a +R$ 12,03 por pregão. Foi calculado com 10.000 reamostragens estacionárias em blocos médios de 10 pregões e inclui zeros nos dias sem sinais. A grade de 27 pontos varia ±20% no limiar de rompimento, no limite de compressão e no limiar de ganho esperado do modelo. 13 pontos passam no n, PF geral e piso anual. Dez também passam no IC95% individual. O ganho adicional foi R$ 412 em 2024, R$ 70 em 2025 e R$ 3.260 em 2026. A combinação foi montada após a leitura da avaliação das pernas individuais. São resultados de desenvolvimento.

## Regras congeladas para reprodução

Usar 1 WIN, stop de 0,30 da média das amplitudes dos 14 pregões anteriores, limitado a 1.000 pontos e arredondado para baixo ao tick. Exigir distância mínima de três ticks. O preço de saída no horário é a abertura observada da barra. O stop aceita a abertura mais adversa se o preço ultrapassar a ordem. Aplicar 15 pontos ida e volta por contrato, incluindo o custo modelado.

Manhã. Inspecionar as janelas de 15 minutos de 9h30 a 11h30. O fechamento da barra M5 recém concluída deve romper a máxima ou mínima das seis barras anteriores em pelo menos 0,0276 ATR. A amplitude das seis barras deve ser no máximo 0,30 ATR. O volume da barra de rompimento deve ser pelo menos 90% da média daquele horário nos 40 pregões anteriores, com pelo menos 25 observações. Entrar no sentido do rompimento, uma vez por manhã, e encerrar 30 minutos após o horário de decisão. A entrada de 9h30 encerra até as 10h. Depois das 10h o sinal só é elegível quando não houve entrada no M2 da manhã, desde que a operação encerre até 13h10.

Tarde. Em janelas de 30 minutos entre 13h30 e 16h30, quando o M2 v2 não ocupa o WIN, estimar P&L bruto esperado de compra e de venda com duas árvores de boosting treinadas em 2022–23. A entrada usa o lado de maior previsão se superar R$ 4,50 brutos. Manter por no máximo 60 minutos e até duas operações não sobrepostas por dia. As variáveis usam apenas barras M5 fechadas e observações passadas do WIN e do WDO. A especificação do modelo, hiperparâmetros e predição estão em futuros.py. Mantêm-se os mesmos parâmetros no replay por minuto. Os retreinos anuais foram testados separadamente e ficaram piores.

Os controles de direção preservam os dias, horários e limites de operações dos sinais. Comprando sempre, o P&L seria −R$ 2.770. Vendendo sempre, R$ 324. Invertendo cada sinal, −R$ 6.188. O intervalo de ganho do candidato contra vender sempre inclui zero. Com atraso de cinco minutos e custo total de 30 pontos, o candidato fez R$ 487 e PF 1,048. O ano de 2025 ficou abaixo de PF 1 nesse cenário.

## Pesquisa de outras arquiteturas

As quatro triagens registram 1.076 configurações principais, antes das grades de estabilidade e do replay por minuto. Os resultados incluem futuros intradiários no WIN e no WDO, pressão antes e depois das janelas da PTAX, sazonalidade e reversão intradiária entre ações e swing comprado de dois a quatro pregões com controles de capital via BOVA11 e cesta de ações. As janelas de PTAX usam os horários da Resolução BCB 45 e preços do WDO como proxy, sem fingir acesso às cotações pontuais do fixing. Nos pares e no swing, o painel de ações permanece sujeito à seleção retrospectiva de tickers. Os estudos de futuros usam a série contínua, barras M1/M5 e proxies de execução. A abertura de uma barra não representa um preço garantido.

Referências primárias: Gao et al. (2018) https://doi.org/10.1016/j.jfineco.2018.05.009 | Jin et al. (2020) https://doi.org/10.1002/fut.22084 | Krohn et al. (2024) https://doi.org/10.1111/jofi.13306 | Heston et al. (2010) https://doi.org/10.1111/j.1540-6261.2010.01573.x | Nagel (2012) https://www.nber.org/papers/w17653

## Como reproduzir

1. Extraia PACOTE_GPT_M2.zip para uma pasta nova e extraia este ZIP sobre ela. O pacote original fornece dados/, relatorios/ e codigo/.
2. Instale NumPy, pandas e scikit-learn num ambiente Python 3. O replay usou scikit-learn 1.8.0. Use a mesma versão para reproduzir o modelo.
3. Execute `python round4/futuros.py`, `python round4/ptax.py`, `python round4/pares.py`, `python round4/swing.py`, `python round4/minuto.py`, `python round4/duas_janelas.py` e `python round4/adaptativo.py`.
4. A pasta study contém os dois leitores auxiliares da rodada anterior e a série do M2-A. O painel das ações cria um cache local na primeira execução.

Os arquivos duas_janelas_resultados.csv, duas_janelas_grade.csv, duas_janelas_placebos.csv e duas_janelas_diario.csv registram o candidato. Os demais arquivos documentam a triagem, os testes de atraso, o retreino e os resultados descartados. Todos os valores em reais são anteriores à tributação.
