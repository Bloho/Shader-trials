# Milestone 1 validation — 2026-09-16

## Changes

- Created an original shaderpack in the previously empty local Git workspace.
- Added one shared geometry renderer, three screen-pass fragments, and one
  screen-pass vertex shader.
- Generated complete root/Overworld/Nether/End entry points from a single manifest.
- Added four explicit color target formats, clear policy, and metadata-only
  blending overrides. No custom texture assets or shadow resources.
- Added a small original block identity map, architecture/reference notes,
  validation scripts, and an installable ZIP builder.

## Completed checks

- **88 program pairs:** includes resolve without cycles or escaping the pack;
  generated world entry points are complete and current; vertex/fragment varying
  declarations match; shared uniforms have compatible types; output indices match
  draw-buffer declarations; no gbuffer render-target feedback sampling.
- **Native compilation/linking:** all 88 pairs passed on Apple M5,
  `OpenGL 2.1 Metal - 91.7`, using the compatibility driver context. No compile or
  link failures, and no OpenGL errors during those checks.
- **Four-attachment framebuffer:** RGBA8/RGBA8/RGBA16F/RGBA32F attachments complete
  successfully in the offscreen test.
- **14 offscreen rendering assertions:** texture × tint × lightmap; source alpha;
  stored surface color/coverage; normal validity; material/lightmap/family data;
  invisible-fragment rejection and metadata preservation; deferred identity;
  translucent scene blending; unblended translucent metadata and identity;
  composite identity; final identity; untextured sky; weather. No OpenGL errors
  occurred at assertion checkpoints.

The offscreen harness manually applies the documented loader state. Its initial
framebuffer transition failed because it retained a read attachment after
detaching that attachment; the harness was corrected, and the final run passes.
That was not a shaderpack failure.

## Still requires Minecraft

No Minecraft session was launched. Iris patches input/output GLSL and chooses
draw-specific state; OptiFine does its own dispatch and compatibility handling.
These exact loader paths, terrain/chunk input layouts, depth/culling, line
expansion, real entity/particle textures, cloud geometry, and dimension switches
cannot be certified by the offscreen harness. The test has no depth attachment;
depth behavior is intentionally left to Minecraft and must be checked there.

This is a **locally validated first-milestone candidate**, not a claim that
every geometry category has already passed in-game or that Minecraft will emit
zero OpenGL errors. Follow TESTING.md before adding effects.
