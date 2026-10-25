# 日常配置：应该在哪里改

| 要改什么 | 优先入口 | 说明 |
|---|---|---|
| fnOS 应用启停/平台依赖 | fnOS 面板 | 不用系统 daemon 命令猜管理方式 |
| 实例入口、包装代理、包装功能 | 包装管理页及已确认的包装配置接口 | 页面可能直接写主配置；先核实际消费路径 |
| 模型 provider/defaults/别名/allowlist | OpenClaw 支持的配置 CLI/WebUI | schema 与当前版本一致；不手改生成 models.json |
| 单会话模型/思考档 | OpenClaw 会话选择器 | 会话覆盖可能保留，改 defaults 不一定改变旧会话 |
| cron | 受支持 cron CLI/工具 | 不编辑 SQLite；command 与 agentTurn 分开 |
| 用户偏好与工作规则 | workspace 的 USER/AGENTS/SOUL 等 MD | 保留用户改动，项目进度放项目 STATE |
| Skills | 支持的 enabled/archive/workshop 配置 | 不手搬托管目录，不因一次报错生成新 skill |
| 独立 bridge | 自己的 supervisor/脚本/受限凭据来源 | 必须显式带正确 HOME；不借用对话 key 盲试 |

## 标准方法

先核 CLI `config file` 与当前 schema/help，读最少字段 → 备份私有基线 → 结构化修改 → validate → 回读 → 一次必要功能验收。文件级恢复要检测后续编辑。不要把任何 `--dry-run` 都当无写入；历史 update preview 路径曾有 ledger 写入静态证据。

主配置通常在 `$APP_HOME/.openclaw/openclaw.json`，但 cron、会话状态、凭据 store 与包装实例数据库不是它的附属 JSON 字段。“唯一真源”仅适用于已确认的主配置消费，不代表整个应用只有一个状态源。进程 env 注入也可能影响行为。

## 模型经验（案例政策，不自动配置他人账户）

全局主模型 Flash/max；K3-256K 使用按模型 high，K3.1 Pro 使用 max；GLM/Ark 保留各自 provider。不要为了按模型默认把全局强制覆盖所有模型。已有源码报告显示会话、agent、按模型 params、全局与 provider 默认分层；cron payload 的显式档位另查其解析链。

MiniMax 正式版 ID 曾未命中 Preview 专属 thinking hook，导致 UI 档位和请求映射不同；本地窄补丁解决案例，但会被升级覆盖。`ultra` 是 harness 模式，不是官方 max 同义词。Kimi 当前能回复不能证明候选 provider 插件已安装，亦不能证明全部 effort/工具/上下文额度已验收。配置方案必须匹配 Code 订阅与按量 API 的实际路线。

Ollama 多余目录项曾来自包装对子进程注入环境，而不是 `.env` 或用户配置中的显式 provider。不要为删除目录行删掉使用相同端口协议的 embedding bridge。排查环境只输出白名单变量的存在布尔值，不打印内容。

## MD、记忆与 Skills

常驻 MD 留稳定规则和偏好，MEMORY 留稳定事实/项目入口，STATE 留阶段进度，日记记有价值变化。旧 choices、逐问落盘、全局 session-state 同步和全量周期摘要不是升级后的必需机制。停用自定义摘要任务保留定义与历史，不删除托管 transcript/索引/DREAMS。

案例选择关闭 workshop 自主生成，人工按重复需求评审已有 skill；这是用户政策，不是必须禁用所有用户的学习能力。变更指令后新会话按需确认，不为了 MD 重启 Gateway。

## Cron 与 bridge

简单观测用 `--command-argv`，不要每五分钟起大模型高档推理。完整命令见 COMMANDS；先保存任务定义，仅替换 payload 所需字段，保持 schedule/delivery/enabled 等既有意图。`health.py` 只判本地服务活着，不证明 embedding 上游与检索正常。

未实现的 `/ready`、热重载凭据、精确 PID supervisor 等不因写进提案就算部署完成。成功恢复既有 HOME 与凭据路径后不重复换 key 或重建索引。
