# WIN — rodada 8 — liderança diária das ações

A hipótese é que a divergência de força entre ações menores, blue chips e o índice contém informação sobre o WIN no pregão seguinte. O desenho é independente do M2. Nenhum sinal, horário disponível ou resultado do v2 entra nas variáveis do método. [Hong, Torous e Valkanov](https://escholarship.org/uc/item/6x49x543)

## Protocolo

O painel contém 48 small caps com dados no começo de 2022 e 9 blue chips com dados no começo de 2023. O universo original tem seleção retrospectiva de papéis. As comparações de retornos usam horizontes de 1, 3, 7 e 15 pregões. As variáveis incluem força relativa, amplitude da participação, dispersão e volume relativo. São padronizadas por estatísticas móveis e deslocadas um pregão antes de gerar ordens. A auditoria alterou os dados de fechamento do dia de execução e confirmou que o sinal e as variáveis daquele dia ficaram iguais.

Cada candidato pode abrir um WIN por dia às 9h10 ou às 10h15, com saída às 10h30, 12h30 ou 16h50 e stop planejado de 30% da mediana da amplitude dos últimos 20 pregões, limitado a R$ 200 por contrato antes do custo e da derrapagem. O replay usa M1 e aproxima a execução pela abertura ou nível de stop, com regra adversa em salto. Compara 15 pontos ida e volta sem atraso e 30 pontos ida e volta com cinco minutos de atraso. A rolagem é aproximada pelo calendário. Os valores estão antes da tributação.

Foram 768 configurações de seguimento e 768 de inversão selecionada no treino. Os modelos ajustaram em 2022, selecionaram parâmetros em 2023 e reajustaram em 2022–23 antes do replay. Nas regras manuais com blue chips, a seleção usou 2023 por disponibilidade dos dados. As séries separam 2024, 2025 e 2026 até outubro. Esses anos já foram explorados no projeto. O controle espelho inverte os sinais das regras de seguimento. Seu destaque foi observado depois da avaliação, então é diagnóstico exploratório.

## Comparação

| Cenário estressado | 2024 | 2025 | 2024–25 | 2026 até outubro |
|---|---:|---:|---:|---:|
| M2 v2, um contrato por entrada | 708 | 3.237 | 3.945 | 4.094 |
| Controle espelho das árvores | 642 | 4.734 | 5.376 | 2.128 |
| M2 v2, dimensionamento original | 1.724 | 5.327 | 7.051 | 5.530 |
| Descolamento contrário selecionado no treino | 1.003 | 1.574 | 2.577 | −7 |

O controle espelho das árvores teve 363 operações em 2024–25, contra 397 do v2 unitário. A diferença estressada foi R$ 1.431 a favor do espelho. O IC95% pareado de −R$ 10,40 a +R$ 15,89 por pregão inclui zero, usando 10.000 reamostragens estacionárias com blocos médios de dez pregões. Sem atraso e a 15 pontos, o espelho fez R$ 6.792, abaixo dos R$ 7.064 do v2 unitário. Nenhuma regra contrária selecionada no treino superou o v2 unitário em 2024–25 sob estresse. Os dois benchmarks vêm da auditoria M1 da rodada 6.

## Reprodução

Extraia PACOTE_GPT_M2.zip e este ZIP sobre a mesma raiz. O pacote original fornece dados/. Com Python 3, NumPy, pandas e scikit-learn, execute `python round8/lideranca.py` e `python round8/inversao.py` a partir da raiz. A tabela contra_resultado.csv inclui resultados por ano e comparações pareadas. contra_diario.csv contém os valores por pregão. Os scripts de seleção e o benchmark congelado estão neste ZIP.
