from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    stats = db.relationship('UserStats', back_populates='user', uselist=False)


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class UserStats(db.Model):
    __tablename__ = 'user_stats'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    fg_pct = db.Column(db.Float, default=0.0)
    three_p_pct = db.Column(db.Float, default=0.0)
    pts = db.Column(db.Float, default=0.0)
    ast = db.Column(db.Float, default=0.0)
    trb = db.Column(db.Float, default=0.0)
    stl = db.Column(db.Float, default=0.0)
    blk = db.Column(db.Float, default=0.0)
    tov = db.Column(db.Float, default=0.0)
    pf = db.Column(db.Float, default=0.0)
    minutes = db.Column(db.Float, default=36.0)
    fg_attempts = db.Column(db.Float, default=15.0)
    ft_attempts = db.Column(db.Float, default=5.0)
    compare_player = db.Column(db.String(100), default='')

    user = db.relationship("User", back_populates="stats", uselist=False)