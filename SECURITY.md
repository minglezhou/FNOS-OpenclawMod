# Security / 安全说明

Do not attach live openclaw.json, .env, credentials, raw process environments or private logs to issues. Share version, sanitized topology, exact error class and minimal reproduction. 本仓库不接收秘密或业务原始数据。

This is community maintenance software. Review a fixed commit before running scripts. Root is required only for the cold capture/metadata comparison and optional privileged inspection; core installation and Node staging run as the application user. Scripts do not establish a trusted network perimeter or prove that every writer is stopped.

Report sensitive findings through a private channel agreed with the repository maintainer. No security email/contact has been invented. Licensing covers newly authored repository content, not fnOS, OpenClaw, Bun or Node themselves.
