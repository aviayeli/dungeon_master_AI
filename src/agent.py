from __future__ import annotations
import anthropic
from src.config import ANTHROPIC_API_KEY, MODEL_NAME, MAX_HISTORY_TURNS
from src.gatekeeper import get_gatekeeper
from src.state import GameState
from src.tools import WEB_SEARCH_TOOL, handle_tool_call

SYSTEM_PROMPT = (
    "אתה דאנג'ן מאסטר מנוסה ומרתק המנהל הרפתקת פנטזיה בעברית.\n"
    "כל תגובותיך חייבות להיות בעברית בלבד. אסור לכתוב בשפה אחרת.\n"
    "תפקידך: לספר סיפור עשיר, לנהל קרבות, לייצג דמויות משנה ולהגיב לפעולות השחקן.\n"
    "השתמש בכלי החיפוש כשתצטרך מידע עובדתי על חוקי D&D, יצורים, קסמים או עולם המשחק.\n"
    "שמור על עקביות בעולם המשחק והגב בצורה הגיונית, מרתקת ויצירתית."
)


def _block_to_dict(block) -> dict:
    if block.type == "text":
        return {"type": "text", "text": block.text}
    return {"type": "tool_use", "id": block.id, "name": block.name, "input": block.input}


class DungeonMasterAgent:
    def __init__(self, state: GameState) -> None:
        self._client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self._state = state
        self._gatekeeper = get_gatekeeper()

    def _player_context(self) -> str:
        p = self._state.player
        inventory = ", ".join(p.inventory) if p.inventory else "ריק"
        return (
            f"מצב השחקן הנוכחי:\n"
            f"שם: {p.name} | מקצוע: {p.character_class}\n"
            f"חיים: {p.health}/{p.max_health} | מיקום: {p.location}\n"
            f"ציוד: {inventory} | תור: {self._state.turn_count + 1}"
        )

    def _truncated_history(self) -> list[dict]:
        # Hard limit: send only the last MAX_HISTORY_TURNS user+assistant pairs
        msgs = self._state.history[-(MAX_HISTORY_TURNS * 2):]
        while msgs and msgs[0]["role"] != "user":
            msgs = msgs[1:]
        return msgs

    def _run_inference(self, messages: list[dict]) -> str:
        while True:
            self._gatekeeper.check_budget()
            response = self._client.messages.create(
                model=MODEL_NAME,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=[WEB_SEARCH_TOOL],
                messages=messages,
            )
            self._gatekeeper.record_usage(
                response.usage.input_tokens,
                response.usage.output_tokens,
            )
            if response.stop_reason != "tool_use":
                for block in response.content:
                    if block.type == "text":
                        return block.text
                return ""
            tool_results = [
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": handle_tool_call(block.name, block.input),
                }
                for block in response.content
                if block.type == "tool_use"
            ]
            messages = messages + [
                {"role": "assistant", "content": [_block_to_dict(b) for b in response.content]},
                {"role": "user", "content": tool_results},
            ]

    def send_message(self, user_input: str) -> str:
        context_msg = {"role": "user", "content": self._player_context()}
        context_ack = {"role": "assistant", "content": "מובן. אמשיך את ההרפתקה בהתאם למצב השחקן."}
        messages = [context_msg, context_ack] + self._truncated_history() + [{"role": "user", "content": user_input}]
        reply = self._run_inference(messages)
        self._state.history.append({"role": "user", "content": user_input})
        self._state.history.append({"role": "assistant", "content": reply})
        self._state.turn_count += 1
        return reply
