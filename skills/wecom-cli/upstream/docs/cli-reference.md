## 使用说明

### 配置凭证 `init`

交互式配置企业微信机器人凭证，加密存储到本地。仅需执行一次。
- 若选择手动配置 Bot ID 和 Secret，获取方式[参考](https://open.work.weixin.qq.com/help2/pc/cat?doc_id=21677)
- 若选择扫码接入，需使用企业微信扫码创建绑定

```bash
wecom-cli init
```

### 查看帮助 `--help`
支持获取各级命令的使用方式

```bash
# 列出所有支持的命令和品类
wecom-cli --help

# 列出指定品类下的所有工具
wecom-cli <category> --help

# 列出指定工具的所需要的输入
wecom-cli <category> <method> --help
```

说明：
- 分类工具列表和工具 schema 都需要动态获取，因此“查看帮助”需要凭证与网络。

### 调用工具

通用格式：

```bash
wecom-cli <category> <method> [json_args] 
```
其中 `category` 为业务品类标识，支持以下值：

| category   | 品类          |
| ---------- | ------------- |
| `contact`  | 通讯录        |
| `doc`      | 文档/智能表格 |
| `meeting`  | 会议          |
| `msg`      | 消息          |
| `schedule` | 日程          |
| `todo`     | 待办          |

工具调用行为：
- `wecom-cli <category>` 获取该品类下的支持调用工具
- `wecom-cli <category> <method> --help`  获取该指定工具的参数定义
- `wecom-cli <category> <method>`  执行调用工具并指定参数为'{}' 
- `wecom-cli <category> <method> 'json_args'`  执行该工具调用

示例：
```bash
## 调用工具 — 获取通讯录可见范围内的成员列表
wecom-cli contact get_userlist '{}'

## 调用工具 — 创建文档
wecom-cli doc create_doc '{"doc_type": 3, "doc_name": "项目周报"}'
```

补充说明：
- 工具调用默认超时为 30 秒；`get_msg_media` 超时为 120 秒。
- `get_msg_media`会把媒体文件下载到本地临时目录，返回结果字段`local_path`为文件保存的路径 。


## 运行时路径

| 项目 | 默认位置 | 备注 |
| --- | --- | --- |
| 配置目录 | `~/.config/wecom` | 可由 `WECOM_CLI_CONFIG_DIR` 覆盖 |
| 机器人凭证 | `<config_dir>/bot.enc` | 配置凭证时创建 |
| MCP 配置缓存 | `<config_dir>/mcp_config.enc` | 配置凭证后更新 |
| 媒体临时目录 | `<system_tmp>/wecom/media` | 可由 `WECOM_CLI_TMP_DIR` 覆盖根目录 |

## 环境变量

| 变量 | 作用 |
| --- | --- |
| `WECOM_CLI_CONFIG_DIR` | 覆盖默认配置目录 |
| `WECOM_CLI_TMP_DIR` | 覆盖媒体临时目录的根目录 |
| `WECOM_CLI_LOG_LEVEL` | 打开 stderr 日志并设置过滤级别 |
| `WECOM_CLI_LOG_FILE` | 打开 JSON 日志输出，按天写入 `ww.log` |
| `WECOM_CLI_MCP_CONFIG_ENDPOINT` | 覆盖默认 MCP 配置接口地址 |
