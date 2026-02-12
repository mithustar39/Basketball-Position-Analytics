import sqlite3
import pandas as pd
import numpy as np

def find_ideal_player_match(db_name ='basketball.db'):
    """
    Finds the specific NBA player that most closely matches user-inputted stats.
    Uses Z-score standardization and Euclidean distance to measure the closest NBA 
    player in terms of stats.
    """
    try:
        conn = sqlite3.connect(db_name)
        
        # Calculate the 'average' and 'spread' for standardization
        df = pd.read_sql("SELECT * FROM nba_players", conn)
        conn.close()

        if df.empty:
            print("Database is empty.")
            return

        stat_cols = ['fg_pct', 'three_p_pct', 'stl', 'blk', 'tov', 'pf', 'pts', 'ast', 'trb']
        
        print("\n--- Create Your Ideal Player Profile ---")
        user_input = {}
        for col in stat_cols:
            user_input[col] = float(input(f"Enter target {col}: "))

        # Transform all stats so they have a Mean of 0 and Standard Deviation of 1
        # This prevents categories from being overshadowed by others
        df_numeric = df[stat_cols].astype(float)
        
        # Calculate means and standard deviations from the database
        means = df_numeric.mean()
        stds = df_numeric.std()

        # Standardize the database
        df_standardized = (df_numeric - means) / stds
        
        # Standardize the user input using the SAME means/stds
        user_vector = np.array([user_input[col] for col in stat_cols])
        user_standardized = (user_vector - means.values) / stds.values

        # We find the straight-line distance in 9-dimensional space (the amount of categroies there are)
        distances = np.linalg.norm(df_standardized.values - user_standardized, axis=1)
        
        # Add distances back to the original dataframe to see names
        df['similarity_score'] = distances
        
        # Print out top 3 matches from the database
        matches = df.sort_values('similarity_score').head(3)

        print("\n--- Your Top NBA Player Matches ---")
        for i, (idx, row) in enumerate(matches.iterrows(), 1):
            print(f"{i}. {row['player_name']} (Distance: {row['similarity_score']:.2f})")
            print(f"   Stats: {row['pts']} PTS, {row['ast']} AST, {row['trb']} REB")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    find_ideal_player_match()
