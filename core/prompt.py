from typing import Dict


def build_prompt(user_text: str, ctx: Dict[str, str] | None = None) -> str:
    ctx = ctx or {}
    prefix = ctx.get("prefix", "User:")
    return f"{prefix} {user_text.strip()}"
