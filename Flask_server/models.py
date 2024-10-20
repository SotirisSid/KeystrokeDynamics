from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # For keystroke_dynamics.db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Keystroke(db.Model):
    __tablename__ = 'keystrokes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    press_press_intervals = db.Column(db.String, nullable=True)
    release_press_intervals = db.Column(db.String, nullable=True)
    hold_times = db.Column(db.String, nullable=True)  # New column for hold times
    total_typing_time = db.Column(db.Float, nullable=True)
    typing_speed = db.Column(db.Float, nullable=True)
    backspace_count = db.Column(db.Integer, nullable=True)
    error_rate = db.Column(db.Float, nullable=True)
    press_to_release_ratio_mean = db.Column(db.Float)

class PreprocessedKeystrokeData(db.Model):
    __tablename__ = 'preprocessed_keystroke_data'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, primary_key=True)
    press_press_interval_mean = db.Column(db.Float, nullable=False)
    release_interval_mean = db.Column(db.Float, nullable=False)
    hold_time_mean = db.Column(db.Float, nullable=False, default=0.0)  # New column for hold time mean
    press_press_interval_variance = db.Column(db.Float, nullable=False)
    release_interval_variance = db.Column(db.Float, nullable=False)
    hold_time_variance = db.Column(db.Float, nullable=False, default=0.0)  # New column for hold time variance
    backspace_count = db.Column(db.Integer, nullable=False)
    error_rate = db.Column(db.Float, nullable=False)
    total_typing_time = db.Column(db.Float, nullable=False)  # Added to store total typing time
    typing_speed_cps = db.Column(db.Float, nullable=False)  # Added to store typing speed
