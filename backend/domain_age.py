import json
import threading
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DOMAIN_AGE_CACHE = BASE_DIR / 'domain_age_cache.json'

UNKNOWN_AGE_FALLBACK_DAYS = 0.0


def _as_age_days(creation_date):
    if creation_date is None:
        return None

    if not isinstance(creation_date, (list, tuple)):
        creation_date = [creation_date]

    for candidate in creation_date:
        if isinstance(candidate, str):
            try:
                candidate = datetime.fromisoformat(candidate.replace('Z', '+00:00'))
            except ValueError:
                continue
        if not isinstance(candidate, datetime):
            continue
        if candidate.tzinfo is None:
            candidate = candidate.replace(tzinfo=timezone.utc)
        age_days = (datetime.now(timezone.utc) - candidate).total_seconds() / 86400.0
        return max(0.0, age_days)

    return None


class DomainAgeService:
    """Cache-backed WHOIS domain-age lookup.

    Cache entries map a registered domain to ``{"age_days": <float|null>}``.
    A ``null`` age means the WHOIS lookup was attempted but could not produce a
    creation date (or failed entirely); those entries are treated as unknown so
    they are not re-queried on every pass.
    """

    def __init__(self, cache_path=DOMAIN_AGE_CACHE, live_fallback=True, timeout=10.0):
        self.cache_path = Path(cache_path)
        self.live_fallback = live_fallback
        self.timeout = timeout
        self._cache = self._load()
        self._lock = threading.Lock()
        self._neutral_age = self._compute_neutral_age()

    def _load(self):
        if not self.cache_path.exists():
            return {}
        try:
            with open(self.cache_path, 'r', encoding='utf-8') as file_handle:
                return json.load(file_handle)
        except (ValueError, OSError):
            return {}

    def _compute_neutral_age(self):
        ages = [
            entry['age_days']
            for entry in self._cache.values()
            if isinstance(entry, dict) and isinstance(entry.get('age_days'), (int, float))
        ]
        if not ages:
            return UNKNOWN_AGE_FALLBACK_DAYS
        ages.sort()
        middle = len(ages) // 2
        if len(ages) % 2 == 0 and len(ages) > 1:
            return float((ages[middle - 1] + ages[middle]) / 2.0)
        return float(ages[middle])

    def save(self):
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.cache_path.with_suffix('.tmp')
        with open(tmp_path, 'w', encoding='utf-8') as file_handle:
            json.dump(self._cache, file_handle, indent=2)
        tmp_path.replace(self.cache_path)

    def age_days(self, domain):
        domain = (domain or '').strip().lower().lstrip('www.')
        if not domain:
            return self._neutral_age

        cached = self._cache.get(domain)
        if isinstance(cached, dict):
            if isinstance(cached.get('age_days'), (int, float)):
                return float(cached['age_days'])
            return self._neutral_age

        if not self.live_fallback:
            return self._neutral_age

        age_days = self._query(domain)
        with self._lock:
            self._cache[domain] = {'age_days': age_days}
        self.save()
        return age_days if age_days is not None else self._neutral_age

    def _query(self, domain):
        try:
            import socket
            socket.setdefaulttimeout(self.timeout)
            import whois
            record = whois.whois(domain)
        except Exception:
            return None

        try:
            return _as_age_days(record.creation_date)
        except Exception:
            return None
