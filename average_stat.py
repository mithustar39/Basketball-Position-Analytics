import pandas as pd

# 3 points percentage, steals, blocks, turnovers, personal fouls, points, assists, rebounds, field goal percentage
# 1. Load the CSV file into a DataFrame
df = pd.read_csv('nba_stats.csv')
stats = ['Field Goal Percentage', '3P%', 'STL', 'BLK', 'TOV', 'PF', 'Points', 'AST', 'TRB']
stats_c = {}
stats_pf = {}
stats_sf = {}
stats_sg = {}
stats_pg = {}

positions = [stats_c, stats_pf, stats_sf, stats_sg, stats_pg]
for j in positions:
    if j == stats_c:
        selected_rows = df.iloc[1:103]
        position = 'C'
    elif j == stats_pf:
        selected_rows = df.iloc[104:211]
        position = 'PF'
    elif j == stats_sf:
        selected_rows = df.iloc[212:311]
        position = 'SF'
    elif j == stats_sg:
        selected_rows = df.iloc[312:415]
        position = 'SG'
    elif j == stats_pg:
        selected_rows = df.iloc[416:569]
        position = 'PG'
    for i in stats:
        average_value = selected_rows[i].mean()
        if i != 'Field Goal Percentage' and i != '3P%':
            average_value = average_value/48 # Divide by the number of minutes in an NBA basketball game
        j[i] = round(average_value, 5) 
