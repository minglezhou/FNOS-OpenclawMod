# 完整命令 / Complete operator commands

Run from a downloaded/reviewed repository checkout in an **independent SSH session**, not the Gateway's own exec child. Each section is a separate phase; read its prerequisites before proceeding. No generic command here stops a service, kills a process, deletes a lock or starts a model call.

在独立 SSH 会话运行，不能由即将停止的 Gateway 自己执行。按阶段推进，不把全文拼成无人值守脚本。`/var/apps` 路径先核实；自定义/多实例必须按自己的布局替换。

## 1. Inventory / 盘点与路径

```bash
python3 -B scripts/inspect.py
sudo python3 -B scripts/inspect.py

# These are path variables, never repurpose the shell's HOME.
APP_USER=trim.openclaw
APP_ROOT=$(readlink -f /var/apps/trim.openclaw/target)
DATA_ROOT=$(readlink -f /var/apps/trim.openclaw/home/data)
APP_VAR=$(readlink -f /var/apps/trim.openclaw/var)
APP_HOME="$DATA_ROOT/home"
STATE_DIR="$APP_HOME/.openclaw"
INSTALL_DIR="$DATA_ROOT/openclaw"
CLI="$APP_ROOT/bin/openclaw"
NODE_BIN="$STATE_DIR/tools/cli-node/tools/node/bin/node"
BUN_BIN=/var/apps/bunjs/target/bin/bun
LOG_PARENT=$(readlink -f /var/apps/trim.openclaw/tmp)
test -d "$DATA_ROOT" && test -d "$APP_VAR" && test -d "$LOG_PARENT" \
  && test -x "$CLI" && test -x "$NODE_BIN" && test -x "$BUN_BIN"
```

If any check fails, stop and supply the actual paths from inventory. Do not silently use system Node or create guessed production directories. 检查失败就定位实际目录，不补造路径。

```bash
sudo -u "$APP_USER" "$CLI" --version
sudo -u "$APP_USER" "$CLI" config file
sudo -u "$APP_USER" "$CLI" config validate
sudo -u "$APP_USER" "$NODE_BIN" --version
sudo -u "$APP_USER" "$BUN_BIN" --version
```

CLI inspection can load application code; only `inspect.py` is designed to avoid invoking core. Never run the application CLI as root. Check exact local `--help` before mutating commands.

## 2. Prepare an exact core version / 精确版本与制品准备

```bash
# Historical example only: choose your reviewed target version.
TARGET_VERSION=2026.10.5
PREP_PARENT=$(mktemp -d)
python3 -B scripts/fetch_release.py \
  --version "$TARGET_VERSION" --out "$PREP_PARENT/release"
```

Read `engines` and lifecycle names/commands. Match Node/platform compatibility before maintenance. `sri_matches=true` validates the downloaded main tarball against npm metadata; it does not audit package code or all transitive dependencies. Downloads are outside production, but network/disk activity is real.

## 3. Maintenance and cold checkpoint / 停写与冷备

Use the fnOS/wrapper stop controls appropriate to the installed build. Observe current processes; investigate residual supervisors, bridge, brokers and business writers. Separately handle scheduled external effects and retain original enabled states. **Do not execute the backup command until all relevant writers are stopped.**

```bash
sudo ps -u "$APP_USER" -o pid,ppid,etime,stat,comm
# Replace example ports with the actual inventory.
sudo ss -ltnp '( sport = :49164 or sport = :11434 )'
```

Select private backup and extraction parent directories **outside all source roots**, with enough space and appropriate ACL behavior. This may require archive + full extraction + later install space; quota/inodes are separate checks. The sample does not auto-include external business state.

```bash
# Edit these two existing paths; they must not be within DATA_ROOT/APP_ROOT/APP_VAR.
BACKUP_PARENT=/path/to/private-backups
VERIFY_PARENT=/path/to/metadata-compatible-temporary-area
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
CHECKPOINT="$BACKUP_PARENT/pre-openclaw-$STAMP"
VERIFY_DIR="$VERIFY_PARENT/restore-verify-$STAMP"

sudo python3 -B scripts/cold_backup.py \
  --source "$DATA_ROOT" --source "$APP_ROOT" --source "$APP_VAR" \
  --out "$CHECKPOINT" --verify-dir "$VERIFY_DIR" \
  --user "$APP_USER" --port 49164 --port 11434 \
  --ack-all-writers-stopped
```

Add `--source /actual/external/state` for every external state root; don't nest sources. Symlink targets outside sources are **not followed**. The script rejects overwrite, overlap, remaining selected listeners/app-user processes, tar warnings, or rsync differences. It cannot detect every external UID writer. Root must run in the host namespace, not a partial container view.

The archive retains numeric ownership/ACL/xattrs with GNU tar; the destination must support them. The comparison covers the selected tree contents/metadata, but not cross-source hardlink topology, every filesystem flag, application semantic correctness or activation. On failure, retain logs/extracted files; do not normalize permissions just to hide differences.

```bash
sudo sh -c 'cd "$1" && sha256sum -c SHA256SUMS.txt' sh "$CHECKPOINT"
```

## 4. Install core without changing the wrapper / 保留壳安装 core

This step is a new guarded script around the historically successful Bun route, not a newly production-tested installer. Keep all writers stopped. The checkpoint must be fresh and match this maintenance window. `--plan` only examines metadata, not whether all prerequisites are semantically true.

The cold checkpoint is root-private; copy only its non-secret receipt to a new app-readable private directory for the script, not the archive or its secret-bearing contents:

```bash
RECEIPT_DIR=$(sudo -u "$APP_USER" mktemp -d "$LOG_PARENT/maintenance.XXXXXXXX")
APP_GROUP=$(id -gn "$APP_USER")
sudo install -o "$APP_USER" -g "$APP_GROUP" -m 600 \
  "$CHECKPOINT/receipt.json" "$RECEIPT_DIR/receipt.json"
CHECKPOINT_RECEIPT="$RECEIPT_DIR/receipt.json"

sudo -u "$APP_USER" env APP_USER="$APP_USER" APP_HOME="$APP_HOME" \
  INSTALL_DIR="$INSTALL_DIR" STATE_DIR="$STATE_DIR" NODE_BIN="$NODE_BIN" BUN_BIN="$BUN_BIN" \
  TARGET_VERSION="$TARGET_VERSION" CHECKPOINT_RECEIPT="$CHECKPOINT_RECEIPT" LOG_PARENT="$LOG_PARENT" \
  bash scripts/upgrade-core.sh --plan

# Explicit mutation: lifecycle scripts execute; no automatic Doctor/start/rollback.
sudo -u "$APP_USER" env APP_USER="$APP_USER" APP_HOME="$APP_HOME" \
  INSTALL_DIR="$INSTALL_DIR" STATE_DIR="$STATE_DIR" NODE_BIN="$NODE_BIN" BUN_BIN="$BUN_BIN" \
  TARGET_VERSION="$TARGET_VERSION" CHECKPOINT_RECEIPT="$CHECKPOINT_RECEIPT" LOG_PARENT="$LOG_PARENT" \
  MAINTENANCE_CONFIRMED=yes bash scripts/upgrade-core.sh --apply
```

Bun uses the exact npm version and network registry; the separately downloaded tgz is not installed here. Existing project `.env`/Bun settings may affect behavior: review locally without printing secrets. An install failure retains logs and package.json/bun.lock copies; those files alone are not a full rollback.

## 5. Migration, activation and acceptance / 迁移与启动

Only after package verification, inspect current Doctor help and follow its version-specific instructions. The following is the maintenance command used in the case; it may migrate state and modify configuration. Do not treat it as read-only.

```bash
sudo -u "$APP_USER" "$CLI" doctor --help
# Review migration instructions and the selected CLI runtime before execution.
DOCTOR_DIR=$(sudo -u "$APP_USER" mktemp -d "$LOG_PARENT/doctor.XXXXXXXX")
sudo -u "$APP_USER" sh -c \
  'umask 077; "$1" doctor --fix >"$2/doctor.log" 2>&1' \
  sh "$CLI" "$DOCTOR_DIR"
```

If the command fails, don't restart automatically. Read bounded private logs, resolve the exact failure, and avoid package-only rollback after migration. If it succeeds, start through the original fnOS/wrapper manager, then check current exe, listener, WebUI/WS and the necessary business paths. Start independent bridge/supervisors only through their known entrypoint with explicit application HOME, preventing duplicates. No historical PID is embedded here.

## 6. Stage Node side-by-side / 并排准备 Node

Do this only if the target core needs a different runtime. Obtain the version/architecture/hash from the official release and verify signed SHASUMS as appropriate. Run as the application user into a new approved private runtime directory:

```bash
NODE_VERSION=v24.19.0  # historical example, not a current recommendation
NODE_ARCH=x64         # use arm64 on a compatible ARM64 host
NODE_SHA256=REPLACE_WITH_VERIFIED_64_HEX_SHA256
NODE_DEST=/absolute/new/private-runtime-candidate
sudo -u "$APP_USER" bash scripts/stage-node.sh \
  "$NODE_VERSION" "$NODE_ARCH" "$NODE_SHA256" "$NODE_DEST"
```

Staging does not activate. If the existing wrapper and CLI already consume a stable symlink, switching that link during maintenance can avoid editing wrapper files. If not, stop here rather than inventing an injection point. Record and verify the old target and new process exe. Platform Bun/Node remains untouched. A generic symlink-switch command is intentionally not provided because an incorrect target can silently move the whole app onto an incompatible runtime.

## 7. Deterministic health cron / 确定性健康检查

First install the reviewed `scripts/health.py` in an approved permanent application-owned tools directory; do not point cron at a temporary download folder. It observes local bridge liveness only, not credentials or upstream embeddings.

```bash
HEALTH_SCRIPT=/absolute/permanent/tools/health.py
JOB_ID=REPLACE_WITH_YOUR_EXISTING_JOB_ID
sudo -u "$APP_USER" "$CLI" cron edit --help
# Save the full existing definition privately via the supported get/export command.
ARGV=$(python3 -c 'import json,sys; print(json.dumps(["/usr/bin/python3","-B",sys.argv[1]]))' "$HEALTH_SCRIPT")
sudo -u "$APP_USER" "$CLI" cron edit "$JOB_ID" \
  --command-argv "$ARGV" --timeout-seconds 20
```

Confirm the target job identity before edit, then read back payload kind/argv and absence of agent fields. Preserve schedule, enabled, delivery and failure alerts unless explicitly changing them. Check command-cwd/env if the new task needs them. Do not create a new five-minute schedule merely by reading this guide. Local script success and the next natural scheduled run are separate acceptance points.
