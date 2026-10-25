#!/usr/bin/env python3
"""Explicit cold capture + isolated restore comparison. Does NOT stop services or activate a restore.

Requires root, GNU tar and rsync. All application processes must already be stopped.
No probe can rule out all external writers: operator acknowledgement remains necessary.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import pwd
import subprocess
import time


def contained(a, b):
    return a == b or b in a.parents


def validate_paths(sources, out, verify):
    sources = [Path(s).resolve(strict=True) for s in sources]
    for s in sources:
        if not s.is_dir() or s == Path('/'):
            raise ValueError('Sources must be non-root directories')
    for i, s in enumerate(sources):
        for t in sources[i+1:]:
            if contained(s, t) or contained(t, s):
                raise ValueError('Overlapping source roots')
    out, verify = Path(out).resolve(), Path(verify).resolve()
    for p in (out, verify):
        if p.exists():
            raise ValueError('Destination must not exist')
        if any(contained(p, s) or contained(s, p) for s in sources):
            raise ValueError('Destination overlaps a source')
    if contained(out, verify) or contained(verify, out):
        raise ValueError('Backup and verification paths overlap')
    return sources, out, verify


def require_quiet(uid, ports):
    # Root enumeration, same network/PID namespace as fnOS is required.
    for p in Path('/proc').iterdir():
        if p.name.isdigit():
            try:
                if p.stat().st_uid == uid:
                    raise RuntimeError('Application process remains: PID '+p.name)
            except FileNotFoundError:
                continue
    for file in ('/proc/net/tcp', '/proc/net/tcp6'):
        for line in Path(file).read_text().splitlines()[1:]:
            f = line.split()
            if f[3] == '0A' and int(f[1].rsplit(':', 1)[1], 16) in ports:
                raise RuntimeError('A selected port is still listening')


def run_logged(argv, out, label):
    with (out/(label+'.stdout')).open('xb') as stdout, (out/(label+'.stderr')).open('xb') as stderr:
        r = subprocess.run(argv, stdout=stdout, stderr=stderr, check=False)
    if r.returncode or (out/(label+'.stderr')).stat().st_size:
        raise RuntimeError(label+' failed/warned; private logs retained')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', action='append', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--verify-dir', required=True)
    p.add_argument('--user', default='trim.openclaw')
    p.add_argument('--port', action='append', type=int, required=True)
    p.add_argument('--ack-all-writers-stopped', action='store_true')
    a = p.parse_args()
    if os.geteuid() != 0 or not a.ack_all_writers_stopped:
        p.error('root and --ack-all-writers-stopped required; see docs')
    uid = pwd.getpwnam(a.user).pw_uid
    if uid == 0 or any(not 1 <= x <= 65535 for x in a.port):
        p.error('Invalid application user/port')
    src, out, verify = validate_paths(a.source, a.out, a.verify_dir)
    # Sample twice, and again after capture/verification. This is observation,
    # not a global lock or proof that another UID cannot write these paths.
    require_quiet(uid, a.port)
    time.sleep(2)
    require_quiet(uid, a.port)
    os.umask(0o077)
    out.mkdir(mode=0o700)
    verify.mkdir(mode=0o700)
    archive = out/'cold.tar'
    run_logged(['tar', '--create', '--file', str(archive), '--acls', '--xattrs',
                '--numeric-owner', '--sparse', '--directory', '/', '--']+
               [str(s).lstrip('/') for s in src], out, 'create')
    require_quiet(uid, a.port)
    h = hashlib.sha256()
    with archive.open('rb') as f:
        for b in iter(lambda: f.read(8*1024*1024), b''):
            h.update(b)
    (out/'SHA256SUMS.txt').write_text(h.hexdigest()+'  cold.tar\n')
    # Only extract this locally created archive; never accept arbitrary tar here.
    run_logged(['tar', '--extract', '--file', str(archive), '--directory', str(verify),
                '--same-owner', '--same-permissions', '--numeric-owner',
                '--acls', '--xattrs', '--xattrs-include=*'], out, 'extract')
    for i, s in enumerate(src):
        dest = verify/str(s).lstrip('/')
        run_logged(['rsync', '-aHAXnc', '--numeric-ids', '--delete',
                    '--itemize-changes', '--', str(s)+'/', str(dest)+'/'], out, 'compare-'+str(i))
        if (out/('compare-'+str(i)+'.stdout')).stat().st_size:
            raise RuntimeError('Restore differs; inspect private comparison logs')
    require_quiet(uid, a.port)
    report = {'archive': str(archive), 'sha256': h.hexdigest(),
              'sources': [str(s) for s in src], 'verify_dir': str(verify),
              'verification_matches': True, 'production_restore_performed': False,
              'external_writers': 'operator_acknowledged_not_proven',
              'cross_source_hardlink_topology': 'not_compared'}
    (out/'receipt.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
