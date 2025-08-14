# ui/components/HeaderBar.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class HeaderBar(BoxLayout):
    def __init__(self, settings_callback=None, **kwargs):
        super().__init__(orientation="horizontal", padding=10, spacing=10, size_hint_y=None, height=50, **kwargs)
        self.settings_callback = settings_callback
        self.build_ui()

    def build_ui(self):
        logo = Label(text="🧠 LV-REX", font_size=20, bold=True)
        self.add_widget(logo)

        status = Label(text="✅ Доступ", font_size=14)
        self.add_widget(status)

        if self.settings_callback:
            settings_btn = Button(text="⚙️", on_press=self.settings_callback)
            self.add_widget(settings_btn)
