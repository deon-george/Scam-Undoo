from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
import re

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / 'datasets'
PHISHING_DATASET = DATASET_DIR / 'verified_online.csv'
LEGITIMATE_DATASET = DATASET_DIR / 'top-1m.csv'
MERGED_DATASET = DATASET_DIR / 'merged_training_data.csv'

DOMAIN_PATTERN = re.compile(
    r'^(?=.{1,253}$)'
    r'([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+'
    r'[a-zA-Z]{2,63}$'
)
IPV4_PATTERN = re.compile(
    r'^(([01]?\d\d?|2[0-4]\d|25[0-5])\.){3}([01]?\d\d?|2[0-4]\d|25[0-5])$'
)


def _valid_netloc(netloc):
    if IPV4_PATTERN.match(netloc):
        return True
    return bool(DOMAIN_PATTERN.match(netloc))


def canonicalize_url(url):
    value = str(url).strip()
    if not value:
        return None

    if '://' not in value:
        value = f'https://{value}'

    parsed = urlsplit(value)
    scheme = parsed.scheme.lower() or 'https'
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip('/')
    query = parsed.query

    if not netloc or not _valid_netloc(netloc):
        return None

    return urlunsplit((scheme, netloc, path, query, ''))


def load_raw_url_sources():
    phishing_frame = pd.read_csv(PHISHING_DATASET, usecols=['url']).copy()
    phishing_frame['url'] = phishing_frame['url'].astype(str).str.strip()
    phishing_frame['label'] = 1
    phishing_frame['source'] = 'phishing'

    legitimate_frame = pd.read_csv(
        LEGITIMATE_DATASET,
        header=None,
        names=['rank', 'domain'],
        usecols=['rank', 'domain'],
    ).copy()
    legitimate_frame['url'] = 'https://' + legitimate_frame['domain'].astype(str).str.strip()
    legitimate_frame['label'] = 0
    legitimate_frame['source'] = 'legitimate'
    legitimate_frame = legitimate_frame[['url', 'label', 'source']]

    return phishing_frame[['url', 'label', 'source']], legitimate_frame


def build_merged_dataset(save_to_disk=True):
    phishing_frame, legitimate_frame = load_raw_url_sources()
    merged_frame = pd.concat([phishing_frame, legitimate_frame], ignore_index=True)
    merged_frame['canonical_url'] = merged_frame['url'].map(canonicalize_url)
    merged_frame = merged_frame.dropna(subset=['canonical_url']).copy()

    merged_frame['source_priority'] = merged_frame['label'].map({1: 0, 0: 1})
    merged_frame = merged_frame.sort_values(
        by=['canonical_url', 'source_priority'],
        ascending=[True, True],
        kind='mergesort',
    )

    merged_frame = merged_frame.drop_duplicates(subset=['canonical_url'], keep='first')
    merged_frame = merged_frame.drop(columns=['source_priority'])
    merged_frame = merged_frame[['url', 'canonical_url', 'label', 'source']].reset_index(drop=True)

    if save_to_disk:
        MERGED_DATASET.parent.mkdir(parents=True, exist_ok=True)
        merged_frame.to_csv(MERGED_DATASET, index=False)

    return merged_frame
