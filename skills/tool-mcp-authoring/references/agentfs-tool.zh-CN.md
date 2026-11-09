# AgentFS 脚本 Tool 合同

适用于有限时长、可独立调用的操作。权威字段为当前客户端的 `toolFrontmatterSchema` 和 `scriptExecutionConfigSchema`（主仓 `packages/schemas/src/agent/tool-frontmatter.ts`），不能以本例替代实际工具合同。

## 文件与参数

在实际 AgentFS 根的 `agents/<自身 id>/tools/<tool-id>/` 保存 `TOOL.md` 和入口文件，读写仍需当前目录权限。每次脚本调用的工作目录为该工具目录；脚本没有因此获得文件系统沙箱。下面是无硬件副作用的教学示例，不是已经安装的工具。

`TOOL.md` 使用 YAML frontmatter；JSON 也是合法 YAML：

```markdown
---
{
  "name": "ExampleEcho",
  "description": "返回传入的文本；不访问设备。",
  "risk_level": "low",
  "executor": "script",
  "status": "enabled",
  "command": "run.cjs",
  "script": { "runtime": "node", "timeout": 5000 },
  "input_schema": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["message"],
    "additionalProperties": false,
    "properties": { "message": { "type": "string", "description": "需要返回的文本。" } }
  }
}
---
返回实际输入，用于验证工具调用链。
```

同目录 `run.cjs`：

```javascript
let input = ''
process.stdin.setEncoding('utf8')
process.stdin.on('data', chunk => { input += chunk })
process.stdin.on('end', () => {
  try {
    const { message } = JSON.parse(input)
    if (typeof message !== 'string') throw new Error('message must be a string')
    process.stdout.write(JSON.stringify({ success: true, content: message }))
  } catch (error) {
    process.stderr.write(String(error))
    process.exitCode = 1
  }
})
```

`script.runtime: node` 只使用已发现的受管 Node，command 必须是工具目录内静态入口；缺运行时会明确失败，不下载也不回退 PATH。先确认真实受管 Node 可用。选择其它运行时则省略 runtime，command 为实际可执行文件，脚本路径与选项用 `script.args` 独立传递。它们不经过 shell；不要把一段 shell 程序或可变用户命令塞进 command。

`node --version` 或 `process.execPath` 只证明该解释器可运行，不证明它属于平台受管 Node。若当前只确认了系统 Node，可省略 `script.runtime`，将已验证的可执行文件绝对路径作为 command，`script.args` 使用 `["run.cjs"]`；路径含空格也保持为完整字符串。遇到 `SCRIPT_RUNTIME_UNAVAILABLE` 时重新核实这两种配置，不以 Bash 中运行成功替代实际 Tool 调用。

参数通过 stdin JSON 传入；stdout 返回结果，诊断写 stderr。返回 JSON 的 success 不能覆盖非零退出码。依赖应安装在真实可解析的位置并记录锁定版本，不假设工具目录能读取开发工作区的 node_modules/虚拟环境。默认 timeout 为 30000 毫秒，最大 600000；持久设备连接不要依赖每次启动的脚本进程存活。

## 保存、刷新和调用

可直接用原 Write/Edit 编写完整材料，再调用 `RefreshAgentFS(changeTypes=["tool"])` 刷新自身注册表，检查失败诊断。也可按当前可用的本机 API 合同创建：`POST /api/agents/<自身 id>/tools` 只生成名称、描述、executor、risk_level 和 body 等骨架；完整 command、script、input_schema 仍须通过完整 TOOL.md 或 `PUT /api/agents/<自身 id>/tools/<tool-id>` 的 `{content: "完整 TOOL.md"}` 补齐。受中介约束、远端或不可用的管理入口不能靠找 token 绕过。

用 `ToolCatalog` 检查用途和当前可见性；已知准确名称而未声明时，使用 `LoadTools(names=["实际工具名"])`（注册身份 DiscoverTools），加载后按真实声明发起下一次模型调用。刷新成功不代表当前 Run 固定上限扩大；改动已经绑定的定义可能需下一轮或新会话。名字缺失时核对刷新诊断、启用状态、权限与 Run 上限，不伪造调用结果。

`RefreshAgentFS` 不替换本轮已经绑定的执行实现。修改已加载 Tool 的 command/runtime 等配置后，如果调用仍使用旧配置，在下一轮或新会话重新发现并验证，不反复刷新重试旧实现；也不以 Bash 直接运行脚本的成功代替正式 Tool 调用回执。

先真实调用无副作用输入，检查输出、非法参数及必要的失败/超时；再在授权设备上验证业务。重启后重新发现并调用。工具默认属于自身 Agent；其他 Agent 的复制/安装和配置沿目标原授权，不因这里创建了目录就全局可用。
