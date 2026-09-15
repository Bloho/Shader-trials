# BlohoShaders architecture — v0.3

## Lighting milestone additions

The user's successful v0.2 test unlocked the next milestone. Four shared files
implement the new look: `lighting.glsl`, `shadow.glsl`, `shadow_config.glsl`, and
`grading.glsl`, plus one shadow caster vertex/fragment pair. No additional scene
postprocess passes or color targets were added.

- **Lighting:** shared forward surface lighting preserves sampled Minecraft
  lightmap levels and vertex AO. With Lighting enabled, a conditional
  `oldLighting=false` property removes the engine's fixed face tint, and normal
  lighting provides directionality. Disabling it restores `oldLighting=true`.
  Direct light follows the shadow-light direction; ambient remains in shadow.
  Local light is warmed without introducing a separate dynamic-light system.
- **Shadows:** a regular orthographic 2048 map covers 96 blocks by default.
  Caster geometry uses the engine's light-camera transform. Receivers transform
  camera-relative position through shadowModelView/shadowProjection, apply a
  small normal offset, and average nine explicit depth comparisons. Visibility
  fades at map boundaries/range. No distorted map, cascade, colored shadow, or
  contact-hardening system. Transparent terrain is excluded. The caster also
  rejects water/plain glass and texture alpha below its binary cutout threshold.
- **Scope:** shadow reception runs for Overworld/root surfaces other than hand.
  Nether/End shadow programs are disabled. They receive simple normal-based face
  shading and local warmth without assuming an Overworld sun. Each world/root has
  a complete shader set: **104 program pairs**.
- **Emission:** the original ID table adds class 5 for selected bright blocks;
  lava/class 5 bright texels can exceed display white. Other resource-pack
  emissive/PBR materials are not automatically inferred.
- **Water:** water's normal is perturbed for shading only, producing animated
  specular highlights and a grazing-angle sky-color sheen. It changes neither
  mesh position nor alpha, and does not implement scene reflections/refraction.
- **Presentation:** colortex0 is now RGBA16F. Existing bloom buffers retain bright
  energy until final presentation. Final adds bloom, adjusts exposure/warmth,
  compresses highlight magnitude while preserving channel ratios, then applies
  saturation, smooth contrast, and optional mild vignette. No copied filmic LUT
  or tone curve. This remains a display-referred, art-directed pipeline; float
  storage does not imply fully linear physical lighting.

Baseline turns all effects off, Atmosphere restores v0.2 settings, Balanced is
the new default, and Vivid is stronger grading at the same rendering cost. The
former ZIPs are preserved. Float scene storage may differ from the original
RGBA8 baseline by small rounding amounts. Shadow allocation/dispatch is selected
by conditional program directives and shadow sampler usage.

The historical sections below remain useful for the geometry/buffer contract;
this section supersedes claims that shadow maps or custom lighting are absent.

## Atmosphere milestone additions

The user confirmed the original baseline in-game. The geometry transform and
texture/lightmap/alpha contract remains intact. The new effects are:

- `lib/fog.glsl`: per-fragment view-space fog before scene blending. Engine fog
  mode, shape, start/end, density, and color are honored, with adjustable distance
  haze. Only scene RGB changes; metadata and alpha do not. Glints/eyes attenuate
  toward black to avoid adding fog color; hand and breaking overlays keep their
  original treatment.
- `lib/clouds.glsl`: original noise-defined sheets at the chosen world height and
  28 blocks above. Deferred reconstructs the viewing ray using depthtex0 and the
  inverse camera matrices, clips intersections against opaque scene depth, and
  composites the farther sheet first. Runs only for Overworld/root with the
  option enabled and camera outside fluids. Vanilla cloud fragments are discarded
  only when their procedural replacement is enabled. Neither layer writes depth.
- `composite1`: thresholds highlights and downsamples scene color into colortex4.
- `composite2`: horizontal normalized triangular blur, colortex4 → colortex5.
- `composite3`: vertical blur, colortex5 → colortex4.
- `final`: blends restrained bloom into scene RGB, preserving alpha.

colortex4 and colortex5 are RGBA16F, half the viewport width/height (one quarter
the pixels), and are never gbuffer outputs. They are fully written each frame,
with regular engine ping-pong swaps. No metadata buffer is reused. There are now
25 programs per dimension/root set, or **100 vertex/fragment pairs**. When bloom
is off, its passes write black and final bypasses it; the small pass/allocation
overhead remains. Disabling all three effects restores the baseline color path.

`settings.glsl`, generated shader-option screens, and Baseline/Balanced presets
control the features. These are presentation presets, not hardware quality tiers.
The settings are independently compilable in all eight on/off combinations.

### Current limits

Clouds approximate soft layers rather than a volumetric medium. No cloud shadows,
temporal reconstruction, atmospheric scattering, or per-pixel volumetric lighting
are involved. Transparent content drawn before deferred without useful depth may
interact with cloud ordering; it needs in-game testing. Cloud motion uses the
engine frame timer, which can reset after long sessions. Bloom is display-space
highlight bloom, not physically based HDR lighting or an emissive-material mask.

The sections below describe the inherited baseline contract; screen-pass changes
above supersede the original identity-only deferred/final behavior.

## Structure

```text
shaders/
  lib/geometry_interface.glsl    shared vertex/fragment contract
  lib/targets.glsl               buffer formats and clear policy
  program/gbuffer/geometry.*     one geometry implementation with input flags
  program/deferred/baseline.fsh  scene/cloud pass before later geometry
  program/composite/baseline.fsh identity pass after geometry
  program/fullscreen.vsh         shared screen quad
  program/composite/bloom_*.fsh  highlight extraction and separable blur
  program/final.fsh              bloom resolve and presentation
  lib/fog.glsl, lib/clouds.glsl   original atmosphere components
  settings.glsl                  effect toggles and controls
  gbuffers_*.vsh/.fsh            root fallback entry points
  deferred.*, composite.*, final.*
  world0/, world-1/, world1/     thin dimension entry points
  shaders.properties            engine settings and metadata blending
  block.properties              original material identity assignments
tools/generate.py               authoritative entry point/flag manifest
```

There are 19 geometry programs and six screen programs per entry-point set,
with four sets (100 pairs). The repetition is loader-facing wrappers, not 100
implementations. Root entries cover fallback dimensions; each named vanilla
dimension has a complete set and defines its dimension for future use.

## Pass sequence and ownership

1. The engine clears scene color to its fog background and clears metadata to zero.
2. Early geometry writes lightmapped color into `colortex0`. Terrain, entities,
   block entities, and the opaque hand also write surface metadata.
3. `deferred` samples current `colortex0`, adds enabled Overworld clouds, and writes
   its alternate texture. The loader
   flips that target; metadata is neither written nor flipped by this pass.
4. Later geometry, including water/translucent terrain, translucent hand, and
   weather, renders onto the resulting scene. Water and translucent hand update
   surface metadata; weather and other overlays write scene color only.
5. `composite` copies the completed scene through another automatic target swap.
6. `composite1`–`composite3` extract and blur highlights using targets 4 and 5.
7. `final` resolves scene color and enabled bloom into the screen framebuffer.

No gbuffer samples a render target it writes. Only bloom buffers use a custom size.
No history, mipmaps, shadow samplers, or persistent buffers are allocated.

## Buffer contract

| Target | Format | Contents | Lifetime |
| --- | --- | --- | --- |
| colortex0 | RGBA16F | scene RGB, including enabled lighting/fog; source alpha follows texture × vertex alpha | scene, deferred, later geometry, composite, final |
| colortex1 | RGBA8 | texture × vertex color, including entity overlay tint; alpha is surface coverage | metadata-writing geometry until next frame |
| colortex2 | RGBA16F | view-space unit normal encoded as n/2 + 1/2; A=normal validity | metadata-writing geometry until next frame |
| colortex3 | RGBA32F | RG=transformed lightmap UV; B=loader material ID; A=geometry family | metadata-writing geometry until next frame |

32-bit material storage avoids losing integer IDs to half-float rounding. Family
values are local schema identifiers: 0=empty, 1=terrain, 2=block entity, 3=entity,
4=hand, 5=translucent terrain, 6=translucent hand. Unassigned material IDs are
retained from the loader; hand material IDs are -1 until item mapping is added.
The small block map assigns water=1, lava=2, six common leaf types=3, plain glass
and pane=4. These IDs do not change appearance. Other blocks are unclassified.

The stored surface color still contains Minecraft's vertex AO and directional
shading. Before implementing custom lighting, revise that input contract so the
same shading is not applied twice; it is not currently raw PBR base color.

`depthtex0`, `depthtex1`, and `depthtex2` are engine-managed depth resources. No
custom depth encoding is introduced. The new cloud pass samples depthtex0.

Metadata is **one record per pixel for the last metadata-writing fragment that
passes depth/alpha testing**. It is never alpha blended. It does not encode
multiple transparent layers. Mixed translucent entities can also be drawn before
deferred on the legacy pipeline. At composite time, translucent terrain may have
replaced the earlier surface metadata. Before adding actual deferred lighting or
reflections, establish separate opaque/translucent ownership or copy the opaque
records at deferred time. This limitation cannot affect current scene color,
because metadata is not used to shade this baseline.

## Geometry inputs

All geometry uses the same `ftransform()` position path. The texture matrix for
unit 0 transforms `gl_MultiTexCoord0`; the lightmap matrix for unit 1 transforms
`gl_MultiTexCoord1`. Vertex RGBA is retained. Surface normals use `gl_NormalMatrix`
and are normalized safely in the fragment stage. `mc_Entity`, `entityId`, and
`blockEntityId` are read only by their corresponding surface variants.

Basic geometry, lines, sky, and modern vanilla clouds use vertex color without
sampling an assumed texture. Sun/moon, glints, eyes, and beacons use texture and
tint without darkening emissive geometry through the lightmap. Lit particles,
weather, and surfaces sample the engine lightmap. `entityColor` is applied to
entities and block entities. Breaking overlays preserve their engine blend mode.

With GLSL 1.20 `gl_FragData`, the loader/fixed-function path performs alpha testing
on output 0. There is no hardcoded discard threshold or global alpha-test override.
`separateAo=false` retains AO in vertex RGB rather than consuming vertex alpha.
`oldLighting=true` requests the engine's directional shading. Output 0 always
retains the engine's blend behavior; only metadata attachments disable blending.

The compatibility line path relies on the loader's transform patching (verified
in Iris's `VanillaTransformer`); there is no copied line-widening implementation.
OptiFine line rendering is an explicit in-game acceptance check.

## Next extension boundary

After atmosphere acceptance, directional lighting belongs in deferred, translucent lighting
in the geometry path, and final presentation stays independent. Shared libraries
can extend the current fog/clouds and later host shadows, water, materials, and animation.
Dimension flags are ready for Overworld/Nether/End distinctions. Profiles should
be introduced only when actual quality/cost settings exist. No empty effect
subsystems or misleading quality profiles are shipped now.
