from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
try:
    from .models import db, User, UserStats
except ImportError:
    from models import db, User, UserStats
import pandas as pd
import sqlite3
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # Change this in production!
app.permanent_session_lifetime = timedelta(hours=1)

# ── SQLAlchemy config (stores users in a separate users.db) ──────────────────
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# ── Flask-Login setup ────────────────────────────────────────────────────────
login_manager = LoginManager(app)
login_manager.login_view = 'login'          # redirect here if not authenticated
login_manager.login_message = 'Please log in to access the Analytics page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ── Create tables on first run ───────────────────────────────────────────────
with app.app_context():
    db.create_all()

# ── NBA data ─────────────────────────────────────────────────────────────────
def get_db_data(db_name='basketball.db'):
    conn = sqlite3.connect(db_name)
    query = "SELECT * FROM nba_players"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

df = get_db_data()


def _get_first_present(row_dict, keys, default=None):
    """Return the first non-null value found for any key in keys."""
    for key in keys:
        if key in row_dict:
            value = row_dict.get(key)
            if value is not None and not pd.isna(value):
                return value
    return default


def _as_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_compare_player(player_row):
    """Map raw DB/CSV columns to stable keys used by templates and charts."""
    return {
        'player_name': str(_get_first_present(player_row, ['player_name', 'Player'], 'Unknown Player')),
        'fg_pct': _as_float(_get_first_present(player_row, ['fg_pct', 'FG%', 'Field Goal Percentage'], 0.0)),
        'three_p_pct': _as_float(_get_first_present(player_row, ['three_p_pct', '3P%', 'Three Point Percentage'], 0.0)),
        'stl': _as_float(_get_first_present(player_row, ['stl', 'STL'], 0.0)),
        'blk': _as_float(_get_first_present(player_row, ['blk', 'BLK'], 0.0)),
        'tov': _as_float(_get_first_present(player_row, ['tov', 'TOV'], 0.0)),
        'pf': _as_float(_get_first_present(player_row, ['pf', 'PF'], 0.0)),
        'pts': _as_float(_get_first_present(player_row, ['pts', 'PTS', 'Points'], 0.0)),
        'ast': _as_float(_get_first_present(player_row, ['ast', 'AST'], 0.0)),
        'trb': _as_float(_get_first_present(player_row, ['trb', 'TRB'], 0.0)),
        'mp': _as_float(_get_first_present(player_row, ['mp', 'mins_played', 'MP', 'Mins Played'], 36.0), 36.0),
        'fg_attempts': _as_float(_get_first_present(player_row, ['fg_attempts', 'FGA', 'Field Goal Attempts'], 0.0)),
        'ft_attempts': _as_float(_get_first_present(player_row, ['ft_attempts', 'FTA', 'Free Throw Attempts'], 0.0)),
    }

# ── Public routes ─────────────────────────────────────────────────────────────
@app.route('/')
def home():
    players_list = df.to_dict(orient='records')
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

# ── Auth routes ───────────────────────────────────────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('analytics'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        if not username or not password:
            flash('Username and password are required.', 'error')
        elif len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
        elif password != confirm:
            flash('Passwords do not match.', 'error')
        elif User.query.filter_by(username=username).first():
            flash('Username already taken. Please choose another.', 'error')
        else:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Account created! You can now log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('analytics'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            # Redirect back to the page they originally tried to visit
            next_page = request.args.get('next')
            return redirect(next_page or url_for('analytics'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ── Protected route ───────────────────────────────────────────────────────────
@app.route('/analytics', methods=['GET', 'POST'])
@login_required
def analytics():
    players_list = df.to_dict(orient='records')

    # Load this user's saved stats from DB
    user_stats_row = UserStats.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        try:
            minutes = float(request.form.get('minutes', 36))
            user_stats = {
                'fg_pct':      float(request.form.get('fg_pct', 0)),
                'three_p_pct': float(request.form.get('three_p_pct', 0)),
                'pts':         float(request.form.get('pts', 0)),
                'ast':         float(request.form.get('ast', 0)),
                'trb':         float(request.form.get('trb', 0)),
                'stl':         float(request.form.get('stl', 0)),
                'blk':         float(request.form.get('blk', 0)),
                'tov':         float(request.form.get('tov', 0)),
                'pf':          float(request.form.get('pf', 0)),
                'minutes':     minutes,
                'fg_attempts': float(request.form.get('fg_attempts', 15)),
                'ft_attempts': float(request.form.get('ft_attempts', 5)),
            }
            compare_name = request.form.get('compare_player', '')

            # Save to DB — update if exists, create if not
            if user_stats_row:
                for key, val in user_stats.items():
                    setattr(user_stats_row, key, val)
                user_stats_row.compare_player = compare_name
            else:
                user_stats_row = UserStats(
                    user_id=current_user.id,
                    compare_player=compare_name,
                    **user_stats
                )
                db.session.add(user_stats_row)
            db.session.commit()

            compare_player = None
            if compare_name:
                matched = df[df['player_name'] == compare_name]
                if not matched.empty:
                    compare_player = normalize_compare_player(matched.iloc[0].to_dict())

            return render_template('results.html', stats=user_stats,
                                   compare_player=compare_player)

        except ValueError:
            return "Please enter valid numbers in all fields."

    # GET — load saved stats for this user's form
    saved_stats = {}
    saved_compare_player = ''
    if user_stats_row:
        saved_stats = {
            col: getattr(user_stats_row, col)
            for col in ['fg_pct', 'three_p_pct', 'pts', 'ast', 'trb',
                        'stl', 'blk', 'tov', 'pf', 'minutes',
                        'fg_attempts', 'ft_attempts']
        }
        saved_compare_player = user_stats_row.compare_player

    return render_template('analytics.html', players=players_list,
                           saved_stats=saved_stats,
                           saved_compare_player=saved_compare_player)

if __name__ == '__main__':
    app.run(debug=True)
