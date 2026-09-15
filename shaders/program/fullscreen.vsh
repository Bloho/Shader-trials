varying vec2 screenUV;

void main() {
    screenUV = gl_MultiTexCoord0.xy;
    // The engine supplies a full-screen quad with texture coordinates [0,1].
    gl_Position = vec4(screenUV * 2.0 - vec2(1.0), 0.0, 1.0);
}
