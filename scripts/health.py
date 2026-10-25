#!/usr/bin/env python3
"""Observe a local embedding bridge; no model calls, credentials or restarts."""
import argparse
import json
import urllib.request


def probe(port):
    result = {'bridge_alive': False, 'upstream_embedding': 'not_tested',
              'restart_performed': False, 'model_request_performed': False}
    try:
        # Do not inherit an HTTP proxy for a loopback request.
        op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with op.open('http://127.0.0.1:%d/health' % port, timeout=5) as r:
            raw = r.read(65537)
            if len(raw) > 65536:
                raise ValueError('response too large')
            result['bridge_alive'] = r.status == 200 and json.loads(raw).get('status') == 'ok'
    except Exception as e:
        # Exception text may contain a server response: report only its class.
        result['error_type'] = type(e).__name__
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port', type=int, default=11434)
    a = p.parse_args()
    if not 1 <= a.port <= 65535:
        p.error('invalid port')
    result = probe(a.port)
    print(json.dumps(result))
    raise SystemExit(0 if result['bridge_alive'] else 1)
