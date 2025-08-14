# screens/settings.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="settings", **kwargs)
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        layout.add_widget(Label(text="Настройки", font_size=20))

        theme_btn = Button(text="Сменить тему")
        layout.add_widget(theme_btn)

        reset_btn = Button(text="Сбросить память")
        layout.add_widget(reset_btn)

        self.add_widget(layout)
