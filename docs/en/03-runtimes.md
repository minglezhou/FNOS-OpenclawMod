# Node, Bun and important dependencies

Start with the target core's engines and native-module/platform requirements. The recorded upgrade retained Node 24.19.0 because it already met the then-current requirement. Do not change a working runtime solely because core is being updated.

| Component | Boundary |
|---|---|
| Platform Node/Bun | Shared, platform-managed; do not overwrite target/bin or its physical target |
| Private OpenClaw Node | Stage side-by-side; activate only through a confirmed consumed pointer |
| Optional installer-only Bun | A private binary may install dependencies without changing the wrapper's running Bun |
| Native dependencies/plugins | Let the owning package manager handle the tree; do not transplant incompatible node_modules |
| Wrapper patch bundle | Reassess compatibility; do not blindly reapply historical line-number patches |

`stage-node.sh` requires an exact version, architecture, expected SHA256 and a new destination. It verifies the official Linux tarball, checks archive paths, unpacks and checks the version. It does not activate a runtime. Follow Node's signed-SHASUMS verification guidance; a checksum obtained alongside the tarball is not independent source authentication.

Before activation, verify architecture, libc/native-module compatibility, engines, space, access, the existing link and real process exe. Keep the previous target. During maintenance a confirmed stable symlink can be atomically switched to the staged directory. **If the wrapper hard-codes its runtime and consumes neither this pointer nor a configurable PATH, a no-wrapper-change runtime switch is not available.** Retain the compatible runtime, use supported platform configuration, or scope a wrapper change separately.

Never overwrite the old version directory. Existing processes may retain old executable inodes. Confirm new process exe after startup; a shell version is insufficient. Runtime rollback must account for native modules and state migrations.

Bun 1.3.9 was used in the recorded upgrade; a newer Bun is not established as necessary. An installer-only private Bun and the wrapper's Bun have separate activation paths. Review package lifecycle scripts and trust OpenClaw explicitly, not every dependency. Bun cache hardlinks can propagate an in-place dist edit into the cache; one pathname is not necessarily one affected copy.
