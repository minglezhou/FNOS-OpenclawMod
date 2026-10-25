#!/usr/bin/env python3
"""Download an exact OpenClaw npm release and verify SRI. Never install or execute it."""
import argparse
import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import urllib.parse
import urllib.request


def exact_version(value):
    if not re.fullmatch(r'\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?', value):
        raise ValueError('An exact numeric version is required; no latest/tags/ranges')
    return value


def check_url(url):
    p = urllib.parse.urlsplit(url)
    if (p.scheme != 'https' or p.hostname != 'registry.npmjs.org' or
            p.username or p.password or p.port not in (None, 443)):
        raise ValueError('Only the HTTPS npm registry origin is allowed')
    return url


class RegistryRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def sri_matches(path, integrity):
    tokens = integrity.split()
    # Prefer SHA-512; do not fall back to weaker algorithms on mismatch.
    candidates = [t for t in tokens if t.startswith('sha512-')]
    if not candidates:
        raise ValueError('No SHA-512 SRI in metadata')
    h = hashlib.sha512()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''):
            h.update(b)
    return any(hmac.compare_digest(h.digest(), base64.b64decode(t[7:], validate=True))
               for t in candidates)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--version', required=True, type=exact_version)
    p.add_argument('--out', required=True, type=Path, help='New private directory outside production')
    p.add_argument('--max-bytes', type=int, default=512*1024*1024)
    a = p.parse_args()
    if a.max_bytes <= 0:
        p.error('--max-bytes must be positive')
    os.umask(0o077)
    a.out.mkdir(mode=0o700, parents=False, exist_ok=False)
    op = urllib.request.build_opener(RegistryRedirect())
    url = check_url('https://registry.npmjs.org/openclaw/'+a.version)
    with op.open(url, timeout=30) as r:
        raw = r.read(4*1024*1024+1)
    if len(raw) > 4*1024*1024:
        raise ValueError('Metadata too large')
    meta = json.loads(raw)
    if meta.get('name') != 'openclaw' or meta.get('version') != a.version:
        raise ValueError('Unexpected package identity')
    dist = meta['dist']
    archive = a.out/('openclaw-'+a.version+'.tgz')
    total = 0
    with op.open(check_url(dist['tarball']), timeout=60) as r, archive.open('xb') as f:
        while True:
            chunk = r.read(1024*1024)
            if not chunk:
                break
            total += len(chunk)
            if total > a.max_bytes:
                raise ValueError('Download size limit exceeded; partial file retained')
            f.write(chunk)
    if not sri_matches(archive, dist['integrity']):
        raise ValueError('SRI mismatch; retained for investigation, DO NOT install')
    report = {'name': 'openclaw', 'version': a.version, 'bytes': total,
              'sri_matches': True, 'integrity': dist['integrity'],
              'engines': meta.get('engines', {}), 'archive': str(archive.resolve()),
              'lifecycle': {k: v for k, v in meta.get('scripts', {}).items()
                            if k in ('preinstall', 'install', 'postinstall')},
              'production_operations_performed': False}
    (a.out/'receipt.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
