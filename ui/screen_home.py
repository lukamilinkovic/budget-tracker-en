"""
ui/screen_home.py
-----------------
Responsibility: home screen — balance overview, transaction list,
search, filtering, add, delete, export, theme toggle.
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color as GColor, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.clock import Clock

from data.storage import Transaction, load, add, delete
from ui.widgets import Card, PrimaryButton, InputField
from utils.theme import color, set_theme, is_dark
from utils.export import export_csv


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._filter = "all"
        self._search = ""
        self._month_offset = 0  # 0 = current month, -1 = last month, etc.
        self._build()

    def on_enter(self):
        self._build()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self):
        self.clear_widgets()
        self._set_background()

        all_transactions = load()
        month_transactions = self._apply_month_filter(all_transactions)
        filtered = self._apply_filter(month_transactions)

        total_income = sum(
            t.amount for t in month_transactions if t.is_income())
        total_expenses = sum(
            t.amount for t in month_transactions if not t.is_income())

        main = BoxLayout(orientation="vertical",
                         padding=[dp(20), dp(50), dp(20), dp(10)], spacing=dp(12))
        main.add_widget(self._header())
        main.add_widget(self._balance_card(total_income, total_expenses))
        main.add_widget(self._action_buttons())
        main.add_widget(self._toolbar())
        main.add_widget(self._search_field())
        main.add_widget(self._transaction_list(
            filtered, len(month_transactions)))
        self.add_widget(main)

    def _set_background(self):
        with self.canvas.before:
            GColor(*color("background"))
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda *_: setattr(self.bg, "pos", self.pos),
                  size=lambda *_: setattr(self.bg, "size", self.size))

    def _current_month_dt(self):
        """Return datetime for the currently viewed month."""
        return datetime.now() + relativedelta(months=self._month_offset)

    # ------------------------------------------------------------------
    # Sections
    # ------------------------------------------------------------------

    def _header(self) -> BoxLayout:
        """Header: My Budget + month nav fully centered, theme toggle overlaid top-right."""
        from kivy.uix.floatlayout import FloatLayout

        outer = FloatLayout(size_hint_y=None, height=dp(80))

        # Centered column spanning full width
        center = BoxLayout(orientation="vertical", spacing=dp(4),
                           size_hint=(1, None), height=dp(80),
                           pos_hint={"x": 0, "y": 0})

        center.add_widget(Label(
            text="My Budget",
            font_size=dp(36), bold=True,
            color=color("primary"), halign="center",
            size_hint_y=None, height=dp(44),
            text_size=(Window.width - dp(40), None)))

        nav = BoxLayout(orientation="horizontal", size_hint_y=None,
                        height=dp(28), spacing=dp(8))

        btn_prev = Button(text="<", font_size=dp(18), bold=True,
                          background_normal="", background_color=(0, 0, 0, 0),
                          color=color("primary"), size_hint_x=None, width=dp(28))
        btn_prev.bind(on_press=lambda _: self._shift_month(-1))

        dt = self._current_month_dt()
        month_label = "This Month" if self._month_offset == 0 else dt.strftime(
            "%B %Y")
        lbl_month = Label(text=month_label, font_size=dp(13), bold=True,
                          color=color("primary"), halign="center",
                          text_size=(Window.width - dp(40), None))

        btn_next = Button(text=">", font_size=dp(18), bold=True,
                          background_normal="", background_color=(0, 0, 0, 0),
                          color=color("primary") if self._month_offset < 0 else color(
                              "secondary"),
                          size_hint_x=None, width=dp(28))
        if self._month_offset < 0:
            btn_next.bind(on_press=lambda _: self._shift_month(1))

        nav.add_widget(btn_prev)
        nav.add_widget(lbl_month)
        nav.add_widget(btn_next)
        center.add_widget(nav)
        outer.add_widget(center)

        # Theme toggle overlaid top-right
        theme_label = "Dark" if not is_dark() else "Light"
        btn_theme = Button(text=theme_label, font_size=dp(11), bold=True,
                           background_normal="", background_color=(0, 0, 0, 0),
                           color=color("secondary"),
                           size_hint=(None, None), width=dp(45), height=dp(30),
                           pos_hint={"right": 1, "top": 1})
        btn_theme.bind(on_press=lambda _: self._toggle_theme())
        outer.add_widget(btn_theme)
        return outer

    def _balance_card(self, income: float, expenses: float) -> Card:
        balance = income - expenses

        PAD_V = dp(18)
        PAD_H = dp(20)
        LBL_H = dp(18)
        BAL_H = dp(44)
        ROW_H = dp(38)
        SPACING = dp(10)
        CARD_H = PAD_V + LBL_H + SPACING + BAL_H + \
            SPACING + dp(1) + SPACING + ROW_H + PAD_V

        card = Card(orientation="vertical", size_hint_y=None, height=CARD_H,
                    padding=[0, PAD_V, 0, PAD_V], spacing=SPACING)

        dt = self._current_month_dt()
        period = "This Month" if self._month_offset == 0 else dt.strftime(
            "%B %Y")
        card.add_widget(Label(
            text=f"Balance — {period}", font_size=dp(12),
            color=color("secondary"), halign="center", valign="middle",
            size_hint_y=None, height=LBL_H,
            text_size=(Window.width - dp(40), None)))

        card.add_widget(Label(
            text=f"EUR {balance:,.2f}", font_size=dp(30), bold=True,
            color=color("primary"), halign="center", valign="middle",
            size_hint_y=None, height=BAL_H,
            text_size=(Window.width - dp(40), None)))

        divider = Widget(size_hint_y=None, height=dp(1))
        with divider.canvas:
            GColor(*color("subtle"))
            from kivy.graphics import Rectangle as Rect
            divider._line = Rect(pos=divider.pos, size=divider.size)
        divider.bind(pos=lambda w, *_: setattr(w._line, "pos", w.pos),
                     size=lambda w, *_: setattr(w._line, "size", w.size))
        card.add_widget(divider)

        row = BoxLayout(orientation="horizontal", size_hint_y=None,
                        height=ROW_H, spacing=dp(0))
        for label, amount in [("Income", income), ("Expenses", expenses)]:
            block = BoxLayout(orientation="vertical", spacing=dp(1))
            block.add_widget(Label(text=label, font_size=dp(10), color=color("secondary"),
                                   halign="center", size_hint_y=None, height=dp(16),
                                   text_size=(Window.width - dp(40), None)))
            block.add_widget(Label(text=f"EUR {amount:,.2f}", font_size=dp(13), bold=True,
                                   color=color("primary"), halign="center",
                                   size_hint_y=None, height=dp(18),
                                   text_size=(Window.width - dp(40), None)))
            row.add_widget(block)
        card.add_widget(row)
        return card

    def _action_buttons(self) -> BoxLayout:
        row = BoxLayout(orientation="horizontal", size_hint_y=None,
                        height=dp(48), spacing=dp(10))
        btn_income = PrimaryButton(text="+ Income", btn_color=color("subtle"),
                                   txt_color=color("primary"))
        btn_income.bind(on_press=lambda _: self.open_add("income"))
        btn_expense = PrimaryButton(text="- Expense", btn_color=color("subtle"),
                                    txt_color=color("primary"))
        btn_expense.bind(on_press=lambda _: self.open_add("expense"))
        btn_charts = PrimaryButton(text="Statistics", btn_color=color("subtle"),
                                   txt_color=color("primary"))

        def go_charts(_):
            charts = self.manager.get_screen("charts")
            charts.set_month(self._month_offset)
            self.manager.current = "charts"
        btn_charts.bind(on_press=go_charts)
        row.add_widget(btn_income)
        row.add_widget(btn_expense)
        row.add_widget(btn_charts)
        return row

    def _toolbar(self) -> BoxLayout:
        """Filter buttons + CSV export."""
        row = BoxLayout(orientation="horizontal", size_hint_y=None,
                        height=dp(50), spacing=dp(8))
        for label, value in [("All", "all"), ("Income", "income"), ("Expenses", "expense")]:
            btn = PrimaryButton(text=label, btn_color=color("subtle"),
                                txt_color=color("primary"))
            btn.bind(on_press=lambda _, v=value: self._set_filter(v))
            row.add_widget(btn)

        btn_csv = PrimaryButton(text="Export CSV", btn_color=color("subtle"),
                                txt_color=color("primary"),
                                size_hint_x=None, width=dp(115))
        btn_csv.bind(on_press=lambda _: self._export())
        row.add_widget(btn_csv)
        return row

    def _search_field(self) -> TextInput:
        field = TextInput(
            hint_text="Search transactions...",
            hint_text_color=color("secondary"),
            text=self._search,
            background_color=color("field_bg"),
            background_normal="",
            foreground_color=color("field_txt"),
            cursor_color=color("field_txt"),
            font_size=dp(14),
            padding=[dp(14), dp(10), dp(14), dp(10)],
            size_hint_y=None,
            height=dp(44),
            multiline=False,
        )
        field.bind(text=self._on_search)
        return field

    def _transaction_list(self, transactions, total: int) -> ScrollView:
        scroll = ScrollView()
        lst = BoxLayout(orientation="vertical", spacing=dp(8),
                        size_hint_y=None, padding=[0, 0, 0, dp(10)])
        lst.bind(minimum_height=lst.setter("height"))

        count_text = f"{len(transactions)} transaction(s)"
        if self._filter != "all" or self._search:
            count_text += f" (of {total})"
        lst.add_widget(Label(text=count_text, font_size=dp(12), color=color("secondary"),
                             halign="left", size_hint_y=None, height=dp(22),
                             text_size=(Window.width - dp(40), None)))

        if not transactions:
            lst.add_widget(Label(
                text="No transactions this month.\nUse + Income or - Expense to add one.",
                font_size=dp(14), color=color("secondary"), halign="center",
                size_hint_y=None, height=dp(80),
                text_size=(Window.width - dp(40), None)))
        else:
            all_t = load()
            for t in reversed(transactions):
                real_idx = all_t.index(t)
                lst.add_widget(self._transaction_row(t, real_idx))
        scroll.add_widget(lst)
        return scroll

    def _transaction_row(self, t: Transaction, idx: int) -> Card:
        row = Card(orientation="horizontal", size_hint_y=None,
                   height=dp(64), padding=[dp(12), dp(8)], spacing=dp(10))

        type_label = Label(
            text="IN" if t.is_income() else "OUT",
            font_size=dp(10), bold=True, color=color("secondary"),
            halign="center", size_hint_x=None, width=dp(30),
            text_size=(dp(30), None))
        row.add_widget(type_label)

        info = BoxLayout(orientation="vertical")
        desc = self._highlight(t.description)
        info.add_widget(Label(text=desc, font_size=dp(14), bold=True,
                              color=color("primary"), halign="left",
                              text_size=(dp(175), None), size_hint_y=None, height=dp(22)))
        info.add_widget(Label(text=t.date, font_size=dp(11), color=color("secondary"),
                              halign="left", text_size=(dp(175), None),
                              size_hint_y=None, height=dp(18)))
        row.add_widget(info)

        sign = "+" if t.is_income() else "-"
        row.add_widget(Label(text=f"{sign} EUR {t.amount:.2f}", font_size=dp(12),
                             bold=True, color=color("primary"), halign="right",
                             text_size=(dp(80), None), size_hint_x=None, width=dp(80)))

        btn_del = Button(text="X", font_size=dp(16), color=(0.75, 0.75, 0.75, 1),
                         background_normal="", background_color=(0, 0, 0, 0),
                         size_hint_x=None, width=dp(30), bold=True)
        btn_del.bind(on_press=lambda _, i=idx: self._confirm_delete(i))
        row.add_widget(btn_del)
        return row

    def _highlight(self, text: str) -> str:
        if not self._search:
            return text
        i = text.lower().find(self._search.lower())
        if i == -1:
            return text
        match = text[i:i + len(self._search)]
        return text[:i] + "*" + match + "*" + text[i + len(self._search):]

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _shift_month(self, delta: int):
        self._month_offset += delta
        self._build()

    def _apply_month_filter(self, transactions):
        dt = self._current_month_dt()
        year, month = dt.year, dt.month
        return [t for t in transactions
                if self._parse_date(t.date, year, month)]

    def _parse_date(self, date_str: str, year: int, month: int) -> bool:
        """Check if transaction date matches the given year/month."""
        try:
            # Format: "DD. MM. YYYY, HH:MM"
            parts = date_str.split(",")[0].strip().split(".")
            t_day = int(parts[0].strip())
            t_month = int(parts[1].strip())
            t_year = int(parts[2].strip())
            return t_year == year and t_month == month
        except Exception:
            return True  # If date can't be parsed, include it

    def _set_filter(self, value: str):
        self._filter = value
        self._build()

    def _on_search(self, widget, text: str):
        self._search = text
        self._build()

    def _apply_filter(self, transactions):
        result = transactions
        if self._filter != "all":
            result = [t for t in result if t.type == self._filter]
        if self._search:
            q = self._search.lower()
            result = [t for t in result
                      if q in t.description.lower() or q in t.date.lower()]
        return result

    def _toggle_theme(self):
        set_theme("light" if is_dark() else "dark")
        self._build()

    def _export(self):
        transactions = load()
        if not transactions:
            self._show_message("No transactions to export.")
            return
        path = export_csv(transactions)
        self._show_message(f"Exported!\n{path}")

    def _show_message(self, text: str):
        content = BoxLayout(orientation="vertical",
                            padding=dp(24), spacing=dp(16))
        content.add_widget(Label(text=text, font_size=dp(14), color=color("primary"),
                                 halign="center", text_size=(dp(260), None),
                                 size_hint_y=None, height=dp(70)))
        btn_ok = PrimaryButton(text="OK", btn_color=color("primary"),
                               txt_color=(1, 1, 1, 1))
        btn_ok.bind(on_press=lambda _: popup.dismiss())
        content.add_widget(btn_ok)
        popup = Popup(title="", content=content, size_hint=(0.85, None),
                      height=dp(180), separator_height=0,
                      background="atlas://data/images/defaulttheme/button",
                      background_color=(1, 1, 1, 1), title_size=0)
        popup.open()

    def open_add(self, type: str):
        from kivy.uix.floatlayout import FloatLayout
        from kivy.graphics import Color as GCol, RoundedRectangle as RR

        title_text = "Add Income" if type == "income" else "Add Expense"
        accent = color("income") if type == "income" else color("expense")

        # Outer overlay — semi-transparent dark background
        overlay = FloatLayout()
        with overlay.canvas.before:
            GCol(0, 0, 0, 0.45)
            overlay._bg = Rectangle(pos=overlay.pos, size=overlay.size)
        overlay.bind(pos=lambda w, *_: setattr(w._bg, 'pos', w.pos),
                     size=lambda w, *_: setattr(w._bg, 'size', w.size))

        # Card container — centered
        card_width = dp(300)
        card_height = dp(300)
        card = BoxLayout(orientation="vertical",
                         size_hint=(None, None),
                         width=card_width, height=card_height,
                         padding=[dp(24), dp(24), dp(24), dp(20)],
                         spacing=dp(14),
                         pos_hint={"center_x": 0.5, "center_y": 0.5})
        with card.canvas.before:
            GCol(*color("card"))
            card._rect = RR(pos=card.pos, size=card.size, radius=[dp(20)])
        card.bind(pos=lambda w, *_: setattr(w._rect, 'pos', w.pos),
                  size=lambda w, *_: setattr(w._rect, 'size', w.size))

        # Title
        lbl_title = Label(text=title_text, font_size=dp(20), bold=True,
                          color=color("primary"), halign="center",
                          size_hint_y=None, height=dp(32),
                          text_size=(card_width - dp(48), None))

        field_amount = InputField(hint_text="Amount (EUR)", input_filter="float",
                                  hint_text_color=color("secondary"))
        field_desc = InputField(hint_text="Description",
                                hint_text_color=color("secondary"))
        field_amount.next_field = field_desc

        def save(_):
            try:
                amount = float(field_amount.text.replace(",", "."))
                if amount <= 0:
                    raise ValueError
            except ValueError:
                field_amount.hint_text = "! Please enter a valid amount"
                return
            add(Transaction.create(type, amount,
                field_desc.text.strip(), self._current_month_dt()))
            popup.dismiss()
            self._build()

        field_amount.on_enter_callback = save
        field_desc.on_enter_callback = save

        # Buttons row
        btn_row = BoxLayout(orientation="horizontal", size_hint_y=None,
                            height=dp(50), spacing=dp(10))
        btn_cancel = PrimaryButton(text="Cancel", btn_color=color("subtle"),
                                   txt_color=color("secondary"))
        btn_save = PrimaryButton(text="Save", btn_color=accent,
                                 txt_color=(1, 1, 1, 1))
        btn_cancel.bind(on_press=lambda _: popup.dismiss())
        btn_save.bind(on_press=save)
        btn_row.add_widget(btn_cancel)
        btn_row.add_widget(btn_save)

        card.add_widget(lbl_title)
        card.add_widget(field_amount)
        card.add_widget(field_desc)
        card.add_widget(btn_row)
        overlay.add_widget(card)

        popup = Popup(title="", content=overlay, size_hint=(1, 1),
                      separator_height=0, background_color=(0, 0, 0, 0),
                      background="", title_size=0)
        popup.open()
        Clock.schedule_once(lambda _: setattr(
            field_amount, "focus", True), 0.15)

    def _confirm_delete(self, idx: int):
        t = load()[idx]
        content = BoxLayout(orientation="vertical",
                            padding=dp(22), spacing=dp(14))
        content.add_widget(Label(text=f'Delete "{t.description}"?', font_size=dp(16),
                                 bold=True, color=color("primary"),
                                 size_hint_y=None, height=dp(40)))
        sign = "+" if t.is_income() else "-"
        content.add_widget(Label(text=f"{sign} EUR {t.amount:.2f}  |  {t.date}",
                                 font_size=dp(13), color=color("secondary"),
                                 size_hint_y=None, height=dp(28)))
        buttons = BoxLayout(orientation="horizontal", spacing=dp(10),
                            size_hint_y=None, height=dp(50))
        btn_cancel = PrimaryButton(text="Cancel", btn_color=color("subtle"),
                                   txt_color=color("primary"))
        btn_delete = PrimaryButton(text="Delete", btn_color=color("expense"),
                                   txt_color=(1, 1, 1, 1))

        def confirm(_):
            delete(idx)
            popup.dismiss()
            self._build()

        btn_cancel.bind(on_press=lambda _: popup.dismiss())
        btn_delete.bind(on_press=confirm)
        buttons.add_widget(btn_cancel)
        buttons.add_widget(btn_delete)
        content.add_widget(buttons)

        popup = Popup(title="", content=content, size_hint=(0.85, None),
                      height=dp(230), separator_height=0,
                      background="atlas://data/images/defaulttheme/button",
                      background_color=(1, 1, 1, 1), title_size=0)
        popup.open()
