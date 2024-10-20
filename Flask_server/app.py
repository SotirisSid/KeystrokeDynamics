import os
from flask import Flask
from config import Config
from models import db
from routes.logout import logout_bp
from routes.auth import auth_bp
from routes.registration import registration_bp 
from routes.ml_models import ml_models_bp
from routes.keystroke_route import preprocess_bp
from routes.train_keystroke import train_keystroke_bp
app = Flask(__name__)
app.config.from_object(Config)
if not os.path.exists('instance/keystroke_dynamics.db'):
    print("Database not found! Please ensure the database file exists in the instance folder.")
db.init_app(app)
app.register_blueprint(logout_bp, url_prefix='/auth') # Register logout route
app.register_blueprint(preprocess_bp) # preprocess routes
app.register_blueprint(auth_bp) # Register authentication route
app.register_blueprint(registration_bp) # Register registration route
app.register_blueprint(ml_models_bp) # Register machine learning model training route   
app.register_blueprint(train_keystroke_bp) # Register data gathering route

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')