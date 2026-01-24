import sqlite3
import pandas as pd

def import_csv_to_sql():
    conn = sqlite3.connect('basketball.db')
    
    # Load the CSV
    df = pd.read_csv('nba_stats.csv')

    # KEY: Map CSV Header -> SQL Table Column
    mapping = {
        'Rk': 'rk',
        'Player': 'player_name',
        'Position': 'position',
        'Game': 'games_played',
        'Games Started': 'games_started',
        'Mins Played': 'mins_played',
        'Field Goals': 'field_goals',
        'Field Goal Attempts': 'fg_attempts',
        'Field Goal Percentage': 'fg_pct',
        '3-Point Field Goals': 'three_p_made',
        '3-Point Field Goal Attempts': 'three_p_attempts',
        '3P%': 'three_p_pct',
        '2P': 'two_p_made',
        '2PA': 'two_p_attempts',
        '2P%': 'two_p_pct',
        'eFG%': 'efg_pct',
        'FT': 'ft_made',
        'FTA': 'ft_attempts',
        'FT%': 'ft_pct',
        'ORB': 'orb',
        'DRB': 'drb',
        'TRB': 'trb',
        'AST': 'ast',
        'STL': 'stl',
        'BLK': 'blk',
        'TOV': 'tov',
        'PF': 'pf',
        'Points': 'pts',
        'Awards': 'awards'
    }

    # Rename and Clean
    df = df.rename(columns=mapping)
    
    # Fill NaN values (especially for players with 0 attempts in 3P%)
    df = df.fillna(0)

    # Append to database
    df.to_sql('nba_players', conn, if_exists='append', index=False)
    
    print(f"Successfully imported {len(df)} players with all attributes.")
    conn.close()

import_csv_to_sql()