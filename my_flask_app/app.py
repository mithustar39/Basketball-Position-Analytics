from flask import Flask, render_template, request
import pandas as pd
import sqlite3

app = Flask(__name__)

def get_db_data(db_name = 'basketball.db'):
    # Connect to your database file
    conn = sqlite3.connect(db_name) 

    query = "SELECT * FROM nba_players"
    df = pd.read_sql_query(query, conn)
    
    conn.close()
    return df

df = get_db_data()

@app.route('/')
def home():
    filtered_df = df.copy()
    players_list = filtered_df.to_dict(orient='records')
    return render_template('home.html', players=players_list)

@app.route('/players')
def players():
    search = request.args.get('search', '').lower()
    position = request.args.get('position', '')

    filtered_df = df.copy()

    if search:
        filtered_df = filtered_df[filtered_df['player_name'].str.lower().str.contains(search)]
    
    if position:
        filtered_df = filtered_df[filtered_df['position'] == position]

    players_list = filtered_df.to_dict(orient='records')
    return render_template('players.html', players=players_list)

@app.route('/analytics', methods=['GET', 'POST'])
def analytics():
    # Provide players for the select dropdown
    players_list = df.to_dict(orient='records')

    if request.method == 'POST':
        # grab the numbers table (input comes in as strings)
        try:
            minutes = float(request.form.get('minutes', 36))
            user_stats = {
                'fg_pct': float(request.form.get('fg_pct', 0)),
                'three_p_pct': float(request.form.get('three_p_pct', 0)),
                'pts': float(request.form.get('pts', 0)),
                'ast': float(request.form.get('ast', 0)),
                'trb': float(request.form.get('trb', 0)),
                'stl': float(request.form.get('stl', 0)),
                'blk': float(request.form.get('blk', 0)),
                'tov': float(request.form.get('tov', 0)),
                'pf': float(request.form.get('pf', 0)),
                'minutes': minutes,
                'fg_attempts': float(request.form.get('fg_attempts', 15)),
                'ft_attempts': float(request.form.get('ft_attempts', 5))
            }

            # optional compare player selected by name
            compare_name = request.form.get('compare_player', '')
            compare_player = None
            if compare_name:
                matched = df[df['player_name'] == compare_name]
                if not matched.empty:
                    compare_player = matched.iloc[0].to_dict()

            return render_template('results.html', stats=user_stats, compare_player=compare_player)

        except ValueError:
            return "Please enter valid numbers in all fields."

    return render_template('analytics.html', players=players_list)

if __name__ == '__main__':
    app.run(debug=True)

