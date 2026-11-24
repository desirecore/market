<!-- locale: zh-CN -->

# 游戏开发 Agent 技能合集

## 范围与来源

这个可选 Apache-2.0 本地包收录 `skills/` 下 79 个游戏开发技能，并在包根目录和每个子技能中放入 [LICENSE](LICENSE) 与 [NOTICE](NOTICE)。详见 [UPSTREAM.md](UPSTREAM.md)。引擎运行时不随包提供。

经过审阅的中英子技能摘要见 [references/child-summaries.json](references/child-summaries.json)。

| 标识 | 摘要 |
|---|---|
| `ai-behavior-trees-utility-ai` | 引擎中立的 NPC 行为树与效用 AI 代码，适用于任何语言：黑板、反应式组合节点、装饰器与响应曲线评分。用于敌人丢失视线后仍追击、每帧重启动作，或在选项间反复横跳。不用于 FSM、转向或寻路（`game-ai`），也不用于 Unreal 的 BT、EQS 与 StateTree（`unreal-behavior-trees`）。 |
| `audio-design` | 引擎中立的游戏音频方法：总线布局、以分贝为单位的音量滑条、响度、对白时压低音乐、自适应音乐与音效变化，并对照 Godot、Unity 与 FMOD/Wwise。用于混音、让音乐随战斗变化、修复重复脚步或节拍同步，或处理削波与泵感。不用于 Godot 音频 API（`godot-audio`）。 |
| `camera-systems` | 构建并调校游戏摄像机，引擎中立，并对照 Godot 与 Cinemachine 3：带死区和预瞄的 2D 跟随、第三人称环绕、第一人称视角与分屏。用于摄像机滞后、跟随抖动、露出关卡边缘、穿墙或随帧率变化。不用于震动（`game-feel`）或物理时间步抖动（`physics-tuning`）。 |
| `create-game-assets` | 规划、生成或采购并校验风格一致的游戏美术：风格指南、精灵、像素画、图块集、图标与纹理，附带 QA 与许可记录。用于制作或用 AI 生成游戏美术、修复假透明，或检查 Steam AI 披露。不用于引擎导入（`godot-tilemap`、`godot-animation`、`unity-tilemap-2d`）、UI 布局（`game-ui-ux`）或声音（`audio-design`）。 |
| `dialogue-systems` | 用 Ink、Yarn Spinner 或小型 JSON 图运行器构建引擎中立的分支对话：台词、选项、条件、变量与本地化 ID。用于 NPC 对话、对话树、短喊、.ink 或 .yarn 文件，或走进死胡同的对话。不用于视觉小说回顾与跳过（`visual-novel`）、任务（`rpg`）或文本框控件（`godot-ui-control`、`game-ui-ux`）。 |
| `game-ai` | 设计引擎中立的敌人与 NPC AI：在 FSM、行为树、效用或 GOAP 中选择，并构建感知、转向与 A* 寻路。用于巡逻与追击、“找到通往玩家的路径”、卡在拐角的智能体，或能透视墙壁的 AI。不用于行为树或效用代码（`ai-behavior-trees-utility-ai`）、Unreal AI（`unreal-behavior-trees`）或 Unity NavMesh（`unity-navmesh`）。 |
| `game-feel` | 为已能运行的机制加入引擎中立的手感：基于创伤的屏幕震动、击停、缓动补间、挤压拉伸与击退。用于游戏发飘、没重量或不够脆，或希望命中与跳跃更爽。不用于土狼时间（`platformer`）、输入缓冲（`input-systems`）、摄像机跟随（`camera-systems`）或 HUD 布局（`game-ui-ux`）。 |
| `game-ui-ux` | 游戏 HUD 与菜单的引擎中立设计规则：锚点与容器、缩放、安全区、手柄焦点、由事件而非轮询驱动的 HUD，以及无障碍下限。用于超宽屏或手机上会坏掉的菜单、血条或背包界面。可与 `godot-ui-control` 或 `roblox-ui` 搭配。不用于按钮手感（`game-feel`）或按键重绑定（`input-systems`）。 |
| `input-systems` | 引擎中立的输入架构，并含 Godot InputMap 代码：命名动作、摇杆死区、缓冲按下，以及带冲突检查的重绑定。用于手柄支持或重绑定菜单，或摇杆漂移、AZERTY 上的 WASD、丢失的按键。不用于土狼时间（`platformer`），也不用于 Unity 与 Unreal 的输入资产（`unity-input-system`、`unreal-enhanced-input`）。 |
| `level-design` | 引擎中立的关卡设计，并含 Godot 检查：来自真实控制器的玩家度量、带软锁检查的钥匙与能力门，以及节奏。用于布置关卡或类银河战士恶魔城门，或玩家迷路、钥匙被挡在自己的门后。不用于生成（`procedural-gen`）、绘制图块（`godot-tilemap`、`unity-tilemap-2d`）或跳跃手感（`platformer`）。 |
| `performance-optimization` | 通过在 Godot、Unity、Unreal 或 Roblox 中测量来查找并修复帧率问题：先分清 CPU 还是 GPU 受限，再做最大项修复（绘制调用、对象池、GC 尖峰）。用于低帧率、卡顿、首次使用卡顿，或要求优化/剖析。不用于包体大小（`unity-build-size`）、物理抖动（`physics-tuning`）或网络延迟（`roblox-networking`、`godot-multiplayer`）。 |
| `physics-tuning` | 引擎中立的物理调校，并含 Godot 检查：固定时间步与插值、防止穿透的 CCD、阻尼、求解器迭代与碰撞层矩阵。用于物体抖动、高速物体穿墙，或物理发飘/不对。不用于各引擎物理 API（`godot-physics`、`unity-physics`、`roblox-physics`、`phaser-arcade-physics`）或跳跃手感（`platformer`）。 |
| `procedural-gen` | 引擎中立的程序生成，以 Python 实现并对照 Godot 与 Unity：带种子的 RNG、地牢布局、波函数坍缩、噪声地形与掉落表。用于地牢生成器、WFC 或 Perlin 地形，或同一种子给出不同地图。不用于 roguelike 局结构（`roguelike`）、卡组构筑（`card-game`）或绘制图块（`godot-tilemap`、`unity-tilemap-2d`）。 |
| `save-systems` | 引擎中立的存档与读档，并含 Godot 与 Python 代码：序列化范围、槽位与自动存档、原子写入与带版本的迁移。用于存读档或继续按钮，或崩溃后存档损坏、补丁后无法读取。不用于 Roblox DataStores（`roblox-datastores`）、数据资产（`godot-resources`、`unity-scriptableobjects`）或类型化存档界面（`rpg`、`visual-novel`）。 |
| `shader-programming` | 引擎中立的着色器方法，以 GLSL 讲述并给出 HLSL 对应：溶解、描边、菲涅尔轮廓与后期效果的原理，以及 GLSL 到 HLSL 的移植。用于效果数学本身，或斑点、移动端闪烁。若只在某一引擎写着色器，单独使用该引擎技能即可（`godot-shaders`、`threejs-materials-lighting`、`pixijs-rendering`）。不用于粒子（`unreal-niagara`）。 |
| `ebitengine-game` | 用 Go 与 Ebitengine v2 创建、调试并打包 2D 游戏：可重试的游玩循环、输入、像素画缩放、文字、音频，以及桌面、WASM 或移动构建。用于 go.mod 依赖 ebiten/v2，或用户要用 Go 做游戏，或像素画模糊、按键丢失、卡顿。不用于引擎补丁；设计可搭配 `game-feel`、`game-ui-ux` 或类型技能。 |
| `card-game` | 在任何引擎中设计卡牌游戏与构筑玩法：把卡牌做成数据并配合一个效果解释器，以及牌库区域、触发栈与带种子的洗牌。用于类杀戮尖塔或 Balatro、TCG，或卡牌复制、洗牌连张。卡牌数据与手牌 UI 可搭配引擎技能（`godot-resources`、`godot-ui-control`、`unity-scriptableobjects`）。不用于网格爬行（`roguelike`）。 |
| `fps-shooter` | 在任何引擎中设计第一人称射击战斗：命中扫描与抛射物、击杀时间、伤害衰减、后坐力模式、瞄准镜灵敏度与延迟补偿命中。用于类 Doom 或 CS 的玩法，或枪感到弱、射击不结算。不用于摄像机装置（`camera-systems`）、震动与击停（`game-feel`）或射线 API（`godot-physics`、`unity-physics`）。 |
| `platformer` | 在任何引擎中设计 2D 平台跳跃：跳跃手感（土狼时间、跳跃缓冲、可变高度、下落重力、拐角修正）、墙跳、危险、检查点与单向平台。用于类马里奥或蔚蓝，或跳跃发飘、滞后。可搭配引擎技能（`godot-2d-movement`、`phaser-arcade-physics`）。不用于通用输入缓冲（`input-systems`）或手感汁液（`game-feel`）。 |
| `puzzle` | 在任何引擎中设计网格与逻辑解谜：三消连锁、推箱子、唯一解网格（数织、数独）、精确撤销与经求解器检查的关卡。用于类 Candy Crush、推箱子或 Picross，或连锁损坏、撤销漂移、无解关卡。不用于物理解谜（`platformer`、`physics-tuning`）或卡牌游戏（`card-game`）。 |
| `roguelike` | 在任何引擎中设计以单局为核心的 roguelike 与 roguelite：局结构、永久死亡、局外成长、带种子与每日挑战、回合顺序与对称视野。用于类 NetHack 或哈迪斯，或单局显得廉价。地牢生成搭配 `procedural-gen`，单局与局外存档搭配 `save-systems`。不用于 roguelike 构筑（`card-game`）。 |
| `rpg` | 在任何引擎中设计 RPG 成长与战斗数值：带修正栈的属性、经验曲线、伤害公式、物品与装备（槽位、稀有度、词缀）以及任务。用于 JRPG 或类暗黑搜刮，或卸装后属性不对。角色与背包存档可搭配 `save-systems`。不用于合成与负重（`survival-crafting`）或对话（`dialogue-systems`）。 |
| `survival-crafting` | 在任何引擎中设计生存合成循环：采集、配方与科技树、负重、腐败、饥饿与温度，以及基地建造。用于类 Minecraft、Valheim 或不饿死，或合成吞材料、需求像杂务。不用于 RPG 装备数值（`rpg`）、地形生成（`procedural-gen`）或存档文件（`save-systems`）。 |
| `tower-defense` | 在任何引擎中设计塔防：车道与迷宫寻路、波次节奏、锁定优先级、装甲与飞行克制，以及金币经济，并带波次曲线检查。用于类气球塔防或 Kingdom Rush，或后期波次不可能/过于轻松、某塔一家独大。不用于寻路（`game-ai`）或生存基地建造（`survival-crafting`）。 |
| `visual-novel` | 用 Ren'Py 或任意引擎做视觉小说与选择驱动故事：路线与结局、随处存档、回顾、仅跳过已读与打字机文本。用于视觉小说或恋爱模拟，或读档错行、跳过读到未读文本、无法到达的结局。不用于更大游戏中的对话或 Ink 与 Yarn（`dialogue-systems`），也不用于文本框控件（`godot-ui-control`）。 |
| `godot-2d-movement` | Godot 4.7 中用 GDScript 写 CharacterBody2D 移动：平台跑跳、顶视角八向运动、斜坡与单向平台，并带无头落地测试。用于 2D 控制器不动、掉穿地板，或 is_on_floor() 始终为假。不用于土狼时间与跳跃手感（`platformer`）、RigidBody2D、射线或 3D（`godot-physics`），也不用于图块关卡（`godot-tilemap`）。 |
| `godot-3d-essentials` | Godot 4.7 的 3D 场景搭建：Camera3D、灯光、WorldEnvironment（天空、环境光、色调映射、雾）、StandardMaterial3D、GridMap 以及局部与全局变换，并带无头场景检查。用于 3D 场景全黑或过曝、网格不可见，或子节点绕错误轴旋转。不用于空间着色器（`godot-shaders`）、刚体与射线（`godot-physics`）或摄像机手感（`camera-systems`）。 |
| `godot-animation` | Godot 4.7 动画 API：AnimationPlayer、AnimationTree 状态机、AnimatedSprite2D 与 create_tween() Tweens，并带无头状态测试。用于 travel() 无效、动画不播放、补间弹回，或日志提示 “Animation not found”。不用于缓动选择（`game-feel`）、精灵美术（`create-game-assets`）或 Unity（`unity-animation`）。 |
| `godot-audio` | Godot 4.7 音频 API：2D/3D AudioStreamPlayer、总线布局、AudioServer 音量与静音、复音、循环导入，以及用于节拍同步的播放位置。用于在 Godot 中接线效、音乐或音量滑条，或声音静音、被切断、不循环、不遵循总线。不用于引擎中立的混音、闪避或自适应音乐（`audio-design`）。 |
| `godot-csharp` | Godot 4.7 中的 C# 与 .NET：partial 节点类、PascalCase 生命周期、[Export] 与 [Signal]、作为 C# 事件的信号、.csproj 以及调用 GDScript。用于 Godot 的 .cs 脚本、把 GDScript 迁到 C#、构建失败，或 Web/Android 导出失败。不用于 GDScript（`godot-gdscript`）、Unity C#（`unity-csharp-scripting`）或导出预设（`godot-export`）。 |
| `godot-export` | 导出 Godot 4.7 项目：模板、面向桌面、Web 与 Android 的 export_presets.cfg、命令行导出与 Web 的 COOP/COEP 头。用于 “No export template found”、空白 Web 构建、SharedArrayBuffer 错误，或导出后文件缺失。不用于 CI 测试（`godot-gdscript-headless-testing`）、商店上传（`steam-publish`、`itch-publish`）或网络同步（`godot-multiplayer`）。 |
| `godot-gdscript` | 面向 Godot 4.7 的 GDScript 2.0：静态类型、@export 与 @onready、await 与协程，以及 3.x 代码迁移。用于 .gd 解析错误（“Cannot infer the type”）、协程永不恢复、@onready 为 null，或升级破坏。不用于信号（`godot-signals-groups`）、场景（`godot-nodes-scenes`）、C#（`godot-csharp`）或 CI 测试（`godot-gdscript-headless-testing`）。 |
| `godot-gdscript-headless-testing` | 用 godot --headless 与失败时非零退出的 SceneTree 运行器来跑 Godot 4.7 GDScript 测试，以便 CI 把关合并。负责 CI 中的 Godot 测试。用于 GitHub Actions 任务，或无头运行挂起、即使有 SCRIPT ERROR 仍以 0 退出。不用于 CI 导出（`godot-export`）、GDScript 语言本身（`godot-gdscript`）或 Unity 测试（`unity-csharp-scripting`）。 |
| `godot-multiplayer` | Godot 4.7 高层多人：ENet 主持与加入、带 rpc_id() 的 @rpc、MultiplayerSpawner 与 MultiplayerSynchronizer，并带双实例无头测试。用于 Godot 在线或局域网合作，或被拒绝的 RPC、客户端缺少生成节点、状态不同步。不用于 Roblox（`roblox-networking`）、服务器导出（`godot-export`）或本机分屏（`camera-systems`）。 |
| `godot-nodes-scenes` | Godot 4.7 场景树结构：可复用的 .tscn 场景、instantiate()、自动加载，以及损坏的 res:// 路径与 uid 检查器。用于生成子弹或敌人，或出现 “Node not found”、“previously freed instance”，或文件移动后场景损坏，即使使用者只说项目坏了。不用于 GDScript 语法（`godot-gdscript`）或信号（`godot-signals-groups`）。 |
| `godot-physics` | Godot 4.7 的 2D/3D 物理 API：各种 body 与 Area 类型、collision_layer 与 mask 位、受伤盒的 Area 信号、RayCast 与空间查询，以及 Jolt（自 4.6 起为 3D 默认）。用于物体相互穿过、body_entered 从不触发，或射线打到自身。不用于引擎中立的抖动与穿透（`physics-tuning`）或 CharacterBody 移动（`godot-2d-movement`）。 |
| `godot-resources` | 用自定义 Resource 在 Godot 4.7 做数据驱动设计：class_name 与 @export 字段、.tres 文件、共享引用与 duplicate_deep()、uid 与线程加载。用于把物品、数值或敌人配置做成数据，或改一个敌人却改到所有敌人、.tres 无法加载。不用于存档槽（`save-systems`）或 C# 版本（`godot-csharp`）。 |
| `godot-shaders` | Godot 4.7 着色语言语法与管线：canvas_item、spatial 与粒子着色器、内置变量、ShaderMaterial 接线、无头编译检查以及 3.x 移植。用于 .gdshader、SHADER ERROR、从 GDScript 设置着色器参数，或效果过曝、排序错误。不用于溶解或描边等效果数学（`shader-programming`）。 |
| `godot-signals-groups` | Godot 4.7 信号与节点组：带类型的信号、用 Callable 的 connect()、一次性与延迟连接、事件总线自动加载与 call_group 广播。用于节点需通信但不要硬引用、处理函数触发两次或从不触发，或日志提示 “already connected”。不用于 GDScript 语法（`godot-gdscript`）或自动加载设置（`godot-nodes-scenes`）。 |
| `godot-tilemap` | Godot 4.7 中用 TileMapLayer 与 TileSet 做图块地图：图集源、数据层、地形自动拼接，以及运行时的 set_cell 或 local_to_map。用于 Godot 的 2D 图块关卡、没有碰撞的图块、点到错误格子，或迁移已弃用的 TileMap。不用于 Unity（`unity-tilemap-2d`）、图块美术（`create-game-assets`）或生成（`procedural-gen`）。 |
| `godot-ui-control` | Godot 4.7 用于菜单与 HUD 的 Control 节点 API：锚点、Container、Theme 与 StyleBox、焦点邻接与拉伸设置，并带无头布局检查。用于 Godot UI 重叠、缩放后漂移、按钮忽略手柄，或不可见面板吞掉点击。不用于引擎中立的 UI 规则（`game-ui-ux`；两者应一起加载）或重绑定（`input-systems`）。 |
| `bevy-ecs` | 用 Rust 构建并调试 Bevy 0.20 游戏：组件、Query 与 Commands 系统、调度、States、观察者与无头测试。用于 Cargo.toml 依赖 bevy、出现 B0001 查询冲突 panic，或 0.20 之前的代码（EventReader、SpriteBundle）。不用于引擎中立的 AI、生成、物理或着色器（`game-ai`、`procedural-gen`、`physics-tuning`、`shader-programming`）。 |
| `defold-core` | 用 Lua 构建并调试 Defold 1.14 游戏：集合、游戏对象、输入焦点、msg.post 消息、工厂、集合代理与 Bob 构建。用于 .collection 或 .script 文件、on_input 从不触发、代理永不加载，或 “could not be found when dispatching message”。不用于 LÖVE（`love2d-core`）、HUD 规则（`game-ui-ux`）或物理手感（`physics-tuning`）。 |
| `love2d-core` | 用 Lua 构建并调试 LÖVE（Love2D）11.x 游戏：main.lua 回调、conf.lua、固定步进、清晰像素缩放、love.filesystem 存档与脚本化运行。用于 main.lua 调用 love.*，或像素画模糊、蓝色错误屏、速度绑在帧率上。不用于 Defold（`defold-core`）或引擎中立的存档与输入（`save-systems`、`input-systems`）。 |
| `pygame-core` | 用 pygame-ce（以 pygame 导入）在 Python 中构建并调试 2D 游戏：事件-更新-绘制循环、增量时间、Surface 与 Rect、Sprite 组与无头测试。用于代码导入 pygame，或窗口显示未响应、速度因电脑而异，或 pygame 与 pygame-ce 冲突。不用于引擎中立的输入或存档（`input-systems`、`save-systems`）或跳跃手感（`platformer`）。 |
| `roblox-characters` | Roblox 玩家角色：CharacterAdded 生命周期、Humanoid 与 HumanoidRootPart、R6、R15 与自定义骨架、重生与 Tools。用于重生后角色脚本损坏、动画不播放或不复制，或冲刺代码与 Humanoid 冲突。不用于命中校验（`roblox-networking`）、力与射线（`roblox-physics`）或摄像机（`camera-systems`）。 |
| `roblox-datastores` | Roblox DataStoreService 持久化：加入时加载、离开与 BindToClose 时保存、UpdateAsync 与 SetAsync、会话锁与 OrderedDataStore 排行榜。用于玩家数据丢失、传送后物品复制，或 “too many requests”。不用于引擎中立存档（`save-systems`）、Luau 基础（`roblox-luau`）或经济数值（`roblox-simulator-economy`）。 |
| `roblox-luau` | Roblox Luau 脚本与代码结构：服务、Instance、Script 与 LocalScript 与 ModuleScript、task 库与带类型的 Luau，并含 selene 与 luau-lsp 检查。用于 LocalScript 不运行、客户端加入后得到 nil，或需要替换 wait()。不用于远程（`roblox-networking`）、存档（`roblox-datastores`）或现场编辑（`roblox-studio-workflow`）。 |
| `roblox-networking` | Roblox 客户端-服务器网络与反作弊：RemoteEvent 与 RemoteFunction 契约、服务器权威、速率限制、命中校验与复制。用于远程信任客户端、作弊者刷远程或刷物品，或命中登记错误。不用于 Luau 基础（`roblox-luau`）、存档（`roblox-datastores`）或力与射线 API（`roblox-physics`）。 |
| `roblox-physics` | Roblox 物理与空间查询：装配体、约束、碰撞组、Raycast 与 Shapecast，以及网络所有权。用于零件掉落或抖动、Touched 不可靠、射线打到射击者，或需要替换 BodyMovers。不用于命中合法性（`roblox-networking`）、Humanoid 移动（`roblox-characters`）或引擎中立调校（`physics-tuning`）。 |
| `roblox-simulator-economy` | 用 Luau 做 Roblox 模拟器、大亨与放置游戏经济：升级成本曲线、每秒收入、转生节奏、大数格式与付费蛋概率，并带 Lune 计算器。用于 baseCost、转生数值或不应获得的货币。不用于 DataStores（`roblox-datastores`）、远程限制（`roblox-networking`）、商店布局（`roblox-ui`）或波次经济（`tower-defense`）。 |
| `roblox-studio-workflow` | 安全编辑已有 Roblox 场景或 Rojo 项目：找到事实来源，并用正确的测试模式或 Studio MCP（execute_luau）证明改动。用于智能体编辑 .rbxl 或 Rojo 项目、通过 Studio MCP 工具工作，或必须报告测了什么。不用于安装 Studio MCP（`roblox-get-started`），也不用于功能代码本身（`roblox-luau`、`roblox-ui`）。 |
| `roblox-ui` | 用 ScreenGui 与 PlayerGui 做 Roblox UI：ResetOnSpawn、UDim2 的缩放与偏移、UIListLayout 弹性、安全区、StyleSheet、手柄选择与触控。用于 Roblox 的 HUD、商店或设置菜单，或手机上裁切、重生重置、丢失手柄焦点。也应加载 `game-ui-ux`。不用于输入映射（`input-systems`）或购买校验（`roblox-networking`）。 |
| `unity-animation` | 用 Animator（Mecanim）做 Unity 6.3 LTS 角色动画：状态与过渡、混合树、Avatar Mask 层、根运动与人形 IK。用于接线 SetTrigger、过渡滞后或不触发、根运动滑动，或上半身层覆盖腿部。不用于 AI 状态机（`game-ai`）、手感（`game-feel`）或 Godot（`godot-animation`）。 |
| `unity-build-pipeline` | 构建并交付 Unity 6.3 LTS 播放器：Build Profiles、IL2CPP 与 Mono、带 link.xml 的托管裁剪、脚本化 BuildPlayer、Addressables 以及 CI 或无头构建。用于自动化 Unity 构建，或仅在播放器中出现 MissingMethodException。不用于包体过大（`unity-build-size`）或商店上传（`steam-publish`、`itch-publish`）。 |
| `unity-build-size` | 找出并缩小使 Unity 6.3 LTS 构建过大的内容：阅读 Build Report、未压缩纹理、glTFast 模型、PCM 音频与各平台杠杆。用于 APK、AAB、WebGL 构建或 Steam depot 超出大小限制，或下载包过大。不用于帧率（`performance-optimization`）、构建脚本或裁剪（`unity-build-pipeline`）或商店上传（`steam-publish`）。 |
| `unity-csharp-scripting` | 编写并修复 Unity 6.3 LTS 的 C# 玩法脚本：MonoBehaviour 生命周期、序列化、.meta/GUID 纪律与命令行测试。用于新建或重命名 .cs 文件、“Missing script”，或 Inspector 中字段丢失。不用于物理（`unity-physics`）、输入（`unity-input-system`）、数据资产（`unity-scriptableobjects`）或构建（`unity-build-pipeline`）。 |
| `unity-input-system` | 用 Input System 包为 Unity 6.3 LTS 接线玩家输入：.inputactions 资产、动作映射、PlayerInput 与控制方案。用于输入无反应或在菜单下触发、FindAction 返回 null、旧 Input 类抛错，或需要移植 Input.GetAxis 代码。不用于引擎中立的缓冲、重映射或死区（`input-systems`）或跳跃手感（`platformer`）。 |
| `unity-navmesh` | 用 AI Navigation 包做 Unity 6.3 LTS 寻路：烘焙 NavMeshSurface、NavMeshAgent、NavMeshLink 跳跃与运行时重烘焙。用于 Unity 敌人应追击或巡逻、智能体不动或瞬移、路径不完整，或缺少 Bake 选项卡。不用于决定 NPC 何时移动（`game-ai`、`ai-behavior-trees-utility-ai`）或受力运动（`unity-physics`）。 |
| `unity-physics` | Unity 6.3 LTS 的 3D 与 2D 物理：Rigidbody 与 Rigidbody2D、力与 linearVelocity、层碰撞矩阵与射线。用于物体掉穿地板、OnTriggerEnter 从不触发，或地面射线打到玩家。不用于引擎中立的穿透调校（`physics-tuning`）、图块碰撞体（`unity-tilemap-2d`）或 NavMesh（`unity-navmesh`）。 |
| `unity-scriptableobjects` | 用 ScriptableObject 做 Unity 6.3 LTS 的数据与解耦：CreateAssetMenu 配置资产、共享运行时变量、事件通道，以及用代码生成的 .asset 文件。用于替换单例、数据驱动的物品或卡牌，或离开 Play 模式后值仍残留。不用于保存进度（`save-systems`）或 Godot Resources（`godot-resources`）。 |
| `unity-tilemap-2d` | Unity 6.3 LTS 的 2D 图块地图：Tile Palette、带 Composite Collider 的 Tilemap Collider 2D、Rule Tiles 与运行时 SetTile。用于绘制或生成图块关卡、图块碰撞体接缝、找不到 RuleTile，或六边形与等轴测网格。不用于关卡设计（`level-design`）、生成（`procedural-gen`）、移动（`unity-physics`）或 Godot（`godot-tilemap`）。 |
| `unreal-behavior-trees` | 用 Behavior Trees、Blackboards、EQS 与 StateTree 做 Unreal Engine 5（UE 5.8）的 NPC AI：带 Observer Aborts 的装饰器、C++ BTTask 节点，以及从 AIController 运行树。用于 UE 敌人 AI、BT_、BB_ 或 EQS_ 资产，“AI 只是站着”或 “MoveTo fails”。不用于引擎中立的行为树或效用代码（`ai-behavior-trees-utility-ai`），也不用于在 FSM 与 BT 之间选择（`game-ai`）。 |
| `unreal-blueprints` | Unreal Engine 5（UE 5.8）的蓝图可视化脚本：Blueprint Class 与关卡蓝图、Event Graph，以及 Cast、接口与 Event Dispatcher。用于蓝图图、一个蓝图如何调用另一个、“cast failed”、缓慢的 Event Tick 或蓝图编译错误。不用于 C++（`unreal-cpp-gameplay`）、输入资产（`unreal-enhanced-input`）或 AI 树（`unreal-behavior-trees`）。 |
| `unreal-cpp-gameplay` | Unreal Engine 5（UE 5.8）的 C++ 玩法代码：UCLASS 与 UPROPERTY 反射、Gameplay Framework、GC 安全指针、Build.cs 与命令行构建。用于 GENERATED_BODY、Live Coding、“unresolved external symbol” 或 UHT 错误。不用于蓝图（`unreal-blueprints`）、Enhanced Input（`unreal-enhanced-input`）或打包（`unreal-packaging`）；引擎源码构建不在范围内。 |
| `unreal-enhanced-input` | 用 Enhanced Input 做 Unreal Engine 5（UE 5.8）的玩家输入：Input Action（IA_）、Mapping Context（IMC_）、ETriggerEvent 绑定与可重映射按键。用于接线移动、视角或开火、做重绑定菜单，或输入无反应、重生后失效、每帧触发。不用于引擎中立的输入设计（`input-systems`）或 Character 类（`unreal-cpp-gameplay`）。 |
| `unreal-niagara` | Unreal Engine 5（UE 5.8）的 Niagara 视效：系统、发射器、User 参数、从 C++ 或蓝图生成、边界以及 GPU 与 CPU 模拟。用于任何 Unreal 粒子效果、NS_ 资产、枪口焰或命中，或效果不显示、在屏幕边缘消失、永不停止。不用于 Unity VFX Graph、着色器编写（`shader-programming`）或击停（`game-feel`）。 |
| `unreal-packaging` | 打包并交付 Unreal Engine 5（UE 5.8）项目：Shipping 构建、cooking、pak/IoStore，以及用 UAT 与 cook 日志阅读的 RunUAT BuildCookRun。用于打包后黑屏、构建中缺少地图、“BUILD FAILED” 或 AutomationTool 退出码。不用于商店上传（`steam-publish`、`itch-publish`）或玩法编译错误（`unreal-cpp-gameplay`）。 |
| `phaser-arcade-physics` | Phaser 4 Arcade Physics 的移动与碰撞：刚体、速度、重力、碰撞器与重叠、组与子弹池。用于 Phaser 平台或顶视角控制器，或精灵忽略物理、onFloor() 始终为假、刚体穿墙。不用于场景与加载器（`phaser-core`）、土狼时间（`platformer`）或穿透理论（`physics-tuning`）。 |
| `phaser-core` | 搭建并调试 Phaser 4 游戏（以及固定的 Phaser 3.90）：Game 配置、Scene 生命周期、加载器、场景切换与 Phaser 3 到 4 的迁移。用于代码导入 phaser，或黑屏、create 中资源为 undefined、HUD 场景落在游戏后面。不用于碰撞器（`phaser-arcade-physics`）、HUD 布局（`game-ui-ux`）或 PixiJS（`pixijs-rendering`）。 |
| `pixijs-rendering` | 用 PixiJS v8 构建并调试 2D 浏览器游戏渲染：异步初始化、Assets 加载、Container 与 Sprite 场景图、指针拖拽，以及 v7 到 v8 迁移。用于使用 pixi.js 的游戏或可玩广告，或空白画布、点击不触发、拖拽在精灵边缘停止。不用于仪表盘或图表、Phaser（`phaser-core`）或 3D（`threejs-scene-setup`）。 |
| `threejs-gltf-loading` | 把 glTF/GLB 模型加载进 three.js r187 并播放其动画：GLTFLoader、DRACO、Meshopt 与 KTX2 解码器、AnimationMixer 交叉淡化与 SkeletonUtils 克隆。用于模型不可见或过小、解码器文件 404、动画不播放，或克隆共享同一骨架。不用于场景搭建（`threejs-scene-setup`）或光照（`threejs-materials-lighting`）。 |
| `threejs-materials-lighting` | 为 three.js r187 场景打光与着色：standard、physical 与 unlit 材质、灯光、阴影、HDR 环境光与色调映射。用于网格全黑或过曝、阴影缺失或粉刺，或 EffectComposer 让画面变暗。不用于渲染器搭建（`threejs-scene-setup`）、模型加载（`threejs-gltf-loading`）或自定义着色器（`shader-programming`）。 |
| `threejs-scene-setup` | 搭建并调试普通 three.js r187 游戏或 3D 场景：import maps、Scene、PerspectiveCamera 与 WebGLRenderer、带 Timer 的 setAnimationLoop、缩放、OrbitControls 与 WebGPURenderer。用于 “Failed to resolve module specifier three”、黑色画布或没有动画。不用于 GLB 加载（`threejs-gltf-loading`）、材质（`threejs-materials-lighting`）或 React Three Fiber。 |
| `game-docs` | 编写并维护游戏设计文档：一页 GDD，带功能索引与简短功能说明，并用链接与状态检查器与代码保持一致。用于“起草 GDD”、“写清这个机制”，或在试玩或改代码后更新文档。不用于未要求文档时直接做游戏（`prototype-fast`、`game-jam`）、README 或关卡布局（`level-design`）。 |
| `game-jam` | 在固定截止日期内规划并交付游戏 jam 作品：阅读 jam 规则、按时间收范围、维护砍功能清单，并在提交前检查构建。用于 Ludum Dare、GMTK、Global Game Jam 或任何 itch.io jam、48 小时游戏，或“我们落后了，该砍什么”。不用于不限时实验（`prototype-fast`）或上传命令（`itch-publish`）。 |
| `itch-publish` | 用 butler CLI 在 itch.io 发布并更新游戏：butler push 到 user/game:channel、频道平台标签、HTML5 构建、--userversion 与 CI 上传。用于“上传到 itch”、HTML5 游戏变成下载而不是游玩、空白或 403 网页构建，或 “invalid target”。不用于 Steam（`steam-publish`）或 jam 范围（`game-jam`）。 |
| `prototype-fast` | 大约一小时内做出可扔掉的可玩原型，用来回答一个问题，通常是“这个机制好玩吗？”：一问简报、灰盒、调试 HUD、试玩，以及保留、放弃或重调的决定。用于“先做个原型”、“先弄出能玩的东西”，或是否保留原型代码。不用于限时 jam（`game-jam`）或关卡体块（`level-design`）。 |
| `steam-publish` | 用 Steamworks 与 SteamPipe 在 Steam 发布或更新游戏：depot、app_build .vdf 脚本、steamcmd 上传、beta 分支、SetLive、商店审核与即将推出。用于 steamcmd、ContentBuilder、“Failed to get application info”、Steam Deck Verified 或“要上 Steam”。不用于 itch.io（`itch-publish`）或游戏代码中的 Steamworks SDK 调用。 |

## 前提

- 按所使用技能另行安装所需引擎或工具链
- DesireCore 兼容客户端
