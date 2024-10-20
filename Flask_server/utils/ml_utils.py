import os
import pandas as pd
import numpy as np
from sqlalchemy.orm import sessionmaker
from models import db, PreprocessedKeystrokeData, User  # Import your models
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score
from sklearn.neural_network import MLPClassifier  # Importing MLPClassifier
import joblib  # Importing joblib for saving models
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

def train_model(preprocessed=True):
    # Create a session
    Session = sessionmaker(bind=db.engine)
    session = Session()

    try:
        if preprocessed:
            # Load preprocessed keystroke data, including new columns
            data = pd.read_sql('SELECT * FROM preprocessed_keystroke_data', session.bind)

            # Define expected columns for features
            expected_columns = [
                'press_press_interval_mean',
                'release_interval_mean',
                'hold_time_mean',
                'press_press_interval_variance',
                'release_interval_variance',
                'hold_time_variance',  # New column added
                'backspace_count',
                'error_rate',
                'total_typing_time',
                'typing_speed_cps'
            ]

            # Select features and target variable
            X = data[expected_columns]
            y = data['user_id']  # Assuming user_id is the target variable

            print("Shape of X:", X.shape)  # Check the shape of X

        else:
            # If not using preprocessed data, implement feature extraction here
            # (This branch may not be needed if you are solely using preprocessed data)
            pass

        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Scale the features and keep them as DataFrames with feature names
        scaler = StandardScaler()
        X_train_scaled_df = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)
        X_test_scaled_df = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)

        # Initialize models including the Neural Network
        models = {
            'Logistic Regression': make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight='balanced')),
            'Random Forest': RandomForestClassifier(n_estimators=100, class_weight='balanced'),
            'Support Vector Machine': SVC(class_weight='balanced'),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=100),
            'Neural Network': MLPClassifier(max_iter=1000)  # Added Neural Network
        }

        # Train and evaluate models
        results = {}
        for model_name, model in models.items():
            model.fit(X_train_scaled_df, y_train)  # Fit using DataFrame with feature names
            y_pred = model.predict(X_test_scaled_df)  # Predict using DataFrame
            accuracy = accuracy_score(y_test, y_pred)
            report = classification_report(y_test, y_pred, zero_division=0)  # Set zero_division to avoid warnings

            # Save the trained model to the "models" folder
            model_path = os.path.join('models', f'{model_name.replace(" ", "_").lower()}.joblib')
            joblib.dump(model, model_path)

            results[model_name] = {
                'accuracy': accuracy,
                'report': report
            }

        return results  # Return the results of the training
    finally:
        session.close()


