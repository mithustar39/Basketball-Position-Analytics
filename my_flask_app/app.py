from pathlib import Path

from flask import Flask, render_template, request
import pandas as pd
import sqlite3

app = Flask(__name__)

# db file form 
DB_PATH = Path(__file__).resolve().parent.parent / "basketball.db"


def get_db_data(db_path: Path = DB_PATH):
    conn = sqlite3.connect(db_path)
    

    query = "SELECT * FROM nba_players"
    df = pd.read_sql_query(query, conn)
    
    conn.close()
    return df

df = get_db_data()

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

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/analytics', methods=['GET', 'POST'])
def analytics():
    if request.method == 'POST':
        # grab the numbers table
        # We use float() because the input comes in as a string
        try:
            user_stats = {
                'fg_pct': float(request.form.get('fg_pct', 0)),
                'three_p_pct': float(request.form.get('three_p_pct', 0)),
                'pts': float(request.form.get('pts', 0)),
                'ast': float(request.form.get('ast', 0)),
                'trb': float(request.form.get('trb', 0)),
                'stl': float(request.form.get('stl', 0)),
                'blk': float(request.form.get('blk', 0)),
                'tov': float(request.form.get('tov', 0)),
                'pf': float(request.form.get('pf', 0))
            }
            
            return render_template('results.html', stats=user_stats)
            
        except ValueError:
            return "Please enter valid numbers in all fields."

    return render_template('analytics.html')

if __name__ == '__main__':
    app.run(debug=True)

