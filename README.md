# FNOS-OpenclawMod

[中文指南](docs/zh-CN/01-architecture.md) · [English guide](docs/en/01-architecture.md)

fnOS AppCenter OpenClaw 的维护经验、分层升级流程和有限作用域脚本。目标是让用户看清 **平台 → 包装壳 → OpenClaw core → 用户状态与外部工具** 的边界。

Community maintenance notes and scoped utilities for the fnOS AppCenter OpenClaw package. This is not an official fnOS or OpenClaw distribution, and not a universal one-click installer.

## 范围 / Scope

- 历史验证基线：单台 fnOS 的 `trim.openclaw`、OpenClaw **2026.9.5 → 2026.10.5**、Bun **1.3.9**、Gateway 私有 Node **24.19.0**。这些是案例版本，不是最新版本推荐。
- Historical baseline: one `trim.openclaw` deployment upgraded from **2026.9.5 to 2026.10.5**, with Bun **1.3.9** and a private Node **24.19.0**. No blanket compatibility claim for other packages or releases.
- 新脚本已作离线边界测试；没有用这套公开脚本再次升级生产 NAS。文档明确区分历史成功流程、新实现和待验证操作。
- Newly authored scripts receive offline checks; they have not been used to repeat a production NAS upgrade. See [test scope](TESTING.md).

## 文档 / Documentation

| 主题 / Topic | 中文 | English |
|---|---|---|
| 壳、core、路径与启动关系 / Architecture | [01](docs/zh-CN/01-architecture.md) | [01](docs/en/01-architecture.md) |
| 不改壳的 core 升级 / Core upgrade | [02](docs/zh-CN/02-upgrade.md) | [02](docs/en/02-upgrade.md) |
| Node/Bun 与依赖 / Dependencies | [03](docs/zh-CN/03-runtimes.md) | [03](docs/en/03-runtimes.md) |
| 日常配置与模型 / Configuration | [04](docs/zh-CN/04-configuration.md) | [04](docs/en/04-configuration.md) |
| 升级后验收与故障 / Acceptance & troubleshooting | [05](docs/zh-CN/05-troubleshooting.md) | [05](docs/en/05-troubleshooting.md) |
| 事故与经验 / Lessons | [06](docs/zh-CN/06-lessons.md) | [06](docs/en/06-lessons.md) |
| curl 使用与发布 / Distribution & publishing | [07](docs/zh-CN/07-distribution.md) | [07](docs/en/07-distribution.md) |

[完整命令 / Commands](docs/COMMANDS.md) · [来源 / Sources](SOURCES.md) · [补丁登记 / Patch register](patches/README.md) · [更新记录 / Changelog](CHANGELOG.md)

## 快速开始 / Quick start

在仓库根目录执行；只读盘点不调用 OpenClaw、不读凭据或进程环境：

Run from the repository root. This inventory does not invoke OpenClaw, read credentials, or print process environments:

```bash
python3 -B scripts/inspect.py
# Need actual process executable paths? Re-run the same read-only tool with sudo:
sudo python3 -B scripts/inspect.py
```

默认通过 `/var/apps/trim.openclaw/home/data` 推导路径；不存在时用 `--data-root` 明确指定。不要直接套用案例中的 `/vol3`。

The default derives paths through fnOS application links; override `--data-root` when needed. Inspect the result before making changes.

## curl 下载只读检查 / Download the read-only inspector

```bash
tmp=$(mktemp -d)
curl --fail --show-error --silent --location --proto '=https' --proto-redir '=https' \
  https://raw.githubusercontent.com/minglezhou/FNOS-OpenclawMod/91db04269ad1bbe3bb041ea57fc6ce86d2b94fa4/scripts/inspect.py \
  -o "$tmp/inspect.py"
python3 -B "$tmp/inspect.py"
```

此命令仅盘点，不升级、不重启、不读取凭据。其他维护命令见 [COMMANDS.md](docs/COMMANDS.md)。
This command inventories the host; it does not upgrade, restart services or read credentials.

## 脚本 / Scripts

| 脚本 | 行为 / Behavior |
|---|---|
| `inspect.py` | 只读路径、版本、身份 / read-only inventory |
| `fetch_release.py` | 下载精确 core 版本并验证 SHA-512 SRI；不安装 / exact release preparation |
| `cold_backup.py` | 已停服后冷备、隔离解压与比对；不恢复生产 / cold capture and comparison |
| `upgrade-core.sh` | 默认须选 `--plan`；`--apply` 明确执行固定版本 Bun 本地依赖更新 / explicit core update |
| `stage-node.sh` | 校验指定 SHA256 后并排放置 Node；不切换运行时 / stage Node without activation |
| `health.py` | 本地 bridge `/health` 观测，无模型调用和重启 / local health observation |

No script automatically stops services, kills processes, deletes locks, changes proxy/authentication settings, edits live SQLite, or activates a production restore. A successful command is not an end-to-end acceptance result.

## 仓库 / Repository

[GitHub: minglezhou/FNOS-OpenclawMod](https://github.com/minglezhou/FNOS-OpenclawMod)

使用经过审阅的固定提交下载脚本，见[下载指南](docs/zh-CN/07-distribution.md)。
Use a reviewed immutable commit for maintenance scripts; see the [download guide](docs/en/07-distribution.md).
