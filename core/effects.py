"""Visual effects - gradients, shadows, vignette, flash."""

from PIL import Image, ImageDraw, ImageFilter
from typing import Tuple
import math

from .easing import flash_fade


def create_gradient_fast(
    width: int,
    height: int,
    color_top: str = "#1a1a2e",
    color_bottom: str = "#0f0f1a"
) -> Image.Image:
    """Vertical gradient background."""
    try:
        import numpy as np

        def hex_to_rgb(h):
            h = h.lstrip('#')
            return [int(h[i:i+2], 16) for i in (0, 2, 4)]

        top = np.array(hex_to_rgb(color_top))
        bottom = np.array(hex_to_rgb(color_bottom))

        gradient = np.zeros((height, width, 3), dtype=np.uint8)

        for y in range(height):
            ratio = y / height
            color = top + (bottom - top) * ratio
            gradient[y, :] = color.astype(np.uint8)

        return Image.fromarray(gradient, 'RGB')
    except ImportError:
        img = Image.new('RGB', (width, height))
        def hex_to_rgb(h):
            h = h.lstrip('#')
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

        top = hex_to_rgb(color_top)
        bottom = hex_to_rgb(color_bottom)

        for y in range(height):
            ratio = y / height
            r = int(top[0] + (bottom[0] - top[0]) * ratio)
            g = int(top[1] + (bottom[1] - top[1]) * ratio)
            b = int(top[2] + (bottom[2] - top[2]) * ratio)
            for x in range(width):
                img.putpixel((x, y), (r, g, b))
        return img


def add_vignette(img: Image.Image, strength: float = 0.4) -> Image.Image:
    """Add dark vignette around edges."""
    try:
        import numpy as np

        arr = np.array(img, dtype=np.float32)
        h, w = arr.shape[:2]

        y, x = np.ogrid[:h, :w]
        cx, cy = w / 2, h / 2

        dist = np.sqrt((x - cx)**2 + (y - cy)**2)
        max_dist = np.sqrt(cx**2 + cy**2)
        dist = dist / max_dist

        vignette = 1 - (dist ** 2) * strength
        vignette = np.clip(vignette, 0, 1)

        arr = arr * vignette[:, :, np.newaxis]
        arr = np.clip(arr, 0, 255).astype(np.uint8)

        return Image.fromarray(arr)
    except ImportError:
        return img


def apply_flash(img: Image.Image, progress: float, intensity: float = 0.2, color: str = "#FFFFFF") -> Image.Image:
    """Apply flash overlay with eased fade."""
    if progress >= 1 or intensity <= 0:
        return img

    opacity = flash_fade(progress) * intensity

    if opacity < 0.01:
        return img

    def hex_to_rgb(h):
        h = h.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    flash_color = hex_to_rgb(color)
    flash = Image.new('RGB', img.size, flash_color)

    return Image.blend(img, flash, opacity)


def create_animated_gradient(
        width: int,
        height: int,
        frame: int,
        total_frames: int,
        color1_start: str = "#1a1a2e",
        color1_end: str = "#2e1a2e",
        color2_start: str = "#0f0f1a",
        color2_end: str = "#1a0f1a",
        cycle_speed: float = 1.0
) -> Image.Image:
    """Create gradient that shifts colors over time."""
    def hex_to_rgb(h):
        h = h.lstrip('#')
        return [int(h[i:i + 2], 16) for i in (0, 2, 4)]

    def lerp_color(c1, c2, t):
        return [int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)]

    cycle = (frame / max(1, total_frames)) * cycle_speed * math.pi * 2
    t = (math.sin(cycle) + 1) / 2

    c1_start = hex_to_rgb(color1_start)
    c1_end = hex_to_rgb(color1_end)
    c2_start = hex_to_rgb(color2_start)
    c2_end = hex_to_rgb(color2_end)

    top = lerp_color(c1_start, c1_end, t)
    bottom = lerp_color(c2_start, c2_end, t)

    try:
        import numpy as np
        gradient = np.zeros((height, width, 3), dtype=np.uint8)

        for y in range(height):
            ratio = y / height
            color = [int(top[i] + (bottom[i] - top[i]) * ratio) for i in range(3)]
            gradient[y, :] = color

        return Image.fromarray(gradient, 'RGB')
    except ImportError:
        img = Image.new('RGB', (width, height))
        for y in range(height):
            ratio = y / height
            r = int(top[0] + (bottom[0] - top[0]) * ratio)
            g = int(top[1] + (bottom[1] - top[1]) * ratio)
            b = int(top[2] + (bottom[2] - top[2]) * ratio)
            for x in range(width):
                img.putpixel((x, y), (r, g, b))
        return img


def draw_rounded_rect(
    draw: ImageDraw.Draw,
    xy: Tuple[int, int, int, int],
    radius: int,
    fill: str
) -> None:
    """Draw a rounded rectangle."""
    x1, y1, x2, y2 = xy

    max_radius = min(x2 - x1, y2 - y1) // 2
    radius = min(radius, max_radius)

    if radius <= 0:
        draw.rectangle(xy, fill=fill)
        return

    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)

    draw.ellipse([x1, y1, x1 + radius * 2, y1 + radius * 2], fill=fill)
    draw.ellipse([x2 - radius * 2, y1, x2, y1 + radius * 2], fill=fill)
    draw.ellipse([x1, y2 - radius * 2, x1 + radius * 2, y2], fill=fill)
    draw.ellipse([x2 - radius * 2, y2 - radius * 2, x2, y2], fill=fill)
