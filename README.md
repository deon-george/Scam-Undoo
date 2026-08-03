# Scam Undoo

Scam Undoo is a full-stack URL phishing and scam detection project with a Python backend, an XGBoost-based classification model, and a React/Vite frontend. The app lets a user submit a URL, extracts simple lexical features from it, and returns a threat category with a confidence score.

## Overview

The project is split into two parts:

- `backend/` provides the Flask API, feature extraction logic, and model training script.
- `frontend/` provides the React user interface for entering a URL and viewing the scan result.

The current implementation classifies URLs into three labels:

- `Legitimate`
- `Medium Threat`
- `High Threat`

## Features

- Real-time URL scanning from a browser-based dashboard.
- Flask API with CORS enabled for frontend integration.
- XGBoost multi-class classifier for URL threat prediction.
- Feature-level transparency in the response so users can see what the model evaluated.
- Clean React/Vite UI with route-based navigation.

## Project Structure

```text
Scam Undoo/
├── backend/
│   ├── app.py
│   ├── features.py
│   ├── train_model.py
│   ├── requirements.txt
│   └── datasets/
│       ├── top-1m.csv
│       └── verified_online.csv
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       ├── index.css
│       └── components/
│           ├── Home.jsx
│           └── Dashboard.jsx
└── README.md
```

## How It Works

1. The user enters a URL in the frontend dashboard.
2. The frontend sends the URL to `POST /api/scan` on the Flask backend.
3. The backend extracts a small set of numeric features from the URL.
4. The trained XGBoost model predicts a probability distribution over the 3 classes.
5. The backend returns the predicted label, confidence, and extracted features.

## Machine Learning Architecture

### Model Type

The current model is an `XGBClassifier` from XGBoost.

### Training Approach

`backend/train_model.py` currently generates synthetic training data for three classes and fits the model on that data. It does not yet train on the CSV files in `backend/datasets/`.

### Model Configuration

- Estimator: `xgboost.XGBClassifier`
- Objective: `multi:softprob`
- Number of classes: `3`
- Evaluation metric: `mlogloss`

### Input Features

The model uses five URL-level features:

1. `url_length` - total character length of the URL.
2. `num_digits` - count of numeric characters in the URL.
3. `num_special_chars` - count of non-alphanumeric characters.
4. `has_ip` - whether the URL contains an IPv4 address.
5. `is_https` - whether the URL scheme is HTTPS.

### Class Definitions

The training script maps classes as follows:

- `0` - `Legitimate`
- `1` - `Medium Threat`
- `2` - `High Threat`

### Persistence

After training, the model is serialized to `model.pkl` with `pickle`.

Important: both `train_model.py` and `app.py` use a relative `model.pkl` path. For consistent behavior, run the training and API from the `backend/` directory so the model is saved and loaded from the same place.

## Backend Details

### Main Files

- `backend/app.py` - Flask application and API route.
- `backend/features.py` - URL feature extraction.
- `backend/train_model.py` - synthetic training data generation and model training.

### API Endpoint

#### `POST /api/scan`

Request body:

```json
{
  "url": "https://example.com"
}
```

Response:

```json
{
  "url": "https://example.com",
  "category": "Legitimate",
  "confidence": 0.98,
  "features": {
    "url_length": 19,
    "num_digits": 0,
    "num_special_chars": 3,
    "has_ip": 0,
    "is_https": 1
  }
}
```

If the model file is missing, the API returns a 500 error with the message:

- `Model not loaded. Please train the model first.`

If the request does not include a URL, the API returns a 400 error.

## Frontend Details

The frontend is a React app built with Vite.

### Routes

- `/` - landing page with project branding and navigation.
- `/dashboard` - scanner page where users submit URLs and view results.

### UI Behavior

- The dashboard calls the backend directly at `http://localhost:5000/api/scan`.
- The result card displays the predicted category, confidence score, and extracted features.
- The UI uses `lucide-react` icons for visual status indicators.

## Setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Train the model:

```bash
python train_model.py
```

Start the API:

```bash
python app.py
```

The Flask server runs on `http://localhost:5000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server will start locally, typically on `http://localhost:5173`.

## Dependencies

### Backend Python Packages

- Flask
- Flask-CORS
- xgboost
- scikit-learn
- pandas
- numpy
- tldextract

### Frontend Packages

- React
- React DOM
- React Router DOM
- lucide-react
- Vite

## Notes and Limitations

- The current model is a proof-of-concept and is trained on synthetic samples, so its predictions are not production-grade.
- The CSV files in `backend/datasets/` are present in the repository, but the current training script does not read them yet.
- The backend expects `model.pkl` to exist before scanning URLs.
- The feature set is intentionally small and only uses lexical URL properties, not page content or network reputation signals.

## Possible Next Improvements

- Replace synthetic training data with a real labeled phishing dataset.
- Add model evaluation metrics and a validation split.
- Persist model version metadata and training provenance.
- Expand feature extraction with domain age, TLD reputation, and URL token analysis.
- Add loading states and backend health checks in the frontend.

## License

No license file is currently included in the repository.