# AgentFS script Tool contract

Use for bounded, independently callable operations. The current client's `toolFrontmatterSchema` and `scriptExecutionConfigSchema` are authoritative (`packages/schemas/src/agent/tool-frontmatter.ts` in the main repository). This example is not a replacement for the actual contract.

## Files and parameters

Place `TOOL.md` and the entry file under the actual AgentFS root's `agents/<own-id>/tools/<tool-id>/`, within current file authority. Each invocation runs in that tool directory; this does not create a filesystem sandbox. The following harmless teaching example is not an installed tool.

`TOOL.md` has YAML frontmatter; JSON is valid YAML:

```markdown
---
{
  "name": "ExampleEcho",
  "description": "Return the supplied text without accessing devices.",
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
    "properties": { "message": { "type": "string", "description": "Text to return." } }
  }
}
---
Return the actual input to verify the tool call chain.
```

Adjacent `run.cjs`:

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

`script.runtime: node` uses only an already discovered managed Node, with command identifying a static entry inside the tool directory. A missing runtime fails explicitly without download or PATH fallback; establish actual managed Node availability first. For another runtime, omit runtime, set command to its real executable and pass the script path/options separately in `script.args`. Execution does not use a shell; do not place a shell program or variable user command in command.

Parameters arrive as stdin JSON; stdout carries results and stderr diagnostics. JSON success cannot override a nonzero exit code. Install dependencies where this entry can actually resolve them and retain locked versions; do not assume access to a development workspace's node_modules or virtual environment. The default timeout is 30000 milliseconds, at most 600000. A new process per call is not a persistent device connection.

## Save, refresh and call

Use the original Write/Edit tools to author complete material, then `RefreshAgentFS(changeTypes=["tool"])` to refresh your own registry and inspect failure diagnostics. Alternatively, when the current local API contract permits it, `POST /api/agents/<own-id>/tools` creates only a skeleton with name, description, executor, risk_level and body. Complete command/script/input_schema still require the full TOOL.md or `PUT /api/agents/<own-id>/tools/<tool-id>` with `{content: "complete TOOL.md"}`. Mediated, remote or unavailable management access does not justify finding a platform token.

Inspect purpose and current visibility through `ToolCatalog`. If an exact known name is undeclared, use `LoadTools(names=["actual tool name"])` (registered identity DiscoverTools); call the actual declaration on the next model request. Refresh does not widen a Run's fixed tool ceiling; changes to an already bound definition may require the next turn or a new session. For a missing name, inspect refresh diagnostics, enabled state, permissions and Run ceiling instead of inventing a result.

Actually invoke a harmless input, inspect output and invalid parameters plus relevant failure/timeout cases, then validate business operations on authorized hardware. Rediscover and call after restart. Tools belong to their Agent by default; copying/installing for another Agent follows that target's original authorization and is not global publication.
