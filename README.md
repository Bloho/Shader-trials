# BlohoShaders

Original Minecraft Java shaderpack foundation for the OptiFine/Iris shader
environment. This repository starts from an empty workspace; no old BlohoShaders
implementation is carried forward.

**v0.3.2 shadow fix:** corrects repeating self-shadow stripes on inclined light-space surfaces. Ore glow remains included.

**v0.3.1 ore glow:** colored/metal ore veins and quartz now glow using the existing
bloom pipeline. Coal/ancient debris glow is optional. The baseline and atmosphere versions were confirmed
working by the user. This version adds directional lighting, sun/moon shadows,
emissive highlights, water sheen, and a stronger color grade. It still needs an
in-game check.

## Install

Copy `dist/BlohoShaders-shadow-fix-v0.3.2.zip` into your Minecraft instance's `shaderpacks`
folder and select **BlohoShaders-ores-v0.3.1** in the shader menu. Do not unzip it
inside another shaderpack. Alternatively, copy this repository into
`shaderpacks/BlohoShaders` with `shaders` immediately inside that folder.

Start with the default resource pack. Test instructions and requested failure
logs are in [docs/TESTING.md](docs/TESTING.md).

## Effects and controls

The default **Balanced** preset aims between vanilla and cinematic:

- Directional sun/moon lighting and one filtered, undistorted shadow map.
- Warm local lighting and brighter lava/glowstone/sea-lantern/shroomlight/lit-lamp texels.
- Stronger bloom, exposure, smooth contrast, saturation, and highlight roll-off.
- Animated water normals for sunlight highlights and an approximate sky sheen.
- Ore vein emission, including deepslate variants, Nether gold, and quartz.
- Biome/fluid-colored distance fog and a restrained atmospheric haze.
- Two moving procedural cloud layers, with day/night/rain color changes.

In **Shader Options**, each effect can be disabled independently. **Baseline
(effects off)** restores vanilla-style rendering and clouds (subject to the game's
cloud setting). **Atmosphere** restores the v0.2 effect settings. **Balanced** is
the new default; **Vivid** increases contrast, saturation, exposure, and bloom.
The earlier baseline and v0.2 ZIPs are retained as separate fallbacks.

**Shader Options → Ore glow** controls the effect and strength. Bloom must be on
for a surrounding halo. Emission itself works with directional lighting off.
Coal/ancient debris glow defaults off because dark coal and deepslate texels are
ambiguous without dedicated masks. Ore masks are tuned to vanilla texture colors;
unusual resource packs may need retuning. This is visual emission, not dynamic
illumination of neighboring blocks, and it does not show hidden ore through walls.

## Foundation

- Shared texture, vertex tint, lightmap, normal, and material plumbing.
- Opaque, cutout, translucent, sky, cloud, entity, hand, particle, weather,
  block-breaking, glint, eye, beacon, and line entry points.
- Root fallback plus explicit Overworld, Nether, and End entry points.
- Four geometry targets (including a floating-point scene), two half-resolution
  bloom targets, a shadow pass, and deferred → composite → bloom → final presentation.
- Minecraft controls alpha testing, scene blending, and depth behavior.

The implementation stays compact: no temporal history, screen-space reflections,
PBR texture dependency, voxel lighting, or volumetric ray marcher. Clouds remain
two soft sheets. Water's reflection is a sky-color approximation, not reflected
terrain. Lighting extends Minecraft's lightmap in display-referred color; the
floating-point scene retains highlights but is not a fully linear physical HDR
pipeline. All new effect code is original; no Kappa assets are required.

The source uses GLSL 1.20 compatibility inputs rather than Kappa's GLSL 4.30
requirement. Minecraft's shader loaders support these inputs; the baseline does
not need compute shaders or advanced GLSL. The intended initial test environment
is Minecraft Java 1.17+ with a matching Iris or OptiFine release. Exact version
compatibility remains unverified until tested in-game; older versions are not
an acceptance target.

## Develop

```sh
python3 tools/generate.py          # regenerate thin entry points and render state
python3 tools/validate.py          # includes, interfaces, outputs, world coverage
python3 tools/validate.py --driver --matrix # representative old/new combinations
python3 tools/smoke_render.py      # macOS offscreen rendering checks
python3 tools/package.py           # validate and build installable ZIP
```

Python 3.9+ and clang are needed for validation. Driver tests need macOS graphics
access and are supplementary to testing both Minecraft loaders. The test tools
never launch Minecraft or alter its installation.

See [architecture](docs/ARCHITECTURE.md), [reference audit](docs/REFERENCE_AUDIT.md),
and [validation results](docs/VALIDATION.md).
