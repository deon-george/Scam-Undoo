"""Dataset loading and reference split for the pre-extracted phishing dataset.

The current dataset (``datasets/dataset_small.csv``) ships fully extracted
features: 111 numeric columns plus a binary ``phishing`` label (0 = legitimate,
1 = phishing). Training no longer canonicalizes raw URLs; it consumes the
pre-extracted columns directly.

Live inference (``features.py``) reproduces the same 111 features from a URL so
the trained model can be served through the API.
"""

from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / 'datasets'
DATASET = DATASET_DIR / 'dataset_small.csv'
LABEL_COLUMN = 'phishing'


def load_raw_dataset(path=DATASET):
    """Read the full pre-extracted dataset.

    Returns a DataFrame with all 111 feature columns plus the ``phishing``
    label column.
    """
    frame = pd.read_csv(path)
    if LABEL_COLUMN not in frame.columns:
        raise ValueError(
            f"Dataset {path} is missing the required '{LABEL_COLUMN}' label column."
        )
    return frame


def feature_columns(frame):
    """Return the sorted list of input feature column names (excluding label)."""
    return [col for col in frame.columns if col != LABEL_COLUMN]


def get_reference_split(path=DATASET, test_size=0.2, random_state=42):
    """Stratified 80/20 split of the dataset for reproducible evaluation.

    Returns ``(train_frame, eval_frame)`` where each frame contains all
    original columns (features + label). The split is stratified on the label
    so both folds keep the original class balance.
    """
    frame = load_raw_dataset(path)
    train_frame, eval_frame = train_test_split(
        frame,
        test_size=test_size,
        random_state=random_state,
        stratify=frame[LABEL_COLUMN],
    )
    return train_frame.reset_index(drop=True), eval_frame.reset_index(drop=True)
