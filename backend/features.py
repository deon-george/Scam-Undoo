import math
import re
from urllib.parse import urlparse

import tldextract

from domain_age import DomainAgeService
from tld_reputation import TldReputationRepository


FEATURE_NAMES = [
    'url_length',
    'num_digits',
    'num_special_chars',
    'has_ip',
    'is_https',
    'domain_age_days',
    'tld_reputation',
    'num_subdomains',
    'hostname_length',
    'hostname_has_hyphen',
    'hostname_entropy',
    'hostname_digit_ratio',
    'num_path_tokens',
    'longest_path_token_length',
    'suspicious_keyword_count',
    'brand_keyword_count',
    'suspicious_file_extension',
]

FEATURE_META = {
    'url_length': {
        'label': 'URL Length',
        'description': 'Total number of characters in the URL. Longer URLs are more commonly used to disguise phishing links.',
    },
    'num_digits': {
        'label': 'Number of Digits',
        'description': 'Count of numeric characters in the URL. Digits are often added to imitate brands or random IDs.',
    },
    'num_special_chars': {
        'label': 'Special Characters',
        'description': 'Count of non-alphanumeric characters. Excessive special characters can obfuscate the real destination.',
    },
    'has_ip': {
        'label': 'IP Address Host',
        'description': 'Whether the host is a raw IPv4 address instead of a domain name, a common phishing pattern.',
    },
    'is_https': {
        'label': 'Uses HTTPS',
        'description': 'Whether the URL uses a secure connection. HTTPS alone does not guarantee a site is safe.',
    },
    'domain_age_days': {
        'label': 'Domain Age (Days)',
        'description': 'Age of the domain in days. Very young domains are far more likely to be used for scams.',
    },
    'tld_reputation': {
        'label': 'TLD Reputation',
        'description': 'Historical phishing rate of the top-level domain. Higher values indicate a riskier TLD.',
    },
    'num_subdomains': {
        'label': 'Number of Subdomains',
        'description': 'How many subdomain levels are prepended. Many subdomains can hide the real destination.',
    },
    'hostname_length': {
        'label': 'Hostname Length',
        'description': 'Length of the hostname. Long hostnames are often used to mimic legitimate brands.',
    },
    'hostname_has_hyphen': {
        'label': 'Hostname Has Hyphen',
        'description': 'Whether the hostname contains a hyphen, a common trick used to imitate brand names.',
    },
    'hostname_entropy': {
        'label': 'Hostname Entropy',
        'description': 'Randomness of the hostname characters. High entropy suggests a randomly generated domain.',
    },
    'hostname_digit_ratio': {
        'label': 'Hostname Digit Ratio',
        'description': 'Proportion of digits in the hostname. Digits in hostnames can signal generated addresses.',
    },
    'num_path_tokens': {
        'label': 'Path Tokens',
        'description': 'Number of meaningful segments in the URL path. Deep paths are sometimes used to confuse users.',
    },
    'longest_path_token_length': {
        'label': 'Longest Path Token',
        'description': 'Length of the longest segment in the URL path.',
    },
    'suspicious_keyword_count': {
        'label': 'Suspicious Keywords',
        'description': 'How many scam-related words (login, verify, secure, prize, etc.) appear in the URL.',
    },
    'brand_keyword_count': {
        'label': 'Brand Keywords',
        'description': 'How many trusted brand names appear while not being the real domain, a classic impersonation signal.',
    },
    'suspicious_file_extension': {
        'label': 'Suspicious File Extension',
        'description': 'Whether the URL points to a risky file type such as .exe, .zip, .apk, or .php.',
    },
}

IP_PATTERN = re.compile(
    r'(([01]?\d\d?|2[0-4]\d|25[0-5])\.){3}([01]?\d\d?|2[0-4]\d|25[0-5])'
)

SUSPICIOUS_KEYWORDS = [
    'login', 'signin', 'sign-in', 'verify', 'verification', 'secure',
    'security', 'account', 'update', 'confirm', 'unlock', 'alert',
    'suspend', 'billing', 'invoice', 'payment', 'webscr', 'recover',
    'password', 'credential', 'wallet', 'bonus', 'gift', 'prize',
    'winner', 'claim', 'free', 'click', 'track', 'redirect', 'auth',
    'token', 'refund', 'support', 'customer', 'service', 'official',
    'webmail', 'logon', 'session', 'case', 'dispatch', 'parcel',
]

BRAND_KEYWORDS = [
    'paypal', 'amazon', 'apple', 'google', 'microsoft', 'outlook',
    'office365', 'facebook', 'instagram', 'whatsapp', 'netflix',
    'wellsfargo', 'chase', 'bankofamerica', 'citibank', 'hsbc',
    'barclays', 'allegro', 'ebay', 'linkedin', 'dropbox', 'adobe',
    'dhl', 'fedex', 'usps', 'payoneer', 'coinbase', 'binance',
    'blockchain', 'steam', 'icloud', 'yahoo', 'santander', 'ing',
    'rabobank', 'postbank',
]

SUSPICIOUS_FILE_EXTENSIONS = [
    '.exe', '.zip', '.apk', '.scr', '.bat', '.jar', '.rar', '.msi',
    '.js', '.php',
]


def _entropy(text):
    if not text:
        return 0.0
    length = len(text)
    counts = {}
    for char in text.lower():
        counts[char] = counts.get(char, 0) + 1
    return -sum(
        (count / length) * math.log2(count / length) for count in counts.values()
    )


def _extract_registered_domain(parsed):
    hostname = parsed.hostname or ''
    extracted = tldextract.extract(hostname)
    domain = extracted.registered_domain or ''
    if '.' not in domain and extracted.domain:
        domain = f'{extracted.domain}.{extracted.suffix}'
    return domain, (extracted.suffix or '').lower(), extracted.subdomain or ''


def extract_features(url, age_service=None, tld_repo=None):
    """
    Extract lexical features from a URL, augmented with network/reputation
    signals (domain age and TLD reputation) when the corresponding services
    are provided.

    Returns (feature_vector, feature_dict) where feature_vector follows
    FEATURE_NAMES ordering.
    """
    parsed = urlparse(url)
    hostname = parsed.hostname or ''
    path = parsed.path or ''
    query = parsed.query or ''

    registered_domain, tld, subdomain = _extract_registered_domain(parsed)

    if age_service is None:
        age_service = DomainAgeService(live_fallback=False)
    if tld_repo is None:
        tld_repo = TldReputationRepository()

    hostname_tokens = [tok for tok in re.split(r'[._\-]+', hostname) if tok]
    path_tokens = [tok for tok in re.split(r'[^a-zA-Z0-9]+', path) if tok]
    longest_path_token = max((len(tok) for tok in path_tokens), default=0)

    hostname_digits = sum(char.isdigit() for char in hostname)
    hostname_has_hyphen = 1 if '-' in hostname else 0

    combined_tokens = hostname_tokens + path_tokens + [tok for tok in query.split('&') if tok]
    combined_text = ' '.join(combined_tokens).lower()

    suspicious_keyword_count = sum(
        1 for keyword in SUSPICIOUS_KEYWORDS if keyword in combined_text
    )

    brand_text = ' '.join(hostname_tokens + path_tokens + [query.lower()])
    brand_keyword_count = sum(
        1
        for brand in BRAND_KEYWORDS
        if brand in brand_text
        and not (
            registered_domain == brand
            or registered_domain.startswith(brand + '.')
        )
    )

    lower_path = path.lower()
    suspicious_file_extension = 1 if any(
        ext in lower_path for ext in SUSPICIOUS_FILE_EXTENSIONS
    ) else 0

    feature_dict = {
        'url_length': len(url),
        'num_digits': sum(char.isdigit() for char in url),
        'num_special_chars': len(re.findall(r'[^a-zA-Z0-9]', url)),
        'has_ip': 1 if IP_PATTERN.search(url) else 0,
        'is_https': 1 if parsed.scheme == 'https' else 0,
        'domain_age_days': round(age_service.age_days(registered_domain), 2),
        'tld_reputation': round(tld_repo.score(tld), 4),
        'num_subdomains': len([part for part in subdomain.split('.') if part]),
        'hostname_length': len(hostname),
        'hostname_has_hyphen': hostname_has_hyphen,
        'hostname_entropy': round(_entropy(hostname), 4),
        'hostname_digit_ratio': round(hostname_digits / len(hostname), 4) if hostname else 0.0,
        'num_path_tokens': len(path_tokens),
        'longest_path_token_length': longest_path_token,
        'suspicious_keyword_count': suspicious_keyword_count,
        'brand_keyword_count': brand_keyword_count,
        'suspicious_file_extension': suspicious_file_extension,
    }

    feature_vector = [feature_dict[name] for name in FEATURE_NAMES]
    return feature_vector, feature_dict
