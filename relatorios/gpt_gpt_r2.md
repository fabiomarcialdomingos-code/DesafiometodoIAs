# WIN M2 v2 — reprodução e triagem

Período avaliado de 03/01/2022 a 30/10/2026. Novembro e dezembro de 2021 entram apenas no aquecimento. São 1.207 pregões observados no período, 138.738 barras WIN e 139.984 WDO nos arquivos completos. Os timestamps M5 identificam a abertura da barra e são tratados como horário de Brasília, conforme o pacote de origem.

## Resultado

O M2 v2 reproduz 905 entradas, 1.145 contratos acumulados, lucro líquido de custos simulados de R$ 26.657,77, PF bruto de 1,4897, PF líquido de 1,4212 e drawdown máximo de R$ 2.108,13. O PF de 2022 a 2026 é 1,18 / 1,25 / 1,26 / 1,86 / 1,98. O ano de 2026 vai até outubro. Um segundo replay, escalar, verifica operação por operação contra o vetorizado.

A reprodução exige a barra das 09h00 para os dois períodos, inclusive tarde. Sem essa condição, seis operações adicionais elevam o total a 911 e o lucro cai para R$ 26.193,71. O ATR do método é a média simples das 14 amplitudes diárias anteriores. O fechamento anterior é o da última barra fornecida. A saída das 17h05 corresponde ao fechamento da barra carimbada 17h00. O stop do replay original é verificado já na barra de entrada e preenchido no nível teórico. O teste de execução arredonda a distância ao tick e admite abertura pior que o stop. Outra execução simulada também atrasa as entradas em cinco minutos.

## Pesquisa de extensões

Foram analisadas 30 regras e 264 configurações, incluindo as centrais. Nenhuma configuração apresentou, simultaneamente, ganho incremental positivo e PF líquido finito acima de 1 em cada ano. Para as regras com dois parâmetros principais, a grade é o produto cartesiano de 0,8 / 1 / 1,2 sobre esses parâmetros. Para a saída no fechamento do gap, só o alvo relativo varia. Constantes secundárias, horários ligados ao mecanismo, stop e teto ficam fixos.

As adições usam um contrato e respeitam uma entrada por pregão. Quando uma alternativa entra antes da tarde, ela pode substituir o M2 Tarde. O ganho incremental considera o P&L dessa troca. Nas regras de filtro ou de saída, o resultado da estratégia inteira é comparado com o v2 completo. O campo n da triagem descreve as operações no trecho alterado. A coluna delta_n descreve a diferença de entradas na estratégia inteira.

Os intervalos percentis de 95% usam 10.000 reamostragens estacionárias pareadas de pregões completos e blocos médios de 5, 10 e 20 pregões. Dias sem sinal entram na série diária com P&L zero. O diagnóstico max-t usa as 30 configurações centrais e blocos médios de 10 pregões. O critério de triagem completa exige todos os pontos da grade com ganho e PF líquido positivos conforme os pisos anuais, limite inferior de 95% acima de zero, p ajustado abaixo de 0,05, ganho positivo a 30 pontos de custo e aumento de pelo menos 10% no P&L ou de 0,5 entrada a cada cinco pregões. São comparações exploratórias no histórico compartilhado. O arquivo diário permite remontar os deltas.

Os dados contínuos não incluem o mapa de vencimentos utilizado para construir a série, ticks ou o livro de ofertas. O lucro é líquido do custo modelado de 15 pontos por contrato, antes de tributação e de eventos específicos da corretora. O preenchimento no primeiro negócio da barra e os stops simulados precisam de confirmação com dados executáveis. A série compartilhada já foi usada no desenvolvimento.

## Arquivos e execução

- `run_m2.py` implementa a leitura das barras, a estratégia de referência e o simulador.
- `screen.py` contém as regras e gera a grade, a triagem e o P&L diário.
- `verify.py` reconcilia o replay escalar, a atribuição do P&L e os estresses.
- `results/operacoes_base.csv` registra as operações do M2 v2.
- `results/atribuicao.csv` separa manhã, tarde e segundo contrato.
- `results/estresse_base.csv` traz custos de 15, 30 e 45 pontos e estresse de execução.
- `results/triagem.csv`, `results/grade.csv` e `results/diario.csv` permitem auditar as extensões.
- `SHA256_DADOS.txt` identifica os CSVs originais.

Extraia `WIN_contN_M5.csv` e `WDO_contN_M5.csv` do pacote original para a mesma pasta dos scripts. Em Python 3 com pandas e NumPy disponíveis, execute `python verify.py` e `python screen.py`. O horário é expresso em minutos desde a meia-noite em `operacoes_base.csv`.
