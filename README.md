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
│   ├── explain.py
│   ├── features.py
│   ├── net_features.py
│   ├── train_model.py
│   ├── requirements.txt
│   └── datasets/
│       └── dataset_small.csv
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
3. The backend extracts 111 numeric features from the URL (lexical/structural features computed directly, plus best-effort network/reputation features resolved at scan time).
4. The trained XGBoost model predicts the probability of phishing.
5. The backend returns the predicted label, confidence, extracted features, and SHAP-based explanation.

## Machine Learning Architecture

### Model Type

The current model is an `XGBClassifier` from XGBoost.

### Training Approach

`backend/train_model.py` trains directly on the pre-extracted dataset in `datasets/dataset_small.csv`, which contains 111 numeric feature columns and a binary `phishing` label. The dataset is split into stratified train/eval folds (80/20), the `XGBClassifier` is fit on the training fold with `objective='binary:logistic'`, and out-of-sample accuracy/ROC-AUC are reported on the held-out fold.

- Estimator: `xgboost.XGBClassifier`
- Objective: `binary:logistic`
- Number of classes: `2`
- Evaluation metric: `logloss`

### Input Features

The model uses these features, in the order defined by `FEATURE_NAMES` in `backend/features.py`:

1. `qty_dot_url` - count (.) in URL
2. `qty_hyphen_url` - count (-) in URL
3. `qty_underline_url` - count (_) in URL
4. `qty_slash_url` - count (/) in URL
5. `qty_questionmark_url` - count (?) in URL
6. `qty_equal_url` - count (=) in URL
7. `qty_at_url` - count (@) in URL
8. `qty_and_url` - count (&) in URL
9. `qty_exclamation_url` - count (!) in URL
10. `qty_space_url` - count ( ) in URL
11. `qty_tilde_url` - count (~) in URL
12. `qty_comma_url` - count (,) in URL
13. `qty_plus_url` - count (+) in URL
14. `qty_asterisk_url` - count (*) in URL
15. `qty_hashtag_url` - count (#) in URL
16. `qty_dollar_url` - count ($) in URL
17. `qty_percent_url` - count (%) in URL
18. `qty_tld_url` - top-level-domain length
19. `length_url` - URL length
20. `qty_dot_domain` - count (.) in domain
21. `qty_hyphen_domain` - count (-) in domain
22. `qty_underline_domain` - count (_) in domain
23. `qty_slash_domain` - count (/) in domain
24. `qty_questionmark_domain` - count (?) in domain
25. `qty_equal_domain` - count (=) in domain
26. `qty_at_domain` - count (@) in domain
27. `qty_and_domain` - count (&) in domain
28. `qty_exclamation_domain` - count (!) in domain
29. `qty_space_domain` - count ( ) in domain
30. `qty_tilde_domain` - count (~) in domain
31. `qty_comma_domain` - count (,) in domain
32. `qty_plus_domain` - count (+) in domain
33. `qty_asterisk_domain` - count (*) in domain
34. `qty_hashtag_domain` - count (#) in domain
35. `qty_dollar_domain` - count ($) in domain
36. `qty_percent_domain` - count (%) in domain
37. `qty_vowels_domain` - count vowels in domain
38. `domain_length` - domain length
39. `domain_in_ip` - URL domain in IP address format
40. `server_client_domain` - domain contains the keywords "server" or "client"
41. `qty_dot_directory` - count (.) in directory
42. `qty_hyphen_directory` - count (-) in directory
43. `qty_underline_directory` - count (_) in directory
44. `qty_slash_directory` - count (/) in directory
45. `qty_questionmark_directory` - count (?) in directory
46. `qty_equal_directory` - count (=) in directory
47. `qty_at_directory` - count (@) in directory
48. `qty_and_directory` - count (&) in directory
49. `qty_exclamation_directory` - count (!) in directory
50. `qty_space_directory` - count ( ) in directory
51. `qty_tilde_directory` - count (~) in directory
52. `qty_comma_directory` - count (,) in directory
53. `qty_plus_directory` - count (+) in directory
54. `qty_asterisk_directory` - count (*) in directory
55. `qty_hashtag_directory` - count (#) in directory
56. `qty_dollar_directory` - count ($) in directory
57. `qty_percent_directory` - count (%) in directory
58. `directory_length` - directory length
59. `qty_dot_file` - count (.) in file
60. `qty_hyphen_file` - count (-) in file
61. `qty_underline_file` - count (_) in file
62. `qty_slash_file` - count (/) in file
63. `qty_questionmark_file` - count (?) in file
64. `qty_equal_file` - count (=) in file
65. `qty_at_file` - count (@) in file
66. `qty_and_file` - count (&) in file
67. `qty_exclamation_file` - count (!) in file
68. `qty_space_file` - count ( ) in file
69. `qty_tilde_file` - count (~) in file
70. `qty_comma_file` - count (,) in file
71. `qty_plus_file` - count (+) in file
72. `qty_asterisk_file` - count (*) in file
73. `qty_hashtag_file` - count (#) in file
74. `qty_dollar_file` - count ($) in file
75. `qty_percent_file` - count (%) in file
76. `file_length` - file length
77. `qty_dot_params` - count (.) in parameters
78. `qty_hyphen_params` - count (-) in parameters
79. `qty_underline_params` - count (_) in parameters
80. `qty_slash_params` - count (/) in parameters
81. `qty_questionmark_params` - count (?) in parameters
82. `qty_equal_params` - count (=) in parameters
83. `qty_at_params` - count (@) in parameters
84. `qty_and_params` - count (&) in parameters
85. `qty_exclamation_params` - count (!) in parameters
86. `qty_space_params` - count ( ) in parameters
87. `qty_tilde_params` - count (~) in parameters
88. `qty_comma_params` - count (,) in parameters
89. `qty_plus_params` - count (+) in parameters
90. `qty_asterisk_params` - count (*) in parameters
91. `qty_hashtag_params` - count (#) in parameters
92. `qty_dollar_params` - count ($) in parameters
93. `qty_percent_params` - count (%) in parameters
94. `params_length` - parameters length
95. `tld_present_params` - TLD presence in arguments
96. `qty_params` - number of parameters
97. `email_in_url` - email present in URL
98. `time_response` - search time (response) domain (lookup)
99. `domain_spf` - domain has SPF
100. `asn_ip` - AS Number (or ASN)
101. `time_domain_activation` - time (in days) of domain activation
102. `time_domain_expiration` - time (in days) of domain expiration
103. `qty_ip_resolved` - number of resolved IPs
104. `qty_nameservers` - number of resolved name servers (NameServers - NS)
105. `qty_mx_servers` - number of MX Servers
106. `ttl_hostname` - time-to-live (TTL) value associated with hostname
107. `tls_ssl_certificate` - valid TLS / SSL Certificate
108. `qty_redirects` - number of redirects
109. `url_google_index` - check if URL is indexed on Google
110. `domain_google_index` - check if domain is indexed on Google
111. `url_shortened` - check if URL is shortened

Target label:

`phishing` - is phishing website

### Persistence

After training, the model is serialized to `model.pkl` with `pickle`.

The model and supporting JSON files are resolved relative to the `backend/` directory, so the commands can be run from that directory as shown below.

## Backend Details

### Main Files

- `backend/app.py` - Flask application and API route.
- `backend/features.py` - URL feature extraction (111 features).
- `backend/net_features.py` - best-effort DNS/WHOIS/HTTP network feature lookups.
- `backend/train_model.py` - dataset loading and model training.
- `backend/data_prep.py` - pre-extracted dataset loading and train/eval split.
- `backend/explain.py` - model feature explanation generation.
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
    "qty_dot_url": 2,
    "length_url": 19,
    "domain_length": 11,
    "qty_vowels_domain": 4,
    "domain_in_ip": 0,
    "server_client_domain": 0,
    "qty_params": -1,
    "email_in_url": 0,
    "tls_ssl_certificate": 1,
    "url_shortened": 0
  },
  "explanation": []
}
```

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
- `backend/datasets/dataset_small.csv` - the pre-extracted training dataset; required when retraining the model.
- `backend/model_features.json` - training metadata; useful for auditing, but the API currently imports `FEATURE_NAMES` directly.
- `frontend/public/Code-black.png` - appears unused; the UI references `Code-black.svg`.

Keep `backend/model.pkl` for the current runtime. The dataset should be retained when model retraining is part of the workflow.

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

Made with ❤️ by Deon George in association with ASCEND organised by MUFIFA