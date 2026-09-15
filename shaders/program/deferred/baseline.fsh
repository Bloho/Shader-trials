#include "/lib/targets.glsl"
#include "/settings.glsl"
#if BLOHO_CLOUDS == 1 && BLOHO_DIMENSION == 0
#include "/lib/clouds.glsl"
#endif
uniform sampler2D colortex0;
varying vec2 screenUV;

void main() {
    // Reads main, writes alt; the engine flips colortex0 after this pass.
    // Later translucent draws blend onto this copied scene.
    vec4 scene = texture2D(colortex0, screenUV);
#if BLOHO_CLOUDS == 1 && BLOHO_DIMENSION == 0
    scene.rgb = blohoClouds(scene.rgb, screenUV);
#endif
    gl_FragData[0] = scene;
}
