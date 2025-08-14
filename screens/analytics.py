# screens/analytics.py
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
import os

class AnalyticsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="analytics", **kwargs)
        self.add_widget(Label(text=self.get_stats(), font_size=16))

    def get_stats(self):
        used_memory = os.path.getsize("memory/memory.json") // 1024
        return f"Использовано памяти: {used_memory} KB"
