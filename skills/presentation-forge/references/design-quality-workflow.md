# Anti-AI-slop 设计质量门

所有新生成页面在正式构建或全量生图前运行：

```bash
python scripts/validate_design_quality.py --session <session>
```

报告固定写入 `reports/design-quality.json`，统一质量门必须读取它。原生可编辑 Deck 构建器会在创建 PowerPoint 对象之前自动运行同一检查。

## 硬错误

- 正文出现设计说明、配图建议、讲者备注或 prompt 文本。
- 默认启用阴影或渐变；只有带明确设计理由的例外才可进入 spec。
- 可编辑模式使用覆盖 85% 以上页面的独立图片对象冒充背景或整页设计。

硬错误使报告成为 `FAIL`，禁止继续生产构建。

## 启发式警告

- 同页超过 4 个卡片，存在无意义卡片化风险。
- 同页超过 5 个圆角矩形。
- 出现无语义的窄边强调条。
- 形状上叠加独立文本框，而文字本可写入形状或通过留白分组。

警告使报告成为 `WARN`。先修复；确有设计理由时，在 `native_deck_spec.json.design_exceptions` 记录 `code`、`slide_number` 和非空 `reason`。不要使用全局“全部忽略”。

```json
{
  "design_exceptions": [
    {"code": "shape-with-overlay-textbox", "slide_number": 4, "reason": "该文本需要独立动画与可访问性朗读顺序。"}
  ]
}
```

设计门只判断结构性坏味道，不替代逐页视觉检查。通过检查也不代表页面已经具有良好构图。
