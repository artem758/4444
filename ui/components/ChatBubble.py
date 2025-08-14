# ui/components/ChatBubble.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty, BooleanProperty

class ChatBubble(BoxLayout):
    text = StringProperty("")
    is_user = BooleanProperty(False)

    def __init__(self, text, is_user=False, **kwargs):
        super().__init__(orientation="horizontal", padding=10, spacing=5, **kwargs)
        self.text = text
        self.is_user = is_user
        self.build_ui()

    def build_ui(self):
        bubble = Label(
            text=self.text,
            size_hint_x=0.8,
            halign="left" if not self.is_user else "right",
            valign="middle",
            color=(1, 1, 1, 1),
            font_size=16
        )
        bubble.text_size = (bubble.width, None)
        self.add_widget(bubble)
        self.size_hint_y = None
        self.height = bubble.texture_size[1] + 20
