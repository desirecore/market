---
name: blender-skills
description: 94 个 Blender 专项技能（.claude/skills 树）的可选 MIT 本地包。需本机安装 Blender，并另行配置 Blender
  MCP。本包在安装树根目录和每个子技能中都包含上游 MIT LICENSE。
version: 2026.11.24
license: MIT
type: hybrid
risk_level: high
tags:
- blender
- 3d
- gamedev
- mcp
- skill-collection
compatibility: Requires local Blender and a separately configured Blender MCP server.
metadata:
  author: arjun988; DesireCore local packaging
  updated_at: '2026-11-24'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
    - en-US
    - zh-CN
    en-US:
      name: Blender Skills
      short_desc: Optional local MIT package of 94 specialist Blender skills (the
        .claude/skills tree). Requires a local Blender install and a separately configured
        Blender MCP server. The package includes the upstream MIT LICENSE in the installed
        tree and in each child skill.
      description: Market-local packaging of arjun988/blender-skills@904f095d8f36a6e72adaebb08d07f884a074743d.
        The DesireCore installer copies only the skill content directory, so LICENSE
        is copied into this package. The duplicate .cursor/skills tree and the documentation
        site are excluded. Package version 2026.11.24.
      body: ./SKILL.md
      translated_by: human
      translated_at: '2026-11-24'
      source_hash: sha256:bd7bf3a14cc6b469
    zh-CN:
      name: Blender 技能合集
      short_desc: 94 个 Blender 专项技能（.claude/skills 树）的可选 MIT 本地包。需本机安装 Blender，并另行配置
        Blender MCP。本包在安装树根目录和每个子技能中都包含上游 MIT LICENSE。
      description: 基于 arjun988/blender-skills@904f095d8f36a6e72adaebb08d07f884a074743d
        的市场本地包装。真实安装器只复制技能内容目录，因此把 LICENSE 放进本包。排除重复的 .cursor/skills 树和文档站点。包版本 2026.11.24。
      body: ./SKILL.zh-CN.md
      translated_by: human
      translated_at: '2026-11-24'
      source_hash: sha256:bd7bf3a14cc6b469
market:
  icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0
    0 24 24" fill="none"><circle cx="8" cy="8" r="3" stroke="#2563EB" stroke-width="1.7"/><circle
    cx="16" cy="8" r="3" stroke="#2563EB" stroke-width="1.7"/><circle cx="12" cy="16"
    r="3" stroke="#2563EB" stroke-width="1.7"/><path d="M10.4 10.2 13.6 13.8M13.6
    10.2 10.4 13.8" stroke="#2563EB" stroke-width="1.5" stroke-linecap="round"/></svg>
  category: development
  maintainer:
    name: mashagua
    url: https://github.com/mashagua
    verified: true
  channel: latest
---

# Blender Skills

## Scope and provenance

This optional local MIT package contains 94 Blender specialist skills from `.claude/skills`, plus the upstream [LICENSE](LICENSE) at the package root and in each child directory. See [UPSTREAM.md](UPSTREAM.md) for the pinned commit and per-file hashes.

It requires a local Blender installation and a separately configured Blender MCP server. This package does not vendor Blender or the MCP server. The duplicate `.cursor/skills` tree is omitted because it repeats the same skill IDs.

Bilingual child summaries (reviewed, not machine-invented) are in [references/child-summaries.json](references/child-summaries.json).

| ID | Summary |
|---|---|
| `analog-found-footage-horror` | Analog, VHS, CRT, and found-footage horror aesthetics for Blender shots including camera imperfections and documentary framing. |
| `animation` | Game-ready animation in Blender including walk/run/idle cycles, combat, mechanical animation, camera animation, constraints, Graph Editor, and NLA workflows via MCP. |
| `anime-style` | Anime and cel-shaded art direction for Blender with hard color breaks, toon shaders, clean silhouettes, and anime proportion language. |
| `apocalypse-worlds` | Apocalyptic and dystopian world art direction for Blender including post-apocalyptic, zombie, alien invasion, post-human, dystopian, and utopian contrast sets. |
| `archviz` | Architectural visualization in Blender for interiors/exteriors with real-world scale, camera composition, PBR materials, and still/animation delivery via MCP. |
| `asset-optimization` | Validates and optimizes Blender assets for polycount, topology, UV efficiency, material count, naming, collections, and game-ready performance. Use before export on all production assets via MCP. |
| `biome-worlds` | Biome and setting art direction for Blender covering underwater, desert, arctic, jungle, underground, and floating-island environments. |
| `blender-director` | Use when starting any Blender asset task, planning a production pipeline, coordinating multiple disciplines, or matching a reference photo/concept art. Invoke for game-ready assets, hard surface, environment, character, creature, export, or any multi-skill Blender workflow. |
| `blender-modeler` | Core Blender modeling specialist for Edit Mode, modifiers, collections, precision modeling, and scene organization. Use for general 3D modeling, blockouts, cleanup, non-destructive workflows, and scene structure in Blender via MCP. |
| `body-horror-style` | Body horror art direction for Blender focusing on flesh wrongness, mutation, fusion, and visceral material storytelling. |
| `brutalist-mood` | Brutalist and concrete-monument mood direction for Blender architecture and scenes with raw concrete, monumental scale, and austere composition. |
| `camera-cinematography` | Cinematic camera work in Blender including framing, lenses, composition, camera animation, and shot language beyond basic rendering setup via MCP. |
| `cartoon-style` | Cartoon art direction for Blender with squash-stretch readable shapes, bold colors, and graphic silhouettes for games and animation. |
| `character-archetypes` | Character archetype art direction for Blender covering fantasy races, horror creatures, roles (knight, assassin, detective), and body types (mecha, android, chibi, etc.). |
| `character-artist` | AAA character modeling for human anatomy, stylization, facial topology, clothing, hair, and animation-ready meshes. Use for game characters, facial expressions, and production character assets in Blender via MCP. |
| `chibi-style` | Chibi and SD proportion art direction for Blender characters with oversized heads, simplified anatomy, and cute silhouette rules. |
| `cloth-sim` | Garment blockout, cloth simulation, pin groups, and bake to shape keys or caches for characters and props in Blender via MCP. |
| `collision-proxy` | Collision proxy authoring for games including UCX/UHX naming, convex hulls, capsules, and simple collider meshes in Blender via MCP. |
| `comic-book-style` | Comic book and graphic-novel art direction for Blender with ink-line emphasis, halftone cues, and high-contrast framing. |
| `compositing` | Blender compositor workflows for beauty stacks, render passes, color grade, glare, and delivery outputs via MCP. |
| `cosmic-eldritch-horror` | Cosmic, eldritch, and Lovecraftian horror art direction for Blender with non-Euclidean cues, impossible scale, and incomprehensible forms. |
| `cozy-wholesome-mood` | Cozy, cute, wholesome, relaxing, and peaceful mood direction for Blender assets and scenes. |
| `creature-artist` | AAA creature modeling for fantasy, aliens, monsters, and organic creature design with believable anatomy and movement. Use for creature blockouts, muscle flow, bone structure, and animation-ready creature assets in Blender via MCP. |
| `dark-gritty-mood` | Dark, grim, gritty, rusty, abandoned, decayed, industrial, lonely, and melancholic mood direction for Blender. |
| `dream-surreal-mood` | Dreamlike, surreal, mysterious, mystical, hopeful, and chaotic mood direction for Blender scenes. |
| `dream-weirdcore-style` | Dreamcore, weirdcore, and traumacore-inspired art direction for Blender with nostalgic wrongness, liminal nostalgia, and surreal childhood spaces. |
| `environment-artist` | AAA environment art for modular kits, buildings, terrain, vegetation, architecture, and scene composition. Use for game-optimized environments, storytelling through space, and modular asset pipelines in Blender via MCP. |
| `export-pipeline` | Production export from Blender to FBX, GLTF, OBJ, USD, and Alembic with scale, pivot, rotation, normals, materials, animation, and collision verification via MCP. |
| `fantasy-worlds` | Fantasy world-building art direction for Blender covering medieval, high fantasy, dark fantasy, and urban fantasy asset language. |
| `folk-horror-style` | Folk horror art direction for Blender with rural ritual uncanny, pastoral daylight dread, and community-wrongness storytelling. |
| `frutiger-aero-style` | Frutiger Aero art direction for Blender with glossy skeuomorphism, aqua UI cues, nature-tech optimism, and mid-2000s futurism. |
| `genre-action-combat` | Art direction for action, hack-and-slash, beat 'em up, and fighting-game readable combat spaces and prop language in Blender. |
| `genre-card-party-idle` | Art direction for card games, deck builders, party games, idle/incremental, educational, and rhythm game presentational spaces in Blender. |
| `genre-metroidvania-roguelike` | Art direction for metroidvania, roguelike, and roguelite games in Blender with biome gates, room modules, and run-readable props. |
| `genre-narrative-vn` | Art direction for visual novel, interactive movie, walking simulator, and story-driven presentation spaces in Blender. |
| `genre-open-world-sandbox` | Art direction for open world and sandbox games in Blender with biome landmarks, traversable scale, and discovery props. |
| `genre-puzzle-platformer` | Art direction for puzzle and platformer games in Blender with readable interactables, jump volumes, and clear hazard language. |
| `genre-racing-sports` | Art direction for racing and sports games in Blender with track landmarks, stadium kits, and high-speed readability. |
| `genre-rpg` | Art direction for RPG, JRPG, CRPG, ARPG, and MMORPG worlds in Blender including loot rarity reads and region identity. |
| `genre-shooter` | Art direction for FPS, TPS, shooter, battle royale, and extraction-shooter maps and props in Blender with sightline and cover language. |
| `genre-soulslike` | Art direction for soulslike games in Blender with monumental melancholy spaces, fog gates, bonfire landmarks, and lethal readability. |
| `genre-stealth` | Art direction for stealth-game spaces in Blender with shadow volumes, patrol-friendly layouts, and concealment materials. |
| `genre-strategy-sim` | Art direction for strategy, RTS, turn-based strategy, tower defense, MOBA, city builder, colony sim, and simulation games in Blender. |
| `genre-survival` | Art direction for survival and survival-horror gameplay spaces in Blender emphasizing resource props, crafting readability, and tension routes. |
| `geometry-nodes` | Blender Geometry Nodes for procedural modeling, scatter systems, vegetation, buildings, pipes, cables, and reusable node groups. Use for procedural asset generation and instancing pipelines via MCP. |
| `godot-export` | Godot-specific Blender export favoring GLTF/GLB with correct scale, materials, animation clips, and collision shapes via MCP. |
| `hair-groom` | Hair and fur grooming in Blender using curves, particle hair, geometry nodes, and game hair-card workflows. Use for characters, creatures, and real-time hair cards via MCP. |
| `hand-painted-style` | Hand-painted texture art direction for Blender with brushwork albedo, soft value transitions, and stylized PBR restraint. |
| `hard-surface` | AAA hard surface modeling for sci-fi, industrial, military, vehicles, weapons, robotics, and mechanical props. Use for boolean/bevel workflows, panel lines, greebles, chamfers, and manufacturing-accurate surfaces in Blender via MCP. |
| `hd-2d-style` | HD-2D art direction combining pixel characters/sprites with 3D environments, depth of field, and theatrical lighting. |
| `historical-worlds` | Historical and period world art direction for Blender including Western, pirate, samurai/ninja, Viking, ancient Egypt/Greece/Rome, Victorian, modern, and military eras. |
| `horror-style` | Psychological horror art direction for Blender assets inspired by Silent Hill, Resident Evil, Chilla's Art, Fear to Fathom, and Iron Lung. Use for sparse industrial environments, analog aesthetics, and tension-driven lighting. |
| `indie-horror-aesthetics` | Indie horror aesthetic pack for Blender covering Silent Hill, Fear to Fathom, Puppet Combo, corporate horror, cabin/forest/hospital horror, and related looks. |
| `isometric-style` | Isometric and strategy-game art direction for Blender including diorama framing, true-iso camera setup, readable silhouettes, and tile asset rules. |
| `lighting` | Cinematic and game lighting in Blender including three-point lighting, HDRI, horror lighting, volumetrics, rim lighting, and mood-driven illumination. Use for look development and scene atmosphere via MCP. |
| `liminal-space-style` | Liminal space and Backrooms art direction for Blender with empty transitional architecture, wrong familiarity, and endless repetition. |
| `lod-pipeline` | Dedicated LOD generation, naming, screen-size targets, and validation for game meshes in Blender via MCP. |
| `lookdev` | Look development loop for Blender assets combining materials, lighting, camera, and screenshot comparison until shading reads correctly via MCP. |
| `lowpoly-style` | Low-poly art direction for Blender inspired by PS1/PS2, Lethal Company, Mouthwashing, and Fear to Fathom. Use for readable silhouettes, minimal polygons, simple materials, and strong atmosphere. |
| `manga-style` | Manga-inspired art direction for Blender emphasizing monochrome value design, speed lines, screentone feel, and manga panel staging. |
| `mascot-puppet-horror` | Mascot and puppet horror art direction for Blender with cheerful brand characters made wrong, felt/foam materials, and uncanny performance. |
| `materials` | Blender PBR and stylized material creation for metal, wood, concrete, fabric, glass, dirt, rust, and procedural shaders. Use for look development, material reuse, and production shading in Blender via MCP. |
| `minimalist-style` | Minimalist and abstract-leaning art direction for Blender with reduced forms, limited palettes, and negative space. |
| `neon-retrofuturism` | Neon, vaporwave, synthwave, and retrofuturistic mood/art direction for Blender with grid horizons, chrome, and dusk palettes. |
| `noir-style` | Noir art direction for Blender with high-contrast lighting, wet streets, silhouettes, and monochrome or limited-color grading. |
| `painterly-style` | Painterly art direction spanning watercolor and oil-painting looks for Blender using soft edges, pigment texture, and illustrative lighting. |
| `physics-sim` | Rigid body, soft body, and destruction setups in Blender including constraints, cell fracture debris, and baked caches via MCP. |
| `pixel-art-style` | Pixel-art and texel-constrained art direction for Blender assets destined for pixel rendering, low-res textures, or HD-2D-adjacent pixel reads. |
| `procedural-modeling` | Procedural asset creation for rocks, buildings, vegetation, roads, terrain, pipes, cables, and sci-fi panels using Geometry Nodes and modifier-based workflows in Blender via MCP. |
| `prop-artist` | Everyday and hero prop modeling for furniture, tools, household objects, kitbash parts, and readable game props. Use when hard-surface is too sci-fi/mechanical and the asset is a grounded prop. |
| `psx-horror-style` | PS1/PSX-era horror art direction combining low-poly affine textures, limited color depth, fog, and psychological horror staging for Blender assets. |
| `qa-review` | Production QA gate for Blender assets using viewport screenshots, validation checklists, naming audits, and ship/no-ship verdicts via MCP. |
| `realistic-style` | Photorealistic AAA art direction for Blender including photogrammetry cleanup, real-world scale, high-poly workflows, PBR accuracy, and scan optimization. Use for cinematic and AAA game realism. |
| `rendering` | Blender rendering with Cycles and Eevee including sampling, denoising, camera setup, render passes, color management, and render optimization. Use for final output and look validation via MCP. |
| `retopology` | Production retopology for animation-ready, low-poly, quad-dominant meshes with proper edge loops and efficient polygon flow. Use after sculpting or high-poly modeling before rigging and UV work in Blender via MCP. |
| `retro-16bit-style` | Retro 16-bit art direction for Blender-assisted SNES/Genesis-era color richness, dither cues, and sprite-like clarity. |
| `retro-8bit-style` | Retro 8-bit art direction for Blender-assisted pixel/low-res aesthetics inspired by NES-era constraints. |
| `rigging` | Production rigging in Blender with armatures, IK/FK, constraints, weight painting, mechanical rigs, facial rigs, and drivers. Use before animation on deforming assets via MCP. |
| `scene-assembly` | Large scene layout in Blender with collections, linking, overrides, streaming-friendly organization, and set assembly via MCP. |
| `sci-fi-punk-worlds` | Sci-fi and punk world art direction for Blender including hard sci-fi, space, cyberpunk, steampunk, dieselpunk, atompunk, solarpunk, biopunk, and clockpunk. |
| `sculpting` | Blender sculpting for organic and hard surface detail using Dyntopo, multiresolution, brushes, alpha workflow, wrinkles, and damage. Use when high-frequency surface detail is needed before retopology in Blender via MCP. |
| `set-dressing` | Set dressing and environmental storytelling placement for interiors and exteriors using prop density, narrative clusters, and readability rules via MCP. |
| `stop-motion-craft-style` | Stop-motion and craft aesthetics for Blender including claymation, paper craft, and handmade physical-material cues. |
| `stylized-style` | Stylized art direction for Blender with shape language, exaggeration, color harmony, NPR rendering, and hand-painted asset workflows. Use for non-photorealistic game and animation projects. |
| `texture-workflow` | Production texture workflow for atlases, baking AO/curvature/normal/roughness maps, decals, and texture memory optimization. Use for game-ready texture pipelines in Blender via MCP. |
| `unity-export` | Unity-specific Blender export for scale, axis, materials, humanoid/generic rigs, LODs, and collision import via MCP. |
| `unreal-export` | Unreal Engine-specific Blender export for FBX scale, LODs, UCX collision, sockets, materials, and skeletal mesh workflows via MCP. |
| `uv-workflow` | Production UV unwrapping for seam placement, UV packing, texel density, UDIM, lightmap UVs, and modular UV layouts. Use when preparing meshes for texturing and engine export in Blender via MCP. |
| `vector-style` | Vector-clean art direction for Blender with flat fills, sharp silhouettes, and UI-like graphic clarity. |
| `vegetation-artist` | Vegetation and foliage authoring for Blender including trees, plants, grass cards, canopy LODs, and game-friendly leaf atlases via MCP. |
| `vehicle-artist` | Dedicated vehicle modeling for cars, trucks, aircraft, ships, boats, mechs, and transit assets with proportion, panel flow, and game LOD awareness in Blender via MCP. |
| `vfx-fx` | Cinematic and game VFX in Blender including smoke, fire, particles, trails, and Geometry Nodes FX setups via MCP. |
| `visual-console-eras` | Visual era art direction for Blender covering PS1–PS5 stylistic cues, retro arcade, DOS, CRT, VHS, and film-grain presentation. |
| `voxel-style` | Voxel and Minecraft-adjacent art direction for Blender with block grid modeling, limited palettes, and chunk-friendly assets. |

## Prerequisites

- Blender installed locally
- A Blender MCP server configured separately
- A DesireCore-compatible client that can load this optional market skill
