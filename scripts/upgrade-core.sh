#!/usr/bin/env bash
# Fixed-version Bun local dependency update. Explicit operator inputs only.
# Does not stop/start services, change the wrapper, run Doctor, or auto-rollback.
set -euo pipefail
umask 077
if [[ ${1:-} == --help || $# == 0 ]]; then
  cat <<'HELP'
Usage: upgrade-core.sh [--plan|--apply]
Required environment:
  APP_USER APP_HOME INSTALL_DIR STATE_DIR NODE_BIN BUN_BIN TARGET_VERSION
  CHECKPOINT_RECEIPT LOG_PARENT
--apply additionally requires MAINTENANCE_CONFIRMED=yes.
Run as APP_USER from an independent maintenance shell. APP_HOME is not $HOME.
The receipt records a cold restore comparison, NOT a platform rollback guarantee.
HELP
  exit 0
fi
[[ $# == 1 && ( $1 == --plan || $1 == --apply ) ]] || { echo 'Invalid arguments' >&2; exit 2; }
for key in APP_USER APP_HOME INSTALL_DIR STATE_DIR NODE_BIN BUN_BIN TARGET_VERSION CHECKPOINT_RECEIPT LOG_PARENT; do
  [[ -n ${!key:-} ]] || { echo "Missing variable: $key" >&2; exit 2; }
done
[[ $(id -u) != 0 && $(id -un) == "$APP_USER" ]] || { echo 'Run as APP_USER, not root' >&2; exit 2; }
[[ $TARGET_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$ ]] || { echo 'Exact version required' >&2; exit 2; }
for path in "$APP_HOME" "$INSTALL_DIR" "$STATE_DIR" "$NODE_BIN" "$BUN_BIN" "$CHECKPOINT_RECEIPT" "$LOG_PARENT"; do
  [[ $path == /* && -e $path ]] || { echo 'Every path must be absolute and exist' >&2; exit 2; }
done
[[ -x $NODE_BIN && -x $BUN_BIN && -d $LOG_PARENT ]] || exit 2
python3 - "$CHECKPOINT_RECEIPT" "$INSTALL_DIR" "$STATE_DIR" <<'PY'
import json, sys
from pathlib import Path
r=json.loads(Path(sys.argv[1]).read_text())
if r.get('verification_matches') is not True:
    raise SystemExit('No successful cold verification receipt')
sources=[Path(p).resolve() for p in r.get('sources', [])]
for s in sys.argv[2:]:
    q=Path(s).resolve()
    if not any(q == p or p in q.parents for p in sources):
        raise SystemExit('Checkpoint inventory does not cover install/state')
p=json.loads((Path(sys.argv[2])/'package.json').read_text())
if 'openclaw' not in p.get('dependencies', {}):
    raise SystemExit('Not a supported local Bun OpenClaw project')
if not (Path(sys.argv[2])/'bun.lock').is_file():
    raise SystemExit('Expected bun.lock; do not silently switch package managers')
PY
printf 'Target: openclaw@%s\nMode: %s\n' "$TARGET_VERSION" "$1"
if [[ $1 == --plan ]]; then exit 0; fi
[[ ${MAINTENANCE_CONFIRMED:-} == yes ]] || { echo 'Maintenance confirmation required' >&2; exit 2; }
# No automatic stop: user must have stopped all writers and prevented restart.
# Minimal secondary check; cannot establish quiescence by process name alone.
if pgrep -u "$APP_USER" -x 'bun|openclaw-gatewa|openclaw-gateway' >/dev/null; then
  echo 'Wrapper/Gateway-like process is still present; aborting' >&2; exit 2
fi
LOG_DIR=$(mktemp -d "$LOG_PARENT/core-update.XXXXXXXX")
chmod 700 "$LOG_DIR"
printf 'INSTALL_LOG=%s/bun-install.log\n' "$LOG_DIR"
cp -p -- "$INSTALL_DIR/package.json" "$LOG_DIR/package.json.before"
cp -p -- "$INSTALL_DIR/bun.lock" "$LOG_DIR/bun.lock.before"
# env HOME is the child's required application identity, not a shell scratch variable.
# This is a network install: the preparatory SRI download is independent and not consumed here.
if ! (cd "$INSTALL_DIR" && env HOME="$APP_HOME" OPENCLAW_CONFIG_PATH="$STATE_DIR/openclaw.json" \
  PATH="$(dirname "$NODE_BIN"):$(dirname "$BUN_BIN"):/usr/bin:/bin" \
  "$BUN_BIN" add --exact --trust --registry https://registry.npmjs.org "openclaw@$TARGET_VERSION") \
  >"$LOG_DIR/bun-install.log" 2>&1; then
  echo 'Install failed; private log retained. No restart or automatic rollback.' >&2; exit 1
fi
python3 - "$INSTALL_DIR" "$TARGET_VERSION" <<'PY'
from pathlib import Path
import json,sys
p=Path(sys.argv[1]); target=sys.argv[2]
core=json.loads((p/'node_modules/openclaw/package.json').read_text())
project=json.loads((p/'package.json').read_text())
ok=(core.get('name')=='openclaw' and core.get('version')==target and
    project.get('dependencies',{}).get('openclaw')==target and
    'openclaw' in project.get('trustedDependencies',[]) and (p/'bun.lock').is_file())
print(json.dumps({'package_verified':ok, 'target':target,
                  'doctor_performed':False,'service_acceptance_pending':True}))
raise SystemExit(0 if ok else 1)
PY
