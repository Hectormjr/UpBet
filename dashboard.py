import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Nota: usar (Alt + Z) para melhor leitura da Querys 

#Configuração do tamanho da pagina
st.set_page_config(layout="wide")

# Conectar ao banco de dados
conn = st.connection("postgresql", type="sql")

# Ler arquivo CSV
df_csv = pd.read_csv("affiliates.csv", sep=",", decimal=".")

# Query para obter o total apostado  
postgre_total_bet_amount = conn.query("CREATE TEMP TABLE total_apostas_por_codigo AS SELECT m.customer_code, SUM(t.amount) AS total_apostado FROM public.bets AS t JOIN public.mapping AS m ON t.customer_id = m.customer_id GROUP BY m.customer_code; SELECT c.customer_id, t.total_apostado FROM public.customers AS c JOIN total_apostas_por_codigo AS t ON c.code = t.customer_code;")

# Query para obter os valores limites
postgre_limit = conn.query("SELECT * FROM public.limits ORDER BY amount ASC ")

# Criação do DataFrame a partir dos dados das apostas do Postgre
df_total_bet_amount=pd.DataFrame(postgre_total_bet_amount)
df_total_bet_amount.columns=['Customer Id','Total Apostado']

# Criação do DataFrame a partir dos dados dos valores da Tabela Limite
df_limit=pd.DataFrame(postgre_limit)
df_limit_percents = df_limit[['amount','porcent']].copy()
df_limit_percents.columns = ['Amount', 'Percent']   

# Renomenado as Colunas do DataFrame do arquivo CSV
df_csv.columns = ['Nome', 'Affiliate Id', 'Data', 'Pagamento CSV', 'customer_id'] 

# Função para verificar o percentual baseado no Total Apostado
def verify_limit(total_amount):
    for index, row in df_limit_percents.iterrows():
        if total_amount <= row['Amount']:
            return row['Percent']
    # Se o total apostado for maior que 500, retorne 50 (enunciado)
    return 50

# Aplicar a função verify_limit ao DataFrame data para calcular a porcentagem a ser cobrada para cada cliente
df_total_bet_amount['Percentual'] = df_total_bet_amount['Total Apostado'].apply(verify_limit)

# Calculo do Pagamento final para cada Afiliado (Pagamento CSV + Pagamento CSV * Percentual_Limite)
df_total_bet_amount['Pagamento Final'] = (df_total_bet_amount['Percentual']/100)*df_csv['Pagamento CSV']+df_csv['Pagamento CSV']

#Junção do DataFrames para exibição e retirada das colunas desnecessarias 
df_final = pd.merge(df_csv, df_total_bet_amount, left_on='customer_id', right_on='Customer Id', how='right')
df_final.drop(columns=['customer_id','Data'], inplace=True)

# Organização das colunas de maneira mais intuitiva
df_final = df_final[['Nome', 'Affiliate Id', 'Customer Id', 'Total Apostado', 'Percentual', 'Pagamento CSV', 'Pagamento Final']]

# Adicionar o símbolo de porcentagem (%) ao Percentual
df_final['Percentual'] = df_final['Percentual'].astype(str) + '%'

# Arredondar os valores numéricos sem casas decimais
df_final['Total Apostado'] = df_final['Total Apostado'].round(0)
df_final['Pagamento CSV'] = df_final['Pagamento CSV'].round(0)
df_final['Pagamento Final'] = df_final['Pagamento Final'].round(0)

# Criação de um novo Dataframe para usar no PieChart para evitar erros devido a conversão de valores para string
df_final_to_pie_chart = df_final.copy()

# Incluindo o cifrão nos valores monetarios
df_final['Total Apostado'] = 'R$ ' + df_final['Total Apostado'].astype(str)
df_final['Pagamento CSV'] = 'R$ ' + df_final['Pagamento CSV'].astype(str)
df_final['Pagamento Final'] = 'R$ ' + df_final['Pagamento Final'].astype(str)

# Ordenando por Nome
df_final = df_final.sort_values(by='Nome')

# Dividindo a 1° Linha da Dashborad em Duas Colunas
col1, col2 = st.columns(2)

#Exibição da tabela
col1.markdown("### Tabela de Afiliados com Total Apostado e Valor de Pagamento Final")
col1.write(df_final.to_html(index=False), unsafe_allow_html=True,)
# st.write(df_limit_percents.to_html(index=False), unsafe_allow_html=True, use_container_width=True)

# Adicional, inclução de grafico de pizza mostrando o percentual do total pago para cada Afiliado
pie_chart_percent_win_peer_afilliate = px.pie(df_final_to_pie_chart, values="Pagamento Final", names="Nome",
                   title="Percentual do total pago para cada Afiliado")

# Ajustar o tamanho do título
pie_chart_percent_win_peer_afilliate.update_layout(title_font_size=25)

# Plotar grafico
col2.plotly_chart(pie_chart_percent_win_peer_afilliate, use_container_width=True)

# Adicional, inclução de grafico de barras horizontais mostrando valor apostado por cada jogador em cada jogo
# Query para obter os valores totais de Amount e Win por game 
postgre_afilliate_bet_in_specific_game = conn.query("SELECT b.game_id, c.customer_id, SUM(b.total_amount) AS total_amount FROM ( SELECT game_id, m.customer_code, SUM(amount) AS total_amount  FROM public.bets  JOIN public.mapping AS m ON bets.customer_id = m.customer_id GROUP BY game_id, m.customer_code ) AS b JOIN public.customers AS c ON b.customer_code = c.code GROUP BY b.game_id, c.customer_id ORDER BY b.game_id ASC;")

# Criação do DataFrame a partir dos dados das apostas do Postgre
df_afilliate_bet_in_specific_game = pd.DataFrame(postgre_afilliate_bet_in_specific_game)
df_afilliate_bet_in_specific_game.columns = ['Jogo','Customer Id', 'Total Apostado']

# Criando outro DataFrame somente com os Nomes e Customer_Id a partir do csv para melhor manipulação
df_csv_names = df_csv[['Nome', 'customer_id']].copy()

#Junção do DataFrames para exibição e retirada das colunas desnecessarias 
df_final_horizontal_bar_chart = pd.merge(df_csv_names, df_afilliate_bet_in_specific_game, left_on='customer_id', right_on='Customer Id', how='right')
df_final_horizontal_bar_chart.drop(columns=['customer_id', 'Customer Id'], inplace=True)

# Definição do grafico
horizontal_bar_chart_afilliate_bet_in_specific_game = px.bar(df_final_horizontal_bar_chart, y="Jogo", x="Total Apostado", color ='Nome', barmode="group", title="Valor apostado por cada Afiliado em cada Jogo", orientation="h")

# Ajustar o tamanho do título
horizontal_bar_chart_afilliate_bet_in_specific_game.update_layout(title_font_size=25)

# Plotar grafico
col2.plotly_chart(horizontal_bar_chart_afilliate_bet_in_specific_game, use_container_width=True)


# Adicional, inclução de grafico de barras mostrando o montante apostado em cada jogo e os ganhos
# Usando a tabelas de Games e os valores de Amount e Win da tabela Bets
# Query para obter os valores totais de Amount e Win por game 
postgre_games_balance = conn.query("SELECT game_id, SUM(amount) AS total_amount, SUM(win) AS total_win FROM public.bets GROUP BY game_id ORDER BY game_id ASC")

# Criação do DataFrame a partir dos dados das apostas do Postgre
df_games_balance = pd.DataFrame(postgre_games_balance)
df_games_balance.columns = ['Jogo', 'Total Apostado', 'Total Ganho']

# Criar um gráfico de barras com duas colunas para cada valor de Jogo
bar_chart_games_balance = px.bar(df_games_balance, x="Jogo", y=["Total Apostado", "Total Ganho"], barmode="group", title="Balanço por Jogo")

# Adicionar valores de cada coluna dentro das barras
bar_chart_games_balance.update_traces(texttemplate='R$ %{y}', textposition='inside')

# Ajustar o tamanho do título
bar_chart_games_balance.update_layout(title_font_size=25)

# Exibir o gráfico
st.plotly_chart(bar_chart_games_balance, use_container_width=True)