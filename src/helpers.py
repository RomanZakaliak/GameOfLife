import os

import numpy as np

_SHADERS_DIR = os.path.join("shaders")
_SHADER_NAMES = ("vertex_shader", "compute_shader", "fragment_shader")


def _load_shader(name: str) -> str:
    path = os.path.join(_SHADERS_DIR, f"{name}.glsl")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except OSError as exc:
        raise RuntimeError(f"Could not load shader '{path}': {exc}") from exc


def _load_all_shaders() -> dict[str, str]:

    return {name: _load_shader(name) for name in _SHADER_NAMES}


def _make_fullscreen_quad() -> np.ndarray:
    return np.array(
        [
            # bottom-left
            -1.0,
            -1.0,
            # bottom-right
            +1.0,
            -1.0,
            # top-left
            -1.0,
            +1.0,
            # top-right
            +1.0,
            +1.0,
        ],
        dtype="f4",
    )
