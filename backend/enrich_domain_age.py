import argparse
import re
import sys
import time

import pandas as pd
import tldextract

from data_prep import LEGITIMATE_DATASET, build_merged_dataset
from domain_age import DomainAgeService


DOMAIN_PATTERN = re.compile(
    r'^(?=.{1,253}$)'
    r'([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+'
    r'[a-zA-Z]{2,63}$'
)


def _registered_domain(url):
    extracted = tldextract.extract(url)
    domain = extracted.registered_domain or ''
    if '.' not in domain and extracted.domain:
        domain = f'{extracted.domain}.{extracted.suffix}'
    domain = domain.lower()
    if not DOMAIN_PATTERN.match(domain):
        return None
    return domain


def main():
    parser = argparse.ArgumentParser(
        description='Batch-enrich the domain age cache with WHOIS lookups.'
    )
    parser.add_argument(
        '--limit', type=int, default=None,
        help='Max number of unique domains to look up (useful for testing).',
    )
    parser.add_argument(
        '--delay', type=float, default=0.1,
        help='Seconds to sleep between WHOIS queries (default: 0.1).',
    )
    parser.add_argument(
        '--cache', default='domain_age_cache.json',
        help='Path to the domain age cache JSON file.',
    )
    parser.add_argument(
        '--seed-top', type=int, default=0,
        help='Enrich the top-N legit domains by rank first (e.g. 100 for '
             'major brands), then continue with the rest.',
    )
    parser.add_argument(
        '--resume', action='store_true',
        help='Keep existing cache entries instead of restarting from scratch.',
    )
    args = parser.parse_args()

    service = DomainAgeService(cache_path=args.cache, live_fallback=True)

    merged_dataset = build_merged_dataset(save_to_disk=True)
    domains = sorted({d for d in map(_registered_domain, merged_dataset['url']) if d})

    if args.seed_top > 0:
        top_frame = pd.read_csv(
            LEGITIMATE_DATASET,
            header=None,
            names=['rank', 'domain'],
            usecols=['rank', 'domain'],
            nrows=args.seed_top,
        )
        top_domains = sorted(
            {
                d
                for d in map(_registered_domain, 'https://' + top_frame['domain'].astype(str))
                if d
            }
        )
        domains = top_domains + [d for d in domains if d not in set(top_domains)]

    if args.resume:
        domains = [d for d in domains if d not in service._cache]

    if args.limit is not None:
        domains = domains[: args.limit]

    total = len(domains)
    print(f'Unique domains to enrich: {total}')
    print('Press Ctrl+C to interrupt; progress is saved after each lookup.')
    print()

    found = 0
    start = time.time()
    try:
        for index, domain in enumerate(domains, start=1):
            age_days = service.age_days(domain)
            if age_days is not None:
                found += 1
            service.save()
            elapsed = time.time() - start
            rate = index / elapsed if elapsed > 0 else 0.0
            eta = (total - index) / rate if rate > 0 else 0.0
            print(
                f'[{index}/{total}] {domain}: '
                f'{"%.1f days" % age_days if age_days is not None else "unknown"} '
                f'({rate:.1f}/s, ETA {eta / 60.0:.1f} min)'
            )
            time.sleep(args.delay)
    except KeyboardInterrupt:
        print('\nInterrupted; cache saved so far.')

    service.save()
    print(f'Done. Cached {found}/{total} domains with a known age.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
