"""URL feature extraction reproducing the 111-feature phishing dataset schema.

The trained model is built on ``datasets/dataset_small.csv``, which contains
111 pre-extracted numeric features plus a binary ``phishing`` label. To serve
the model from a live URL (the ``/api/scan`` endpoint), we must reproduce those
same 111 features from a raw URL.

Lexical/structural features (URL, domain, directory, file, params) are computed
deterministically. Network/reputation features (age, ASN, DNS, TLS, redirects,
response time) are resolved at scan time via ``net_features`` and default to 0
on failure. The two external-only signals (Google index lookups, URL-shortener
status) are not computed and default to 0; they were never derivable from a
single URL without third-party APIs.

Feature order MUST match the dataset column order exactly.
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

import tldextract

from net_features import collect_network_features


# The 17 special characters that get per-section character counters. The order
# here matches the dataset column order (dot, hyphen, underline, slash, ...).
_SPECIAL_CHARS = [
    '.', '-', '_', '/', '?', '=', '@', '&', '!', ' ', '~', ',', '+', '*', '#',
    '$', '%',
]

_IPV4_RE = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
_IPV6_RE = re.compile(r'^[0-9a-fA-F:]+:[0-9a-fA-F:]*$')
_EMAIL_RE = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')

# Network features are best-effort; these signals require third-party APIs
# (search-index probing, shortener databases) and are not computed.
_EXTERNAL_DEFAULT_FEATURES = {
    'url_google_index': 0,
    'domain_google_index': 0,
    'url_shortened': 0,
}


FEATURE_NAMES = [
    'qty_dot_url', 'qty_hyphen_url', 'qty_underline_url', 'qty_slash_url',
    'qty_questionmark_url', 'qty_equal_url', 'qty_at_url', 'qty_and_url',
    'qty_exclamation_url', 'qty_space_url', 'qty_tilde_url', 'qty_comma_url',
    'qty_plus_url', 'qty_asterisk_url', 'qty_hashtag_url', 'qty_dollar_url',
    'qty_percent_url', 'qty_tld_url', 'length_url',
    'qty_dot_domain', 'qty_hyphen_domain', 'qty_underline_domain',
    'qty_slash_domain', 'qty_questionmark_domain', 'qty_equal_domain',
    'qty_at_domain', 'qty_and_domain', 'qty_exclamation_domain',
    'qty_space_domain', 'qty_tilde_domain', 'qty_comma_domain',
    'qty_plus_domain', 'qty_asterisk_domain', 'qty_hashtag_domain',
    'qty_dollar_domain', 'qty_percent_domain', 'qty_vowels_domain',
    'domain_length', 'domain_in_ip', 'server_client_domain',
    'qty_dot_directory', 'qty_hyphen_directory', 'qty_underline_directory',
    'qty_slash_directory', 'qty_questionmark_directory', 'qty_equal_directory',
    'qty_at_directory', 'qty_and_directory', 'qty_exclamation_directory',
    'qty_space_directory', 'qty_tilde_directory', 'qty_comma_directory',
    'qty_plus_directory', 'qty_asterisk_directory', 'qty_hashtag_directory',
    'qty_dollar_directory', 'qty_percent_directory', 'directory_length',
    'qty_dot_file', 'qty_hyphen_file', 'qty_underline_file', 'qty_slash_file',
    'qty_questionmark_file', 'qty_equal_file', 'qty_at_file', 'qty_and_file',
    'qty_exclamation_file', 'qty_space_file', 'qty_tilde_file',
    'qty_comma_file', 'qty_plus_file', 'qty_asterisk_file', 'qty_hashtag_file',
    'qty_dollar_file', 'qty_percent_file', 'file_length',
    'qty_dot_params', 'qty_hyphen_params', 'qty_underline_params',
    'qty_slash_params', 'qty_questionmark_params', 'qty_equal_params',
    'qty_at_params', 'qty_and_params', 'qty_exclamation_params',
    'qty_space_params', 'qty_tilde_params', 'qty_comma_params',
    'qty_plus_params', 'qty_asterisk_params', 'qty_hashtag_params',
    'qty_dollar_params', 'qty_percent_params', 'params_length',
    'tld_present_params', 'qty_params', 'email_in_url',
    'time_response', 'domain_spf', 'asn_ip', 'time_domain_activation',
    'time_domain_expiration', 'qty_ip_resolved', 'qty_nameservers',
    'qty_mx_servers', 'ttl_hostname', 'tls_ssl_certificate', 'qty_redirects',
    'url_google_index', 'domain_google_index', 'url_shortened',
]

# SHAP explanations fall back to a title-cased feature name when absent.
FEATURE_META = {}


def _char_counts(text):
    return {ch: text.count(ch) for ch in _SPECIAL_CHARS}


def _is_ip(hostname):
    return bool(_IPV4_RE.match(hostname) or _IPV6_RE.match(hostname))


def _split_path(path):
    """Return (directory_str, file_str) for a URL path.

    A trailing slash or empty path yields an empty file string. A path with no
    intermediate directories yields an empty directory string.
    """
    segments = path.split('/')
    # Drop leading empty segment produced by the leading '/'.
    while segments and segments[0] == '':
        segments.pop(0)
    if not segments:
        return '', ''
    file_str = segments[-1]
    directory_str = '/'.join(segments[:-1])
    return directory_str, file_str


def extract_features(url, compute_network=True):
    """Extract the 111-feature vector for a URL.

    Returns ``(feature_vector, feature_dict)`` where ``feature_vector`` follows
    the ``FEATURE_NAMES`` ordering.
    """
    raw = str(url).strip()
    if '://' not in raw:
        raw = f'https://{raw}'

    parsed = urlparse(raw)
    hostname = (parsed.hostname or '').lower()
    path = parsed.path or ''
    query = parsed.query or ''

    # --- Domain decomposition ------------------------------------------------
    if _is_ip(hostname):
        domain_str = hostname
        tld = ''
        domain_in_ip = 1
    else:
        extracted = tldextract.extract(hostname)
        domain_str = extracted.registered_domain or hostname
        tld = (extracted.suffix or '').lower()
        domain_in_ip = 0

    directory_str, file_str = _split_path(path)

    # --- URL section ---------------------------------------------------------
    url_counts = _char_counts(raw)
    features = {
        'qty_dot_url': url_counts['.'],
        'qty_hyphen_url': url_counts['-'],
        'qty_underline_url': url_counts['_'],
        'qty_slash_url': url_counts['/'],
        'qty_questionmark_url': url_counts['?'],
        'qty_equal_url': url_counts['='],
        'qty_at_url': url_counts['@'],
        'qty_and_url': url_counts['&'],
        'qty_exclamation_url': url_counts['!'],
        'qty_space_url': url_counts[' '],
        'qty_tilde_url': url_counts['~'],
        'qty_comma_url': url_counts[','],
        'qty_plus_url': url_counts['+'],
        'qty_asterisk_url': url_counts['*'],
        'qty_hashtag_url': url_counts['#'],
        'qty_dollar_url': url_counts['$'],
        'qty_percent_url': url_counts['%'],
        'qty_tld_url': len(tld),
        'length_url': len(raw),
    }

    # --- Domain section ------------------------------------------------------
    domain_counts = _char_counts(domain_str)
    vowels = sum(1 for ch in domain_str if ch in 'aeiouAEIOU')
    features.update({
        'qty_dot_domain': domain_counts['.'],
        'qty_hyphen_domain': domain_counts['-'],
        'qty_underline_domain': domain_counts['_'],
        'qty_slash_domain': domain_counts['/'],
        'qty_questionmark_domain': domain_counts['?'],
        'qty_equal_domain': domain_counts['='],
        'qty_at_domain': domain_counts['@'],
        'qty_and_domain': domain_counts['&'],
        'qty_exclamation_domain': domain_counts['!'],
        'qty_space_domain': domain_counts[' '],
        'qty_tilde_domain': domain_counts['~'],
        'qty_comma_domain': domain_counts[','],
        'qty_plus_domain': domain_counts['+'],
        'qty_asterisk_domain': domain_counts['*'],
        'qty_hashtag_domain': domain_counts['#'],
        'qty_dollar_domain': domain_counts['$'],
        'qty_percent_domain': domain_counts['%'],
        'qty_vowels_domain': vowels,
        'domain_length': len(domain_str),
        'domain_in_ip': domain_in_ip,
        'server_client_domain': (
            1 if ('server' in domain_str or 'client' in domain_str) else 0
        ),
    })

    # --- Directory section ---------------------------------------------------
    if directory_str:
        dir_counts = _char_counts(directory_str)
        features.update({
            'qty_dot_directory': dir_counts['.'],
            'qty_hyphen_directory': dir_counts['-'],
            'qty_underline_directory': dir_counts['_'],
            'qty_slash_directory': dir_counts['/'],
            'qty_questionmark_directory': dir_counts['?'],
            'qty_equal_directory': dir_counts['='],
            'qty_at_directory': dir_counts['@'],
            'qty_and_directory': dir_counts['&'],
            'qty_exclamation_directory': dir_counts['!'],
            'qty_space_directory': dir_counts[' '],
            'qty_tilde_directory': dir_counts['~'],
            'qty_comma_directory': dir_counts[','],
            'qty_plus_directory': dir_counts['+'],
            'qty_asterisk_directory': dir_counts['*'],
            'qty_hashtag_directory': dir_counts['#'],
            'qty_dollar_directory': dir_counts['$'],
            'qty_percent_directory': dir_counts['%'],
            'directory_length': len(directory_str),
        })
    else:
        for key in (
            'qty_dot_directory', 'qty_hyphen_directory', 'qty_underline_directory',
            'qty_slash_directory', 'qty_questionmark_directory', 'qty_equal_directory',
            'qty_at_directory', 'qty_and_directory', 'qty_exclamation_directory',
            'qty_space_directory', 'qty_tilde_directory', 'qty_comma_directory',
            'qty_plus_directory', 'qty_asterisk_directory', 'qty_hashtag_directory',
            'qty_dollar_directory', 'qty_percent_directory', 'directory_length',
        ):
            features[key] = -1

    # --- File section --------------------------------------------------------
    if file_str:
        file_counts = _char_counts(file_str)
        features.update({
            'qty_dot_file': file_counts['.'],
            'qty_hyphen_file': file_counts['-'],
            'qty_underline_file': file_counts['_'],
            'qty_slash_file': file_counts['/'],
            'qty_questionmark_file': file_counts['?'],
            'qty_equal_file': file_counts['='],
            'qty_at_file': file_counts['@'],
            'qty_and_file': file_counts['&'],
            'qty_exclamation_file': file_counts['!'],
            'qty_space_file': file_counts[' '],
            'qty_tilde_file': file_counts['~'],
            'qty_comma_file': file_counts[','],
            'qty_plus_file': file_counts['+'],
            'qty_asterisk_file': file_counts['*'],
            'qty_hashtag_file': file_counts['#'],
            'qty_dollar_file': file_counts['$'],
            'qty_percent_file': file_counts['%'],
            'file_length': len(file_str),
        })
    else:
        for key in (
            'qty_dot_file', 'qty_hyphen_file', 'qty_underline_file', 'qty_slash_file',
            'qty_questionmark_file', 'qty_equal_file', 'qty_at_file', 'qty_and_file',
            'qty_exclamation_file', 'qty_space_file', 'qty_tilde_file',
            'qty_comma_file', 'qty_plus_file', 'qty_asterisk_file', 'qty_hashtag_file',
            'qty_dollar_file', 'qty_percent_file', 'file_length',
        ):
            features[key] = -1

    # --- Params section ------------------------------------------------------
    if query:
        param_counts = _char_counts(query)
        features.update({
            'qty_dot_params': param_counts['.'],
            'qty_hyphen_params': param_counts['-'],
            'qty_underline_params': param_counts['_'],
            'qty_slash_params': param_counts['/'],
            'qty_questionmark_params': param_counts['?'],
            'qty_equal_params': param_counts['='],
            'qty_at_params': param_counts['@'],
            'qty_and_params': param_counts['&'],
            'qty_exclamation_params': param_counts['!'],
            'qty_space_params': param_counts[' '],
            'qty_tilde_params': param_counts['~'],
            'qty_comma_params': param_counts[','],
            'qty_plus_params': param_counts['+'],
            'qty_asterisk_params': param_counts['*'],
            'qty_hashtag_params': param_counts['#'],
            'qty_dollar_params': param_counts['$'],
            'qty_percent_params': param_counts['%'],
            'params_length': len(query),
            'tld_present_params': (
                1 if re.search(r'[A-Za-z0-9.-]+\.[A-Za-z]{2,24}', query) else 0
            ),
            'qty_params': query.count('&') + 1,
        })
    else:
        for key in (
            'qty_dot_params', 'qty_hyphen_params', 'qty_underline_params',
            'qty_slash_params', 'qty_questionmark_params', 'qty_equal_params',
            'qty_at_params', 'qty_and_params', 'qty_exclamation_params',
            'qty_space_params', 'qty_tilde_params', 'qty_comma_params',
            'qty_plus_params', 'qty_asterisk_params', 'qty_hashtag_params',
            'qty_dollar_params', 'qty_percent_params', 'params_length',
            'tld_present_params', 'qty_params',
        ):
            features[key] = -1

    # --- Email in URL --------------------------------------------------------
    features['email_in_url'] = 1 if _EMAIL_RE.search(raw) else 0

    # --- Network / reputation features --------------------------------------
    if compute_network:
        features.update(collect_network_features(raw))
    else:
        features.update({
            'time_response': 0.0,
            'domain_spf': 0,
            'asn_ip': 0,
            'time_domain_activation': 0,
            'time_domain_expiration': 0,
            'qty_ip_resolved': 0,
            'qty_nameservers': 0,
            'qty_mx_servers': 0,
            'ttl_hostname': 0,
            'tls_ssl_certificate': 0,
            'qty_redirects': 0,
        })

    # --- External-only signals (not derivable from a single URL) ------------
    features.update(_EXTERNAL_DEFAULT_FEATURES)

    feature_vector = [features[name] for name in FEATURE_NAMES]
    return feature_vector, features
