# BlohoShaders

Original Minecraft Java shaderpack foundation for the OptiFine/Iris shader
environment. This repository starts from an empty workspace; no old BlohoShaders
implementation is carried forward.

**Milestone 1 candidate: local validation passes; Minecraft acceptance is pending.**

## Install

Copy `dist/BlohoShaders-baseline.zip` into your Minecraft instance's `shaderpacks`
folder and select **BlohoShaders-baseline** in the shader menu. Do not unzip it
inside another shaderpack. Alternatively, copy this repository into
`shaderpacks/BlohoShaders` with `shaders` immediately inside that folder.

Start with the default resource pack. Test instructions and requested failure
logs are in [docs/TESTING.md](docs/TESTING.md).

## Baseline

- Shared texture, vertex tint, lightmap, normal, and material plumbing.
- Opaque, cutout, translucent, sky, cloud, entity, hand, particle, weather,
  block-breaking, glint, eye, beacon, and line entry points.
- Root fallback plus explicit Overworld, Nether, and End entry points.
- Four color targets and minimal deferred → composite → final presentation.
- Minecraft controls alpha testing, scene blending, and depth behavior.

No custom lighting, shadows, fog, sky, cloud synthesis, postprocessing, temporal
history, PBR, water distortion, or performance profiles are enabled. This is a
geometry and framebuffer foundation, not a pixel-identical recreation of all
vanilla rendering (in particular, vanilla distance/underwater fog is not yet
reimplemented). No visual subsystem should be added before the acceptance test.

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
python3 tools/validate.py --driver # macOS OpenGL compile/link checks
python3 tools/smoke_render.py      # macOS offscreen rendering checks
python3 tools/package.py           # validate and build installable ZIP
```

Python 3.9+ and clang are needed for validation. Driver tests need macOS graphics
access and are supplementary to testing both Minecraft loaders. The test tools
never launch Minecraft or alter its installation.

See [architecture](docs/ARCHITECTURE.md), [reference audit](docs/REFERENCE_AUDIT.md),
and [validation results](docs/VALIDATION.md).
