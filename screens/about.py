# screens/about.py
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label

class AboutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="about", **kwargs)
        self.add_widget(Label(
            text="LV-REX\nЦифровой мозг\nРазработано Артёмом",
            font_size=18,
            halign="center"
        ))
