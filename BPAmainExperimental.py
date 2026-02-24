import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from average_stat import positions

def get_user_stats():
    """Prompts user for specific NBA metrics and normalizes by game length."""
    print("\n--- Enter Your Per-Game Stats ---")
    
    fg_pct = float(input("Field Goal Percentage (e.g., 0.45): "))
    three_p_pct = float(input("3-Point Percentage (e.g., 0.35): "))
    stl = float(input("Steals: "))
    blk = float(input("Blocks: "))
    tov = float(input("Turnovers: "))
    pf = float(input("Personal Fouls: "))
    pts = float(input("Points: "))
    ast = float(input("Assists: "))
    trb = float(input("Total Rebounds: "))
    game_min = int(input("Game Length (minutes): "))

    # Normalizing stats per minute to ensure fair comparison
    user_stats = {
        'Field Goal Percentage': fg_pct,
        '3P%': three_p_pct,
        'STL': stl / game_min,
        'BLK': blk / game_min,       
        'TOV': tov / game_min,
        'PF': pf / game_min,             
        'Points': pts / game_min,
        'AST': ast / game_min,
        'TRB': trb / game_min    
    }
    return user_stats

def find_best_position_fit(user_stats, positions):
    """Analyzes user stats against database averages and returns skill placement."""
    comparisons = [[0]*9 for _ in range(5)]
    stat_keys = ['Field Goal Percentage', '3P%', 'STL', 'BLK', 'TOV', 'PF', 'Points', 'AST', 'TRB']

    for i, pos_dict in enumerate(positions):
        for a, stat_name in enumerate(stat_keys):
            comparisons[i][a] = (user_stats[stat_name] - pos_dict[stat_name]) / pos_dict[stat_name]
    
    absComparisons = np.abs(comparisons)
    positionComparisons = np.mean(absComparisons, axis=1)

    bestFitIndex = np.argmin(positionComparisons)
    pos_names = ["Center", "Power Forward", "Small Forward", "Shooting Guard", "Point Guard"]
    best_pos = pos_names[bestFitIndex]

    print(f"\n--- Best Position Fit: {best_pos} ---")

    # Determine skills to improve vs skills above average
    # We sort the percentage differences for the best fitting position
    sorted_stats = [x for _, x in sorted(zip(comparisons[bestFitIndex], stat_keys))]
    
    aboveAve = ", ".join(sorted_stats[:3])  # Top 3 relative to position
    improve = ", ".join(sorted_stats[-3:])   # Bottom 3 relative to position

    return best_pos, improve, aboveAve

def find_ideal_player_match(user_stats, db_name='basketball.db'):
    """Finds the closest NBA player match and returns the name and distance."""
    try:
        conn = sqlite3.connect(db_name)
        df = pd.read_sql("SELECT * FROM nba_players", conn)
        conn.close()

        # Map user_stats keys to DB column names
        mapping = {
            'Field Goal Percentage': 'fg_pct', '3P%': 'three_p_pct', 'STL': 'stl',
            'BLK': 'blk', 'TOV': 'tov', 'PF': 'pf', 'Points': 'pts', 'AST': 'ast', 'TRB': 'trb'
        }
        
        stat_cols = list(mapping.values())
        df_numeric = df[stat_cols].astype(float)
        
        means, stds = df_numeric.mean(), df_numeric.std()
        df_standardized = (df_numeric - means) / stds
        
        # Prepare user vector
        user_vector = np.array([user_stats[k] for k in mapping.keys()])
        user_standardized = (user_vector - means.values) / stds.values

        distances = np.linalg.norm(df_standardized.values - user_standardized, axis=1)
        df['similarity_score'] = distances
        
        match = df.sort_values('similarity_score').iloc[0]
        return match['player_name'], round(match['similarity_score'], 2)

    except Exception as e:
        print(f"Match Error: {e}")
        return "Unknown", 0

def update_user_data_stats(user_stats, best_pos, improve, aboveAve, player_match, db_name='basketball.db'):
    """Creates a user_analysis table and stores all collected data."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                points_per_min REAL,
                best_position TEXT,
                skills_above_avg TEXT,
                skills_to_improve TEXT,
                nba_comparison TEXT
            )
        ''')

        # Insert the data
        cursor.execute('''
            INSERT INTO user_analysis (timestamp, points_per_min, best_position, skills_above_avg, skills_to_improve, nba_comparison)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_stats['Points'],
            best_pos,
            aboveAve,
            improve,
            player_match
        ))

        conn.commit()
        conn.close()
        print("\n--- Data successfully saved to database! ---")

    except sqlite3.Error as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    stats = get_user_stats()
    
    best_pos, to_improve, excels_in = find_best_position_fit(stats, positions)
    
    player_name, distance = find_ideal_player_match(stats)
    print(f"Closest NBA Player: {player_name}")

    update_user_data_stats(stats, best_pos, to_improve, excels_in, player_name)