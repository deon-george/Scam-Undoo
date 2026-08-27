"""Train the XGBoost phishing classifier on the pre-extracted dataset.

The dataset (``datasets/dataset_small.csv``) contains 111 numeric features plus
a binary ``phishing`` label. We train an ``XGBClassifier`` on a stratified
train split and evaluate it on a held-out eval split so the console reports
real, out-of-sample performance (not just in-sample fit).
"""

from pathlib import Path

import json

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score

from data_prep import get_reference_split
from features import FEATURE_NAMES


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / 'model.json'
MODEL_FEATURES_PATH = BASE_DIR / 'model_features.json'


def main():
    train_frame, eval_frame = get_reference_split()

    missing = [name for name in FEATURE_NAMES if name not in train_frame.columns]
    if missing:
        raise ValueError(f'Dataset missing expected feature columns: {missing}')

    X_train = train_frame[FEATURE_NAMES].to_numpy(dtype=float)
    y_train = train_frame['phishing'].to_numpy(dtype=int)
    X_eval = eval_frame[FEATURE_NAMES].to_numpy(dtype=float)
    y_eval = eval_frame['phishing'].to_numpy(dtype=int)

    model = xgb.XGBClassifier(
        objective='binary:logistic',
        eval_metric='logloss',
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # --- Held-out evaluation -------------------------------------------------
    probabilities = model.predict_proba(X_eval)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    accuracy = accuracy_score(y_eval, predictions)
    auc = roc_auc_score(y_eval, probabilities)

    print('Training rows:        ', len(train_frame))
    print('Evaluation rows:      ', len(eval_frame))
    print('Features:             ', len(FEATURE_NAMES))
    print('Eval accuracy:        ', f'{accuracy:.4f}')
    print('Eval ROC-AUC:         ', f'{auc:.4f}')
    print(classification_report(y_eval, predictions, digits=4))

    model.save_model(MODEL_PATH)

    with open(MODEL_FEATURES_PATH, 'w', encoding='utf-8') as file_handle:
        json.dump(FEATURE_NAMES, file_handle, indent=2)
        file_handle.write('\n')

    print(f'Model trained and saved to {MODEL_PATH.name}')


if __name__ == '__main__':
    main()
