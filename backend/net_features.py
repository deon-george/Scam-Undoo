"""Best-effort network/reputation feature lookups for live URL scanning.

These complement the purely lexical features computed in ``features.py``. Each
caller expects a numeric value that lines up with the pre-extracted dataset
encoding:

- ``time_response``: HTTP response time in seconds (0.0 if unreachable).
- ``domain_spf``: 1 if the domain publishes an SPF TXT record, else 0.
- ``asn_ip``: autonomous system number of the resolved host (0 if unknown).
- ``time_domain_activation``: days since domain creation (0 if unknown).
- ``time_domain_expiration``: days until domain expiry (0 if unknown).
- ``qty_ip_resolved``: count of A/AAAA records (0 if none).
- ``qty_nameservers``: count of NS records (0 if none).
- ``qty_mx_servers``: count of MX records (0 if none).
- ``ttl_hostname``: TTL of the A record in seconds (0 if unknown).
- ``tls_ssl_certificate``: 1 if a valid TLS handshake succeeds, else 0.
- ``qty_redirects``: number of HTTP redirects followed (0 if none/unreachable).

All functions are individually wrapped so a single failing lookup never breaks
the whole feature vector; they return safe defaults on error or timeout.
"""

from __future__ import annotations

import socket
import ssl
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

import dns.resolver
import tldextract
import whois


# DNS is network-bound; keep lookups fast so scanning stays responsive.
_RESOLVER_TIMEOUT = 4.0
_RESOLVER_LIFETIME = 6.0
_HTTP_TIMEOUT = 6.0


def _make_resolver():
    resolver = dns.resolver.Resolver()
    resolver.timeout = _RESOLVER_TIMEOUT
    resolver.lifetime = _RESOLVER_LIFETIME
    return resolver


def _host_from_url(url):
    host = urlparse(url).hostname
    if host:
        return host.lower().lstrip('.')
    return ''


def _registered_domain(url):
    """Bare registered domain (e.g. ``google.com``) for NS/MX/SPF/WHOIS.

    DNS records and WHOIS are registered at the domain (not the host), so
    querying ``www.google.com`` for NS/MX returns no answer.
    """
    host = _host_from_url(url)
    if not host:
        return ''
    extracted = tldextract.extract(host)
    return (extracted.registered_domain or host).lower()


def lookup_response_time(url):
    """Seconds elapsed for an HTTPS GET; 0.0 if the host is unreachable."""
    host = _host_from_url(url)
    if not host:
        return 0.0
    start = time.monotonic()
    try:
        import urllib.request

        request = urllib.request.Request(
            f'https://{host}',
            headers={'User-Agent': 'Mozilla/5.0 ScamUndooScanner/1.0'},
        )
        with urllib.request.urlopen(request, timeout=_HTTP_TIMEOUT):
            return round(time.monotonic() - start, 6)
    except Exception:
        return 0.0


def lookup_tls_certificate(url):
    """1 if a valid TLS handshake to the host succeeds, else 0."""
    host = _host_from_url(url)
    if not host:
        return 0
    context = ssl.create_default_context()
    try:
        with socket.create_connection((host, 443), timeout=_HTTP_TIMEOUT) as sock:
            with context.wrap_socket(sock, server_hostname=host):
                return 1
    except Exception:
        return 0


def lookup_redirects(url):
    """Count HTTP redirects followed to the final destination (0 if none)."""
    host = _host_from_url(url)
    if not host:
        return 0
    redirects = 0
    current = f'https://{host}'
    try:
        import urllib.request

        opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler())
        request = urllib.request.Request(
            current,
            headers={'User-Agent': 'Mozilla/5.0 ScamUndooScanner/1.0'},
        )
        response = opener.open(request, timeout=_HTTP_TIMEOUT)
        # opener follows redirects internally; compare final URL chain length.
        history = getattr(response, 'history', None)
        if history:
            redirects = len(history)
    except Exception:
        return 0
    return redirects


def lookup_spf(url):
    """1 if the domain publishes an SPF ``v=spf1`` TXT record, else 0."""
    domain = _registered_domain(url)
    if not domain:
        return 0
    try:
        resolver = _make_resolver()
        for record in resolver.resolve(domain, 'TXT'):
            text = record.to_text().strip('"')
            if text.lower().startswith('v=spf1'):
                return 1
    except Exception:
        return 0
    return 0


def _resolve_a(host, resolver):
    """Return (count, ttl, [ip,...]) for A/AAAA records."""
    ips = []
    ttl = 0
    for rtype in ('A', 'AAAA'):
        try:
            answer = resolver.resolve(host, rtype)
            ttl = int(getattr(answer, 'ttl', 0) or ttl)
            ips.extend(str(r.address) for r in answer)
        except Exception:
            continue
    return len(ips), ttl, ips


def lookup_ip_resolved(url):
    host = _host_from_url(url)
    if not host:
        return 0
    count, _, _ = _resolve_a(host, _make_resolver())
    return count


def lookup_ttl(url):
    host = _host_from_url(url)
    if not host:
        return 0
    _, ttl, _ = _resolve_a(host, _make_resolver())
    return ttl


def lookup_nameservers(url):
    domain = _registered_domain(url)
    if not domain:
        return 0
    try:
        answer = _make_resolver().resolve(domain, 'NS')
        return len(answer)
    except Exception:
        return 0


def lookup_mx(url):
    domain = _registered_domain(url)
    if not domain:
        return 0
    try:
        answer = _make_resolver().resolve(domain, 'MX')
        return len(answer)
    except Exception:
        return 0


def lookup_asn(url):
    """AS number of the resolved host via origin WHOIS; 0 if unknown."""
    host = _host_from_url(url)
    if not host:
        return 0
    _, _, ips = _resolve_a(host, _make_resolver())
    if not ips:
        try:
            ips = [socket.gethostbyname(host)]
        except Exception:
            return 0
    ip = ips[0]
    try:
        # Query the RIR origin database for the IP's routing origin.
        query = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        query.settimeout(_RESOLVER_LIFETIME)
        query.connect(('whois.cymru.com', 43))
        query.sendall(f'-r {ip}\n'.encode())
        data = b''
        while True:
            chunk = query.recv(4096)
            if not chunk:
                break
            data += chunk
        query.close()
        text = data.decode(errors='ignore').splitlines()
        if len(text) >= 2:
            # Format: "AS | IP | AS Name"
            asn = text[1].split('|')[0].strip()
            return int(asn) if asn.isdigit() else 0
    except Exception:
        return 0


def lookup_domain_age(url):
    """Return (activation_days, expiration_days); 0 if unknown."""
    domain = _registered_domain(url)
    if not domain:
        return 0, 0
    try:
        info = whois.whois(domain)
        creation = info.creation_date
        expiration = info.expiration_date
        now = datetime.now(timezone.utc)

        def _to_days(value):
            if not value:
                return 0
            if isinstance(value, list):
                value = value[0]
            if value.tzinfo is not None:
                value = value.astimezone(timezone.utc).replace(tzinfo=None)
            return max(0, (now.replace(tzinfo=None) - value).days)

        activation = _to_days(creation)
        expiration_days = _to_days(expiration)
        return activation, expiration_days
    except Exception:
        return 0, 0

def collect_network_features(url):
    """Compute every network-dependent feature for ``url``.

    Returns a dict keyed by the dataset feature name. Each value is computed
    independently and defaults to 0 on any failure, so partial network outages
    degrade gracefully rather than crashing the scan.
    """
    activation, expiration = lookup_domain_age(url)
    return {
        'time_response': lookup_response_time(url),
        'domain_spf': lookup_spf(url),
        'asn_ip': lookup_asn(url),
        'time_domain_activation': activation,
        'time_domain_expiration': expiration,
        'qty_ip_resolved': lookup_ip_resolved(url),
        'qty_nameservers': lookup_nameservers(url),
        'qty_mx_servers': lookup_mx(url),
        'ttl_hostname': lookup_ttl(url),
        'tls_ssl_certificate': lookup_tls_certificate(url),
        'qty_redirects': lookup_redirects(url),
    }
