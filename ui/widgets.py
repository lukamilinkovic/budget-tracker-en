"""
ui/widgets.py
-------------
Responsibility: reusable UI components.
No business logic — visual components only.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.animation import Animation

from utils.theme import color, RADIUS


def _darken(c, amount=0.10):
    """Return a slightly darkened version of a color tuple."""
    r, g, b, a = c
    return (max(0, r - amount), max(0, g - amount), max(0, b - amount), a)


class Card(BoxLayout):
    """White card with rounded corners."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self._color = Color(*color("card"))
            self.rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(RADIUS["card"])]
            )
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *_):
        self.rect.pos = self.pos
        self.rect.size = self.size


class PrimaryButton(Button):
    """Primary action button with rounded corners, hover darkening and bubble scale."""

    SCALE_UP = 1.08    # 8% bigger on hover
    ANIM_DUR = 0.12    # seconds

    def __init__(self, btn_color=None, txt_color=None, **kwargs):
        super().__init__(**kwargs)
        self._base_color = btn_color or color("subtle")
        self._hovered = False
        self._base_height = dp(50)
        self._base_font = dp(15)

        self.background_color = (0, 0, 0, 0)
        self.background_normal = ""
        self.color = txt_color if txt_color is not None else color("primary")
        self.bold = True
        self.font_size = self._base_font
        self.size_hint_y = None
        self.height = self._base_height

        with self.canvas.before:
            self._bg_color = Color(*self._base_color)
            self.rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(RADIUS["button"])]
            )
        self.bind(pos=self._sync, size=self._sync)
        Window.bind(mouse_pos=self._on_mouse_pos)

    def _sync(self, *_):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def _on_mouse_pos(self, window, pos):
        if not self.get_root_window():
            return
        local = self.to_widget(*pos)
        inside = self.collide_point(*local)

        if inside and not self._hovered:
            self._hovered = True
            # Darken background
            self._bg_color.rgba = _darken(self._base_color)
            # Animate scale up
            Animation.cancel_all(self)
            anim = Animation(
                height=self._base_height * self.SCALE_UP,
                font_size=self._base_font * self.SCALE_UP,
                d=self.ANIM_DUR,
                t="out_quad"
            )
            anim.start(self)

        elif not inside and self._hovered:
            self._hovered = False
            # Restore background
            self._bg_color.rgba = self._base_color
            # Animate scale back down
            Animation.cancel_all(self)
            anim = Animation(
                height=self._base_height,
                font_size=self._base_font,
                d=self.ANIM_DUR,
                t="out_quad"
            )
            anim.start(self)

    def on_parent(self, widget, parent):
        if parent is None:
            Window.unbind(mouse_pos=self._on_mouse_pos)
        else:
            Window.bind(mouse_pos=self._on_mouse_pos)


class InputField(TextInput):
    """Styled TextInput with Tab -> next field and Enter -> callback support."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = color("field_bg")
        self.background_normal = ""
        self.foreground_color = color("field_txt")
        self.cursor_color = color("field_txt")
        self.selection_color = (*color("income")[:3], 0.35)
        self.font_size = dp(16)
        self.padding = [dp(16), dp(14), dp(16), dp(14)]
        self.size_hint_y = None
        self.height = dp(52)
        self.multiline = False
        self.on_enter_callback = None
        self.next_field = None

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[1] == "enter" and self.on_enter_callback:
            self.on_enter_callback(self)
            return True
        if keycode[1] == "tab" and self.next_field:
            self.next_field.focus = True
            return True
        return super().keyboard_on_key_down(window, keycode, text, modifiers)
