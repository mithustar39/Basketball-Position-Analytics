from average_stat import positions, stats
import numpy as np
import pandas  
import sqlite3

statTypes = ['Field Goal Percentage', '3P%', 'STL', 'BLK', 'TOV', 'PF', 'Points', 'AST', 'TRB']

# Function to collect user's basketball statistics as input
def get_user_stats():
    """Prompts user for specific NBA metrics."""

    print("\n--- Enter Your Per-Game Stats ---")  # Display header message
    # Return a dictionary containing all user-entered statistics as floats
    
    fg_pct = float(input("Field Goal Percentage (e.g., 0.45): "))  # User input for field goal percentage
    three_p_pct = float(input("3-Point Percentage (e.g., 0.35): "))  # User input for three-point percentage
    stl = float(input("Steals: "))  # User input for steals per game
    blk = float(input("Blocks: "))  # User input for blocks per game
    tov = float(input("Turnovers: "))  # User input for turnovers per game
    pf = float(input("Personal Fouls: "))  # User input for personal fouls per game
    pts = float(input("Points: "))  # User input for points per game
    ast = float(input("Assists: "))  # User input for assists per game
    trb = float(input("Total Rebounds: "))  # User input for total rebounds per game
    min = int(input("Game Length: "))  # User input for minutes played per game

    user_stats = {
        'Field Goal Percentage': fg_pct,
        '3P%': three_p_pct,
        'STL': stl / min,
        'BLK': blk / min,       
        'TOV': tov / min,
        'PF': pf / min,             
        'Points': pts / min,
        'AST': ast / min,
        'TRB': trb / min    
    }

    return user_stats # Return the list of user statistics for further analysis

# Function to determine the best position fit based on user statistics
def find_best_position_fit(user_stats, positions, statTypes):
    """
    Analyzes user stats against database averages using Euclidean distance.
    """

    comparisons = [[0]*9 for _ in range(5)]  # Initialize a 5x9 matrix to store percentage differences


    for i, j in enumerate(positions):
        for a, b in enumerate(statTypes):
            comparisons[i][a] = (user_stats[b] - j[b])/j[b] 
    absComparisons = np.abs(comparisons)  # Take the absolute value of the percentage differences
    positionComparisons = np.mean(absComparisons, axis=1)  # Calculate the mean percentage difference for each position

    bestFit = positionComparisons[0]
    bestFitIndex = 0

    for i, j in enumerate(positionComparisons):
        if bestFit > j:
            bestFit = j
            bestFitIndex = i # Find the index of the position with the smallest mean percentage difference 

    print("\n--- Best Position Fit ---")  # Display header message for best position fit
    if bestFitIndex == 0:
        print("Your best position fit is: Center (C)")  # Output if the best fit is Center
    elif bestFitIndex == 1:
        print("Your best position fit is: Power Forward (PF)")  # Output if the best fit is Power Forward
    elif bestFitIndex == 2:
        print("Your best position fit is: Small Forward (SF)")  # Output if the best fit is Small Forward
    elif bestFitIndex == 3:
        print("Your best position fit is: Shooting Guard (SG)")  # Output if the best fit is Shooting Guard
    elif bestFitIndex == 4:
        print("Your best position fit is: Point Guard (PG)")  # Output if the best fit is Point Guard   

    statistics = ['Field Goal Percentage', '3P%', 'STL', 'BLK', 'TOV', 'PF', 'Points', 'AST', 'TRB']

    for i in range(1, len(comparisons[bestFitIndex])):
        key = comparisons[bestFitIndex][i]
        key_stat = statistics[i]
        j = i -1
        while (j>0 and key<comparisons[bestFitIndex][j]):
            comparisons[bestFitIndex][j + 1] = comparisons[bestFitIndex][j]
            statistics[j + 1] = statistics[j]
            j -= 1
        comparisons[bestFitIndex][j + 1]= key
        statistics[j + 1] = key_stat



    print(f"Statistics needing improvement: 1. {statistics[-1]}, 2. {statistics[-2]}, 3. {statistics[-3]}")  # Output the top three statistics that are closest to the average for the best fit position
    print(f"Statistics that are above average: 1. {statistics[0]}, 2. {statistics[1]}, 3. {statistics[2]}")  # Output the top three statistics that are furthest from the average for the best fit position

def compareSpecificPlayer(user_stats, statTypes): 
    

    conn  = sqlite3.connect('basketball.db')
    
    cursor = conn.cursor()
    
    playerName = input("Please enter the first and last name of the player you wish to compare with: ")
    playerStats = {}
    
    # query the correct table and column names from the imported CSV
    cursor.execute("SELECT * FROM nba_players WHERE player_name = ?", (playerName,))
    player = cursor.fetchone()

    if player:
        # turn row into dict for readable output
        columns = [description[0] for description in cursor.description]
        player_dict = dict(zip(columns, player))
    else:
        print("Player not found.")

    comparisonsSpecific = [[0]*len(statTypes) for _ in range(1)]  # Initialize a 1xN matrix for percentage differences

    # help with github chat so learn :
    # database columns corresponding to the human-readable stat names
    statNameTemp = ['fg_pct', 'three_p_pct', 'stl', 'blk', 'tov', 'pf', 'pts', 'ast', 'orb']
    # create a mapping from display names -> db keys
    stat_map = dict(zip(statTypes, statNameTemp))

    # convert player stats from strings to floats using the db field names
    for stat in statTypes:
        db_key = stat_map[stat]
        # some rows may lack the key (unlikely), so use get with default 0
        player_dict[db_key] = float(player_dict.get(db_key, 0))

    # compute percent differences using mapped keys for the player data
    for a, stat in enumerate(statTypes):
        user_val = user_stats[stat]
        player_val = player_dict[stat_map[stat]]
        comparisonsSpecific[0][a] = (user_val - player_val) / player_val if player_val != 0 else 0
    absComparisons = np.abs(comparisonsSpecific)  # Take the absolute value of the percentage differences
    playerComparisons = np.mean(absComparisons, axis=1)  # Calculate the mean percentage difference for each position

    print("Mean Percent Difference:")
    print(playerComparisons)

    conn.close()

    
    
compareSpecificPlayer(get_user_stats(), statTypes)
