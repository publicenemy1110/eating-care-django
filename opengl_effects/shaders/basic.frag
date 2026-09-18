#version 330 core

in vec3 vWorldPos;
in vec3 vNormal;
in vec2 vTex;
in vec4 vLightSpace;

uniform vec3 uCameraPos;
uniform vec3 uLightPos;
uniform vec3 uLightColor;
uniform vec3 uObjectColor;
uniform float uFogStart;
uniform float uFogEnd;
uniform vec3 uFogColor;
uniform bool uUseProcedural;
uniform sampler2D uShadowMap;

out vec4 FragColor;

float shadowFactor(vec4 lightSpace) {
    vec3 proj = lightSpace.xyz / lightSpace.w;
    proj = proj * 0.5 + 0.5;
    if (proj.z > 1.0 || proj.x < 0.0 || proj.x > 1.0 || proj.y < 0.0 || proj.y > 1.0) {
        return 1.0;
    }
    float closest = texture(uShadowMap, proj.xy).r;
    float current = proj.z - 0.002;
    float shadow = current > closest ? 0.35 : 1.0;
    return shadow;
}

vec3 proceduralColor(vec2 uv) {
    float stripes = sin(12.0 * uv.x + 8.0 * uv.y) * 0.5 + 0.5;
    float rings = sin(20.0 * length(uv - 0.5)) * 0.5 + 0.5;
    float marble = sin(5.0 * (uv.x + uv.y) + 3.0 * sin(7.0 * uv.x)) * 0.5 + 0.5;
    vec3 c1 = vec3(0.15, 0.45, 0.85);
    vec3 c2 = vec3(0.9, 0.85, 0.75);
    return mix(c1, c2, mix(stripes, rings, marble));
}

void main() {
    vec3 N = normalize(vNormal);
    vec3 L = normalize(uLightPos - vWorldPos);
    vec3 V = normalize(uCameraPos - vWorldPos);
    vec3 H = normalize(L + V);

    vec3 albedo = uUseProcedural ? proceduralColor(vTex) : uObjectColor;

    float diff = max(dot(N, L), 0.0);
    float spec = pow(max(dot(N, H), 0.0), 48.0);

    float shadow = shadowFactor(vLightSpace);

    vec3 ambient = 0.12 * albedo;
    vec3 diffuse = diff * albedo * uLightColor * shadow;
    vec3 specular = spec * vec3(0.9) * uLightColor * shadow;

    vec3 lit = ambient + diffuse + specular;

    float dist = length(uCameraPos - vWorldPos);
    float fogFactor = clamp((uFogEnd - dist) / (uFogEnd - uFogStart), 0.0, 1.0);
    vec3 color = mix(uFogColor, lit, fogFactor);

    FragColor = vec4(color, 1.0);
}
