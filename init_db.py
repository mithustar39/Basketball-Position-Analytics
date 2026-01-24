import sqlite3
import pandas as pd
import os

def import_csv_to_sql(csv_filepath='nba_stats.csv', db_name='basketball.db'):
    """
    Imports NBA player statistics from a CSV file into a SQLite database.

    This function performs the following steps:
    1. Loads a raw basketball statistics CSV.
    2. Maps non-standard or character-heavy headers (e.g., '3P%') to SQL-friendly names.
    3. Handles missing values (NaN) that occur when players have zero attempts in a category.
    4. Appends the cleaned data into the 'nba_players' table in the target database.

    Args:
        csv_filepath (str): The path to the source CSV file. Defaults to 'nba_stats.csv'.
        db_name (str): The name of the SQLite database file. Defaults to 'basketball.db'.

    Returns:
        None

    Raises:
        FileNotFoundError: If the specified CSV file does not exist.
        sqlite3.Error: If there is an issue connecting to or writing to the database.
    """
    
    # Check if file exists before processing to provide a clear error message
    if not os.path.exists(csv_filepath):
        print(f"Error: The file '{csv_filepath}' was not found.")
        return

    try:
        # Establish connection to the SQLite database
        conn = sqlite3.connect(db_name)
        
        # Load raw data into a pandas DataFrame
        df = pd.read_csv(csv_filepath)

        # Dictionary mapping CSV headers to clean, standardized SQL column names.
        # This ensures consistency for future SQL queries (avoiding %, -, and spaces).
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

        # Rename columns based on the mapping defined above
        df = df.rename(columns=mapping)
        
        # Handle players who did not take a shot in a specific category (e.g., 3P%).
        # Pandas loads these as NaN (Not a Number), which can break math operations.
        # Filling with 0 ensures the database remains numeric and queryable.
        df = df.fillna(0)

        # Write the cleaned DataFrame to the 'nba_players' table.
        # 'if_exists=append' allows you to keep existing data and add new records.
        df.to_sql('nba_players', conn, if_exists='append', index=False)
        
        print(f"Successfully imported {len(df)} players with all attributes.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Ensure the connection is closed even if an error occurs
        if conn:
            conn.close()

if __name__ == "__main__":
    import_csv_to_sql()