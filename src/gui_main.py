from __future__ import annotations
import tkinter as tk
from tkinter import messagebox

from src.gui_center import CenterPanel
from src.gui_panels import LeftPanel, RightPanel
from src.sdk import DungeonMasterSDK

BG = "#1a1a2e"
PANEL_BG = "#16213e"
TEXT = "#e0e0e0"
ACCENT = "#c84b31"
BUTTON_BG = "#0f3460"


class App(tk.Tk):
    def __init__(self, sdk: DungeonMasterSDK) -> None:
        super().__init__()
        self._sdk = sdk
        self.title("Dungeon Master AI — הרפתקת פנטזיה")
        self.configure(bg=BG)
        self.geometry("1200x760")
        self.minsize(900, 600)
        self.protocol("WM_DELETE_WINDOW", self._on_quit)
        self._build_layout()
        self._refresh_panels()

    # ------------------------------------------------------------------
    # Layout construction
    # ------------------------------------------------------------------

    def _build_layout(self) -> None:
        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        self._left = LeftPanel(main)
        self._left.grid(row=0, column=0, sticky="nsew", padx=(5, 2), pady=5)

        self._center = CenterPanel(main)
        self._center.grid(row=0, column=1, sticky="nsew", padx=2, pady=5)

        self._right = RightPanel(main)
        self._right.grid(row=0, column=2, sticky="nsew", padx=(2, 5), pady=5)

        self._build_input()

    def _build_input(self) -> None:
        bottom = tk.Frame(self, bg=PANEL_BG, pady=6)
        bottom.pack(fill="x", side="bottom", padx=5, pady=(0, 5))

        entry_row = tk.Frame(bottom, bg=PANEL_BG)
        entry_row.pack(fill="x", padx=10, pady=(4, 4))

        send_btn = tk.Button(entry_row, text="שלח ⏎", bg=ACCENT, fg="white",
                              font=("Arial", 11, "bold"), command=self._on_send,
                              relief="flat", padx=14, cursor="hand2")
        send_btn.pack(side="left")

        self._entry = tk.Entry(entry_row, bg=BUTTON_BG, fg=TEXT, font=("Arial", 12),
                                insertbackground=TEXT, relief="flat", justify="right")
        self._entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._entry.bind("<Return>", lambda _: self._on_send())
        self._entry.focus_set()

        btn_row = tk.Frame(bottom, bg=PANEL_BG)
        btn_row.pack(fill="x", padx=10)
        for label, cmd in [
            ("עזרה", lambda: self._quick("עזרה, מה אני יכול לעשות?")),
            ("שמור", self._on_save),
            ("טען", self._on_load),
            ("מלאי", lambda: self._quick("הצג את המלאי שלי")),
            ("יציאה", self._on_quit),
        ]:
            tk.Button(btn_row, text=label, bg=BUTTON_BG, fg=TEXT, font=("Arial", 10),
                       command=cmd, relief="flat", padx=12, pady=3,
                       cursor="hand2").pack(side="left", padx=3)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_send(self) -> None:
        text = self._entry.get().strip()
        if not text or self._sdk.is_thinking:
            return
        self._entry.delete(0, "end")
        self._center.add_player_message(text)
        self._center.start_loading()
        self._right.log_event(f"שלחת: {text[:35]}")
        self._sdk.send_message(text, on_reply=self._cb_reply, on_error=self._cb_error)

    def _cb_reply(self, reply: str) -> None:
        self.after(0, self._apply_reply, reply)

    def _apply_reply(self, reply: str) -> None:
        self._center.stop_loading()
        self._center.add_dm_message(reply)
        self._refresh_panels()
        self._right.log_event("הדאנג'ן מאסטר הגיב")
        try:
            self._sdk.save_game()
        except Exception:
            pass

    def _cb_error(self, exc: Exception) -> None:
        self.after(0, self._apply_error, exc)

    def _apply_error(self, exc: Exception) -> None:
        self._center.stop_loading()
        self._center.add_error(str(exc))
        self._right.log_event(f"שגיאה: {str(exc)[:45]}")

    def _quick(self, cmd: str) -> None:
        self._entry.delete(0, "end")
        self._entry.insert(0, cmd)
        self._on_send()

    def _on_save(self) -> None:
        try:
            self._sdk.save_game()
            self._right.log_event("משחק נשמר")
        except Exception as exc:
            messagebox.showerror("שגיאת שמירה", str(exc))

    def _on_load(self) -> None:
        try:
            self._sdk.load_game()
            self._refresh_panels()
            self._center.add_system("משחק נטען בהצלחה")
            self._right.log_event("משחק נטען")
        except Exception as exc:
            messagebox.showerror("שגיאת טעינה", str(exc))

    def _on_quit(self) -> None:
        if messagebox.askyesno("יציאה", "האם לשמור לפני היציאה?"):
            try:
                self._sdk.save_game()
            except Exception:
                pass
        self.destroy()

    def _refresh_panels(self) -> None:
        try:
            stats = self._sdk.get_player_stats()
            self._left.refresh(stats)
            self._right.refresh(stats, self._sdk.get_cost_stats())
        except Exception:
            pass
