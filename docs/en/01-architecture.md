# Wrapper and OpenClaw architecture

| Layer | Responsibility | Boundary |
|---|---|---|
| fnOS platform | AppCenter, lifecycle, permissions, reverse proxy, shared runtimes | Shared dependencies may serve other applications |
| trim.openclaw wrapper | Bun server, instance records, UI/API, proxy, configuration seeding, spawning core | Updating the wrapper is not updating core |
| OpenClaw core | Gateway, models/tools, sessions, scheduler, migrations | The observed deployment is Bun-spawned, not a standalone systemd service |
| Application state | Configuration, databases, credentials, workspace | Package installation does not replace migration or backup |
| Independent tools | Embedding bridge, supervisor, download workers | Stopping Gateway does not prove they stopped |

Observed startup: fnOS `cmd/main start` sets the environment and runs the Bun wrapper; the wrapper resolves the instance/configuration/CLI and spawns Gateway under Node. Wrapper stop, HTTP stop and Gateway signal handling are separate code paths. `unref()` is not proof of exit-cascade behavior. The observed reconciler updated status; its name does not establish automatic restart behavior.

## Path map

Set `APP=trim.openclaw`. Resolve fnOS links rather than hard-coding a volume. Multiple-instance/system-managed modes can use different configuration and runtime paths.

| Purpose | Entry or relative path |
|---|---|
| Lifecycle | `/var/apps/$APP/cmd/main` |
| Wrapper root | `/var/apps/$APP/target`, often `/volN/@appcenter/$APP` |
| Wrapper server / CLI shim | `server/index.js` / `bin/openclaw` under wrapper root |
| Data root | Verify `/var/apps/$APP/home/data`, often `/volN/@apphome/$APP/data` |
| Local core project | `$DATA_ROOT/openclaw`, with package.json and bun.lock |
| Installed core | `$INSTALL_DIR/node_modules/openclaw` |
| Application HOME / state | `$DATA_ROOT/home` / `$APP_HOME/.openclaw` |
| Workspace | `$DATA_ROOT/workspace` |
| Wrapper persistent runtime data | `/var/apps/$APP/var`, often `/volN/@appdata/$APP` |
| Wrapper instance database | `$DATA_ROOT/monitor/monitor.sqlite` |
| Proxy socket | Wrapper root `/trim.openclaw.sock` |
| Gateway log | Instance logPath; observed `$INSTALL_DIR/gateway.log` |

Gateway 49164 and bridge 11434 were observed loopback ports, not universal defaults. Include externally referenced business state in backup inventories. A CLI shim must preserve the application's HOME/configuration; the passwd home may not exist.

Platform runtimes: `/var/apps/bunjs/target/bin/bun` and `/var/apps/nodejs_v24/target/bin/node`. The observed Gateway/broker used `$STATE_DIR/tools/cli-node/tools/node-v24.19.0/bin/node`; the shim prepended `tools/cli-node/tools/node/bin`.

Compare realpath, device/inode and hash before calling differing path strings a conflict. A shell's `node --version` does not identify Gateway's runtime; inspect `/proc/<current-pid>/exe`. Avoid printing full command lines or process environments because they may contain credentials.
