#version 330 core

in vec4 vColor;
out vec4 FragColor;

void main() {
    vec2 c = gl_PointCoord - vec2(0.5);
    float d = dot(c, c);
    if (d > 0.25) {
        discard;
    }
    float alpha = smoothstep(0.25, 0.05, d) * vColor.a;
    FragColor = vec4(vColor.rgb, alpha);
}
