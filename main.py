"""
main.py
-------
Entry point. Initializes the window and screen manager only.
No business logic here.
"""

from ui.screen_charts import ChartsScreen
from ui.screen_home import HomeScreen
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.app import App
import sys
import os

# Ensure imports and file paths always resolve relative to this file,
# regardless of where Python is launched from.
_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _root)
os.chdir(_root)


Window.size = (390, 844)


class BudgetApp(App):
    def build(self):
        self.title = "Budget Tracker"
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(ChartsScreen(name="charts"))
        return sm


if __name__ == "__main__":
    BudgetApp().run()
