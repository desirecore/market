# Appearance choices

Choose appearance independently from the movement method. Anime, pets, mascots and public figures are subject categories. Photo-to-anime is an input transformation. HD is an output/sampling choice, not a guarantee of beautiful frames or smooth motion.

## Pixel

- Generate deliberate low-resolution pixel artwork: coherent square clusters, stepped contours, simplified readable face/costume, consistent limited colors. Preserve identity anchors from the reference. Converting a detailed illustration to a small blurry raster alone does not establish the requested pixel style.
- For light motion, use `export_pack.py --render-style pixel`: its logical 160px composition and nearest-neighbor 320px output preserve the existing pixel workflow. Keep accents and contours on the pixel grid; do not smooth them or repeatedly resample between frames.
- Keep captions legible and still. Use crisp outline treatment and a font covering the language. Choose a final size that preserves intentional pixel blocks; do not silently run the HD deformation path because it is the default.
- For a requested full action, generate coherent pixel poses and pilot them. Use [the pixel action exporter](pixel-actions.md), which preserves the logical grid and nearest-neighbor sampling. The HD keyframe exporter is a separate rendering route.

## Illustration

- Match the accepted anime, chibi or illustration rendering rather than switching style because the input happens to be a photograph. For an explicit photo-to-illustration request, establish an illustrated identity reference before deriving the pack; keep hair, recognizable face, silhouette and signature clothing.
- Specify concrete model invariants: eye color/spacing, face contour, hair ornaments, hat dimensions, costume panels, buttons/bows and hand type. For actions, let the body and costume move naturally while retaining their construction. Avoid extreme changes that a pilot has shown to distort the face.
- Export detailed artwork directly from its source crop in HD, normally 512px. A smooth resizer does not repair a malformed drawing. Use light motion or the complete-action workflow as requested; high resolution does not select one for the user.
- For a clay-look stylized mascot, use the same non-pixel HD pose-compositing route while preserving its accepted matte material, bead eyes, volume and lighting; do not impose drawn outlines or flatten it into anime. This material treatment is not proof of rigged 3D motion. Paper-collage scenery belongs to the film composition, not to a forced conversion of the character.

## Photographic

- Preserve the accepted person's likeness or pet's markings, natural proportions, clothing/fur and lighting. Resolve ambiguous named identities from the handle/reference. Do not automatically add makeup, beautification, facial reshaping or an anime conversion.
- Light motion can preserve an accepted photo-derived pose without per-frame redraw. Consecutive gestures need consistent generated poses and visual review; first pilot a restrained motion before expanding an unproven photographic action.
- Compare the original crop and decoded output at the same useful size when evaluating blur. Follow [clarity.md](clarity.md); a larger canvas cannot restore absent source detail. Photo-like skin/fur also needs palette/playback inspection in the final GIF.
- Keep successful restrained public-figure examples available. The rejected selfie/beauty test below is not a default recipe; it does not ban photographic people or prevent a new explicitly requested experiment. Do not silently reuse that rejected recipe for a different portrait.

## Lenticular card purpose

Photographic and illustrated pairs can also become [electronic lenticular cards](lenticular.md). Route that purpose to its own source-pairing and full-bleed GIF workflow; a two-state flip is not an articulated gesture. Source compatibility matters more than the character label, and a single photograph still requires a second state.

## Sample status

These are this project's version-specific user decisions, not universal judgments about characters, genres or all future output:

| Sample/version | Status and use |
| --- | --- |
| Whale maid / pixel secretary; approved princess pixel light-motion sample expanded to a pack | Accepted pixel/light-motion references |
| Four-character pixel action pack: glasses boy, hooded girl, astronaut cat, penguin; five actions each | User accepted the exact 20-GIF set and requested publication; reference for pixel/full-character actions, not a guarantee for new generations |
| Clay bakery trio: croissant, toast, coffee; original three GIFs | User accepted this clay-look pose-sequence sample; retain the shared sage apron and material anchors |
| Manman Bakery 15-second clay-and-collage fusion film | User accepted this version and requested publication; reference for brand-film purpose, not a new universal appearance mode or a guarantee of physical contact precision |
| Earlier accepted Luffy action, Naruto/Miku full-action samples; illustrated princess curtsy expanded to a pack | Accepted illustrated-action references for the respective approach |
| Accepted sparse public-figure gestures, including Lei Jun/Stephen Chow/Sam Altman examples | Retain photographic examples; do not replace their rendering with a rejected selfie treatment |
| Anya/Doraemon old four-character full-action versions | Rejected for choppy/frame-skipping playback; not successful full-action templates |
| Anya/Doraemon repaired versions in `examples/anime-stability/` | Assistant-reviewed candidates; user acceptance pending |
| Latest four-character stability test: new Luffy, Sakuragi, Conan, Totoro | Test versions, user acceptance pending; not automatically promoted because an earlier version of Luffy was accepted |
| Nine half-face lenticular cards in `examples/lenticular-cards/` | Published at user request; source/style differences documented per card. Spider-Man uses the exact user-selected first close crop, not rejected narrow/patched versions. Later five remain distinct from the earlier accepted four; publication does not guarantee all future source pairs. |
| Selfie peace-sign / natural makeup / beauty-filter animation experiment | Abandoned; exclude from recommended templates |
| Frozen-body / isolated-arm rig presented as a full-character action | Rejected for that brief; do not substitute it for coordinated acting |

Maintain status at the exact revision level. User-requested expansion of an approved sample carries its chosen appearance/movement forward, but generation, technical validation or assistant review alone do not imply user acceptance. A rejection belongs to that output/version; it does not blacklist the character or every photographic sticker.
