# Where to change configuration

| Change | Preferred surface |
|---|---|
| fnOS application lifecycle/shared dependencies | fnOS UI, using the actual platform manager |
| Wrapper instance/proxy behavior | Confirmed wrapper configuration/UI; it may write core configuration directly |
| Providers/defaults/aliases/allowlist | Supported OpenClaw configuration CLI/WebUI, matching installed schema |
| Session model/thinking | Session selector; existing overrides may outlive default changes |
| Cron | Supported cron API/CLI, never direct SQLite editing |
| Preferences/instructions | Workspace USER/AGENTS/SOUL; project progress in project STATE |
| Skills | Supported enabled/archive/workshop controls, not manual managed-directory moves |
| Independent bridge | Its supervisor, scripts and restricted credential source with explicit application HOME |

Use the active configuration path and current help/schema; back up privately, apply the narrow change, validate, read back and perform one relevant acceptance check. Guard against later edits before rollback. Do not treat every dry-run as read-only: an earlier update-preview source trace reached ledger writes.

The main configuration is usually `$APP_HOME/.openclaw/openclaw.json`; cron, sessions, credential stores and wrapper instance records have separate ownership. Generated models.json is not a manual configuration surface. Environment injection can also change behavior.

## Model lessons, not account presets

The case uses Flash/max globally, K3-256K/high per model and K3.1 Pro/max. Preserve per-model defaults instead of flattening everything into the global setting. Session, agent, per-model parameters and provider defaults are separate; inspect explicit cron overrides independently.

A MiniMax release ID missed a Preview-only thinking hook; a narrow local patch addressed this case but upgrades may overwrite it. Harness `ultra` is not vendor `max`. A working Kimi reply does not prove a candidate plugin is installed or every effort/tool/context entitlement works. Distinguish Code subscriptions from usage-priced APIs.

Unexpected Ollama entries in the case came from wrapper-injected child environment. Do not remove an embedding bridge just because it uses an Ollama-like local interface. Inspect only boolean presence of allowlisted environment keys, never their values.

Keep stable preferences/rules in root MD, stable facts/pointers in MEMORY and progress in project STATE. Mechanical per-question journals, choices files and global session-state duplication are not inherently required. Disabling old summaries does not authorize deleting history, transcripts, indexes or native DREAMS output. Manual skill generation was a case policy, not a universal requirement. New conversations can load revised instructions without restarting Gateway.

Use deterministic command jobs for health checks instead of invoking a high-thinking model every five minutes. Preserve schedule/delivery/enabled when changing a payload. `health.py` observes local liveness only. Planned readiness endpoints, credential hot reload and supervisor redesign remain unimplemented unless there is actual deployment evidence.
