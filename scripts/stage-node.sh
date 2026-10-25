#!/usr/bin/env bash
# Download and unpack an explicitly selected official Node binary into a NEW directory.
# Does not change symlinks, wrapper, PATH, platform dependencies, or running processes.
set -euo pipefail
umask 077
if [[ $# != 4 ]]; then
  echo 'Usage: stage-node.sh VERSION ARCH EXPECTED_SHA256 NEW_DESTINATION' >&2
  echo 'Example VERSION=v24.19.0 ARCH=x64; obtain SHA from official verified SHASUMS.' >&2
  exit 2
fi
version=$1 arch=$2 digest=$3 dest=$4
[[ $(id -u) != 0 ]] || { echo 'Run as the application user, not root' >&2; exit 2; }
[[ $version =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ && ( $arch == x64 || $arch == arm64 ) && $digest =~ ^[0-9a-fA-F]{64}$ ]] || exit 2
[[ $dest == /* && ! -e $dest && ! -L $dest ]] || { echo 'New absolute destination required' >&2; exit 2; }
mkdir -m 700 -- "$dest"
name="node-$version-linux-$arch"
curl --fail --show-error --silent --location --proto '=https' --proto-redir '=https' \
  --connect-timeout 20 --max-time 900 "https://nodejs.org/dist/$version/$name.tar.xz" -o "$dest/node.tar.xz"
printf '%s  %s\n' "$digest" "$dest/node.tar.xz" | sha256sum -c -
python3 - "$dest/node.tar.xz" "$name" <<'PY'
import sys,tarfile,posixpath
with tarfile.open(sys.argv[1]) as t:
    members=t.getmembers(); names=set(); links=set()
    def safe(n):
        return not n.startswith('/') and '..' not in n.split('/') and n.split('/')[0]==sys.argv[2]
    for m in members:
        n=m.name.rstrip('/')
        if n in names or not safe(n) or not (m.isfile() or m.isdir() or m.issym() or m.islnk()):
            raise SystemExit('Unsafe/duplicate archive member')
        names.add(n)
        if m.issym() or m.islnk():
            if m.linkname.startswith('/'):
                raise SystemExit('Absolute link rejected')
            target=posixpath.normpath(posixpath.join(posixpath.dirname(n),m.linkname) if m.issym() else m.linkname)
            if not safe(target): raise SystemExit('Escaping link rejected')
            links.add(n)
    for n in names:
        p=posixpath.dirname(n)
        while p:
            if p in links: raise SystemExit('Archive member under link rejected')
            p=posixpath.dirname(p)
PY
tar -xJf "$dest/node.tar.xz" -C "$dest" --no-same-owner
actual=$("$dest/$name/bin/node" --version)
[[ $actual == "$version" ]] || { echo 'Runtime version mismatch' >&2; exit 1; }
printf 'STAGED_NODE=%s/%s/bin/node\nVERSION=%s\nACTIVATED=false\n' "$dest" "$name" "$actual"
