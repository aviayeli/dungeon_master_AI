from __future__ import annotations
import itertools
import tkinter as tk

PANEL_BG = "#16213e"
ENTRY_BG = "#0f3460"
TEXT = "#e0e0e0"
DM_COLOR = "#ffd700"
PLAYER_COLOR = "#87ceeb"
ERROR_COLOR = "#e74c3c"

_SPINNER = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


class CenterPanel(tk.Frame):
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, bg=PANEL_BG)
        self._loading = False
        self._loading_id: str | None = None
        self._spinner = itertools.cycle(_SPINNER)
        self._build()

    def _build(self) -> None:
        frame = tk.Frame(self, bg=PANEL_BG)
        frame.pack(fill="both", expand=True, padx=5, pady=(5, 0))

        scrollbar = tk.Scrollbar(frame, bg=ENTRY_BG, troughcolor=PANEL_BG)
        scrollbar.pack(side="right", fill="y")

        self._chat = tk.Text(
            frame, bg=PANEL_BG, fg=TEXT, font=("Arial", 11),
            wrap="word", state="disabled", relief="flat",
            padx=14, pady=10, yscrollcommand=scrollbar.set,
        )
        self._chat.pack(fill="both", expand=True)
        scrollbar.config(command=self._chat.yview)

        self._chat.tag_config("dm_lbl", foreground=DM_COLOR, justify="right",
                               font=("Arial", 9, "bold"))
        self._chat.tag_config("dm", foreground=DM_COLOR, justify="right",
                               font=("Arial", 11))
        self._chat.tag_config("player_lbl", foreground=PLAYER_COLOR, justify="right",
                               font=("Arial", 9, "bold"))
        self._chat.tag_config("player", foreground=PLAYER_COLOR, justify="right",
                               font=("Arial", 11))
        self._chat.tag_config("error", foreground=ERROR_COLOR, justify="right",
                               font=("Arial", 10, "italic"))
        self._chat.tag_config("sys", foreground="#888888", justify="right",
                               font=("Arial", 9, "italic"))

        self._status_var = tk.StringVar(value="")
        self._status_lbl = tk.Label(self, textvariable=self._status_var,
                                     bg=PANEL_BG, fg="#888888", font=("Arial", 9))
        self._status_lbl.pack(pady=3)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_player_message(self, text: str) -> None:
        self._insert("אתה:\n", "player_lbl")
        self._insert(f"{text}\n\n", "player")

    def add_dm_message(self, text: str) -> None:
        self._insert("דאנג'ן מאסטר:\n", "dm_lbl")
        self._insert(f"{text}\n\n", "dm")
        self._scroll_bottom()

    def add_error(self, text: str) -> None:
        self._insert(f"⚠ {text}\n\n", "error")
        self._scroll_bottom()

    def add_system(self, text: str) -> None:
        self._insert(f"— {text} —\n\n", "sys")
        self._scroll_bottom()

    def start_loading(self) -> None:
        self._loading = True
        self._animate()

    def stop_loading(self) -> None:
        self._loading = False
        if self._loading_id:
            self.after_cancel(self._loading_id)
            self._loading_id = None
        self._status_var.set("")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _animate(self) -> None:
        if not self._loading:
            return
        self._status_var.set(f"הדאנג'ן מאסטר חושב {next(self._spinner)}")
        self._loading_id = self.after(100, self._animate)

    def _insert(self, text: str, tag: str) -> None:
        self._chat.config(state="normal")
        self._chat.insert("end", text, tag)
        self._chat.config(state="disabled")

    def _scroll_bottom(self) -> None:
        self._chat.see("end")
