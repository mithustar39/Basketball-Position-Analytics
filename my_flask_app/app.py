from flask import Flask, render_template, request, session
import pandas as pd
import sqlite3
import os
import logging
from datetime import timedelta

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
app.permanent_session_lifetime = timedelta(hours=1)

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, '..'))


def resolve_db_path():
    candidate_paths = [
        os.path.join(PROJECT_ROOT, 'basketball.db'),
        os.path.join(APP_DIR, 'basketball.db'),
    ]

    for candidate_path in candidate_paths:
        if os.path.exists(candidate_path):
            return candidate_path

    return candidate_paths[0]


def get_db_data(db_name=resolve_db_path()):
    try:
        conn = sqlite3.connect(db_name)
        query = "SELECT * FROM nba_players"
        data_frame = pd.read_sql_query(query, conn)
        conn.close()
        app.logger.info('Loaded %s players from %s', len(data_frame), db_name)
        return data_frame
    except Exception:
        app.logger.exception('Failed to load database from %s', db_name)
        return pd.DataFrame(columns=['player_name', 'position', 'fg_pct', 'three_p_pct', 'pts', 'ast', 'trb', 'stl', 'blk', 'tov', 'pf', 'mins_played', 'fg_attempts', 'ft_attempts'])


df = get_db_data()


@app.route('/health')
def health():
    return {
        'status': 'ok',
        'players_loaded': int(len(df)),
        'db_path': resolve_db_path(),
    }, 200

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

    if search and 'player_name' in filtered_df.columns:
        name_series = filtered_df['player_name'].fillna('').astype(str).str.lower()
        filtered_df = filtered_df[name_series.str.contains(search, na=False)]
    
    if position and 'position' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['position'].fillna('').astype(str) == position]

    players_list = filtered_df.to_dict(orient='records')
    return render_template('players.html', players=players_list)

@app.route('/analytics', methods=['GET', 'POST'])
def analytics():
    session.permanent = True
    # Provide players for the select dropdown
    players_list = df.to_dict(orient='records')

    # Retrieve saved stats from session
    saved_stats = session.get('user_stats', {})
    saved_compare_player = session.get('compare_player_name', '')

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

            # Save stats to session
            session['user_stats'] = user_stats

            # optional compare player selected by name
            compare_name = request.form.get('compare_player', '')
            session['compare_player_name'] = compare_name
            compare_player = None
            if compare_name and 'player_name' in df.columns:
                matched = df[df['player_name'].fillna('').astype(str) == compare_name]
                if not matched.empty:
                    compare_player = matched.iloc[0].to_dict()

            return render_template('results.html', stats=user_stats, compare_player=compare_player)

        except ValueError:
            return "Please enter valid numbers in all fields."

    return render_template('analytics.html', players=players_list, saved_stats=saved_stats, saved_compare_player=saved_compare_player)


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    app.logger.exception('Unhandled exception during request: %s', error)
    return 'Internal Server Error. Check Render logs for traceback.', 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)