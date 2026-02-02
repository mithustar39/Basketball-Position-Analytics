import pandas as pd
# 3 points pecentage, steals, blocks, turnovers, personal fouls, points, assists, rebounds, field goal percentage
# 1. Load the CSV file into a DataFrame
# Replace 'your_file.csv' with the actual path to your file
df = pd.read_csv('nba_stats.csv')
stats = ['Field Goal Percentage', '3P%', 'STL', 'BLK', 'TOV', 'PF', 'Points', 'AST', 'TRB']
stats_c = {}
stats_pf = {}
stats_sf = {}
stats_sg = {}
stats_pg = {}


for i in stats:
    selected_rows = df.iloc[1:103]
    average_value = selected_rows[i].mean()
    stats_c[i] = average_value

print(f"These are the stats for position C: {stats_c}")

for i in stats:
    selected_rows = df.iloc[104:211]
    average_value = selected_rows[i].mean()
    stats_pf[i] = average_value

print(f"These are the stats for position PF: {stats_pf}")

for i in stats:
    selected_rows = df.iloc[212:311]
    average_value = selected_rows[i].mean()
    stats_pg[i] = average_value

print(f"These are the stats for position PG: {stats_pg}")
for i in stats:
    selected_rows = df.iloc[312:415]
    average_value = selected_rows[i].mean()
    stats_sf[i] = average_value

print(f"These are the stats for position SF: {stats_sf}")

for i in stats:
    selected_rows = df.iloc[416:569]
    average_value = selected_rows[i].mean()
    stats_sg[i] = average_value

print(f"These are the stats for position SG: {stats_sg}")