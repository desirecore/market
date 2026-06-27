# Helpers — 人类需求模板

当你需要创建新 helper 时，请向模型提供以下信息：

**命令格式**

```bash
wecom <category> +<helper_name>
```

**行为描述**

e.g.

1. 调用 category.method { ...req_example } { ...res_example }
2. 随后调用 category.method2 { ...req_example }
3. 返回步骤 2 的结果
