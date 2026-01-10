# webgl_canvas.py
import random

# Realistic GPU renderers and vendors (common ones)
GPU_RENDERERS = [
    "ANGLE (Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0)",
    "ANGLE (NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0)",
    "ANGLE (AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0)",
    "Google SwiftShader",
    "Intel Iris OpenGL Engine",
    "Apple M1 GPU",
]

GPU_VENDORS = ["Intel Inc.", "NVIDIA Corporation", "AMD", "Google Inc.", "Apple Inc."]

# Canvas fingerprint seeds (simulate subtle variations)
CANVAS_SEEDS = [
    "canvas_fp_1",
    "canvas_fp_2",
    "canvas_fp_3",
    "canvas_fp_4",
    "canvas_fp_5",
]


def get_random_webgl():
    """
    Returns a realistic simulated WebGL fingerprint dictionary.
    """
    return {
        "vendor": random.choice(GPU_VENDORS),
        "renderer": random.choice(GPU_RENDERERS),
        "webgl_version": "WebGL 1.0",
        "extensions": [
            "EXT_texture_filter_anisotropic",
            "OES_element_index_uint",
            "WEBGL_debug_renderer_info",
        ],
    }


def get_random_canvas():
    """
    Returns a simulated Canvas fingerprint string.
    In a real browser, this would be pixel data, here we simulate variations.
    """
    return random.choice(CANVAS_SEEDS)
