from flask import Blueprint, request, jsonify
from utils.ml_utils import train_model

##this script is used to train the machine learning model by calling the train_model function

ml_models_bp = Blueprint('ml_models', __name__)

@ml_models_bp.route('/train_model', methods=['POST'])
def train_ml_model():
    try:
        model = train_model()
        return jsonify({'message': 'Model trained successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
