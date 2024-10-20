from flask import Blueprint, request, jsonify
from flask import current_app
import jwt
import datetime
from werkzeug.security import check_password_hash
from utils.preprocess_keystrokes import process_single_keystroke_data  # Import the new function
from utils.evaluate_metrics import evaluate_model  # Import the evaluate_model function
from models import db, User, PreprocessedKeystrokeData
import os
import joblib  # Import joblib for loading models
import pandas as pd  # Import pandas
import globals
from utils.calculate_features import calculate_keystroke_features  # Import the feature calculation function

# This script is used to authenticate a user and generate a JWT token for the user
auth_bp = Blueprint('auth', __name__)

def generate_token(username):
    """
    Generate a JWT token for the authenticated user.
    """
    try:
        token = jwt.encode({
            'sub': username,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=10)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        return token
    except Exception as e:
        print(f"Error generating token: {e}")  # Log the error
        return None

@auth_bp.route('/authenticate', methods=['POST'])
def authenticate():
    try:
        # Retrieve the JSON data from the request
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Invalid JSON'}), 400

        # Extract required fields
        username = data.get('username')
        password = data.get('password')
        press_times = data.get('key_press_times', '')
        release_times = data.get('key_release_times', '')
        backspace_count = data.get('backspace_count', 0)
        error_rate = data.get('error_rate', 0.0)
        print(f"key_press_times: {press_times}")
        print(f"key_release_times: {release_times}")

        # Validate and process press_times and release_times
        if isinstance(press_times, str):
            press_times = [float(x) for x in press_times.split(',')]
        if isinstance(release_times, str):
            release_times = [float(x) for x in release_times.split(',')]

        if not isinstance(press_times, list) or not isinstance(release_times, list):
            return jsonify({'error': 'press_times and release_times must be lists'}), 400

        # Calculate keystroke features
        keystroke_features = calculate_keystroke_features(press_times, release_times)
        print("Keystroke features: " + str(keystroke_features))

        # Process the keystroke data
        processed_data = process_single_keystroke_data(
            username,
            keystroke_features['press_press_intervals'],
            keystroke_features['release_press_intervals'],
            keystroke_features['hold_times'],
            keystroke_features['total_typing_time'],
            keystroke_features['typing_speed_cps'],
            backspace_count,
            error_rate
        )

        if processed_data is None:
            return jsonify({'error': 'Error processing keystroke data.'}), 500

        # Prepare the feature vector for model prediction
        feature_vector = [
            processed_data['press_press_interval_mean'],
            processed_data['release_interval_mean'],
            processed_data['hold_time_mean'],
            processed_data['press_press_interval_variance'],
            processed_data['release_interval_variance'],
            processed_data['hold_time_variance'],
            processed_data['backspace_count'],
            processed_data['error_rate'],
            processed_data['total_typing_time'],
            processed_data['typing_speed_cps']
        ]
        print(f"Feature vector for prediction: {feature_vector}")

        # Find the user in the database
        user = User.query.filter_by(username=username).first()

        # Validate the user and password
        if user and check_password_hash(user.password, password):
            # Check if the user has enough preprocessed keystroke entries
            keystroke_count = PreprocessedKeystrokeData.query.filter_by(user_id=user.id).count()
            if keystroke_count < 10:
                token = generate_token(username)
                return jsonify({
                    'authenticated': True,
                    'token': token,
                    'predictions': ['No predictions yet. Train the model to add predictions.']
                }), 200

            # Increment the new_keystrokes counter
            globals.new_keystrokes += 1

            # Add the new keystroke data to the database
            new_entry = PreprocessedKeystrokeData(
                user_id=user.id,
                press_press_interval_mean=processed_data['press_press_interval_mean'],
                release_interval_mean=processed_data['release_interval_mean'],
                hold_time_mean=processed_data['hold_time_mean'],
                press_press_interval_variance=processed_data['press_press_interval_variance'],
                release_interval_variance=processed_data['release_interval_variance'],
                hold_time_variance=processed_data['hold_time_variance'],
                backspace_count=backspace_count,
                error_rate=error_rate,
                total_typing_time=processed_data['total_typing_time'],
                typing_speed_cps=processed_data['typing_speed_cps']
            )
            db.session.add(new_entry)
            db.session.commit()
            print("Data added to the database")

            # Generate the JWT token
            token = generate_token(username)
            print("Token: " + token)

            # Load the trained models from the "models" folder and make predictions
            model_names = [
                'logistic_regression.joblib',
                'random_forest.joblib',
                'support_vector_machine.joblib',
                'gradient_boosting.joblib',
                'neural_network.joblib'
            ]
            prediction_messages = []
            
            for model_name in model_names:
                model_path = os.path.join('models', model_name)
                model = joblib.load(model_path)  # Load the trained model

                # Create DataFrame for predictions
                df_features = pd.DataFrame([feature_vector], columns=[
                    'press_press_interval_mean', 'release_interval_mean',
                    'hold_time_mean', 'press_press_interval_variance', 
                 'release_interval_variance',
                    'hold_time_variance', 'backspace_count', 
                    'error_rate', 'total_typing_time', 'typing_speed_cps'
                ])

                prediction = model.predict(df_features)  # Make a prediction
                predicted_user_id = int(prediction[0])  # Assuming this returns the user ID
                print(f"Model: {model_name}, Prediction: {predicted_user_id}")

                # Check if the predicted user ID matches the authenticated user's ID
                if predicted_user_id == user.id:
                    message = f"{model_name.replace('.joblib', '')} predicts that you are the valid user."
                else:
                    message = f"{model_name.replace('.joblib', '')} predicts that you are an intruder."

                prediction_messages.append(message)
                print(prediction_messages)

            # Include predictions in the response
            return jsonify({
                'authenticated': True,
                'token': token,
                'predictions': prediction_messages  # Include model prediction messages in the response
            }), 200  # Return token on successful authentication
        else:
            return jsonify({'error': 'Authentication failed'}), 401

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500  # Return the actual error message in the response
