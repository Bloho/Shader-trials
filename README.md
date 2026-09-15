# BlohoShaders

Original Minecraft Java shaderpack foundation for the OptiFine/Iris shader
environment. This repository starts from an empty workspace; no old BlohoShaders
implementation is carried forward.

**v0.2 atmosphere milestone:** the vanilla baseline was confirmed working by the
user. Bloom, fog, and soft procedural clouds are now implemented and locally
validated; this new version still needs an in-game check.

## Install

Copy `dist/BlohoShaders-atmosphere-v0.2.zip` into your Minecraft instance's `shaderpacks`
folder and select **BlohoShaders-atmosphere-v0.2** in the shader menu. Do not unzip it
inside another shaderpack. Alternatively, copy this repository into
`shaderpacks/BlohoShaders` with `shaders` immediately inside that folder.

Start with the default resource pack. Test instructions and requested failure
logs are in [docs/TESTING.md](docs/TESTING.md).

## Effects and controls

The default **Balanced** preset aims between vanilla and cinematic:

- Soft highlight bloom, with strength, threshold, and radius controls.
- Biome/fluid-colored distance fog and a restrained atmospheric haze.
- Two moving procedural cloud layers, with day/night/rain color changes.

In **Shader Options**, each effect can be disabled independently. **Baseline
(effects off)** restores the accepted geometry presentation and vanilla clouds
(subject to the game's cloud setting). **Balanced** restores the default values.
The original `dist/BlohoShaders-baseline.zip` is retained as a separate fallback.

## Foundation

- Shared texture, vertex tint, lightmap, normal, and material plumbing.
- Opaque, cutout, translucent, sky, cloud, entity, hand, particle, weather,
  block-breaking, glint, eye, beacon, and line entry points.
- Root fallback plus explicit Overworld, Nether, and End entry points.
- Four geometry targets, two half-resolution bloom targets, and modular
  deferred → composite → bloom → final presentation.
- Minecraft controls alpha testing, scene blending, and depth behavior.

Clouds are a lightweight layered approximation, not full volumetric clouds. Bloom
uses the existing display-space scene, so it can glow on bright non-emissive
surfaces too. Fog is evaluated per surface before transparency blending. There
are no shadow maps, custom terrain lighting, temporal history, PBR, water
reflections, or color grading yet. Those remain subsequent milestones after this
version is tested. All new effect code is original; no Kappa assets are required.

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
python3 tools/validate.py --driver --matrix # all 8 effect-toggle combinations
python3 tools/smoke_render.py      # macOS offscreen rendering checks
python3 tools/package.py           # validate and build installable ZIP
```

Python 3.9+ and clang are needed for validation. Driver tests need macOS graphics
access and are supplementary to testing both Minecraft loaders. The test tools
never launch Minecraft or alter its installation.

See [architecture](docs/ARCHITECTURE.md), [reference audit](docs/REFERENCE_AUDIT.md),
and [validation results](docs/VALIDATION.md).
