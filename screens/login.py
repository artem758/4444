# screens/login.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label

class LoginScreen(Screen):
    def __init__(self, payment, manager_callback, **kwargs):
        super().__init__(name="login", **kwargs)
        self.payment = payment
        self.manager_callback = manager_callback
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        layout.add_widget(Label(text="Введите Family Pass", font_size=20))
        self.code_input = TextInput(multiline=False, password=True)
        layout.add_widget(self.code_input)

        btn = Button(text="Активировать", on_press=self.activate)
        layout.add_widget(btn)

        trial_btn = Button(text="Начать пробный режим", on_press=self.trial)
        layout.add_widget(trial_btn)

        self.add_widget(layout)

    def activate(self, instance):
        code = self.code_input.text.strip()
        if self.payment.activate_family_pass(code):
            self.manager_callback("main")

    def trial(self, instance):
        if self.payment.start_trial():
            self.manager_callback("main")
