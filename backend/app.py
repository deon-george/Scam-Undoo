from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import os
from domain_age import DomainAgeService
from explain import build_explanation
from features import FEATURE_NAMES, extract_features
from tld_reputation import TldReputationRepository

app = Flask(__name__)
CORS(app)

MODEL_PATH = Path(__file__).resolve().parent / 'model.pkl'

# Load model if exists, otherwise it will crash on scan but we assume train_model.py is run first
model = None
if MODEL_PATH.exists():
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)

age_service = DomainAgeService(live_fallback=True)
tld_repo = TldReputationRepository()

@app.route('/api/scan', methods=['POST'])
def scan_url():
    if not model:
        return jsonify({'error': 'Model not loaded. Please train the model first.'}), 500

    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # Extract features
    feature_vector, feature_dict = extract_features(
        url, age_service=age_service, tld_repo=tld_repo
    )

    if len(feature_vector) != len(FEATURE_NAMES):
        return jsonify({'error': 'Feature mismatch. Please retrain the model.'}), 500
    
    # Predict using XGBoost
    X_input = np.array([feature_vector])
    probabilities = model.predict_proba(X_input)[0]

    if len(probabilities) == 2:
        phishing_probability = float(probabilities[1])
        predicted_class = int(phishing_probability >= 0.5)
        category = 'High Threat' if predicted_class == 1 else 'Legitimate'
        confidence = phishing_probability if predicted_class == 1 else float(probabilities[0])
    else:
        predicted_class = int(np.argmax(probabilities))
        confidence = float(probabilities[predicted_class])

        categories = {
            0: 'Legitimate',
            1: 'Medium Threat',
            2: 'High Threat'
        }

        category = categories.get(predicted_class, 'Unknown')
    
    explanation = build_explanation(
        model, feature_vector, FEATURE_NAMES, category, confidence
    )

    return jsonify({
        'url': url,
        'category': category,
        'confidence': confidence,
        'features': feature_dict,
        'explanation': explanation,
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
