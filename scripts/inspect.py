#!/usr/bin/env python3
"""Read-only fnOS inventory. Does not run OpenClaw, read secrets, or stop services."""
import argparse
import json
import os
import pwd
from pathlib import Path


def file_info(path):
    p = Path(path)
    try:
        st = p.stat()
        return {'path': str(p), 'resolved': str(p.resolve(strict=True)),
                'dev': st.st_dev, 'ino': st.st_ino, 'uid': st.st_uid,
                'gid': st.st_gid, 'mode': oct(st.st_mode & 0o7777)}
    except OSError as e:
        return {'path': str(p), 'errno': e.errno}


def package_summary(path):
    try:
        d = json.loads(Path(path).read_text())
        return {'name': d.get('name'), 'version': d.get('version'),
                'engines': d.get('engines'),
                'openclaw_dependency': d.get('dependencies', {}).get('openclaw'),
                'openclaw_trusted': 'openclaw' in d.get('trustedDependencies', [])}
    except (OSError, ValueError, TypeError) as e:
        return {'error_type': type(e).__name__}


def processes(uid):
    result, errors = [], []
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():
            continue
        try:
            if p.stat().st_uid != uid:
                continue
            result.append({'pid': int(p.name), 'comm': (p/'comm').read_text().strip(),
                           'exe': os.readlink(p/'exe'), 'cwd': os.readlink(p/'cwd')})
        except OSError as e:
            errors.append({'pid': int(p.name), 'errno': e.errno})
    return {'processes': result, 'errors': errors, 'stop_verified': False}


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--app', default='trim.openclaw')
    a.add_argument('--user', default='trim.openclaw')
    a.add_argument('--data-root', type=Path)
    args = a.parse_args()
    # Derive through fnOS links; never assume vol3 on another machine.
    platform = Path('/var/apps') / args.app
    data = args.data_root or platform/'home/data'
    state = data/'home/.openclaw'
    paths = [platform/'cmd/main', platform/'target/server/index.js',
             platform/'target/bin/openclaw', data, data/'openclaw', state,
             state/'tools/cli-node/tools/node/bin/node',
             Path('/var/apps/bunjs/target/bin/bun'),
             Path('/var/apps/nodejs_v24/target/bin/node')]
    report = {'read_only': True, 'paths': [file_info(p) for p in paths],
              'project_package': package_summary(data/'openclaw/package.json'),
              'core_package': package_summary(data/'openclaw/node_modules/openclaw/package.json')}
    try:
        report['runtime'] = processes(pwd.getpwnam(args.user).pw_uid)
    except KeyError:
        report['runtime'] = {'error': 'application user not found'}
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
