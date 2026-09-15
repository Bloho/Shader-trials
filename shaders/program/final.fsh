#include "/settings.glsl"
#if BLOHO_GRADE == 1
#include "/lib/grading.glsl"
#endif
uniform sampler2D colortex0;
#if BLOHO_BLOOM == 1
uniform sampler2D colortex4;
#endif
varying vec2 screenUV;

void main() {
    vec4 scene = texture2D(colortex0, screenUV);
#if BLOHO_BLOOM == 1
    vec3 bloom = texture2D(colortex4, screenUV).rgb;
    // Add bloom before highlight compression, so bright energy is not clipped.
#if BLOHO_GRADE == 1
    scene.rgb += bloom * BLOOM_STRENGTH;
#else
    scene.rgb += bloom * BLOOM_STRENGTH * (1.0 - clamp(scene.rgb, 0.0, 1.0));
#endif
#endif
#if BLOHO_GRADE == 1
    scene.rgb = blohoGrade(scene.rgb, screenUV);
#endif
    gl_FragColor = scene;
}
