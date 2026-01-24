import sqlite3
import pandas as pd

def check_database_health(db_name='basketball.db'):
    """
    Performs a diagnostic audit on the NBA players database to ensure data integrity.

    This function executes four specific health checks:
    1. Row Count: Verifies the total number of records imported.
    2. Null Integrity: Checks for missing values in critical columns (Name, Points, FG%).
    3. Alignment Check: Pulls a random sample to visually verify data-to-column mapping.
    4. Logical Validation: Displays top scorers to ensure the numeric data is sorted correctly.

    Args:
        db_name (str): The filename of the SQLite database to check. Defaults to 'basketball.db'.

    Returns:
        None: Prints a health report directly to the console.
    """
    try:
        conn = sqlite3.connect(db_name)
        print(f"--- Database Health Report: {db_name} ---")
        
        # 1. Total Count Check
        # Confirms the table isn't empty and gives a scale of the dataset.
        total_players = pd.read_sql('SELECT COUNT(*) FROM nba_players', conn).iloc[0,0]
        print(f"Total Players Imported: {total_players}")
        
        # 2. Null Value Check
        # Uses the difference between total rows and non-null counts to find holes in data.
        null_checks = pd.read_sql('''
            SELECT 
                COUNT(*) - COUNT(player_name) AS missing_names,
                COUNT(*) - COUNT(pts) AS missing_pts,
                COUNT(*) - COUNT(fg_pct) AS missing_fg_pct
            FROM nba_players
        ''', conn)
        print(f"\nMissing Data Summary:\n{null_checks}")
        
        # 3. Random Sample Check
        # Helps identify if columns were shifted during import (e.g., names in the position column).
        print("\nRandom Sample (Verify if stats match the names):")
        sample = pd.read_sql('''
            SELECT player_name, position, pts, trb, ast, three_p_pct 
            FROM nba_players 
            ORDER BY RANDOM() 
            LIMIT 5
        ''', conn)
        print(sample)
        
        # 4. Top Scorers Check (Logic Check)
        # Verifies that numeric columns (pts) are being treated as numbers and not strings.
        print("\nTop 3 Scorers (Logic Check):")
        top_scorers = pd.read_sql('''
            SELECT player_name, pts 
            FROM nba_players 
            ORDER BY pts DESC 
            LIMIT 3
        ''', conn)
        print(top_scorers)

    except sqlite3.Error as e:
        print(f"Database error during health check: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Ensure the connection is always closed
        if conn:
            conn.close()

if __name__ == "__main__":
    check_database_health()