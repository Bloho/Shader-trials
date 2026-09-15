#ifndef BLOHO_GEOMETRY_INTERFACE
#define BLOHO_GEOMETRY_INTERFACE
varying vec4 vertexTint;
#ifdef BLOHO_TEXTURED
varying vec2 surfaceUV;
#endif
#ifdef BLOHO_LIGHTMAP
varying vec2 lightUV;
#endif
#ifdef BLOHO_SURFACE
varying vec3 viewNormal;
varying float materialId;
#endif
#endif
