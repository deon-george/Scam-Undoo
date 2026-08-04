import json
from pathlib import Path

import tldextract


BASE_DIR = Path(__file__).resolve().parent
TLD_REPUTATION_JSON = BASE_DIR / 'tld_reputation.json'

GLOBAL_PHISHING_RATE_FALLBACK = 0.5


def _tld_of(url):
    extracted = tldextract.extract(url)
    return (extracted.suffix or '').lower()


def build_tld_reputation(labeled_frame, min_observations=5):
    """Compute empirical phishing rate per TLD from labeled training data.

    Returns a dict of TLD -> phishing rate. TLDs with fewer than
    ``min_observations`` samples are excluded so a single malicious URL cannot
    paint an entire TLD; those fall back to the global phishing rate.
    """
    frame = labeled_frame[['url', 'label']].copy()
    frame['tld'] = frame['url'].map(_tld_of)
    frame = frame[frame['tld'] != '']

    stats = (
        frame.groupby('tld')['label']
        .agg(['mean', 'count'])
        .reset_index()
    )
    stats = stats[stats['count'] >= min_observations]

    reputation = dict(zip(stats['tld'], stats['mean']))
    return reputation, float(frame['label'].mean())


def save_tld_reputation(reputation, global_rate, path=TLD_REPUTATION_JSON):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        'global_phishing_rate': float(global_rate),
        'reputation': reputation,
    }
    with open(path, 'w', encoding='utf-8') as file_handle:
        json.dump(payload, file_handle, indent=2)


def load_tld_reputation(path=TLD_REPUTATION_JSON):
    path = Path(path)
    if not path.exists():
        return {}, GLOBAL_PHISHING_RATE_FALLBACK
    with open(path, 'r', encoding='utf-8') as file_handle:
        payload = json.load(file_handle)
    reputation = payload.get('reputation', {})
    global_rate = payload.get('global_phishing_rate', GLOBAL_PHISHING_RATE_FALLBACK)
    return reputation, float(global_rate)


class TldReputationRepository:
    def __init__(self, path=TLD_REPUTATION_JSON):
        self.reputation, self.global_rate = load_tld_reputation(path)

    def score(self, tld):
        tld = (tld or '').strip().lower()
        if tld in self.reputation:
            return float(self.reputation[tld])
        return self.global_rate
