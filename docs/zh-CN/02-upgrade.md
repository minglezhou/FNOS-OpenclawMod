# 保留壳的 core 升级流程

本案例已成功完成 2026.9.5 → 2026.10.5；不是任意旧版直升最新版保证。当前官方迁移路径可能要求桥接版本或不同数据库流程，先核目标发布说明与已安装 CLI。命令见 [完整命令](../COMMANDS.md)。

## 流程与检查点

1. **盘点与定版本**：识别安装类型、实际 Node、Bun、应用身份、CLI shim、外部业务 state；选精确 core 版本，不用 latest、caret 或浮动 tag。下载目标元数据/制品，核 name/version/SRI、engines 和 lifecycle；只下载不执行脚本。
2. **确定维护窗口**：独立 SSH 控制通道；核正在执行的业务、scheduler/cron 及可能的恢复补跑。暂停需要隔离外部副作用的触发器，并保存原状态；后续恢复不能盲目全部 enable。
3. **停完整写入链**：按当前 fnOS/包装入口停服务，重新发现 Gateway、broker、supervisor、下载器等残留。不能复用旧 PID；不把停壳等同于停全部子进程。脚本不代为 kill。
4. **一致冷备**：至少 core 所在数据根、壳文件、壳运行数据，以及明确的外部 state；平台 Node/Bun 若不动，记录其版本和来源，若要动则另含恢复方案。内置 backup 可能跳过 regenerable runtime，不足以单独覆盖本流程。
5. **隔离恢复比对**：在无冲突且元数据兼容的临时目录解压，内容、权限、属主及所需 ACL/xattr 对比。哈希与 tar -t 不等于恢复成功。案例首个目标目录产生纯 permission 差异，换兼容目录后零差异；不能笼统归咎于 tar 不存 uid/gid。
6. **应用用户安装精确 core**：在现有 Bun 本地工程下 `bun add --exact --trust ... openclaw@<版本>`；不全局安装、不重装 AppCenter 壳、不重跑 install_callback、不修改平台共享 runtime。
7. **迁移与校验**：检查 package.json name/version、上层依赖精确版本、bun.lock、trustedDependencies；用已选择的兼容 Node 运行当前版本支持的 Doctor 迁移。Doctor/`--fix` 是维护动作，不是无副作用测试。
8. **从原管理入口启动与业务验收**：检查实际新进程、端口、启动阶段、数据库状态、WebUI、最小模型/工具调用及必要渠道；单独确认 cron 已按原意恢复且没有重复外发。详细见 05。

## 脚本边界

`cold_backup.py` 为新实现：GNU tar 采集后用 rsync checksum dry-run 比对；root 视角检查应用用户进程与指定端口，但不能证明其他 UID/namespace 没有写入。管理员需控制所有写入者；跨 source 硬链接拓扑未比较。备份/验证目录不能覆盖或嵌套在 source 中。

`upgrade-core.sh --plan` 只校验输入与回执。`--apply` 安装并执行受信任包的 lifecycle，不运行 Doctor、不启动、不自动回退；失败保留私有日志。新脚本只通过本仓库离线检查，生产执行须先核当前实例。

`fetch_release.py` 的预下载用于评审，**Bun 安装会另行访问 registry**，不是安装已验证的 tgz；不能把两者描述成同一字节绑定的离线安装。安装时检查包身份与精确依赖；更高供应链要求应另做锁定完整依赖树的发布流程。

## 失败与回退

失败停止推进，不重复 update 或重启碰运气。保留安装/迁移日志及原文件；确认是否已迁移数据库。仅降级 npm 包不能撤销 state schema。完整回退需停止新写入并一致恢复匹配版本的 core、state、runtime 与包装数据，同时处理检查点后的业务变化及不可撤销外部副作用。

本仓库不提供通用一键生产 restore：不同 fnOS 布局与业务写入者无法由一个默认脚本安全推断。已有隔离比对也不是生产激活演练。
