## 核心概念

- **视频会议（Meeting）**：飞书视频会议实例，通过 meeting_id 标识。
- **会议纪要（Note）**：视频会议结束后生成的结构化文档，包含主纪要和逐字稿。
- **妙记（Minutes）**：飞书智能会议纪要服务，支持视频/音频的转写和智能总结，通过 minute_token 标识。
- **主纪要文档（MainDoc）**：会议纪要的主文档，包含 AI 生成的总结和待办。
- **逐字稿（VerbatimDoc）**：会议的逐句文字记录，包含说话人和时间戳。

## 资源关系

```
Meeting (视频会议)
├── Note (会议纪要)
│   ├── MainDoc (主纪要文档)
│   ├── VerbatimDoc (逐字稿)
│   └── SharedDoc (会中共享文档)
└── Minutes (妙记)
    ├── Transcript (文字记录)
    ├── Summary (总结)
    ├── Todos (待办)
    └── Chapters (章节)
```

> **注意**：`+search` 只能查询已结束的历史会议。查询未来的日程安排请使用 [lark-calendar](../lark-calendar/SKILL.md)。
>
> **优先级**：当用户搜索历史会议时，应优先使用 `vc +search` 而非 `calendar events search`。calendar 的搜索面向日程，vc 的搜索面向已结束的会议记录，支持按参会人、组织者、会议室等维度过滤。
