# Minecraft acceptance test

## Setup

1. Copy `dist/BlohoShaders-baseline.zip` into the **active instance's**
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
  Enable the corresponding game settings. No custom sky or volumetric clouds.
- **Lines:** block selection outline and fishing line. This specifically tests
  the loader's handling of modern line geometry.
- **Dimensions:** visit Overworld, Nether, and End; repeat terrain, entity, hand,
  and transparency checks. Return through portals to check reloads.
- **Lifecycle:** resize the window, toggle fullscreen, reload shaders by toggling
  the pack off/on, change render distance, save/rejoin, and change dimensions.
  There should be no black frame that persists or previous-frame trails.

Fog parity with vanilla is outside this baseline: distant terrain and underwater
visibility can differ. Do not treat absent custom shadows, fog, water reflections,
or atmosphere as a failure of the geometry milestone.

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
