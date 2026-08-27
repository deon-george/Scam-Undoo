# Scam Undoo

Scam Undoo is a full-stack URL phishing and scam detection project with a Python backend, an XGBoost classification model, and a React/Vite frontend. The app lets a user submit a URL, extracts lexical and reputation features, and returns a threat category, confidence score, and feature explanation.

## Overview

The project is split into two parts:

- `backend/` provides the Flask API, feature extraction logic, and model training script.
- `frontend/` provides the React user interface for entering a URL and viewing the scan result.

The current implementation classifies URLs into two labels:

- `Legitimate`
- `High Threat`

## Features

- Real-time URL scanning from a browser-based dashboard.
- Flask API with CORS enabled for frontend integration.
- XGBoost binary classifier for URL threat prediction.
- Feature-level transparency in the response so users can see what the model evaluated.
- Clean React/Vite UI with route-based navigation.

## Project Structure

```text
Scam Undoo/
├── backend/
│   ├── app.py
│   ├── data_prep.py
│   ├── domain_age.py
│   ├── explain.py
│   ├── features.py
│   ├── tld_reputation.py
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
3. The backend extracts 17 numeric features from the URL.
4. The trained XGBoost model predicts the probability of phishing.
5. The backend returns the predicted label, confidence, extracted features, and SHAP-based explanation.

## Machine Learning Architecture

### Model Type

The current model is an `XGBClassifier` from XGBoost.

### Training Approach

`backend/train_model.py` builds a merged dataset from the phishing URLs in `verified_online.csv` and the legitimate domains in `top-1m.csv`. Duplicate canonical URLs are removed, the legitimate class is downsampled to balance the phishing class, and the model is trained with `objective='binary:logistic'`.

### Model Configuration

- Estimator: `xgboost.XGBClassifier`
- Objective: `binary:logistic`
- Number of classes: `2`
- Evaluation metric: `logloss`

### Input Features

The model uses these 17 features, in the order defined by `FEATURE_NAMES` in `backend/features.py`:

1. `url_length` - total character length of the URL.
2. `num_digits` - count of numeric characters in the URL.
3. `num_special_chars` - count of non-alphanumeric characters.
4. `has_ip` - whether the URL contains an IPv4 address.
5. `is_https` - whether the URL scheme is HTTPS.
6. `domain_age_days` - age of the registered domain in days.
7. `tld_reputation` - historical phishing rate for the top-level domain.
8. `num_subdomains` - number of subdomain levels.
9. `hostname_length` - hostname character length.
10. `hostname_has_hyphen` - whether the hostname contains a hyphen.
11. `hostname_entropy` - Shannon entropy of the hostname.
12. `hostname_digit_ratio` - proportion of hostname characters that are digits.
13. `num_path_tokens` - number of non-empty path tokens.
14. `longest_path_token_length` - length of the longest path token.
15. `suspicious_keyword_count` - count of scam-related keywords in URL text.
16. `brand_keyword_count` - count of brand names used outside their registered domain.
17. `suspicious_file_extension` - whether the path contains a configured risky extension.

### Persistence

After training, the model is serialized to `model.pkl` with `pickle`.

The model and supporting JSON files are resolved relative to the `backend/` directory, so the commands can be run from that directory as shown below.

## Backend Details

### Main Files

- `backend/app.py` - Flask application and API route.
- `backend/features.py` - URL feature extraction.
- `backend/train_model.py` - dataset preparation and model training.
- `backend/data_prep.py` - URL canonicalization, deduplication, and label preparation.
- `backend/domain_age.py` - domain-age lookup and cache handling.
- `backend/tld_reputation.py` - TLD reputation calculation and lookup.
- `backend/explain.py` - model feature explanation generation.

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
    "is_https": 1,
    "domain_age_days": 3650.0
  },
  "explanation": []
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

## Generated and Optional Files

The following files or directories are generated, local-only, or training-only and can be removed from a runtime-only checkout:

- `backend/venv/`, `frontend/node_modules/`, `backend/__pycache__/`, and `frontend/dist/` - recreate them from the dependency files or build commands.
- `backend/datasets/merged_training_data.csv` - generated by `data_prep.py`; it is not required by the running API.
- `backend/datasets/top-1m.csv` and `backend/datasets/verified_online.csv` - required only when retraining the model.
- `backend/model_features.json` - training metadata; useful for auditing, but the API currently imports `FEATURE_NAMES` directly.
- `frontend/public/Code-black.png` - appears unused; the UI references `Code-black.svg`.

Keep `backend/model.pkl`, `backend/domain_age_cache.json`, and `backend/tld_reputation.json` for the current runtime. The datasets should be retained when model retraining is part of the workflow.

`frontend/index.html` also contains a leftover `/vite.svg` favicon reference, but that asset is not present. It can be removed or replaced with an existing favicon.

## Notes and Limitations

- The model is a proof-of-concept and should be evaluated with a held-out dataset before production use.
- Domain age may use cached values during training and live WHOIS fallback during API inference.
- The backend expects `model.pkl` to exist before scanning URLs.
- The model does not inspect page content. Domain age and TLD reputation are the only non-lexical signals currently used.

## Possible Next Improvements

- Add model evaluation metrics and a validation split.
- Persist model version metadata and training provenance.
- Add automated checks that the serialized model feature order matches `FEATURE_NAMES`.
- Add loading states and backend health checks in the frontend.

