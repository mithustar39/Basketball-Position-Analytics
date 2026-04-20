from flask import Flask, render_template, request, session
import pandas as pd
import sqlite3
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.permanent_session_lifetime = timedelta(days=365)

def get_db_data(db_name = 'basketball.db'):
    # Connect to your database file
    conn = sqlite3.connect(db_name) 

    query = "SELECT * FROM nba_players"
    df = pd.read_sql_query(query, conn)
    
    conn.close()
    return df

df = get_db_data()

STAT_FIELDS = [
    {'key': 'fg_pct', 'label': 'Field Goal %', 'is_percent': True, 'default': '0.450', 'tip': 'Enter as decimal (e.g. 0.455)'},
    {'key': 'three_p_pct', 'label': '3-Point %', 'is_percent': True, 'default': '0.350', 'tip': 'Enter as decimal (e.g. 0.320)'},
    {'key': 'pts', 'label': 'Points (PPG)', 'is_percent': False, 'default': '15.0', 'tip': 'Average points per game'},
    {'key': 'ast', 'label': 'Assists', 'is_percent': False, 'default': '4.0', 'tip': 'Total assists per game'},
    {'key': 'trb', 'label': 'Rebounds', 'is_percent': False, 'default': '5.0', 'tip': 'Total rebounds per game'},
    {'key': 'stl', 'label': 'Steals', 'is_percent': False, 'default': '1.2', 'tip': 'Aggressive defense tracking'},
    {'key': 'blk', 'label': 'Blocks', 'is_percent': False, 'default': '0.5', 'tip': 'Rim protection tracking'},
    {'key': 'tov', 'label': 'Turnovers', 'is_percent': False, 'default': '2.0', 'tip': 'Ball security (lower is better)'},
    {'key': 'pf', 'label': 'Fouls', 'is_percent': False, 'default': '2.5', 'tip': 'Personal fouls per game'},
    {'key': 'minutes', 'label': 'Minutes Played (per game)', 'is_percent': False, 'default': '36', 'tip': 'Your average minutes per game'},
    {'key': 'fg_attempts', 'label': 'Field Goal Attempts (per game)', 'is_percent': False, 'default': '15', 'tip': 'Your FGA per game'},
    {'key': 'ft_attempts', 'label': 'Free Throw Attempts (per game)', 'is_percent': False, 'default': '5', 'tip': 'Your FTA per game'},
]


def format_stat_value(key, value):
    if value is None:
        return 'No input provided'

    if key in {'fg_pct', 'three_p_pct'}:
        return f'{value * 100:.1f}%'

    return f'{value:.1f}'

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
    session.permanent = True
    # Provide players for the select dropdown
    players_list = df.to_dict(orient='records')

    # Retrieve saved stats from session
    saved_stat_inputs = session.get('stat_inputs', {})
    saved_compare_player = session.get('compare_player_name', '')
    saved_selected_stats = session.get('selected_stats', [field['key'] for field in STAT_FIELDS])

    if request.method == 'POST':
        selected_stats = request.form.getlist('selected_stats')
        session['selected_stats'] = selected_stats

        compare_name = request.form.get('compare_player', '').strip()
        session['compare_player_name'] = compare_name

        stat_inputs = {}
        selected_rows = []
        missing_rows = []

        try:
            compare_player = None
            if compare_name:
                matched = df[df['player_name'] == compare_name]
                if not matched.empty:
                    compare_player = matched.iloc[0].to_dict()

            for field in STAT_FIELDS:
                raw_value = request.form.get(field['key'], '').strip()
                stat_inputs[field['key']] = raw_value

                if raw_value == '':
                    missing_rows.append({
                        'key': field['key'],
                        'label': field['label'],
                        'reason': 'No input provided',
                    })
                    continue

                value = float(raw_value)
                row = {
                    'key': field['key'],
                    'label': field['label'],
                    'value': value,
                    'user_display': format_stat_value(field['key'], value),
                    'selected': field['key'] in selected_stats,
                }

                if compare_player is not None:
                    compare_value = compare_player.get(field['key'])
                    row['compare_value'] = compare_value
                    row['compare_display'] = format_stat_value(field['key'], compare_value)

                if field['key'] in selected_stats:
                    selected_rows.append(row)
                else:
                    missing_rows.append({
                        'key': field['key'],
                        'label': field['label'],
                        'reason': 'Not selected',
                    })

            session['stat_inputs'] = stat_inputs

            return render_template(
                'results.html',
                selected_rows=selected_rows,
                missing_rows=missing_rows,
                compare_player=compare_player,
                compare_player_name=compare_name,
            )

        except ValueError:
            return 'Please enter valid numbers for the stats you selected.'

    return render_template(
        'analytics.html',
        players=players_list,
        saved_stat_inputs=saved_stat_inputs,
        saved_compare_player=saved_compare_player,
        saved_selected_stats=saved_selected_stats,
        stat_fields=STAT_FIELDS,
    )

if __name__ == '__main__':
    app.run(debug=True)

