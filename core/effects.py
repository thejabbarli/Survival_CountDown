"""Visual effects - gradients, shadows, vignette, flash."""

from PIL import Image, ImageDraw, ImageFilter
from typing import Tuple, Optional


def create_gradient(
        width: int,
        height: int,
        color_top: str = "#1a1a2e",
        color_bottom: str = "#0f0f1a"
) -> Image.Image:
    """Create vertical gradient background."""
    img = Image.new('RGB', (width, height))

    # Parse colors
    def hex_to_rgb(h):
        h = h.lstrip('#')
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

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


def create_gradient_fast(
        width: int,
        height: int,
        color_top: str = "#1a1a2e",
        color_bottom: str = "#0f0f1a"
) -> Image.Image:
    """Faster gradient using numpy."""
    try:
        import numpy as np

        def hex_to_rgb(h):
            h = h.lstrip('#')
            return [int(h[i:i + 2], 16) for i in (0, 2, 4)]

        top = np.array(hex_to_rgb(color_top))
        bottom = np.array(hex_to_rgb(color_bottom))

        gradient = np.zeros((height, width, 3), dtype=np.uint8)

        for y in range(height):
            ratio = y / height
            color = top + (bottom - top) * ratio
            gradient[y, :] = color.astype(np.uint8)

        return Image.fromarray(gradient, 'RGB')
    except ImportError:
        return create_gradient(width, height, color_top, color_bottom)


def add_vignette(img: Image.Image, strength: float = 0.4) -> Image.Image:
    """Add dark vignette around edges."""
    import numpy as np

    arr = np.array(img, dtype=np.float32)
    h, w = arr.shape[:2]

    # Create radial gradient
    y, x = np.ogrid[:h, :w]
    cx, cy = w / 2, h / 2

    # Normalized distance from center
    dist = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    max_dist = np.sqrt(cx ** 2 + cy ** 2)
    dist = dist / max_dist

    # Vignette factor (1 at center, darker at edges)
    vignette = 1 - (dist ** 2) * strength
    vignette = np.clip(vignette, 0, 1)

    # Apply
    arr = arr * vignette[:, :, np.newaxis]
    arr = np.clip(arr, 0, 255).astype(np.uint8)

    return Image.fromarray(arr)


def draw_rounded_rect(
        draw: ImageDraw.Draw,
        xy: Tuple[int, int, int, int],
        radius: int,
        fill: str
) -> None:
    """Draw a rounded rectangle."""
    x1, y1, x2, y2 = xy

    # Clamp radius
    max_radius = min(x2 - x1, y2 - y1) // 2
    radius = min(radius, max_radius)

    # Draw main rectangles
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)

    # Draw corners
    draw.ellipse([x1, y1, x1 + radius * 2, y1 + radius * 2], fill=fill)
    draw.ellipse([x2 - radius * 2, y1, x2, y1 + radius * 2], fill=fill)
    draw.ellipse([x1, y2 - radius * 2, x1 + radius * 2, y2], fill=fill)
    draw.ellipse([x2 - radius * 2, y2 - radius * 2, x2, y2], fill=fill)


def create_shadow(size: int, radius: int = 8, blur: int = 10, opacity: int = 100) -> Image.Image:
    """Create a drop shadow image."""
    # Make shadow slightly larger for blur
    shadow_size = size + blur * 2
    shadow = Image.new('RGBA', (shadow_size, shadow_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)

    # Draw rounded black rect
    margin = blur
    draw_rounded_rect(
        draw,
        (margin, margin, margin + size, margin + size),
        radius,
        (0, 0, 0, opacity)
    )

    # Blur it
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))

    return shadow


def flash_overlay(img: Image.Image, intensity: float = 0.3, color: str = "#FFFFFF") -> Image.Image:
    """Add flash overlay (for beat hits)."""
    if intensity <= 0:
        return img

    def hex_to_rgb(h):
        h = h.lstrip('#')
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    flash_color = hex_to_rgb(color)
    flash = Image.new('RGB', img.size, flash_color)

    return Image.blend(img, flash, intensity)
