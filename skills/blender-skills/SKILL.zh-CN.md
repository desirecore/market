<!-- locale: zh-CN -->

# Blender 技能合集

## 范围与来源

这个可选 MIT 本地包收录 `.claude/skills` 下的 94 个 Blender 专项技能，并在包根目录和每个子技能目录放入上游 [LICENSE](LICENSE)。固定提交与逐文件哈希见 [UPSTREAM.md](UPSTREAM.md)。

需要本机安装 Blender，并另行配置 Blender MCP。本包不附带 Blender 或 MCP 服务。重复的 `.cursor/skills` 树已省略，因为技能 ID 相同。

经过审阅的中英子技能摘要见 [references/child-summaries.json](references/child-summaries.json)。

| 标识 | 摘要 |
|---|---|
| `analog-found-footage-horror` | 为 Blender 镜头提供模拟、VHS、CRT 与寻获影像式恐怖美学，包括摄像机缺陷与纪录片式取景。 |
| `animation` | 在 Blender 中制作可进游戏的动画，涵盖走跑待机循环、战斗、机械动画、摄像机动画、约束、Graph Editor 与 NLA 流程，通过 MCP 完成。 |
| `anime-style` | Blender 的动漫与赛璐璐风格美术指导，强调硬色块、卡通着色器、清晰剪影与动漫比例语言。 |
| `apocalypse-worlds` | Blender 末世与反乌托邦世界美术指导，包括后末日、僵尸、外星入侵、后人类、反乌托邦及乌托邦对照套装。 |
| `archviz` | 在 Blender 中做室内外建筑可视化，使用真实世界尺度、摄像机构图、PBR 材质，并通过 MCP 交付静帧或动画。 |
| `asset-optimization` | 校验并优化 Blender 资产的面数、拓扑、UV 效率、材质数量、命名、集合与游戏性能。在所有生产资产导出前通过 MCP 使用。 |
| `biome-worlds` | Blender 生物群系与场景美术指导，覆盖水下、沙漠、极地、丛林、地下与浮空岛环境。 |
| `blender-director` | 在开始任何 Blender 资产任务、规划生产管线、协调多专业，或对照参考照片/概念稿时使用。适用于游戏资产、硬表面、环境、角色、生物、导出及任何多技能 Blender 工作流。 |
| `blender-modeler` | Blender 核心建模专项，覆盖编辑模式、修改器、集合、精密建模与场景组织。用于一般三维建模、体块、清理、非破坏流程与场景结构，通过 MCP 完成。 |
| `body-horror-style` | Blender 肢体恐怖美术指导，聚焦肉体违和、变异、融合与内脏质感叙事。 |
| `brutalist-mood` | 为 Blender 建筑与场景提供粗野主义与混凝土纪念碑式情绪指导，强调裸露混凝土、纪念碑尺度与克制构图。 |
| `camera-cinematography` | 在 Blender 中做电影化摄像机工作，包括构图、镜头、画面构成、摄像机动画，以及超越基础渲染设置的镜头语言，通过 MCP 完成。 |
| `cartoon-style` | Blender 卡通美术指导，以可挤压拉伸的可读形状、大胆用色与图形化剪影服务游戏与动画。 |
| `character-archetypes` | Blender 角色原型美术指导，覆盖奇幻种族、恐怖生物、职业角色（骑士、刺客、侦探）及体型（机甲、安卓、Q 版等）。 |
| `character-artist` | 面向 AAA 的角色建模，包括人体解剖、风格化、面部拓扑、服装、头发与可动画网格。用于游戏角色、面部表情与生产级角色资产，通过 MCP 在 Blender 中完成。 |
| `chibi-style` | Blender 角色的 Q 版与 SD 比例美术指导，采用超大头部、简化解剖与可爱剪影规则。 |
| `cloth-sim` | 在 Blender 中通过 MCP 为角色与道具做服装体块、布料模拟、固定点组，并烘焙为形态键或缓存。 |
| `collision-proxy` | 为游戏编写碰撞代理，包括 UCX/UHX 命名、凸包、胶囊体与简单碰撞网格，通过 MCP 在 Blender 中完成。 |
| `comic-book-style` | Blender 漫画与图像小说美术指导，强调墨线、网点暗示与高对比构图。 |
| `compositing` | Blender 合成器流程，用于美化栈、渲染通道、调色、眩光与交付输出，通过 MCP 完成。 |
| `cosmic-eldritch-horror` | Blender 宇宙、邪神与洛夫克拉夫特式恐怖美术指导，包含非欧线索、不可能的尺度与难以理解的形态。 |
| `cozy-wholesome-mood` | 为 Blender 资产与场景提供温馨、可爱、治愈、放松与平和的情绪指导。 |
| `creature-artist` | 面向 AAA 的生物建模，覆盖奇幻生物、外星人、怪物与有机生物设计，追求可信解剖与运动。用于生物体块、肌肉走向、骨骼结构与可动画生物资产，通过 MCP 在 Blender 中完成。 |
| `dark-gritty-mood` | 为 Blender 提供黑暗、阴沉、粗糙、锈蚀、废弃、腐朽、工业、孤独与忧郁的情绪指导。 |
| `dream-surreal-mood` | 为 Blender 场景提供梦境、超现实、神秘、秘术、希望与混乱的情绪指导。 |
| `dream-weirdcore-style` | 受 dreamcore、weirdcore 与 traumacore 启发的 Blender 美术指导，强调怀旧的违和感、阈限怀旧与超现实童年空间。 |
| `environment-artist` | 面向 AAA 的环境美术，覆盖模块化套件、建筑、地形、植被、建筑与场景构图。用于为游戏优化的环境、以空间讲故事及模块化资产管线，通过 MCP 在 Blender 中完成。 |
| `export-pipeline` | 从 Blender 生产导出到 FBX、GLTF、OBJ、USD 与 Alembic，并校验缩放、轴心、旋转、法线、材质、动画与碰撞，通过 MCP 完成。 |
| `fantasy-worlds` | Blender 奇幻世界观美术指导，覆盖中世纪、高奇幻、黑暗奇幻与都市奇幻的资产语言。 |
| `folk-horror-style` | Blender 民俗恐怖美术指导，强调乡村仪式的诡异、田园白昼恐惧与共同体违和叙事。 |
| `frutiger-aero-style` | Blender 的 Frutiger Aero 美术指导，包含光泽拟物、水色界面线索、自然科技乐观与 2000 年代中期未来主义。 |
| `genre-action-combat` | 为动作、砍杀、清版与格斗游戏在 Blender 中设计可读的战斗空间与道具语言。 |
| `genre-card-party-idle` | 为卡牌、构筑、派对、放置/增量、教育与节奏游戏在 Blender 中做展示性空间的美术指导。 |
| `genre-metroidvania-roguelike` | 为类银河战士恶魔城、rogue-like 与 rogue-lite 游戏在 Blender 中做美术指导，包含区域门、房间模块与可在单局中读懂的道具。 |
| `genre-narrative-vn` | 为视觉小说、互动电影、步行模拟与叙事驱动的展示空间提供 Blender 美术指导。 |
| `genre-open-world-sandbox` | 为开放世界与沙盒游戏在 Blender 中做美术指导，包含生物群系地标、可穿越尺度与探索道具。 |
| `genre-puzzle-platformer` | 为解谜与平台游戏在 Blender 中做美术指导，强调可读的可互动物体、跳跃空间与清晰的危险语言。 |
| `genre-racing-sports` | 为竞速与体育游戏在 Blender 中做美术指导，包含赛道地标、场馆套件与高速可读性。 |
| `genre-rpg` | 为 RPG、JRPG、CRPG、ARPG 与 MMORPG 世界在 Blender 中做美术指导，包括掉落稀有度读法与地区识别。 |
| `genre-shooter` | 为 FPS、TPS、射击、大逃杀与撤离射击地图及道具在 Blender 中做美术指导，强调视野线与掩体语言。 |
| `genre-soulslike` | 为类魂游戏在 Blender 中做美术指导，包含纪念碑式忧郁空间、雾门、篝火地标与致命可读性。 |
| `genre-stealth` | 为潜行游戏空间在 Blender 中做美术指导，包含阴影体积、便于巡逻的布局与掩蔽材质。 |
| `genre-strategy-sim` | 为策略、RTS、回合策略、塔防、MOBA、城市建造、殖民地模拟与模拟经营游戏在 Blender 中做美术指导。 |
| `genre-survival` | 为生存与生存恐怖玩法空间在 Blender 中做美术指导，强调资源道具、合成可读性与张力路径。 |
| `geometry-nodes` | 用 Blender 几何节点做程序化建模、散布系统、植被、建筑、管道、线缆与可复用节点组。用于程序化资产生成与实例化管线，通过 MCP 完成。 |
| `godot-export` | 面向 Godot 的 Blender 导出，优先 GLTF/GLB，并校正缩放、材质、动画片段与碰撞形状，通过 MCP 完成。 |
| `hair-groom` | 在 Blender 中用曲线、粒子毛发、几何节点与游戏发卡流程做毛发梳理。用于角色、生物与实时发卡，通过 MCP 完成。 |
| `hand-painted-style` | Blender 手绘纹理美术指导，采用笔触反照率、柔和明度过渡与克制的风格化 PBR。 |
| `hard-surface` | 面向 AAA 的硬表面建模，覆盖科幻、工业、军事、载具、武器、机器人与机械道具。用于布尔/倒角流程、分缝线、细节件、倒角与接近制造精度的表面，通过 MCP 在 Blender 中完成。 |
| `hd-2d-style` | HD-2D 美术指导，将像素角色/精灵与三维环境、景深与舞台灯光结合。 |
| `historical-worlds` | Blender 历史与时代世界美术指导，包括西部、海盗、武士/忍者、维京、古埃及/希腊/罗马、维多利亚、现代与军事年代。 |
| `horror-style` | 受寂静岭、生化危机、Chilla's Art、Fear to Fathom 与 Iron Lung 启发的 Blender 心理恐怖资产美术指导。用于稀疏工业环境、模拟美学与张力驱动的灯光。 |
| `indie-horror-aesthetics` | Blender 独立恐怖美学包，覆盖寂静岭、Fear to Fathom、Puppet Combo、企业恐怖、小屋/森林/医院恐怖及相关外观。 |
| `isometric-style` | Blender 等轴测与策略游戏美术指导，包括立体模型取景、真等轴摄像机设置、可读剪影与地块资产规则。 |
| `lighting` | 在 Blender 中做电影与游戏灯光，包括三点布光、HDRI、恐怖灯光、体积光、轮廓光与情绪照明。用于造型开发与场景氛围，通过 MCP 完成。 |
| `liminal-space-style` | Blender 阈限空间与后室美术指导，强调空荡的过渡建筑、错误的熟悉感与无尽重复。 |
| `lod-pipeline` | 在 Blender 中通过 MCP 专门生成 LOD、命名、屏幕尺寸目标并做游戏网格校验。 |
| `lookdev` | Blender 资产的造型开发循环，结合材质、灯光、摄像机与截图对比，直到着色读感正确，通过 MCP 完成。 |
| `lowpoly-style` | 受 PS1/PS2、Lethal Company、Mouthwashing 与 Fear to Fathom 启发的 Blender 低多边形美术指导。用于可读剪影、最少面数、简单材质与强烈氛围。 |
| `manga-style` | Blender 漫画风美术指导，强调单色明度设计、速度线、网点质感与漫画分镜调度。 |
| `mascot-puppet-horror` | Blender 吉祥物与木偶恐怖美术指导，把欢快的品牌角色做“不对劲”，使用毡/泡沫材质与诡异表演。 |
| `materials` | 在 Blender 中创建 PBR 与风格化材质，覆盖金属、木材、混凝土、织物、玻璃、泥土、铁锈与程序着色器。用于造型开发、材质复用与生产着色，通过 MCP 完成。 |
| `minimalist-style` | Blender 极简与偏抽象的美术指导，采用简化形体、有限调色与留白。 |
| `neon-retrofuturism` | 为 Blender 提供霓虹、蒸汽波、合成波与复古未来主义的情绪/美术指导，包含网格地平线、镀铬与黄昏色盘。 |
| `noir-style` | Blender 黑色电影美术指导，使用高对比灯光、湿漉街道、剪影，以及单色或有限色彩的调色。 |
| `painterly-style` | 覆盖水彩与油画观感的 Blender 绘画风美术指导，使用柔边、颜料纹理与插画式光线。 |
| `physics-sim` | 在 Blender 中设置刚体、柔体与破坏效果，包括约束、细胞破碎碎片与烘焙缓存，通过 MCP 完成。 |
| `pixel-art-style` | 为将用于像素渲染、低分辨率纹理或接近 HD-2D 的像素读感的 Blender 资产，提供像素艺术与纹素约束的美术指导。 |
| `procedural-modeling` | 用几何节点与基于修改器的流程，在 Blender 中程序化制作岩石、建筑、植被、道路、地形、管道、线缆与科幻面板，通过 MCP 完成。 |
| `prop-artist` | 日常与英雄级道具建模，覆盖家具、工具、家用物品、套件零件与可读的游戏道具。当硬表面过于科幻/机械、而资产是落地道具时使用。 |
| `psx-horror-style` | PS1/PSX 时代恐怖美术指导，将低多边形仿射纹理、有限色深、雾效与心理恐怖调度用于 Blender 资产。 |
| `qa-review` | Blender 资产的生产 QA 关卡，使用视口截图、校验清单、命名审查与可否交付的结论，通过 MCP 完成。 |
| `realistic-style` | 面向 Blender 的照片级 AAA 美术指导，包括摄影测量清理、真实世界尺度、高模流程、PBR 精度与扫描优化。用于电影级与 AAA 游戏写实。 |
| `rendering` | 用 Cycles 与 Eevee 在 Blender 中渲染，包括采样、降噪、摄像机设置、渲染通道、色彩管理与渲染优化。用于最终输出与造型校验，通过 MCP 完成。 |
| `retopology` | 为可动画、低多边形、以四边为主的网格做生产级重拓扑，保证正确循环边与高效布线。在雕刻或高模之后、绑定与 UV 之前，通过 MCP 在 Blender 中使用。 |
| `retro-16bit-style` | Blender 辅助的复古 16 位美术指导，面向超任/世嘉时代的丰富色彩、抖动线索与精灵般的清晰度。 |
| `retro-8bit-style` | Blender 辅助的复古 8 位美术指导，面向受红白机时代约束启发的像素/低分辨率美学。 |
| `rigging` | 在 Blender 中做生产级绑定，包括骨架、IK/FK、约束、权重绘制、机械绑定、面部绑定与驱动器。在变形资产做动画之前通过 MCP 使用。 |
| `scene-assembly` | 在 Blender 中布置大型场景，使用集合、链接、覆盖、便于流式加载的组织与布景组装，通过 MCP 完成。 |
| `sci-fi-punk-worlds` | Blender 科幻与朋克世界美术指导，包括硬科幻、太空、赛博朋克、蒸汽朋克、柴油朋克、原子朋克、太阳朋克、生物朋克与时钟朋克。 |
| `sculpting` | 在 Blender 中做有机与硬表面细节雕刻，使用动态拓扑、多重分辨率、笔刷、alpha 流程、皱褶与破损。在重拓扑前需要高频表面细节时，通过 MCP 使用。 |
| `set-dressing` | 为室内外做布景摆放与环境叙事，使用道具密度、叙事组团与可读性规则，通过 MCP 完成。 |
| `stop-motion-craft-style` | Blender 定格与手作美学，包括黏土动画、纸艺与手工物理材质线索。 |
| `stylized-style` | Blender 风格化美术指导，包含形体语言、夸张、色彩和谐、非真实感渲染与手绘资产流程。用于非写实的游戏与动画项目。 |
| `texture-workflow` | 生产级纹理流程，用于图集、烘焙 AO/曲率/法线/粗糙度贴图、贴花与贴图内存优化。用于 Blender 中可进游戏的纹理管线，通过 MCP 完成。 |
| `unity-export` | 面向 Unity 的 Blender 导出，处理缩放、轴向、材质、人形/通用骨架、LOD 与碰撞导入，通过 MCP 完成。 |
| `unreal-export` | 面向 Unreal Engine 的 Blender 导出，处理 FBX 缩放、LOD、UCX 碰撞、插槽、材质与骨骼网格流程，通过 MCP 完成。 |
| `uv-workflow` | 生产级 UV 展开，覆盖缝线布置、UV 打包、纹素密度、UDIM、光照贴图 UV 与模块化 UV 布局。在 Blender 中为贴图与引擎导出准备网格时，通过 MCP 使用。 |
| `vector-style` | Blender 矢量般干净的美术指导，使用平涂、锐利剪影与接近 UI 的图形清晰度。 |
| `vegetation-artist` | 在 Blender 中制作植被与植物，包括树木、植物、草卡、树冠 LOD 与便于游戏使用的叶片图集，通过 MCP 完成。 |
| `vehicle-artist` | 专用于汽车、卡车、飞行器、船舶、船只、机甲与交通资产的载具建模，关注比例、板件走向与游戏 LOD，通过 MCP 在 Blender 中完成。 |
| `vfx-fx` | 在 Blender 中做电影与游戏视效，包括烟、火、粒子、拖尾与几何节点特效设置，通过 MCP 完成。 |
| `visual-console-eras` | Blender 主机世代视觉美术指导，覆盖 PS1–PS5 风格线索、复古街机、DOS、CRT、VHS 与胶片颗粒呈现。 |
| `voxel-style` | Blender 体素与类 Minecraft 美术指导，使用方块网格建模、有限调色与便于分块的资产。 |

## 前提

- 本机已安装 Blender
- 另行配置的 Blender MCP 服务
- 能够加载本可选市场技能的 DesireCore 兼容客户端
