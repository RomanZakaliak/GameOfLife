// ===========================================================================
// Compute Shader (Fragment) – Game of Life next-generation logic
// ===========================================================================
//
// This shader runs once per pixel of the output texture.  Each pixel
// represents one cell in the grid.  It reads the CURRENT generation
// from a texture and writes the NEXT generation into the framebuffer
// (which is attached to the "next" texture via an FBO).
//
// How it works:
//   1. Figure out the UV coordinate of this pixel (passed from vertex shader).
//   2. For each of the 8 surrounding neighbours, sample the texture
//      at a one-pixel offset and check if the red channel > 0.5
//      (meaning "alive").
//   3. Apply Conway's Game of Life rules:
//        • A dead  cell with exactly 3 neighbours becomes alive.
//        • A live  cell with 2 or 3 neighbours stays alive.
//        • Everything else dies (or stays dead).
//   4. Write the result into the red channel of the output colour.
//
// Texture sampling note:
//   UV coordinates go from 0.0 to 1.0, but we need to step exactly
//   one cell at a time.  Since the texture has `gridSize` cells,
//   one cell = 1.0 / gridSize in UV space.  That's `pixelSize` below.
//
//   Edge behaviour: by default, OpenGL clamps texture reads at the
//   border, so cells on the edge effectively see "dead" neighbours
//   outside the grid (no wrapping).
// ===========================================================================

#version 330 core

// The current generation texture, bound to slot 0 from Python.
uniform sampler2D current;

// Grid dimensions in cells (e.g. 81 x 61).  Passed from Python so
// we can calculate the UV offset for one cell.
uniform vec2 gridSize;

// Interpolated texture coordinate from the vertex shader (0…1).
in vec2 texCoord;

// The colour we write into the FBO's texture attachment.
// Only the red channel matters (alive / dead).
out vec4 outColor;

void main() {

    vec2 pixelSize = 1.0 / gridSize;
    vec2 uv = clamp(texCoord, pixelSize * 0.5, vec2(1.0) - pixelSize * 0.5);


    int neighbors = 0;

    for (int dy = -1; dy <= 1; dy++) {
        for (int dx = -1; dx <= 1; dx++) {
            if (dx == 0 && dy == 0) continue;

            vec2 neighborUV = uv + vec2(float(dx), float(dy)) * pixelSize;

            float alive = texture(current, neighborUV).r;
            neighbors += int(alive > 0.5);
        }
    }

    float currentState = texture(current, uv).r;
    bool isAlive = currentState > 0.5;


    bool nextAlive = false;

    if (neighbors == 3) {
        nextAlive = true;
    } else if (isAlive && neighbors == 2) {
        nextAlive = true;
    }

    outColor = vec4(float(nextAlive), 0.0, 0.0, 1.0);
}
