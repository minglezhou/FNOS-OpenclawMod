# Sources and evidence / 来源与证据

Compiled 2026-10-25. 本仓库区分三类证据，官方网页是滚动文档，不保证与历史安装版完全一致。

## A. Official references checked for this edition / 本版查阅的官方资料

- OpenClaw updating: https://docs.openclaw.ai/install/updating — update/migration ownership, backup boundaries and version-dependent migration requirements. Do not transplant commands intended for a global installation into a fnOS local Bun project.
- Bun lifecycle scripts: https://bun.sh/docs/pm/lifecycle — trustedDependencies and lifecycle execution. Our explicit trust applies to the selected package, not all downloaded code.
- Bun add: https://bun.sh/docs/pm/cli/add — exact dependency installation. Local installed `bun add --help` is authoritative for available flags.
- Node downloads: https://nodejs.org/en/download — official distribution entry and signed SHASUMS verification link. Historical Node 24.19.0 is a case version, not a latest recommendation.
- GNU tar permissions: https://www.gnu.org/software/tar/manual/html_node/Setting-Access-Permissions.html — recorded modes and extraction flags.
- GNU tar attributes: https://www.gnu.org/software/tar/manual/html_section/Attributes.html and https://www.gnu.org/software/tar/manual/tar.html — ownership/permissions, ACL and xattr considerations.

## B. Operator case evidence / 用户维护回执（未公开原件）

- Fixed-version 2026.9.5 → 2026.10.5 local Bun upgrade; dependency pinned exactly; Node 24.19.0; Bun 1.3.9; Doctor and subsequent basic UI/model acceptance.
- Cold tar isolation comparison: initial permissions-only differences; new compatible extraction location yielded zero differences. No claim of a full production rollback drill.
- Wrapper/main path source excerpts and /proc exe observations; these describe one fnOS package, not every vendor build.
- Bridge HOME correction followed by actual HTTP 200 / finite 1536-dimensional embo-01 vector / approximately 0.445 seconds.
- Command health cron conversion, removal of key-fragment logging, and document deployment with 18/18 matching hashes. Natural cron scheduling and all-memory retrieval were not inferred from those checks.

## C. Historical handovers / 历史 handover

Two earlier handovers covered an older wrapper/core upgrade and later audit. They supplied leads about seeding, runtime differences, proxy decoding and permissions. Contradicted claims (fixed orphan behavior, unconditional reconcile restart, PPID=1 requirements, version-default-as-effective-value, no owner metadata in tar) are not retained as current truths.

No raw handovers, personal USER/MEMORY files, configs, tokens, process environments or business logs are distributed. Some command recipes are newly authored generalizations; see TESTING.md for their limited validation.
