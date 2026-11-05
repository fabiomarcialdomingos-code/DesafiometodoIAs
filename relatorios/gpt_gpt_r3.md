# WIN M2 — rodada 3

Os scripts desta rodada usam os dados e os CSVs do pacote PACOTE_GPT_M2.zip. A análise é retrospectiva. A janela de escolha das alternativas do M2-A é 2022–23. A avaliação temporal usa 709 pregões de 2024 a outubro de 2026. A forma das hipóteses já foi estudada nesse histórico. É necessário um período novo para medir execução e desempenho fora de amostra.

## Reprodução

O M2 v2 reproduz 905 entradas, R$ 26.657,77 líquidos do custo simulado e PF 1,421. O replay fracionário do M2-A reproduz as 1.659 operações do CSV, incluindo as 17 com beta negativo, e todo o P&L por operação a menos de R$ 0,000000001. O PF fracionário do M2-A usa operações individuais. No hedge inteiro, o PF usa o P&L diário da cesta porque o resultado do hedge agregado é compartilhado. As diferenças diárias em reais permitem comparação direta.

O código original anexado para a ação depende de p2b_regra.py, ausente. A regra foi reconstruída com o núcleo anexado, a especificação e a reconciliação contra o CSV. Para o Noturno, os scripts específicos de grade também não vieram. A reconstrução independente com a janela relativa ao fechamento produz 160 operações, R$ 6.234,41 e PF 2,24. A versão fixa às 18h20 produz 93. A convenção histórica da janela relativa usa a disponibilidade observada de barras para inferir o horário da sessão curta. É um diagnóstico retrospectivo. Horários oficiais por data, mapeamento de vencimentos e dados de leilão são necessários para usar a versão em teste prospectivo.

## Execução e comparabilidade

A carteira de ações usa quantidades inteiras, custo de 10 bps ida e volta nas small caps e 6 bps nas blue chips. Ajusta o hedge total em WIN inteiro ao sair de componentes. O hedge IND usa o lote da B3 de cinco IND, aproximadamente 25 WIN em exposição. O stop por papel usa a marcação de ação mais o hedge teórico proporcional para disparar a saída, e o hedge físico inteiro compõe o P&L da cesta. O stop é verificado no fechamento da barra e executado na próxima abertura observada. Quando inexiste abertura observável no restante da grade de caixa, a marcação no último fechamento elegível é registrada como proxy. A saída às 16h45 reduziu o uso desse proxy de 866 para 1 no teste, com 1.123 entradas. Uma abertura de barra observada também não garante preenchimento a esse preço.

O corte de liquidez usa informação conhecida antes do pregão dentro do painel disponível. A lista de 50 foi escolhida perto do fim do histórico e o pacote não contém todos os papéis extintos, deslistados ou excluídos da seleção. O exercício reduz seleção por informação futura dentro do painel e não elimina sobrevivência.

O P&L diário da carteira soma as três mesas sem compensar ordens no WIN. A alocação real requer conta, disponibilidade de garantias, regras de venda e execução de leilão. O risco diário é a soma conservadora dos riscos planejados, inclusive períodos que não se sobrepõem. O Kelly maximiza crescimento logarítmico no P&L em R por dia, dentro de 0 e do limite que evita patrimônio não positivo nas observações reamostradas. O R divide o P&L pelo orçamento planejado daquele pregão. Os intervalos usam bootstrap estacionário em blocos médios de 10 pregões. Nas cestas foi estimado como uma fração única do risco total, sem otimizar pesos independentes.

## Decisão de pesquisa

O seletor do M2-A escolhe pelo menor PF entre cenário normal e cenário com atraso de cinco minutos mais custo 50% maior, no treino. As 288 configurações de treino incluem universo, limiar, stop, número de nomes e saída. A grade de 81 combinações do vencedor cruza ±20% no limiar inferior, superior, força do WIN e stop. Em 2024–26, 68 de 81 atendem aos pisos de PF, anos e quantidade, e zero atendem adicionalmente ao IC95% de incremento sobre o M2-A congelado. O placebo de escala compara R$120 de risco por operação com 1,5 vezes o P&L da regra de R$80. O placebo do v2 compara o segundo contrato com alocações pareadas por ano, lado do gap e faixa de risco, com ajuste de orçamento somado.

No Noturno, 13 de 54 células passaram nos pisos anuais e no IC incremental, antes dos estresses. A abertura de 26/10/2026 gerou até R$6.215 de perda em um contrato na grade. Essa cotação é corroborada internamente pelo IND, e a queda também aparece em BOVA11 no pacote. Atraso de cinco minutos do sinal central coincide com o encerramento agendado e não produz preenchimentos. P&L overnight entra no dia da realização.

As três extensões de WIN baseadas em absorção da abertura somam 27 configurações de dois limiares. Todas falham em pelo menos um critério no período 2024–26. Os resultados completos incluem PF líquido anual, número bruto e incremental de entradas, IC95% pareado e estresse. Mantém-se o v2 como referência de pesquisa. A execução do M2-A com saída antecipada é candidata a monitoramento em papel. A terceira perna permanece em pesquisa.

## Reexecutar

1. Extraia o PACOTE_GPT_M2.zip em uma pasta nova.
2. Extraia este ZIP sobre a mesma pasta. Ele acrescenta LEIA_RODADA3.md e study/.
3. Use Python 3 com NumPy e pandas. A primeira execução cria um cache de cerca de 300 MB para o painel.
4. Execute, da raiz da pasta, `python study/pesquisa.py`, `python study/carteira.py` e `python study/risco.py`. Para conferir a reprodução do WIN isoladamente, execute `python study/win_base.py`.

### Tabelas

- A_resultados.csv, A_treino.csv, A_grade.csv, A_series.csv
- N_resultados.csv, N_operacoes.csv, N_grade.csv, N_caudas.csv
- WIN_extensoes.csv, WIN_1_lote_orcamento.csv
- carteira_resultados.csv, carteira_diario.csv, placebos.csv
