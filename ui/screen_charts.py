"""
ui/screen_charts.py
-------------------
Responsibility: charts screen — donut chart and bar chart, filtered by month.
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color as GColor, Rectangle
from kivy.metrics import dp

from data.storage import load
from ui.widgets import Card
from utils.theme import color, COLORS
from utils.charts import donut_chart, bar_chart


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

        with self.canvas.before:
            GColor(*color("background"))
            bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda *_: setattr(bg, "pos", self.pos),
                  size=lambda *_: setattr(bg, "size", self.size))

        all_transactions = load()
        transactions = self._filter_by_month(all_transactions)

        income = sum(t.amount for t in transactions if t.is_income())
        expenses = sum(t.amount for t in transactions if not t.is_income())

        dt = self._current_month_dt()
        period = "This Month" if self._month_offset == 0 else dt.strftime(
            "%B %Y")

        main = BoxLayout(orientation="vertical",
                         padding=[dp(20), dp(10), dp(20), dp(10)], spacing=dp(14))

        # Header
        header = BoxLayout(orientation="horizontal",
                           size_hint_y=None, height=dp(44))
        btn_back = Button(text="< Back", font_size=dp(15), bold=True,
                          background_normal="", background_color=(0, 0, 0, 0),
                          color=color("primary"), size_hint_x=None, width=dp(80))
        btn_back.bind(on_press=lambda _: setattr(
            self.manager, "current", "home"))
        header.add_widget(btn_back)
        header.add_widget(Label(text=f"Statistics — {period}", font_size=dp(18),
                                bold=True, color=color("primary"), halign="center",
                                text_size=(dp(220), None)))
        main.add_widget(header)

        # Summary cards
        summary = BoxLayout(orientation="horizontal", size_hint_y=None,
                            height=dp(72), spacing=dp(10))
        balance = income - expenses
        for label, value, c in [
            ("Income",   income,   color("income")),
            ("Expenses", expenses, color("expense")),
            ("Balance",  balance,  color("income")
             if balance >= 0 else color("expense")),
        ]:
            card = Card(orientation="vertical", padding=dp(10), spacing=dp(2))
            card.add_widget(Label(text=label, font_size=dp(10), color=color("secondary"),
                                  halign="center", text_size=(dp(90), None)))
            card.add_widget(Label(text=f"EUR {value:.2f}", font_size=dp(13), bold=True,
                                  color=c, halign="center", text_size=(dp(90), None)))
            summary.add_widget(card)
        main.add_widget(summary)

        # Donut chart
        donut_card = Card(orientation="vertical", size_hint_y=None,
                          height=dp(240), padding=dp(8))
        donut_card.add_widget(donut_chart(income, expenses))
        main.add_widget(donut_card)

        # Bar chart
        bar_card = Card(orientation="vertical", size_hint_y=None,
                        height=dp(210), padding=dp(8))
        bar_card.add_widget(bar_chart(transactions))
        main.add_widget(bar_card)

        # Transaction count
        main.add_widget(Label(
            text=f"{len(transactions)} transaction(s) in {period}",
            font_size=dp(12), color=color("secondary"),
            halign="center", size_hint_y=None, height=dp(24),
            text_size=(dp(300), None)))

        self.add_widget(main)
