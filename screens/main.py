from core.ai import MistralEngine
from interface.prompt import get_user_prompt
from datetime import datetime
import os

log_path = "logs/inference.log"
os.makedirs("logs", exist_ok=True)

def log_interaction(prompt: str, response: str):
    with open(log_path, "a", encoding="utf-8") as log:
        now = datetime.now()
        log.write(f"[{now}]\nPrompt: {prompt}\nResponse: {response}\n{'-'*40}\n")

def main():
    ai = MistralEngine()
    while True:
        prompt = get_user_prompt()
        if prompt.lower() in ["exit", "quit"]: break
        response = ai.generate(prompt)
        print(f"\n🧠 Ответ от Mistral:\n{response}\n")
        log_interaction(prompt, response)

if __name__ == "__main__":
    main()
    