"""
ui/screen_charts.py
-------------------
Responsibility: charts screen — donut chart and bar chart, filtered by month.
Black & green terminal aesthetic. Light/dark aware.

Fixes:
  • Header pinned to very top via FloatLayout
  • Back button: proper square [✕] using a wrapper widget (avoids Kivy
    canvas.before pos-init bug with Button subclasses)
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color as GColor, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.core.window import Window

from data.storage import load
from ui.widgets import Card
from utils.theme import color, is_dark
from utils.charts import donut_chart, bar_chart


# ── Helpers ─────────────────────────────────────────────────────────────────

def _green():
    return color("income")


def _red():
    return color("expense")


def _pale():
    # bright text colour regardless of mode
    return color("primary")


def _moss():
    return color("secondary")


def _black():
    return color("background")


# ── Square [✕] back button ──────────────────────────────────────────────────
# We use a FloatLayout wrapper so the border/fill rectangles are drawn AFTER
# Kivy has positioned the widget — this avoids the (0,0) init-position bug
# that appears when subclassing Button and drawing in __init__.

def _make_close_btn(on_press_cb):
    SIZE = dp(34)

    wrapper = FloatLayout(size_hint=(None, None), width=SIZE, height=SIZE)

    # Bordered square drawn on the wrapper canvas
    with wrapper.canvas:
        # outer border colour
        border_col = GColor(0, 0, 0, 0)   # placeholder — updated in _refresh
        border_rect = RoundedRectangle(
            pos=(0, 0), size=(SIZE, SIZE), radius=[dp(6)])
        # inner fill
        fill_col = GColor(0, 0, 0, 0)
        PAD = dp(2)
        fill_rect = RoundedRectangle(
            pos=(PAD, PAD), size=(SIZE - PAD * 2, SIZE - PAD * 2), radius=[dp(5)]
        )

    def _refresh(*_):
        m = _moss()
        b = _black()
        border_col.rgba = m
        border_rect.pos = wrapper.pos
        border_rect.size = wrapper.size
        fill_col.rgba = b
        fill_rect.pos = (wrapper.x + PAD, wrapper.y + PAD)
        fill_rect.size = (wrapper.width - PAD * 2, wrapper.height - PAD * 2)

    wrapper.bind(pos=_refresh, size=_refresh)

    # Transparent button layered on top (handles touch)
    btn = Button(
        text="✕",
        font_size=dp(15),
        bold=True,
        background_normal="",
        background_color=(0, 0, 0, 0),
        color=_pale(),
        size_hint=(1, 1),
    )
    btn.bind(on_press=on_press_cb)
    wrapper.add_widget(btn)

    return wrapper


# ── Stat pill ────────────────────────────────────────────────────────────────

class _StatPill(BoxLayout):
    """Slim card with coloured left accent stripe."""

    def __init__(self, label: str, value: str, accent: tuple, **kwargs):
        super().__init__(
            orientation="vertical",
            padding=[dp(14), dp(10), dp(14), dp(10)],
            spacing=dp(2),
            **kwargs,
        )
        with self.canvas.before:
            self._bg_col = GColor(*color("card"))
            self._bg = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(12)])
            self._stripe_col = GColor(*accent)
            self._stripe = RoundedRectangle(pos=self.pos,
                                            size=(dp(3), self.height),
                                            radius=[dp(2)])
        self.bind(pos=self._sync, size=self._sync)

        self.add_widget(Label(
            text=label.upper(), font_size=dp(8.5), bold=True,
            color=_moss(), halign="center",
            text_size=(dp(90), None), size_hint_y=None, height=dp(14),
        ))
        self.add_widget(Label(
            text=value, font_size=dp(13), bold=True,
            color=accent, halign="center",
            text_size=(dp(90), None), size_hint_y=None, height=dp(20),
        ))

    def _sync(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._stripe.pos = self.pos
        self._stripe.size = (dp(3), self.height)


# ── Screen ───────────────────────────────────────────────────────────────────

class ChartsScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._month_offset = 0

    def set_month(self, offset: int):
        self._month_offset = offset

    def on_enter(self):
        self._build()

    def _current_month_dt(self):
        return datetime.now() + relativedelta(months=self._month_offset)

    def _filter_by_month(self, transactions):
        dt = self._current_month_dt()
        year, month = dt.year, dt.month
        result = []
        for t in transactions:
            try:
                parts = t.date.split(",")[0].strip().split(".")
                t_month = int(parts[1].strip())
                t_year = int(parts[2].strip())
                if t_year == year and t_month == month:
                    result.append(t)
            except Exception:
                result.append(t)
        return result

    def _build(self):
        self.clear_widgets()

        # Full-screen background
        with self.canvas.before:
            GColor(*_black())
            bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda *_: setattr(bg, "pos", self.pos),
                  size=lambda *_: setattr(bg, "size", self.size))

        transactions = self._filter_by_month(load())
        income = sum(t.amount for t in transactions if t.is_income())
        expenses = sum(t.amount for t in transactions if not t.is_income())
        balance = income - expenses

        dt = self._current_month_dt()
        period = "This Month" if self._month_offset == 0 else dt.strftime(
            "%B %Y")

        HEADER_H = dp(54)

        # ── Root FloatLayout ─────────────────────────────────────────────────
        root = FloatLayout()

        # ── Scrollable body (sits below header) ──────────────────────────────
        scroll = ScrollView(
            size_hint=(1, None),
            size=(Window.width, Window.height - HEADER_H),
            pos=(0, 0),
        )

        body = BoxLayout(
            orientation="vertical",
            padding=[dp(16), dp(10), dp(16), dp(16)],
            spacing=dp(12),
            size_hint_y=None,
        )
        body.bind(minimum_height=body.setter("height"))

        # Thin separator
        sep = Widget(size_hint_y=None, height=dp(1))
        with sep.canvas:
            GColor(*_moss())
            sep._ln = Rectangle(pos=sep.pos, size=sep.size)
        sep.bind(pos=lambda w, *_: setattr(w._ln, "pos", w.pos),
                 size=lambda w, *_: setattr(w._ln, "size", w.size))
        body.add_widget(sep)

        # Stat pills
        pills_row = BoxLayout(orientation="horizontal",
                              size_hint_y=None, height=dp(68), spacing=dp(8))
        bal_accent = _green() if balance >= 0 else _red()
        for lbl, val, acc in [
            ("Income",   f"€{income:,.2f}",  _green()),
            ("Expenses", f"€{expenses:,.2f}", _red()),
            ("Balance",  f"€{balance:,.2f}",  bal_accent),
        ]:
            pills_row.add_widget(_StatPill(label=lbl, value=val, accent=acc))
        body.add_widget(pills_row)

        # Donut chart
        donut_card = Card(orientation="vertical",
                          size_hint_y=None, height=dp(248), padding=dp(6))
        donut_card.add_widget(donut_chart(income, expenses))
        body.add_widget(donut_card)

        # Bar chart
        bar_card = Card(orientation="vertical",
                        size_hint_y=None, height=dp(218), padding=dp(6))
        bar_card.add_widget(bar_chart(transactions))
        body.add_widget(bar_card)

        # Footer
        bal_sign = "+" if balance >= 0 else ""
        body.add_widget(Label(
            text=f"{len(transactions)} transaction(s)  ·  net {bal_sign}€{balance:,.2f}",
            font_size=dp(10.5), color=bal_accent,
            halign="center", size_hint_y=None, height=dp(22),
            text_size=(Window.width - dp(36), None),
        ))

        scroll.add_widget(body)
        root.add_widget(scroll)

        # ── Header — pinned to top ───────────────────────────────────────────
        # Background strip
        hdr_bg = Widget(size_hint=(1, None), height=HEADER_H,
                        pos_hint={"x": 0, "top": 1})
        with hdr_bg.canvas:
            GColor(*_black())
            hdr_bg._r = Rectangle(pos=hdr_bg.pos, size=hdr_bg.size)
        hdr_bg.bind(pos=lambda w, *_: setattr(w._r, "pos", w.pos),
                    size=lambda w, *_: setattr(w._r, "size", w.size))
        root.add_widget(hdr_bg)

        # Header row
        hdr = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None), height=HEADER_H,
            pos_hint={"x": 0, "top": 1},
            padding=[dp(12), dp(10), dp(12), dp(10)],
            spacing=dp(10),
        )

        close_btn = _make_close_btn(
            lambda _: setattr(self.manager, "current", "home")
        )
        hdr.add_widget(close_btn)

        hdr.add_widget(Label(
            text=f"STATISTICS  ·  {period.upper()}",
            font_size=dp(13), bold=True,
            color=_pale(),
            halign="center",
            text_size=(Window.width - dp(80), None),
        ))

        root.add_widget(hdr)
        self.add_widget(root)
