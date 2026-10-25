# Post-upgrade acceptance and troubleshooting

Verify core/project dependency versions, actual runtimes, configuration and migration results. Start through the original manager; inspect ports, startup/database phases and WebUI. Run one relevant model/tool acceptance case and observe required schedules/delivery. Installation exit zero, valid configuration, listening port, visible model, successful reply and correct business output are separate claims.

| Symptom | Check first | Avoid |
|---|---|---|
| Wrapper alive, no Gateway | Gateway startup logs and active config | Repeated restarts or blind downgrade |
| Config valid, startup fails | Runtime auth constraints, migration, Node/native dependencies | Treating schema validity as startup proof |
| Connecting after restart | Startup/DB verification and WS authentication | Immediate SIGKILL |
| Connecting long after startup | Correct basePath HTTP, WS/F12, remote proxy | Attributing everything to cold start/bridge |
| Root-path 404 | Actual instance basePath | Declaring WebUI unavailable |
| Decoding failure with HTTP 200 | Decompressed body vs forwarded encoding/length headers | Blind network changes or dropping every header |
| EACCES | Application identity and exact file metadata | Recursive global chown |
| Unmanaged-install refusal | Installation type and owning package manager | Global reinstall or forcing wrapper state |
| Bridge local missing-key 502 | HOME, existing credential source, permissions | Printing or swapping credentials blindly |
| Model-phase cron timeout | Whether a deterministic task is agentTurn | Infinite timeout or embedding restarts |
| Plugin differs from wrapper pin | Actual compatibility and reinstall behavior | Reinstalling into an old pinned version |

An explicit token mode fixed one case; it is not a universal authentication patch. Origins/proxy trust require the actual trusted network chain. Do not publish wildcard origins, invented client IPs, disabled device authentication or stripping forwarded headers as default fixes. Cloudflare access remains a separate deployment topic.

Logs include wrapper info.log, instance gateway.log and `/tmp/openclaw/openclaw-YYYY-MM-DD.log`. Read bounded relevant windows and redact before sharing. Listener warnings and lease waits alone are not a fatal diagnosis. Never delete locks solely by age.

Do not repeatedly restart a recovered service merely to complete a checklist. Capture remote browser evidence only when the fault recurs, with tokens, query secrets and headers removed. Local health success does not close an unrelated scheduled-backup failure.
