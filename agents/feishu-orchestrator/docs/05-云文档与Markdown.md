# 云文档与 Markdown

**对助手说**：「把这份纪要整理成飞书文档」「读一下这个文档链接」

**实测命令**：

```bash
lark-cli docs +create --doc-format markdown \
  --content '<title>标题</title>
正文' --as user
lark-cli markdown +create --name x.md --content @./x.md --as user
```

**要点**：
- `lark-doc` 管的是**在线文档的正文**；`lark-markdown` 管的是**云空间里作为普通文件存放的 `.md`**。两者是不同对象，别混。
- 把本地 Markdown 变成在线文档要走导入（`drive +import --type docx`），不是 `markdown +create`。
- 复制文档用 `drive +copy`，**不要**「读出来再新建一份」——那会丢格式、评论和权限。
- 所有 `@file` 路径**只接受相对路径**，绝对路径会被拒为 `unsafe file path`。

---

> 命令与结论均来自真机验证（2026-09-01，220 个已授权 scope）。未实际跑通的能力在[能力边界](./13-能力边界.md)中如实标注。
> 返回：[Agent 说明](../README.md) · [文档索引](./README.md)
