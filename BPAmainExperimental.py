import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from average_stat import positions

def get_user_stats():
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

    sorted_stats = [x for _, x in sorted(zip(comparisons[bestFitIndex], stat_keys))]
    
    aboveAve = ", ".join(sorted_stats[:3])
    improve = ", ".join(sorted_stats[-3:])

    sorted_pairs = sorted(zip(comparisons[bestFitIndex], stat_keys))
    worst_stats = [stat for _, stat in sorted_pairs[:3]]

    print("Worst Stats:", ", ".join(worst_stats))

    try:
        conn = sqlite3.connect('basketball.db')
        df = pd.read_sql("SELECT * FROM nba_players", conn)
        conn.close()

        mapping = {
            'Field Goal Percentage': 'fg_pct',
            '3P%': 'three_p_pct',
            'STL': 'stl',
            'BLK': 'blk',
            'TOV': 'tov',
            'PF': 'pf',
            'Points': 'pts',
            'AST': 'ast',
            'TRB': 'trb'
        }

        best_players_for_weakness = {}

        # Stats where LOWER is better
        inverse_stats = ['TOV', 'PF']

        for stat in worst_stats:
            db_col = mapping[stat]
            df[db_col] = df[db_col].astype(float)

            if stat in inverse_stats:
                # Lower is better
                best_idx = df[db_col].idxmin()
            else:
                # Higher is better
                best_idx = df[db_col].idxmax()

            best_player_row = df.loc[best_idx]
            best_players_for_weakness[stat] = best_player_row['player_name']

        print("Best NBA Players for Your Weak Stats:")
        for stat, player in best_players_for_weakness.items():
            print(f"{stat}: {player}")

    except Exception as e:
        print(f"Error finding players for weak stats: {e}")
        best_players_for_weakness = {}

def find_ideal_player_match(user_stats, db_name='basketball.db'):
    try:
        conn = sqlite3.connect(db_name)
        df = pd.read_sql("SELECT * FROM nba_players", conn)
        conn.close()

        mapping = {
            'Field Goal Percentage': 'fg_pct', '3P%': 'three_p_pct', 'STL': 'stl',
            'BLK': 'blk', 'TOV': 'tov', 'PF': 'pf', 'Points': 'pts', 'AST': 'ast', 'TRB': 'trb'
        }
        
        stat_cols = list(mapping.values())
        df_numeric = df[stat_cols].astype(float)
        
        means, stds = df_numeric.mean(), df_numeric.std()
        df_standardized = (df_numeric - means) / stds
        
        user_vector = np.array([user_stats[k] for k in mapping.keys()])
        user_standardized = (user_vector - means.values) / stds.values

        distances = np.linalg.norm(df_standardized.values - user_standardized, axis=1)
        df['similarity_score'] = distances
        
        match = df.sort_values('similarity_score').iloc[0]
        return match['player_name'], round(match['similarity_score'], 2)

    except Exception as e:
        print(f"Match Error: {e}")
        return "Unknown", 0

def compareSpecificPlayer(user_stats, statTypes): 
    
    conn  = sqlite3.connect('basketball.db')
    
    cursor = conn.cursor()
    
    playerName = input("Please enter the first and last name of the player you wish to compare with: ")
    playerStats = {}
    
    cursor.execute("SELECT * FROM nba_players WHERE player_name = ?", (playerName,))
    player = cursor.fetchone()

    if player:
        columns = [description[0] for description in cursor.description]
        player_dict = dict(zip(columns, player))
    else:
        print("Player not found.")

    comparisonsSpecific = [[0]*len(statTypes) for _ in range(1)]

    statNameTemp = ['fg_pct', 'three_p_pct', 'stl', 'blk', 'tov', 'pf', 'pts', 'ast', 'orb']
    stat_map = dict(zip(statTypes, statNameTemp))

    for stat in statTypes:
        db_key = stat_map[stat]
        player_dict[db_key] = float(player_dict.get(db_key, 0))

    for a, stat in enumerate(statTypes):
        user_val = user_stats[stat]
        player_val = player_dict[stat_map[stat]]
        comparisonsSpecific[0][a] = (user_val - player_val) / player_val if player_val != 0 else 0

    absComparisons = np.abs(comparisonsSpecific)
    playerComparisons = np.mean(absComparisons, axis=1)

    print("Mean Percent Difference:")
    print(playerComparisons)

    conn.close()

def update_user_data_stats(user_stats, best_pos, improve, aboveAve, player_match, db_name='player.db'):
    try:
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
    try:
        conn = sqlite3.connect(db_name)
        
        query = "SELECT * FROM user_analysis ORDER BY timestamp DESC"
        history_df = pd.read_sql(query, conn)
        conn.close()

        if history_df.empty:
            print("\nNo history found. Complete a few assessments first!")
            return

        print("\n" + "="*45)
        print("          USER PERFORMANCE DASHBOARD          ")
        print("="*45)

        total_sessions = len(history_df)
        most_common_pos = history_df['best_position'].mode()[0]
        
        print(f"Total Sessions Logged: {total_sessions}")
        print(f"Primary Skill Identity: {most_common_pos}")

        if total_sessions > 1:
            latest_pts = history_df.iloc[0]['points_per_min']
            initial_pts = history_df.iloc[-1]['points_per_min']
            improvement = ((latest_pts - initial_pts) / initial_pts) * 100
            
            print(f"Scoring Efficiency Trend: {improvement:+.1f}% since first session")

        print("\n--- Recent Skill Analysis History ---")
        summary_table = history_df[['timestamp', 'best_position', 'nba_comparison']].head(5)
        print(summary_table.to_string(index=False))

        recent_improve = history_df.iloc[0]['skills_to_improve']
        print(f"\nFocus Areas for Next Practice: \n-> {recent_improve}")
        print("="*45)

    except Exception as e:
        print(f"Dashboard Error: {e}")

def clear_player_data(db_name='player.db'):
    confirm = input("\n WARNING: This will delete ALL your saved progress. Type 'DELETE' to confirm: ")
    
    if confirm == 'DELETE':
        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM user_analysis")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='user_analysis'")
            
            conn.commit()
            conn.close()
            print("\n Database cleared successfully. You are starting with a clean slate.")
        except sqlite3.Error as e:
            print(f"Error clearing database: {e}")
    else:
        print("\nOperation cancelled. Your data is safe.")

def main_menu():
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
        print("4. Compare to Specific NBA Player")
        print("5. Exit")
        
        choice = input("\nSelect an option (1-3): ")

        if choice == '1':
            stats = get_user_stats()
            best_pos, to_improve, excels_in = find_best_position_fit(stats, positions)
            player_name, distance = find_ideal_player_match(stats, db_name=DB_NBA)
            print(f"\nYour closest NBA twin is: {player_name}")
            update_user_data_stats(stats, best_pos, to_improve, excels_in, player_name, db_name=DB_USER)
            
        elif choice == '2':
            generate_user_dashboard(db_name=DB_USER)
            
        elif choice == '3':
            clear_player_data(db_name=DB_USER)

        elif choice == '4':
            stats = get_user_stats()
            stat_keys = ['Field Goal Percentage', '3P%', 'STL', 'BLK', 'TOV', 'PF', 'Points', 'AST', 'TRB']
            compareSpecificPlayer(stats, stat_keys)
        
        elif choice == '5':
            print("Keep practicing. Goodbye!")
            Running = False

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    initialize_user_db()
    main_menu()
