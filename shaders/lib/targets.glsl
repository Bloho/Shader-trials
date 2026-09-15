// Engine directives are deliberately in a comment: RGBA8 etc. are loader
// tokens, not GLSL identifiers. Included by the deferred fragment entry point.
/*
const int colortex0Format = RGBA16F;
const int colortex1Format = RGBA8;
const int colortex2Format = RGBA16F;
const int colortex3Format = RGBA32F;
const int colortex4Format = RGBA16F;
const int colortex5Format = RGBA16F;
*/
const bool colortex0Clear = true;
const bool colortex1Clear = true;
const bool colortex2Clear = true;
const bool colortex3Clear = true;
const bool colortex4Clear = true;
const bool colortex5Clear = true;
// Leave colortex0's clear color at the engine default (current fog color).
const vec4 colortex1ClearColor = vec4(0.0);
const vec4 colortex2ClearColor = vec4(0.0);
const vec4 colortex3ClearColor = vec4(0.0);
const vec4 colortex4ClearColor = vec4(0.0);
const vec4 colortex5ClearColor = vec4(0.0);
