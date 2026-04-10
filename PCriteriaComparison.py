import sqlite3
import pandas as pd
import numpy as np


def get_top_player_matches(user_input, db_name='basketball.db', top_n=3):
    """
    Returns the top N closest NBA player matches for a provided stat profile.
    """
    conn = sqlite3.connect(db_name)
    df = pd.read_sql("SELECT * FROM nba_players", conn)
    conn.close()

    if df.empty:
        return []

    stat_cols = ['fg_pct', 'three_p_pct', 'stl', 'blk', 'tov', 'pf', 'pts', 'ast', 'trb']

    df_numeric = df[stat_cols].astype(float)
    means = df_numeric.mean()
    stds = df_numeric.std().replace(0, 1)

    df_standardized = (df_numeric - means) / stds

    user_vector = np.array([float(user_input[col]) for col in stat_cols], dtype=float)
    user_standardized = (user_vector - means.values) / stds.values

    distances = np.linalg.norm(df_standardized.values - user_standardized, axis=1)

    df['similarity_score'] = distances
    matches = (
        df
        .sort_values('similarity_score')
        .head(top_n)
        [['player_name', 'position', 'pts', 'ast', 'trb', 'similarity_score']]
        .copy()
    )

    matches['similarity_score'] = matches['similarity_score'].round(2)
    return matches.to_dict(orient='records')

def find_ideal_player_match(db_name ='basketball.db'):
    """
    Finds the specific NBA player that most closely matches user-inputted stats.
    Uses Z-score standardization and Euclidean distance to measure the closest NBA 
    player in terms of stats.
    """
    try:
        stat_cols = ['fg_pct', 'three_p_pct', 'stl', 'blk', 'tov', 'pf', 'pts', 'ast', 'trb']
        
        print("\n--- Create Your Ideal Player Profile ---")
        user_input = {}
        for col in stat_cols:
            user_input[col] = float(input(f"Enter target {col}: "))

        matches = get_top_player_matches(user_input, db_name=db_name, top_n=3)

        if not matches:
            print("Database is empty.")
            return

        print("\n--- Your Top NBA Player Matches ---")
        for i, row in enumerate(matches, 1):
            print(f"{i}. {row['player_name']} (Distance: {row['similarity_score']:.2f})")
            print(f"   Stats: {row['pts']} PTS, {row['ast']} AST, {row['trb']} REB")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    find_ideal_player_match()
