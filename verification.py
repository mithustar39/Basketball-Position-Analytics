import sqlite3
import pandas as pd

def check_database_health():
    conn = sqlite3.connect('basketball.db')
    
    print("--- Database Health Report ---")
    
    # 1. Total Count Check
    total_players = pd.read_sql('SELECT COUNT(*) FROM nba_players', conn).iloc[0,0]
    print(f"Total Players Imported: {total_players}")
    
    # 2. Null Value Check (Look for missing stats)
    # This checks if any critical stats came in as NULL/empty
    null_checks = pd.read_sql('''
        SELECT 
            COUNT(*) - COUNT(player_name) AS missing_names,
            COUNT(*) - COUNT(pts) AS missing_pts,
            COUNT(*) - COUNT(fg_pct) AS missing_fg_pct
        FROM nba_players
    ''', conn)
    print(f"\nMissing Data Summary:\n{null_checks}")
    
    # 3. Random Sample Check
    # This displays 5 random players to ensure columns aligned correctly
    print("\nRandom Sample (Verify if stats match the names):")
    sample = pd.read_sql('''
        SELECT player_name, position, pts, trb, ast, three_p_pct 
        FROM nba_players 
        ORDER BY RANDOM() 
        LIMIT 5
    ''', conn)
    print(sample)
    
    # 4. Top Scorers Check (Logic Check)
    print("\nTop 3 Scorers (Logic Check):")
    top_scorers = pd.read_sql('''
        SELECT player_name, pts 
        FROM nba_players 
        ORDER BY pts DESC 
        LIMIT 3
    ''', conn)
    print(top_scorers)

    conn.close()

if __name__ == "__main__":
    check_database_health()