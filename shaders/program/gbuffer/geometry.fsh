#include "/lib/geometry_interface.glsl"

#ifdef BLOHO_TEXTURED
uniform sampler2D gtexture;
#endif
#ifdef BLOHO_LIGHTMAP
uniform sampler2D lightmap;
#endif
#ifdef BLOHO_ENTITY_TINT
uniform vec4 entityColor;
#endif

void main() {
    vec4 surface = vertexTint;
#ifdef BLOHO_TEXTURED
    surface *= texture2D(gtexture, surfaceUV);
#endif
#ifdef BLOHO_ENTITY_TINT
    surface.rgb = mix(surface.rgb, entityColor.rgb, entityColor.a);
#endif
    vec3 illumination = vec3(1.0);
#ifdef BLOHO_LIGHTMAP
    illumination = texture2D(lightmap, lightUV).rgb;
#endif
    // With legacy gl_FragData, Iris/OptiFine applies the current alpha test.
    // Do not replace the input alpha with opaque alpha or a fixed threshold.
    gl_FragData[0] = vec4(surface.rgb * illumination, surface.a);

#ifdef BLOHO_SURFACE
    // Metadata is never alpha blended. This is a single visible surface,
    // not a representation of multiple translucent layers.
    gl_FragData[1] = surface;
    float normalLength = length(viewNormal);
    vec3 unitNormal = vec3(0.0);
    float normalValid = 0.0;
    if (normalLength > 0.0) {
        unitNormal = viewNormal / normalLength;
        normalValid = 1.0;
    }
    gl_FragData[2] = vec4(unitNormal * 0.5 + 0.5, normalValid);
    gl_FragData[3] = vec4(lightUV, materialId, BLOHO_FAMILY);
#endif
}
