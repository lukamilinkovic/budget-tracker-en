"""
utils/theme.py
--------------
Responsibility: colors and visual style — light and dark mode.
Single source of truth for all colors.

Accent color: blue (#3B82F6 / #60A5FA) — neutral action color,
distinct from green (income) and red (expense) in both themes.
"""

_active = "light"


def set_theme(name: str):
    global _active
    _active = name


def is_dark() -> bool:
    return _active == "dark"


_LIGHT = {
    "background": (0.97, 0.97, 0.95, 1),
    "card":       (1.00, 1.00, 1.00, 1),
    "income":     (0.18, 0.80, 0.44, 1),   # green
    "expense":    (0.95, 0.30, 0.23, 1),   # red
    "accent":     (0.23, 0.51, 0.96, 1),   # blue  #3B82F6
    "primary":    (0.10, 0.10, 0.10, 1),
    "secondary":  (0.60, 0.60, 0.60, 1),
    "subtle":     (0.93, 0.93, 0.90, 1),
    "field_bg":   (0.93, 0.93, 0.90, 1),
    "field_txt":  (0.10, 0.10, 0.10, 1),
}

_DARK = {
    "background": (0.10, 0.10, 0.12, 1),
    "card":       (0.16, 0.16, 0.20, 1),
    "income":     (0.18, 0.80, 0.44, 1),   # green
    "expense":    (0.95, 0.30, 0.23, 1),   # red
    # lighter blue #60A5FA — pops on dark bg
    "accent":     (0.38, 0.64, 0.98, 1),
    "primary":    (0.92, 0.92, 0.92, 1),
    "secondary":  (0.55, 0.55, 0.60, 1),
    "subtle":     (0.22, 0.22, 0.26, 1),
    "field_bg":   (0.22, 0.22, 0.26, 1),
    "field_txt":  (0.92, 0.92, 0.92, 1),
}

FONT = {"xl": 28, "lg": 22, "md": 16, "sm": 13, "xs": 11}
RADIUS = {"card": 16, "button": 14, "field": 12}


def color(key: str) -> tuple:
    """Return color value for the active theme."""
    return (_DARK if is_dark() else _LIGHT)[key]


class _ColorProxy(dict):
    def __getitem__(self, key):
        return color(key)


COLORS = _ColorProxy()
