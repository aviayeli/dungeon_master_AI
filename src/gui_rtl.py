from __future__ import annotations
from bidi.algorithm import get_display


def rtl(text: str) -> str:
    return get_display(text)
