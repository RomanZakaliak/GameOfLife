"""
=============================================================================
 renderer.py  –  OpenGL / ModernGL rendering backend
=============================================================================

Glossary of OpenGL concepts used here (for the non-GL reader):
─────────────────────────────────────────────────────────────
• Texture     – A 2D image that lives on the GPU.  We use two of them to
                represent the "current" and "next" generation of the grid.
                Each pixel in the texture is one cell; the red channel
                stores alive (1.0) or dead (0.0).

• Shader      – A small program that runs *on the GPU*.  There are two
                kinds we use:
                  ▸ Vertex shader   – decides WHERE to draw (we just draw
                    a rectangle that fills the whole screen).
                  ▸ Fragment shader – decides WHAT COLOR each pixel gets.
                    We have two fragment shaders:
                      1. "compute" – reads the current-generation texture,
                         counts neighbours, applies Game-of-Life rules,
                         and writes the next generation.
                      2. "display" – reads the current-generation texture
                         and converts the red-channel value into a visible
                         colour so you can actually see the grid.

• Program     – A linked pair of (vertex + fragment) shaders, ready to run.

• VAO         – Vertex Array Object.  Bundles a vertex buffer (the quad
                corner positions) together with a shader program so a
                single `.render()` call draws the quad with that program.

• FBO         – Framebuffer Object.  Normally the GPU draws to the screen.
                An FBO redirects drawing into a texture instead.  We use
                one FBO to render the *next generation* into `next_tex`
                without touching the screen.

• Texture     – `.use(slot)` binds the texture to a numbered "slot".
  binding       The shader uniform (e.g. `uniform sampler2D current`)
                is told which slot to read from via `prog["current"] = slot`.

• TRIANGLE    – Two triangles that share an edge, forming a rectangle that
  STRIP         covers the whole screen (–1…+1 in clip-space).  The vertex
                shader converts these coordinates into 0…1 UV coordinates
                so the fragment shader can sample the texture.

Rendering pipeline each frame:
──────────────────────────────
  1. (if not paused)  compute pass  ──────────────────────────────────────
     ┌────────────┐   compute_fbo  ┌────────────┐
     │ current_tex│──► fragment   ──►│  next_tex  │
     └────────────┘   shader       └────────────┘
     Then swap current_tex ↔ next_tex.

  2. display pass  ───────────────────────────────────────────────────────
     ┌────────────┐    screen     ┌─────────────┐
     │ current_tex│──► fragment  ──►│ your monitor│
     └────────────┘    shader     └─────────────┘
=============================================================================
"""

from __future__ import annotations

import moderngl as mgl
import numpy as np

from src import options as op
from src.helpers import _load_all_shaders, _make_fullscreen_quad


class Renderer:
    def __init__(self) -> None:

        self._ctx: mgl.Context = mgl.create_context()
        self._ctx.viewport = (0, 0, op.WIDTH, op.HEIGHT)

        self._grid_w: int = op.H_RES
        self._grid_h: int = op.V_RES

        shaders = _load_all_shaders()
        vert_src = shaders["vertex_shader"]

        self._compute_prog: mgl.Program = self._ctx.program(
            vertex_shader=vert_src,
            fragment_shader=shaders["compute_shader"],
        )
        self._display_prog: mgl.Program = self._ctx.program(
            vertex_shader=vert_src,
            fragment_shader=shaders["fragment_shader"],
        )

        quad = _make_fullscreen_quad()
        vbo: mgl.Buffer = self._ctx.buffer(quad.tobytes())

        self._compute_vao: mgl.VertexArray = self._ctx.vertex_array(
            self._compute_prog, [(vbo, "2f", "position")]
        )
        self._display_vao: mgl.VertexArray = self._ctx.vertex_array(
            self._display_prog, [(vbo, "2f", "position")]
        )

        self._current_tex: mgl.Texture = self._ctx.texture(
            (self._grid_w, self._grid_h), 4
        )
        self._next_tex: mgl.Texture = self._ctx.texture((self._grid_w, self._grid_h), 4)

        for tex in (self._current_tex, self._next_tex):
            tex.filter = (mgl.LINEAR, mgl.NEAREST)

        self._compute_fbo: mgl.Framebuffer = self._ctx.framebuffer(
            color_attachments=[self._next_tex]
        )

        self._compute_prog["gridSize"] = (
            float(self._grid_w),
            float(self._grid_h),
        )

        self._compute_prog["current"] = 0
        self._display_prog["tex"] = 0
        self._display_prog["uTime"] = 0.0

    def release(self) -> None:
        self._ctx.release()

    def init_grid_random(self) -> None:
        data = (
            np.random.randint(0, 2, (self._grid_h, self._grid_w, 4), dtype=np.uint8)
            * 255
        )
        self._current_tex.write(data.tobytes())

    def init_grid(self, data: np.ndarray) -> None:
        if data.shape != (self._grid_h, self._grid_w, 4):
            raise ValueError(
                f"Expected shape ({self._grid_h}, {self._grid_w}, 4), got {data.shape}"
            )
        self._current_tex.write(data.tobytes())

    def step(self) -> None:
        self._compute_fbo.use()
        self._ctx.clear(0.0, 0.0, 0.0, 1.0)

        self._current_tex.use(0)

        self._compute_vao.render(mgl.TRIANGLE_STRIP)

        self._current_tex, self._next_tex = self._next_tex, self._current_tex
        self._compute_fbo = self._ctx.framebuffer(color_attachments=[self._next_tex])

    def draw(self) -> None:
        self._ctx.screen.use()
        self._ctx.clear(0.0, 0.0, 0.0, 1.0)

        self._current_tex.use(0)
        self._display_vao.render(mgl.TRIANGLE_STRIP)

    def write_cell(self, grid_x: int, grid_y: int) -> None:
        self.write_cells([(grid_x, grid_y)])

    def write_cells(self, coords: list[tuple[int, int]]) -> None:
        if not coords:
            return

        raw_texture: bytes = self._current_tex.read()
        grid = (
            np.frombuffer(raw_texture, dtype=np.uint8)
            .reshape((self._grid_h, self._grid_w, 4))
            .copy()
        )

        for gx, gy in coords:
            if 0 <= gx < self._grid_w and 0 <= gy < self._grid_h:
                grid[gy, gx, 0] = 255

        self._current_tex.write(grid.tobytes())

    def update_time_uniform(self, time: float) -> None:
        self._display_prog["uTime"] = time

    @property
    def grid_width(self) -> int:
        return self._grid_w

    @property
    def grid_height(self) -> int:
        return self._grid_h
