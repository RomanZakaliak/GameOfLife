// ===========================================================================
// Vertex Shader – positions the full-screen quad
// ===========================================================================
//
// This shader runs once per vertex (we have 4 vertices forming a quad).
// Its only job is to:
//   1. Pass the vertex position through to gl_Position so OpenGL knows
//      where to draw.
//   2. Compute a UV texture coordinate (0…1) from the clip-space
//      position (–1…+1) so the fragment shader can sample the grid
//      texture.
//
// Clip-space reminder:
//     (-1,+1)          (+1,+1)
//        ┌────────────────┐
//        │                │
//        │   visible      │
//        │   screen       │
//        │                │
//        └────────────────┘
//     (-1,-1)          (+1,-1)
//
// UV-space (texture coordinates):
//     (0, 1)            (1, 1)
//        ┌────────────────┐
//        │                │
//        │   texture      │
//        │                │
//        └────────────────┘
//     (0, 0)            (1, 0)
//
// The conversion is: uv = clipPosition * 0.5 + 0.5
//   e.g. -1 * 0.5 + 0.5 = 0,  +1 * 0.5 + 0.5 = 1
// ===========================================================================

#version 330 core

// Input: the 2D position of this vertex, supplied from the VBO via the VAO.
// Values are in clip-space: (-1,-1) to (+1,+1).
in vec2 position;

// Output: the texture coordinate passed to the fragment shader.
// The GPU automatically interpolates this across the quad surface,
// so every fragment (pixel) receives a unique UV between 0 and 1.
out vec2 texCoord;

void main() {
    // Convert clip-space (-1…+1) to texture-space (0…1).
    texCoord = position * 0.5 + 0.5;

    // gl_Position is a built-in output that tells OpenGL the final
    // position of this vertex.  Z=0 (flat 2D), W=1 (no perspective).
    gl_Position = vec4(position, 0.0, 1.0);
}
