// ===========================================================================
// Display Shader (Fragment) – Visualises the grid on screen
// ===========================================================================
//
// This shader runs once per screen pixel.  Its job is purely cosmetic:
// read the current-generation texture and convert the raw red-channel
// value (0.0 = dead, 1.0 = alive) into a colour the user can see.
//
// The compute shader stores the game state in the RED channel only.
// This display shader reads that channel and maps it:
//   • alive (r > 0.5)  →  bright green
//   • dead  (r ≤ 0.5)  →  black (background)
//
// Because the grid texture is much smaller than the screen (e.g. 81×61
// cells vs. 800×600 pixels), OpenGL stretches the texture to fill the
// quad.  The NEAREST filter (set in renderer.py) ensures each cell
// appears as a crisp, blocky square rather than a blurry smear.
//
// You can customise the alive/dead colours here without touching any
// Python code – this shader is the only place that controls appearance.
// ===========================================================================

#version 330 core

uniform sampler2D tex;
uniform float uTime;

in vec2 texCoord;

out vec4 fragColor;

void main() {
    vec4 cell = texture(tex, texCoord);
    float alive = cell.r;
    float normalTime = abs(sin(uTime) * 3.1415) ;
    float intensity = step(0.5, alive);

    fragColor = vec4(normalTime, intensity, cos(texCoord.y) * normalTime , 1.);
}
