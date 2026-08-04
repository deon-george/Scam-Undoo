from pathlib import Path
import pickle

import numpy as np
import pandas as pd
import xgboost as xgb

from data_prep import MERGED_DATASET, build_merged_dataset
from domain_age import DomainAgeService
from features import FEATURE_NAMES, extract_features
from tld_reputation import (
    TLD_REPUTATION_JSON,
    TldReputationRepository,
    build_tld_reputation,
    save_tld_reputation,
)


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / 'model.pkl'
MODEL_FEATURES_PATH = BASE_DIR / 'model_features.json'


def build_feature_matrix(url_series, age_service, tld_repo):
    feature_rows = [
        extract_features(url, age_service=age_service, tld_repo=tld_repo)[0]
        for url in url_series
    ]
    return np.asarray(feature_rows, dtype=float)


def main():
    merged_dataset = build_merged_dataset(save_to_disk=True)

    reputation, global_rate = build_tld_reputation(merged_dataset)
    save_tld_reputation(reputation, global_rate)
    tld_repo = TldReputationRepository()
    print(f'TLD reputation saved to {TLD_REPUTATION_JSON.name} '
          f'({len(reputation)} TLDs, global phishing rate {global_rate:.4f})')

    phishing_frame = merged_dataset[merged_dataset['label'] == 1].copy()
    legitimate_frame = merged_dataset[merged_dataset['label'] == 0].copy()

    sample_size = min(len(phishing_frame), len(legitimate_frame))
    phishing_sample = phishing_frame
    legitimate_sample = legitimate_frame.sample(n=sample_size, random_state=42)

    training_frame = pd.concat([phishing_sample, legitimate_sample], ignore_index=True)
    training_frame = training_frame.sample(frac=1.0, random_state=42).reset_index(drop=True)

    age_service = DomainAgeService(live_fallback=False)
    X = build_feature_matrix(training_frame['url'], age_service, tld_repo)
    y = training_frame['label'].to_numpy(dtype=int)

    X_frame = pd.DataFrame(X, columns=FEATURE_NAMES)

    model = xgb.XGBClassifier(
        objective='binary:logistic',
        eval_metric='logloss',
        n_estimators=250,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_frame, y)

    with open(MODEL_PATH, 'wb') as file_handle:
        pickle.dump(model, file_handle)

    with open(MODEL_FEATURES_PATH, 'w', encoding='utf-8') as file_handle:
        file_handle.write('\n'.join(FEATURE_NAMES))

    print(f'Merged dataset saved to {MERGED_DATASET}')
    print(f'Training rows: {len(training_frame)}')
    print(f'Phishing rows used: {len(phishing_sample)}')
    print(f'Legitimate rows used: {len(legitimate_sample)}')
    print(f'Features ({len(FEATURE_NAMES)}): {", ".join(FEATURE_NAMES)}')
    print(f'Model trained and saved to {MODEL_PATH.name}')


if __name__ == '__main__':
    main()
