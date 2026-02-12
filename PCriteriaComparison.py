import sqlite3
import pandas as pd
import numpy as np

def find_ideal_player_match(db_name='basketball.db'):
    """
    Finds the specific NBA player that most closely matches user-inputted stats.
    Uses Z-score standardization and Euclidean distance for high accuracy.
    """
    try:
        conn = sqlite3.connect(db_name)
        
        # 1. Load the entire dataset
        # We need the whole table to calculate the 'average' and 'spread' for standardization
        df = pd.read_sql("SELECT * FROM nba_players", conn)
        conn.close()

        if df.empty:
            print("Database is empty.")
            return

        # 2. Define the stats we are analyzing
        stat_cols = ['fg_pct', 'three_p_pct', 'stl', 'blk', 'tov', 'pf', 'pts', 'ast', 'trb']
        
        # 3. Get User Input
        print("\n--- Create Your Ideal Player Profile ---")
        user_input = {}
        for col in stat_cols:
            user_input[col] = float(input(f"Enter target {col}: "))

        # 4. STANDARDIZATION (The "Secret Sauce")
        # We transform all stats so they have a Mean of 0 and Standard Deviation of 1
        # This prevents 'Points' from drowning out 'Steals'
        df_numeric = df[stat_cols].astype(float)
        
        # Calculate means and standard deviations from the database
        means = df_numeric.mean()
        stds = df_numeric.std()

        # Standardize the database
        df_standardized = (df_numeric - means) / stds
        
        # Standardize the user input using the SAME means/stds
        user_vector = np.array([user_input[col] for col in stat_cols])
        user_standardized = (user_vector - means.values) / stds.values

        # 5. Calculate Euclidean Distance
        # We find the straight-line distance in 9-dimensional space
        distances = np.linalg.norm(df_standardized.values - user_standardized, axis=1)
        
        # Add distances back to the original dataframe to see names
        df['similarity_score'] = distances
        
        # 6. Find the Top 3 Matches
        matches = df.sort_values('similarity_score').head(3)

        print("\n--- Your Top NBA Player Matches ---")
        for i, (idx, row) in enumerate(matches.iterrows(), 1):
            print(f"{i}. {row['player_name']} (Distance: {row['similarity_score']:.2f})")
            print(f"   Stats: {row['pts']} PTS, {row['ast']} AST, {row['trb']} REB")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    find_ideal_player_match()