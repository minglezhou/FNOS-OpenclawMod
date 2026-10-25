# Lessons and evidence boundaries

Recorded 2026-10-25 from sanitized operator receipts and two earlier handovers. Raw private files, identities, account details, job IDs and business paths are not included. Later corrections supersede earlier handover assertions.

| Lesson | Evidence | Limit |
|---|---|---|
| Core and wrapper can be updated separately | Successful exact Bun local upgrade 2026.9.5 → 2026.10.5 | Not a compatibility guarantee for every combination |
| Root CLI can leave ownership problems | Earlier EACCES investigation | Run as application user; do not generalize recursive chown |
| Built-in backup is not a whole-system image | Archive inventory excluded core/wrapper/runtime | Maintain an explicit cold inventory |
| Restore metadata depends on destination | Same archive compared cleanly in a compatible directory | Do not claim tar omits ownership |
| Multiple Node sources coexist | PATH and actual process exe differed | Resolve links and inspect real executable identity |
| Unreadable is not clear | /proc permissions and shared network namespace | Only actual FD evidence establishes socket ownership |
| Test count is not source identity | Source-bound runner distinguished the intended 38 tests from unrelated 16 | Final offline 38+2 success did not prove production restore |
| Release and Preview IDs can hit different hooks | Matcher and offline payload comparison | A successful response does not prove thinking parameters |
| HOME is a runtime dependency | Restoring HOME produced an actual 200/1536-dimension embedding | Not complete retrieval acceptance |
| Operational health checks need not use models | agentTurn replaced with deterministic command | Local success is not natural schedule acceptance |
| Stale instructions cause rework | Conflicting historical runbooks | Centralize current policy and archive old instructions |

Do not stop authorized work because context metadata says no active tools, repeat approval for every already-authorized step, or rerun model/history suites for documentation edits. Each test should answer a current unresolved question. Fake fetch, archive hash and exit zero are not full service acceptance.

Publish generic layouts and mechanisms, not raw credentials, private instructions, actual job IDs or complete business logs. New public scripts remain offline-tested utilities, not relabeled production-proven tools. Contributions should state applicable versions/hashes, minimal diff, failure behavior, rollback and actual acceptance evidence.
