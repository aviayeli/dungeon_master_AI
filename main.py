from __future__ import annotations
import tkinter as tk
from tkinter import messagebox

from src.config import DEFAULT_PLAYER_CLASS
from src.gui_main import App
from src.gui_rtl import bind_rtl_entry, rtl
from src.sdk import DungeonMasterSDK

BG = "#1a1a2e"
PANEL_BG = "#16213e"
TEXT = "#e0e0e0"
ACCENT = "#c84b31"
BUTTON_BG = "#0f3460"


def _new_game_dialog(root: tk.Tk) -> tuple[str, str] | None:
    dialog = tk.Toplevel(root)
    dialog.title(rtl("משחק חדש"))
    dialog.configure(bg=BG)
    dialog.resizable(False, False)
    dialog.grab_set()

    tk.Label(dialog, text=rtl("ברוך הבא, גיבור!"), bg=BG, fg=ACCENT,
             font=("Arial", 16, "bold")).pack(pady=(20, 4))
    tk.Label(dialog, text=rtl("מה שמך?"), bg=BG, fg=TEXT,
             font=("Arial", 11)).pack()
    name_var = tk.StringVar()
    name_entry = tk.Entry(dialog, textvariable=name_var, bg=PANEL_BG, fg=TEXT,
                           font=("Arial", 12), relief="flat", justify="right", width=24)
    name_entry.pack(padx=30, pady=8)
    bind_rtl_entry(name_entry)
    name_entry.focus_set()

    tk.Label(dialog, text=rtl("בחר מקצוע:"), bg=BG, fg=TEXT,
             font=("Arial", 11)).pack(pady=(8, 2))
    class_var = tk.StringVar(value=DEFAULT_PLAYER_CLASS)
    for cls in ["לוחם", "קוסם", "גנב", "כומר", "קשת"]:
        tk.Radiobutton(dialog, text=rtl(cls), variable=class_var, value=cls,
                        bg=BG, fg=TEXT, selectcolor=BUTTON_BG, activebackground=BG,
                        font=("Arial", 11), anchor="e").pack(anchor="e", padx=60)

    result: list[tuple[str, str]] = []

    def _confirm() -> None:
        n = name_var.get().strip()
        if not n:
            messagebox.showwarning(rtl("שגיאה"), rtl("יש להזין שם!"), parent=dialog)
            return
        result.append((n, class_var.get()))
        dialog.destroy()

    tk.Button(dialog, text=rtl("התחל הרפתקה! ⚔"), bg=ACCENT, fg="white",
               font=("Arial", 12, "bold"), command=_confirm,
               relief="flat", padx=20, pady=6, cursor="hand2").pack(pady=18)
    dialog.bind("<Return>", lambda _: _confirm())
    root.wait_window(dialog)
    return result[0] if result else None


def _start_session(root: tk.Tk, sdk: DungeonMasterSDK) -> bool:
    try:
        sdk.load_game()
        save_found = True
    except Exception:
        save_found = False

    if save_found:
        if messagebox.askyesno(rtl("ברוך הבא"), rtl("נמצא משחק שמור. האם לטעון אותו?"), parent=root):
            return True

    data = _new_game_dialog(root)
    if not data:
        return False
    sdk.new_game(*data)
    return True


def main() -> None:
    root = tk.Tk()
    root.withdraw()
    sdk = DungeonMasterSDK()
    if not _start_session(root, sdk):
        root.destroy()
        return
    root.destroy()
    App(sdk).mainloop()


if __name__ == "__main__":
    main()
