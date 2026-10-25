# Upgrade core while retaining the wrapper

The recorded 2026.9.5 → 2026.10.5 upgrade succeeded; this is not permission to skip required bridge releases or migrations. Check target release notes and the installed CLI. See [complete commands](../COMMANDS.md).

1. Inventory installation ownership, real runtimes, shim, state and external data. Select an exact version. Fetch metadata/tarball, verify identity/SRI and inspect engines/lifecycle without executing package code.
2. Establish an independent SSH maintenance channel. Inspect active tasks and scheduling/recovery behavior. Preserve trigger states before pausing anything whose external effects require isolation; do not blindly re-enable every job afterward.
3. Stop through supported platform/wrapper controls, then identify residual Gateway, broker, supervisors and business workers. Never reuse a historical PID or assume stopping the wrapper stops all children. Repository scripts do not kill processes.
4. Capture a consistent cold checkpoint covering the core/data root, wrapper files/runtime data and explicitly inventoried external state. Built-in backups may exclude regenerable runtimes. Unchanged platform dependencies need recorded versions/sources; changing them requires their own recovery plan.
5. Extract into a new isolated directory on a metadata-compatible filesystem. Compare content, permissions, ownership and required ACL/xattrs. Listing a tar or hashing it does not verify restoration. The case initially showed permission-only differences; a compatible destination produced zero differences.
6. As the application user, update the existing Bun local project with an exact dependency. Do not use a global install, reinstall AppCenter, rerun install_callback or replace shared platform runtimes.
7. Check core name/version, exact project dependency, bun.lock and trustedDependencies. Run the supported migration/Doctor flow with a compatible Node. Doctor is a maintenance operation, not a read-only test.
8. Start through the original manager and verify actual runtime, ports, startup/database state, WebUI and minimal model/tool behavior. Reconcile schedules and external deliveries separately.

## Automation limits

`cold_backup.py` is newly authored: GNU tar capture, isolated extraction, rsync checksum dry-run comparison. Its root process/port observations do not prove absence of external-UID or namespace writers. Cross-source hardlink topology is not compared. Paths must be non-overlapping and destinations new.

`upgrade-core.sh --plan` validates inputs and a prior receipt. `--apply` performs a network Bun install and trusted lifecycle execution; it does not run Doctor, start services or roll back. Scripts have offline tests, not a new production NAS acceptance claim.

The preparatory SRI tarball **is not consumed by the Bun install**. Bun resolves/downloads independently. Do not call this a byte-bound offline install; stronger supply-chain requirements need a complete dependency-tree locking workflow.

On failure, retain evidence and stop. Do not blindly retry update/restart. Package downgrade cannot undo a newer state schema. Full rollback requires a coherent version/state/runtime/wrapper checkpoint and a decision on post-checkpoint writes and irreversible external effects. No generic one-click production restore is provided; isolated comparison is not activation rehearsal.
