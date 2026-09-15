// Fog is evaluated per surface before alpha blending, so glass, particles and
// water use their own distance rather than an opaque depth behind them.
uniform int fogMode;
uniform int fogShape;
uniform float fogStart;
uniform float fogEnd;
uniform float fogDensity;
uniform vec3 fogColor;
uniform float far;
uniform float rainStrength;

float blohoVisibility(vec3 viewPosition) {
    float distanceToEye = length(viewPosition);
    if (fogShape == 1) {
        distanceToEye = max(length(viewPosition.xz), abs(viewPosition.y));
    }
    float visibility = 1.0;
    // OpenGL fog mode enum values, not artistic constants.
    if (fogMode == 9729 && fogEnd > fogStart) {
        visibility = 1.0 - smoothstep(fogStart, fogEnd, distanceToEye);
    } else if (fogMode == 2048) {
        visibility = exp(-max(fogDensity, 0.0) * distanceToEye);
    } else if (fogMode == 2049) {
        float opticalDistance = max(fogDensity, 0.0) * distanceToEye;
        visibility = exp(-opticalDistance * opticalDistance);
    }
    // A restrained distance haze in addition to the engine's biome/fluid fog.
    // Guard against absent uniforms in offline tools or unsupported loaders.
    if (far > 0.0) {
        float hazeDistance = max(distanceToEye - 16.0, 0.0);
        float density = FOG_STRENGTH * (1.0 + 1.8 * rainStrength) / max(far * 2.8, 128.0);
        visibility *= exp(-hazeDistance * density);
    }
    return clamp(visibility, 0.0, 1.0);
}

vec3 blohoFog(vec3 color, vec3 viewPosition) {
    float visibility = blohoVisibility(viewPosition);
#ifdef BLOHO_ADDITIVE
    // Additive overlays must fade to zero, not add a second fog-colored veil.
    return color * visibility;
#else
    return mix(fogColor, color, visibility);
#endif
}
