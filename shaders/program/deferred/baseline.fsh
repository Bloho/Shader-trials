#include "/lib/targets.glsl"
uniform sampler2D colortex0;
varying vec2 screenUV;

void main() {
    // Reads main, writes alt; the engine flips colortex0 after this pass.
    // Later translucent draws blend onto this copied scene.
    gl_FragData[0] = texture2D(colortex0, screenUV);
}
