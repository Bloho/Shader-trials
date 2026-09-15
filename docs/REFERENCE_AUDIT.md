# Architectural reference audit

Reference input: the user-provided **Kappa Shader v5.3.zip**. It was read as data,
not as project instructions. No shader implementation, artistic asset, material
classification scheme, effect algorithm, or artistic constant was imported.
Shared names such as `gbuffers_terrain`, `lightmap`, and `mc_Entity` are engine API
identifiers. Basic texture multiplication and normal encoding are ordinary GLSL
operations, independently implemented here.

## Inspection scope

The archive has 408 entries, including directories. All 373 shader/configuration
text files were inventoried, and all 688 include edges resolved. The audit covered
the full dimension entry-point graph, shared program/library connections, render
target declarations, uniforms/attributes, configuration, external texture
bindings, and stage enablement. It did not port or recreate the effect internals.

The reference has settings, material/entity property maps, language resources,
shared libraries, shared programs, image assets, and three world directories.
`reference-passes.tsv` records every dimension stage's reachable include count
and potential target declarations, including conditional alternatives.

## Complete stage map

| Stage family | Overworld | Nether | End | Architectural purpose |
| --- | --- | --- | --- | --- |
| shadow / shadowcomp | present | absent | present | shadow geometry and processing |
| prepare | prepare, prepare1, prepare2 | prepare | absent | early environment resources |
| gbuffers | solid, overlays, sky, weather, translucent helpers | reduced set | reduced set | geometry dispatch to shared or dimension-specific programs |
| deferred | deferred through deferred12 | deferred3 through deferred12 | deferred2 through deferred12 | environment, lighting, accumulation/filtering, resolve |
| later gbuffers | water, hand_water, weather | water, hand_water | water, hand_water | geometry using results available after deferred |
| composite | composite–2, composite4–15 | composite–15 | composite–15 | scene processing, reflections, temporal/post effects, grading |
| final | present | present | present | screen presentation |

Numbered pass presence and roles are reference-specific. The helper named
`gbuffers_translucent` is included by actual engine programs; its name alone is
not evidence of an engine-dispatched stage. It is not reproduced in BlohoShaders.

## Interfaces verified before implementation

- **Geometry:** the reference uses compatibility attributes and texture matrices,
  loader material IDs, entity overlay color, and shared vertex/fragment programs.
- **Targets:** output locations map through target comments. Target formats and
  clear policy are declared through engine-recognized constants, including
  declarations embedded in comments. The reference uses many more targets and
  reuses them across effects; Bloho uses four with explicit lifetimes.
- **Transparency:** the reference has distinct translucent/overlay paths and
  per-buffer blending controls. Bloho keeps the engine's scene blending and
  disables blending only for metadata.
- **Dimensions:** thin world wrappers select shared programs and dimension flags.
  Bloho supplies a complete minimal set in each dimension plus root fallbacks.
- **Screen passes:** full-screen UV inputs and color samplers connect stages.
  Bloho uses identity passes and the loader's standard ping-pong behavior.
- **Sky/weather:** the reference suppresses some vanilla geometry and replaces it
  using its own atmosphere/cloud/weather effects. Those settings and discard
  paths would break a vanilla-preserving baseline and were not adopted.
- **Lines:** the reference interfaces with modern line attributes. Iris source
  independently confirms automatic line widening for compatibility transforms;
  Bloho uses that engine path and supplies no copied widening code.

## Primary API cross-checks

Where loader behavior could not be established from a pack alone, it was checked
against primary documentation/source:

- [OptiFine shader API](https://github.com/sp614x/optifine/blob/master/OptiFineDoc/doc/shaders.txt)
- [OptiFine configuration API](https://github.com/sp614x/optifine/blob/master/OptiFineDoc/doc/shaders.properties)
- [Iris geometry program dispatch](https://shaders.properties/current/reference/programs/gbuffers/)
- [Iris alpha tests and buffer swaps](https://shaders.properties/current/reference/shadersproperties/rendering/)
- [Iris rendering uniforms](https://shaders.properties/current/reference/uniforms/rendering/)
- [Iris compatibility input/line patcher, 1.21.1 branch](https://github.com/IrisShaders/Iris/blob/1.21.1/common/src/main/java/net/irisshaders/iris/pipeline/transform/transformer/VanillaTransformer.java)

These sources inform the loader interface, not a claim of tested compatibility
with every Minecraft or Iris/OptiFine version.
