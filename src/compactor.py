from __future__ import annotations
import anthropic
from src.config import ANTHROPIC_API_KEY, MODEL_NAME
from src.gatekeeper import get_gatekeeper

_FRESH_PROMPT = "סכם בקצרה (2-3 משפטים בעברית) את האירועים המרכזיים בהרפתקה:\n\n{turns}"
_UPDATE_PROMPT = "סיכום קודם:\n{prior}\n\nאירועים חדשים:\n{turns}\n\nעדכן את הסיכום ל-2-3 משפטים בעברית:"


def _turns_to_text(messages: list[dict]) -> str:
    parts = []
    for msg in messages:
        role = "שחקן" if msg["role"] == "user" else "DM"
        content = msg["content"] if isinstance(msg["content"], str) else str(msg["content"])
        parts.append(f"{role}: {content[:200]}")
    return "\n".join(parts)


class Compactor:
    def __init__(self) -> None:
        self._client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self._gatekeeper = get_gatekeeper()

    def summarize(self, messages: list[dict], prior_summary: str = "") -> str:
        if not messages:
            return prior_summary
        turns = _turns_to_text(messages)
        prompt = _UPDATE_PROMPT.format(prior=prior_summary, turns=turns) if prior_summary else _FRESH_PROMPT.format(turns=turns)
        self._gatekeeper.check_budget()
        response = self._client.messages.create(
            model=MODEL_NAME,
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}],
        )
        self._gatekeeper.record_usage(response.usage.input_tokens, response.usage.output_tokens)
        return response.content[0].text.strip() if response.content else prior_summary
