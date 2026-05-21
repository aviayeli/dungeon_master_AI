from __future__ import annotations
import tkinter as tk
from bidi.algorithm import get_display


def rtl(text: str) -> str:
    return get_display(text)


def get_rtl_text(entry: tk.Entry) -> str:
    return getattr(entry, "_rtl_logical", entry.get())


def set_rtl_text(entry: tk.Entry, text: str) -> None:
    entry._rtl_logical = text
    entry.delete(0, "end")
    if text:
        entry.insert(0, get_display(text))


def bind_rtl_entry(entry: tk.Entry) -> None:
    entry._rtl_logical = ""

    def _refresh() -> None:
        logical = entry._rtl_logical
        entry.delete(0, "end")
        if logical:
            entry.insert(0, get_display(logical))

    def _on_key(event: tk.Event) -> str | None:
        if event.keysym == "BackSpace":
            if entry._rtl_logical:
                entry._rtl_logical = entry._rtl_logical[:-1]
                _refresh()
            return "break"
        if event.char and event.char.isprintable() and not (event.state & 0x4):
            entry._rtl_logical += event.char
            _refresh()
            return "break"
        return None

    entry.bind("<Key>", _on_key)
