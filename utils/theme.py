"""
utils/theme.py
--------------
Responsibility: colors and visual style — light and dark mode.
Both modes use the black-and-dark-green palette.

Dark:  near-black bg  + forest green accents
Light: dark-green bg  + brighter green accents on off-white cards
"""

_active = "dark"


def set_theme(name: str):
    global _active
    _active = name


def is_dark() -> bool:
    return _active == "dark"


_DARK = {
    "background": (0.031, 0.039, 0.031, 1),   # #080A08  near-black
    "card":       (0.055, 0.067, 0.055, 1),   # #0E110E  dark card
    "income":     (0.114, 0.725, 0.329, 1),   # #1DB954  forest green
    "expense":    (0.800, 0.200, 0.200, 1),   # #CC3333  muted red
    "accent":     (0.114, 0.725, 0.329, 1),   # forest green
    "primary":    (0.784, 0.941, 0.784, 1),   # #C8F0C8  pale green-white
    "secondary":  (0.227, 0.353, 0.227, 1),   # #3A5A3A  dark moss
    "subtle":     (0.082, 0.118, 0.082, 1),   # #151E15  very dark green-grey
    "field_bg":   (0.082, 0.118, 0.082, 1),
    "field_txt":  (0.784, 0.941, 0.784, 1),
}

_LIGHT = {
    "background": (0.937, 0.961, 0.937, 1),   # #EFF5EF  pale green-white
    "card":       (1.000, 1.000, 1.000, 1),   # pure white cards
    # #118838  darker green (readable on white)
    "income":     (0.067, 0.549, 0.224, 1),
    "expense":    (0.720, 0.133, 0.133, 1),   # #B82222  darker red
    "accent":     (0.067, 0.549, 0.224, 1),   # same dark green
    "primary":    (0.039, 0.118, 0.039, 1),   # #0A1E0A  near-black green text
    "secondary":  (0.290, 0.451, 0.290, 1),   # #4A734A  mid-green
    "subtle":     (0.859, 0.918, 0.859, 1),   # #DBEBDB  light green-grey
    "field_bg":   (0.878, 0.929, 0.878, 1),   # #E0EDE0
    "field_txt":  (0.039, 0.118, 0.039, 1),   # same as primary
}

FONT = {"xl": 28, "lg": 22, "md": 16, "sm": 13, "xs": 11}
RADIUS = {"card": 16, "button": 14, "field": 12}


def color(key: str) -> tuple:
    return (_DARK if is_dark() else _LIGHT)[key]


class _ColorProxy(dict):
    def __getitem__(self, key):
        return color(key)


COLORS = _ColorProxy()
