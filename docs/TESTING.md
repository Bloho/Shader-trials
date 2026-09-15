# Minecraft acceptance test

## v0.2 bloom, fog, and clouds

The user confirmed the first baseline renders normally. Install
`BlohoShaders-atmosphere-v0.2.zip` as a **separate pack** and start with **Balanced**.
Keep the original baseline ZIP for direct comparisons. The checks below focus on
the new effects, followed by the geometry regression checklist.

1. **Bloom:** compare torches, lava, glowstone, sunlit white blocks, and a dark
   cave. Toggle Bloom and vary its strength/radius. Highlights should gain soft
   halos; dark surfaces should not get a gray veil. This is scene-highlight bloom,
   so white non-emissive surfaces can also glow. Check the window edges, resize,
   and toggle fullscreen for stale textures or stretched blur.
2. **Fog:** look across distant terrain, a cave entrance, and through overlapping
   water/glass. Toggle Fog. Test rain, underwater, lava in spectator/creative,
   the Nether, and the End. Fog should use the current biome/fluid color without
   making transparent texture holes opaque. Eyes/glints should fade, not add a
   fog-colored glow. The atmospheric haze slider controls the extra haze, not
   the engine's base distance/fluid fog; disable Fog to remove both.
3. **Clouds:** look up in the Overworld during day, sunset, night, and rain. Clouds
   should drift and leave gaps; they should not cover nearby mountains or your
   hand. Fly below, through, and above the configured height (default 224). Try
   coverage and height controls. These are two soft sheets, so do not expect the
   interior of a volumetric cloud. Check particles, transparent entities, and glass
   against clouds for ordering issues. The legacy pipeline can draw those at
   different times, and their depth behavior must be checked in Minecraft.
4. **Fallback:** switch to **Baseline (effects off)**. Bloom and fog should vanish
   and vanilla clouds should return when enabled in Video Settings. Compare
   terrain, transparency, hand, and sky with the accepted original baseline ZIP.
5. **Dimensions/reload:** Overworld clouds must not appear in the Nether or End.
   Switch dimensions and reload each effect combination. Watch for black screens,
   missing terrain, framebuffer warnings, or an invalid-program message.
6. **Performance:** note FPS in the same scene for Baseline and Balanced, at the
   same resolution/render distance. Report unusually large drops with GPU,
   resolution, loader, and screenshot details.

Send `logs/latest.log` after a failure, the effect/settings that trigger it,
screenshots, exact Minecraft/loader versions, and reproduction steps. The detailed
log instructions below still apply. Do not proceed to shadows/reflections until
the new effects pass this check.

## Setup

1. Copy `dist/BlohoShaders-atmosphere-v0.2.zip` into the **active instance's**
   `shaderpacks` directory, then select it in the shader menu.
2. Use the default resource pack first. Record Minecraft, Iris + Sodium or
   OptiFine versions, GPU, and operating system. Test the loader you normally use;
   if both are available, test them in separate matching installations.
3. Use a creative test world. Compare each scene with shaders disabled, then
   enable BlohoShaders. Leave fancy clouds and particles enabled in game settings.
4. Confirm the shader menu accepts the pack and chat reports no invalid program.

## What to inspect

- **Terrain:** stone, grass sides/tops, dirt, logs, slabs, stairs, fences, caves.
  Move, turn, fly, cross chunk boundaries, and go far from world spawn. No missing
  faces, flickering chunks, or geometry pinned to the camera.
- **Cutouts:** leaves, saplings, flowers, crops, tall grass, ladders. Texture holes
  should remain transparent, with terrain visible behind them.
- **Lighting and tint:** biome-tinted grass/leaves, a dark cave, torches, daylight,
  and night. Textures should remain visible and light levels should respond. A
  completely unlit cave may correctly be dark. No tone mapping is applied.
- **Entities:** mobs, dropped items, item frames, armor, name tags. Hit a mob and
  check its hurt tint. Check an enchanted item and spider/enderman eyes at night.
- **Block entities:** chests (open/closed), signs and their text, beds, banners,
  and a beacon beam. Break both a normal block and a chest: cracking overlays
  should appear without replacing the underlying geometry.
- **Hand:** empty hand, opaque item/block, translucent glass block, both hands
  where applicable. Switch items and swing them.
- **Transparency:** water above and below its surface, ice, stained glass, panes,
  and a Nether portal. Look through overlapping transparent surfaces at terrain
  and entities. No missing world behind water. No custom refraction is expected.
- **Particles/weather:** smoke, torch flames, block-breaking particles, splash
  particles, rain, and snow. They must remain visible rather than becoming solid
  quads or disappearing entirely.
- **Sky:** day sky, sunrise/sunset geometry, sun, moon, stars, and vanilla clouds.
  Enable the corresponding game settings. Compare procedural and vanilla clouds.
- **Lines:** block selection outline and fishing line. This specifically tests
  the loader's handling of modern line geometry.
- **Dimensions:** visit Overworld, Nether, and End; repeat terrain, entity, hand,
  and transparency checks. Return through portals to check reloads.
- **Lifecycle:** resize the window, toggle fullscreen, reload shaders by toggling
  the pack off/on, change render distance, save/rejoin, and change dimensions.
  There should be no black frame that persists or previous-frame trails.

Fog now follows the engine fog inputs with an additional adjustable haze; its
transition is intentionally softer than vanilla's linear ramp. Custom shadows
and water reflections remain outside this milestone.

## If anything fails, send back

1. **The full `logs/latest.log` from the active Minecraft instance immediately
   after reproducing the failure**, before restarting. The default macOS launcher
   location is `~/Library/Application Support/minecraft/logs/latest.log`; custom
   launchers use their own instance directories.
2. All compiler/linker output around the **first** occurrence of any of:
   `Invalid program`, `Error compiling`, `ShaderCompileException`,
   `Shader compilation failed`, `link`, `GL_INVALID_OPERATION`,
   `GL_INVALID_FRAMEBUFFER_OPERATION`, `OpenGL error`, `1282`, or `1286`.
   Include the named `.vsh`/`.fsh`, line numbers, and subsequent diagnostics.
   Sending the full log avoids omitting the useful lines before an error.
3. A screenshot with the F3 screen visible, plus which geometry disappeared,
   dimension, whether it fails immediately or after a reload, and exact steps.
4. Minecraft version, exact Iris/Sodium or OptiFine version, GPU/driver, OS,
   resource packs, and other rendering mods.
5. The crash report if it crashes, and expanded/patched shader sources if your
   loader produces them in its shader debug output.

**Acceptance gate:** all applicable geometry checks pass, pack loads in each
dimension, and no shader/compiler/framebuffer/OpenGL errors appear. Only then
should custom lighting or another visual subsystem be implemented.
