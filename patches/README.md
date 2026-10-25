# Patch register / 补丁登记

This first release records patches and their boundaries; it does **not** blindly apply source replacements to unknown fnOS builds. 本版不附无版本门禁的 sed 一键补丁。

| Area / 范围 | Recorded lesson / 经验 | Deployment policy / 处置 |
|---|---|---|
| Wrapper configuration seeding | Older seed paths wrote keys retired by newer core / 旧 seed 写退役字段 | Check actual writer and schema; no blanket delete / 按实际写入点修 |
| Proxy response decoding | Decoded body with stale encoding/length headers / 解压 body 与头不一致 | Confirm Bun/proxy behavior before a narrow fix / 不盲删所有头 |
| Forwarded headers / Origin / auth | Trust-boundary changes can hide attribution or weaken auth / 代理与鉴权有安全边界 | No generic bypass patch / 不提供通用绕过 |
| Runtime PATH | Shim and wrapper may consume different Node / 多层 runtime | Prefer side-by-side staging and an existing supported pointer / 不覆盖共享 runtime |
| Ollama injection | Wrapper child env can advertise an unwanted provider / 壳环境可影响目录 | Check injection source; do not delete embedding bridge |
| MiniMax release-ID thinking | Preview-only exact match missed GA ID / 正式版未命中 | Case-specific core patch; revalidate after upgrade |
| Kimi provider candidate | Offline candidate vs working live calls are distinct / 候选与线上可用不同 | No automatic installation; preserve current working route |
| Bridge HOME | Explicit app HOME restored existing credentials / HOME 修复凭据定位 | Apply in its supervisor, not Gateway auth |

Historical MiniMax case: core `2026.10.5`, file `thinking-Dg9lPaiN.mjs`.
Before SHA256: `9db0cb36450ee3788e631f5bd1ce1989dfa4df186809065070c89d7056f919d6`.
After SHA256: `2735006487fdee91ad06c6cbc28bff167b7d034ffd88c6660aa3c3257ce0be03`.
The change added exact normalized `MiniMax-M3.1-Flash` alongside `MiniMax-M3.1-Flash-Preview`, without prefix matching. The Bun cache hardlink also changed. These hashes identify a historical case, not downloadable vendor artifacts or proof the patch is still needed.

Future executable patches must assert source identity, preserve metadata, avoid modifying a shared hardlink unexpectedly, retain private backups, stop on mismatch, test the affected behavior, and include guarded rollback. 后续可执行补丁必须包含这些保护，不以旧行号替代字节核对。
