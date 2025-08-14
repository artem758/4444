# ui/components/InputBar.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

class InputBar(BoxLayout):
    def __init__(self, send_callback, mic_callback=None, **kwargs):
        super().__init__(orientation="horizontal", spacing=10, padding=10, size_hint_y=None, height=50, **kwargs)
        self.send_callback = send_callback
        self.mic_callback = mic_callback
        self.build_ui()

    def build_ui(self):
        self.input = TextInput(hint_text="Введите запрос...", multiline=False)
        self.add_widget(self.input)

        send_btn = Button(text="📤", on_press=self.send)
        self.add_widget(send_btn)

        if self.mic_callback:
            mic_btn = Button(text="🎙️", on_press=self.mic_callback)
            self.add_widget(mic_btn)

    def send(self, instance):
        text = self.input.text.strip()
        if text:
            self.send_callback(text)
            self.input.text = ""
