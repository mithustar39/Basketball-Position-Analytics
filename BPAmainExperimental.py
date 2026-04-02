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

def update_user_data_stats(user_stats, best_pos, improve, aboveAve, player_match, db_name='player.db'):
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

def initialize_user_db(db_name='player.db'):
    """Ensures the player.db has the correct table structure before we start."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
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
    conn.commit()
    conn.close()

def generate_user_dashboard(db_name='basketball.db'):
    """
    Retrieves and visualizes historical user data to show progress over time.
    Provides a 'Retrospective' of skill placement and growth.
    """
    try:
        conn = sqlite3.connect(db_name)
        
        # Load the user's history
        query = "SELECT * FROM user_analysis ORDER BY timestamp DESC"
        history_df = pd.read_sql(query, conn)
        conn.close()

        if history_df.empty:
            print("\nNo history found. Complete a few assessments first!")
            return

        print("\n" + "="*45)
        print("          USER PERFORMANCE DASHBOARD          ")
        print("="*45)

        # 1. Summary Metrics
        total_sessions = len(history_df)
        most_common_pos = history_df['best_position'].mode()[0]
        
        print(f"Total Sessions Logged: {total_sessions}")
        print(f"Primary Skill Identity: {most_common_pos}")

        # 2. Progress Logic (Comparing first session to last)
        if total_sessions > 1:
            # Latest session is at index 0 because of 'ORDER BY timestamp DESC'
            latest_pts = history_df.iloc[0]['points_per_min']
            initial_pts = history_df.iloc[-1]['points_per_min']
            improvement = ((latest_pts - initial_pts) / initial_pts) * 100
            
            print(f"Scoring Efficiency Trend: {improvement:+.1f}% since first session")

        # 3. Retrospective Skill History
        print("\n--- Recent Skill Analysis History ---")
        # Displaying the last 5 entries in a clean table format
        summary_table = history_df[['timestamp', 'best_position', 'nba_comparison']].head(5)
        print(summary_table.to_string(index=False))

        # 4. Action Items (Based on the most recent assessment)
        recent_improve = history_df.iloc[0]['skills_to_improve']
        print(f"\nFocus Areas for Next Practice: \n-> {recent_improve}")
        print("="*45)

    except Exception as e:
        print(f"Dashboard Error: {e}")

def clear_player_data(db_name='player.db'):
    """
    Safely deletes all records from the user_analysis table.
    """
    # Double-check confirmation
    confirm = input("\n⚠️ WARNING: This will delete ALL your saved progress. Type 'DELETE' to confirm: ")
    
    if confirm == 'DELETE':
        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            
            # TRUNCATE equivalent in SQLite
            cursor.execute("DELETE FROM user_analysis")
            
            # Also reset the auto-increment ID counter to 1
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='user_analysis'")
            
            conn.commit()
            conn.close()
            print("\n✅ Database cleared successfully. You are starting with a clean slate.")
        except sqlite3.Error as e:
            print(f"Error clearing database: {e}")
    else:
        print("\nOperation cancelled. Your data is safe.")

def main_menu():
    """
    The central hub for the application. 
    Routes the user between data entry, analysis, and the dashboard.
    """
    DB_NBA = 'basketball.db'
    DB_USER = 'player.db'
    Running = True 

    while Running:
        print("\n" + "="*30)
        print("   NBA PLAYER ANALYZER 2025   ")
        print("="*30)
        print("1. Log New Game Stats")
        print("2. View Progress Dashboard")
        print("3. Delete Existing Player Data")
        print("4. Exit")
        
        choice = input("\nSelect an option (1-3): ")

        if choice == '1':
            # 1. Collect
            stats = get_user_stats()
            
            # 2. Analyze (Requires positions list from your average_stat file)
            best_pos, to_improve, excels_in = find_best_position_fit(stats, positions)
            
            # 3. Match (Checking against the NBA database)
            player_name, distance = find_ideal_player_match(stats, db_name=DB_NBA)
            print(f"\nYour closest NBA twin is: {player_name}")
            
            # 4. Save (Storing in the User database)
            update_user_data_stats(stats, best_pos, to_improve, excels_in, player_name, db_name=DB_USER)
            
        elif choice == '2':
            generate_user_dashboard(db_name=DB_USER)
            
        elif choice == '3':
            clear_player_data(db_name=DB_USER)
        
        elif choice == '4':
            print("Keep practicing. Goodbye!")
            running = False

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    initialize_user_db()
    main_menu()