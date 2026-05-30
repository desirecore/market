# Built-in Templates (内置模板)

Ready-to-use, brand-styled Mermaid for DesireCore's own architecture patterns.
Adapt the labels to the user's subject; keep the header and `classDef`s intact.
All four are verified to render.

## 1. Agent architecture (Agent 架构图)

Mirrors the delegate / skills / memory layout (`lib/agent-service/builtin-tools/delegate.ts`).

```mermaid
%%{init: {'theme':'base','themeVariables':{'primaryColor':'#F0F5FF','primaryBorderColor':'#007AFF','primaryTextColor':'#1d1d1f','lineColor':'#6e6e73','fontFamily':'-apple-system,SF Pro Text,Noto Sans SC,sans-serif'}}}%%
flowchart TD
    classDef agent  fill:#F6F3FF,stroke:#AF52DE,color:#1d1d1f
    classDef system fill:#F0F5FF,stroke:#007AFF,color:#1d1d1f
    classDef biz    fill:#F0FDF4,stroke:#34C759,color:#1d1d1f

    U(["User"]):::biz
    Core("DesireCore Core"):::system
    A1{{"Legal Agent"}}:::agent
    A2{{"Data Agent"}}:::agent
    Skills["Skills / MCP Tools"]:::biz
    Mem[("Conversation Memory")]:::system

    U --> Core
    Core --> A1
    Core --> A2
    A1 --> Skills
    A2 --> Skills
    A1 -.-> Mem
    A2 -.-> Mem
```

## 2. Delegate 6 modes (Delegate 六种模式)

The unified delegate tool and its six execution modes.

```mermaid
%%{init: {'theme':'base','themeVariables':{'primaryColor':'#F0F5FF','primaryBorderColor':'#007AFF','primaryTextColor':'#1d1d1f','lineColor':'#6e6e73','fontFamily':'-apple-system,SF Pro Text,Noto Sans SC,sans-serif'}}}%%
flowchart LR
    classDef system fill:#F0F5FF,stroke:#007AFF,color:#1d1d1f
    classDef agent  fill:#F6F3FF,stroke:#AF52DE,color:#1d1d1f

    D("Delegate Tool"):::system
    D --> S["sync: block & await"]:::agent
    D --> AS["async: fire & report back"]:::agent
    D --> W["worker: ephemeral SubAgent"]:::agent
    D --> F["fan-out: parallel / sequential"]:::agent
    D --> H["handoff: hand session to user"]:::agent
    D --> V["via-messaging: fallback wait"]:::agent
```

## 3. Three-tier conversation memory (三层对话记忆)

active → recent (L0/L1) → archive (L2); writes are dotted
(`lib/schemas/agent-service/conversation-memory.ts`).

```mermaid
%%{init: {'theme':'base','themeVariables':{'primaryColor':'#F0F5FF','primaryBorderColor':'#007AFF','primaryTextColor':'#1d1d1f','lineColor':'#6e6e73','fontFamily':'-apple-system,SF Pro Text,Noto Sans SC,sans-serif'}}}%%
flowchart LR
    classDef system fill:#F0F5FF,stroke:#007AFF,color:#1d1d1f
    classDef warn   fill:#FFFBF0,stroke:#FF9500,color:#1d1d1f

    New(["New Message"]):::warn
    Active["active: ongoing matters"]:::system
    Recent["recent: L0 / L1 summaries"]:::system
    Archive[("archive: L2 full log")]:::system

    New --> Active
    Active -.->|compact| Recent
    Recent -.->|archive after 180d| Archive
```

## 4. Relation graph (关系图谱，6 种边)

The six edge types projected by `lib/agent-service/relations/projector.ts`, each
drawn with a distinct edge style. Edge weight decays over time (30-day half-life).

```mermaid
%%{init: {'theme':'base','themeVariables':{'primaryColor':'#F0F5FF','primaryBorderColor':'#007AFF','primaryTextColor':'#1d1d1f','lineColor':'#6e6e73','fontFamily':'-apple-system,SF Pro Text,Noto Sans SC,sans-serif'}}}%%
flowchart TD
    classDef agent fill:#F6F3FF,stroke:#AF52DE,color:#1d1d1f
    classDef biz   fill:#F0FDF4,stroke:#34C759,color:#1d1d1f

    A1{{"Agent A"}}:::agent
    A2{{"Agent B"}}:::agent
    A3{{"Agent C"}}:::agent
    U(["User"]):::biz

    A1 -->|delegate| A2
    A1 -.->|mention| A3
    A2 ===|co_task| A3
    A2 --o|hierarchy| A1
    A3 -->|seek_help| A1
    A1 --x|escalation| U
```

## Other diagram types

For sequence / state / ER / class diagrams, keep the same `%%{init}%%` header for
a consistent light theme. Example sequence diagram:

```mermaid
%%{init: {'theme':'base','themeVariables':{'primaryColor':'#F0F5FF','primaryBorderColor':'#007AFF','primaryTextColor':'#1d1d1f','lineColor':'#6e6e73','fontFamily':'-apple-system,SF Pro Text,Noto Sans SC,sans-serif'}}}%%
sequenceDiagram
    actor U as User
    participant C as DesireCore Core
    participant A as Sub-Agent
    participant M as Memory
    U->>C: request
    C->>A: delegate (sync)
    A->>M: write fact
    A-->>C: result
    C-->>U: reply
```
