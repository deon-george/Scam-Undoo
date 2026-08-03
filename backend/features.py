import re
from urllib.parse import urlparse

def extract_features(url):
    """
    Extract simple numerical features from a URL.
    """
    parsed = urlparse(url)
    
    # Feature 1: URL Length
    url_length = len(url)
    
    # Feature 2: Number of digits in URL
    num_digits = sum(c.isdigit() for c in url)
    
    # Feature 3: Number of special characters in URL
    num_special_chars = len(re.findall(r'[^a-zA-Z0-9]', url))
    
    # Feature 4: Contains IP address (often suspicious)
    ip_pattern = re.compile(
        r'(([01]?\d\d?|2[0-4]\d|25[0-5])\.){3}([01]?\d\d?|2[0-4]\d|25[0-5])'
    )
    has_ip = 1 if ip_pattern.search(url) else 0
    
    # Feature 5: Is HTTPS
    is_https = 1 if parsed.scheme == 'https' else 0
    
    return [url_length, num_digits, num_special_chars, has_ip, is_https], {
        'url_length': url_length,
        'num_digits': num_digits,
        'num_special_chars': num_special_chars,
        'has_ip': has_ip,
        'is_https': is_https
    }
