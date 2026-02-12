# Import average statistics for each position from the average_stat module
from average_stat import positions
import numpy as np  

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
def find_best_position_fit(user_stats, positions):
    """
    Analyzes user stats against database averages using Euclidean distance.
    """

    comparisons = [[0]*9 for _ in range(5)]  # Initialize a 5x9 matrix to store percentage differences


    for i, j in enumerate(positions):
        for a, b in enumerate(['Field Goal Percentage', '3P%', 'STL', 'BLK', 'TOV', 'PF', 'Points', 'AST', 'TRB']):
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

find_best_position_fit(get_user_stats(), positions)
