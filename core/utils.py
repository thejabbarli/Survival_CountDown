"""Utility functions for color operations."""


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB values to hex color."""
    return f"#{r:02x}{g:02x}{b:02x}"


def hex_to_grayscale(hex_color: str, darken: float = 0.4) -> str:
    """Convert hex color to grayscale."""
    r, g, b = hex_to_rgb(hex_color)
    gray = int(0.299 * r + 0.587 * g + 0.114 * b)
    gray = int(gray * darken)
    return rgb_to_hex(gray, gray, gray)


def get_luminance(hex_color: str) -> float:
    """Calculate luminance of a color (0-1)."""
    r, g, b = hex_to_rgb(hex_color)
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255


def get_contrast_color(hex_color: str) -> str:
    """Return black or white for best contrast."""
    return "black" if get_luminance(hex_color) > 0.5 else "white"
