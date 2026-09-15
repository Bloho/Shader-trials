#include "/settings.glsl"
uniform sampler2D colortex0;
#if BLOHO_BLOOM == 1
uniform sampler2D colortex4;
#endif
varying vec2 screenUV;

void main() {
    vec4 scene = texture2D(colortex0, screenUV);
#if BLOHO_BLOOM == 1
    vec3 bloom = texture2D(colortex4, screenUV).rgb;
    // Restrained display-space bloom. Preserve source alpha and avoid a global
    // exposure/tonemapping change to the already accepted vanilla scene.
    scene.rgb += bloom * BLOOM_STRENGTH * (1.0 - clamp(scene.rgb, 0.0, 1.0));
#endif
    gl_FragColor = scene;
}
