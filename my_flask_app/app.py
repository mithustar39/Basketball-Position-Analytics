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

@app.route('/stats')
def stats():
    return render_template('stats.html')

if __name__ == '__main__':
    app.run(debug=True)

