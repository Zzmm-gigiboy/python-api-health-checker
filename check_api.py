"""HTTP smoke-test CLI with nonzero exit status and optional JSON report."""
import argparse
import json
import sys
from datetime import datetime, timezone
from urllib.error import URLError, HTTPError
from urllib.request import urlopen


def probe(base_url: str, timeout: float = 3.0) -> dict:
    url = base_url.rstrip('/') + '/health'
    report = {'endpoint': url, 'checked_at': datetime.now(timezone.utc).isoformat()}
    try:
        with urlopen(url, timeout=timeout) as res:
            data = json.loads(res.read().decode('utf-8'))
            report.update({
                'http_status': res.status,
                'healthy': res.status == 200 and isinstance(data, dict) and data.get('status') == 'ok',
            })
    except (URLError, HTTPError, OSError, json.JSONDecodeError, ValueError) as e:
        report.update({'healthy': False, 'error': str(e)})
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description='Smoke-check a REST API health endpoint')
    parser.add_argument('--url', required=True, help='API base URL, e.g. http://127.0.0.1:8000')
    parser.add_argument('--timeout', type=float, default=3)
    parser.add_argument('--out', help='Optional JSON report file')
    args = parser.parse_args(argv)
    if args.timeout <= 0: parser.error('--timeout must be positive')
    report = probe(args.url, args.timeout)
    rendered = json.dumps(report, indent=2)
    print(rendered)
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f: f.write(rendered + '\n')
    return 0 if report['healthy'] else 1


if __name__ == '__main__':
    sys.exit(main())
