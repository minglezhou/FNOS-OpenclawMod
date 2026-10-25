# 升级后验收与常见故障

## 一次有意义的验收

确认 core 与项目依赖版本、实际 Node/Bun、配置校验、Doctor 迁移结果；从原管理入口启动后查 listener、启动阶段、数据库完整性与 WebUI。随后选一个实际使用模型做简短回复/必要工具验收，不全量重复测所有 provider。最后核必要 cron 的自然运行与外发结果。

“安装 exit=0”“config valid”“端口监听”“WebUI 打开”“模型 available”“单次回复”“业务数据正确”是不同证据，不互相替代。没有新失败不继续叠测试套件。

| 症状 | 优先检查 | 不要直接做 |
|---|---|---|
| Gateway 不存在，壳仍在 | Gateway 日志/最近启动 stderr、实际配置路径 | 反复点重启或装回旧 core |
| valid 但启动失败 | runtime-only 认证约束、迁移要求、Node 原生加载 | 认定 validate 已证明能启动 |
| 首次打开连接中 | 冷启动阶段、后台完整性校验、WS 鉴权 | 立即 SIGKILL |
| 长时间运行后仍连接中 | 正确 basePath HTTP、WS/F12、远程代理链 | 全归因于冷启动或 bridge |
| 根路径 HTTP 404 | 实例真正 basePath | 以 404 证明 UI 无法访问 |
| 解码失败 HTTP 200 | Bun fetch 解压与转发 Content-Encoding/Length 是否一致 | 盲改网络或删除所有响应头 |
| EACCES | 应用用户、文件 owner、具体路径元数据 | 全盘 chown -R |
| 更新提示 unmanaged install | 当前安装类型与包管理器 | 强行全局安装或改壳安装状态 |
| bridge 缺 key、本地 502 | HOME、原凭据来源、可读性 | 打印 key 或把对话 key 挪作 embedding |
| cron 60 秒模型阶段超时 | payload 是否 agentTurn，是否需要推理 | 把时间加到无限或重启 embedding |
| 插件版本与壳 pin 不同 | 已装版本/实际兼容、重装路径副作用 | 点重装把新插件降回旧 pin |

## 具体历史边界

认证 mode 曾需明确选择 token；不要机械设置所有用户的 auth.mode 或清除其 password。allowedOrigins 与 trustedProxies 需依据实际可信代理链；不要开 `*`、伪造客户 IP、关闭设备认证或把“strip forwarded headers”作为公共默认修复。Cloudflare 外网访问是独立配置任务，本文无已部署结论。

日志候选：包装 `info.log`、实例 `gateway.log`、`/tmp/openclaw/openclaw-YYYY-MM-DD.log`。默认只读相关时间窗并脱敏；不要上传原始日志/配置。MaxListeners 警告或 lease 等待不等于退出根因，先关联实际退出码与阶段。保留现场，不按锁年龄单独删锁。

## 恢复优先级

可用服务不为补齐形式验收反复重启。明确错误 → 最小修改 → 一次结果验证。若已经恢复，等待自然使用证据；只有重现远程 UI 故障时再采 F12，且遮盖 token/query/header。定时备份失败和健康脚本成功也要分别处理，不能互相覆盖。
