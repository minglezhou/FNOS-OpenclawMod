# Node、Bun 与重要依赖

## 先判断是否需要动

目标 core 的 package.json engines 是必要输入，实际 Node 还需能加载当前平台上的原生依赖。案例中 Node 24.19.0 满足当时 core engines，**没有为了升级 core 再换 Node**。保持兼容 runtime 可显著减少变更面。

| 对象 | 推荐边界 |
|---|---|
| fnOS 平台 Node/Bun | 共享依赖由平台管理；不直接覆盖 `/var/apps/*/target/bin` 或其物理目标 |
| OpenClaw 私有 Node | 并排版本目录，先 stage；只有确认启动链消费稳定指针后才能切换 |
| 安装专用 Bun | 可选私有二进制，仅用于包安装；不会改变正在运行的壳 Bun |
| core 依赖/原生插件 | 使用当前包管理器处理依赖树；不要手工复制不同 Node ABI 的 node_modules |
| 包装供应的补丁 | 升级后重新核匹配，不按旧行号 sed 盲打 |

## 私有 Node 的可行路径

`stage-node.sh` 要求精确版本、x64/arm64、可信来源的 SHA256 和新目录。它下载官方 Linux 包、验证摘要、检查归档路径，再解压并核版本；不切换任何生产 symlink。官方 SHASUMS 签名验证方法见 SOURCES；与 tarball 同源下载的摘要可校验传输，但不能单独替代来源认证。

维护前检查：架构、glibc/原生模块兼容、目标 engines、空间、目录读写权限、现有稳定指针和实际进程 exe。升级前记录原 link target；维护窗口内可将稳定 symlink 原子切到已验证的新目录。**若壳硬编码旧 runtime，而不读取该指针或可配置 PATH，则无法在完全不动壳的前提下让壳采用新 Node。** 此时保留兼容 runtime、使用平台支持设置，或把最小壳改动作为独立任务。

不要覆盖旧版本目录；新进程用新 Node、旧进程仍持有旧 inode。启动后通过当前 PID 的 exe 确认；单看 shell 版本不够。rollback 必须同时考虑原生模块与状态迁移，不能仅切回 symlink 就宣称恢复完成。

## Bun 与缓存

本次历史安装使用 Bun 1.3.9；没有证明必须升级 Bun。目标升级确需新版包管理功能时，另行下载可信官方发行物到私有目录，仅把安装脚本 BUN_BIN 指向它；这与包装 server 使用的 Bun 是不同决定。

Bun 的 trustedDependencies 控制相关 lifecycle 执行，脚本使用 `--trust` 只为 OpenClaw 显式添加信任，不信任整个依赖生态。审查目标 lifecycle；默认缓存可能硬链接到 node_modules，原位修改 dist 可能同步改变缓存副本。不要把“只改一个文件”当成只影响一个目录。
