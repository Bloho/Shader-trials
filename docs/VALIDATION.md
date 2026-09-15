# Validation — 2026-09-16

## v0.2 atmosphere milestone

The user confirmed the original baseline works normally in Minecraft. That
confirmation authorized the next incremental effects milestone.

New changes: per-surface fog, original layered procedural Overworld clouds,
half-resolution bloom extraction/blur, independent options, and Baseline/Balanced
presets. The original ZIP remains untouched; the new package is
`BlohoShaders-atmosphere-v0.2.zip`.

- **800 compile/link variants passed:** 100 program pairs × all eight independent
  bloom/fog/cloud toggle combinations, on Apple M5 / OpenGL 2.1 Metal - 91.7.
- Static checks cover includes, generated entry points/properties, vertex/fragment
  varyings, shared uniform types, output indices, and six-target routing.
- **28 offscreen checks passed:** the 14 baseline regression checks, five fog
  checks (including alpha/metadata and additive overlays), four bloom checks
  (two-axis spread, alpha, and dark-scene rejection), and five cloud checks
  (visibility, opaque occlusion, fluid and dimension bypass).
- A synthetic 512×512 cloud render was visually inspected. The layers are
  visible, soft-edged, and fade near the horizon. This is a shader-harness image,
  not an in-game screenshot or proof of the final appearance in Minecraft.
- No OpenGL errors at the native test checkpoints. ZIP integrity is checked by
  the package builder.

The new effects are **not yet tested in Minecraft**. Loader option parsing,
actual fog uniforms, transparency ordering, shader reloads, dimension changes,
and FPS still need the v0.2 acceptance check in TESTING.md. The native harness
does not exercise Iris's rewritten shader variants or Minecraft's draw dispatch.

## Milestone 1 history

The following records the original baseline validation, before the user's
subsequent successful in-game test.

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
