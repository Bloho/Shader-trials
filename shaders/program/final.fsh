uniform sampler2D colortex0;
varying vec2 screenUV;

void main() {
    gl_FragColor = texture2D(colortex0, screenUV);
}
