from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from src.config import MAX_COST_USD
from src.gui_rtl import rtl

BG = "#1a1a2e"
PANEL_BG = "#16213e"
TEXT = "#e0e0e0"
ACCENT = "#c84b31"
BUTTON_BG = "#0f3460"


class LeftPanel(tk.Frame):
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, bg=PANEL_BG, width=210)
        self.pack_propagate(False)
        self._build()

    def _build(self) -> None:
        tk.Label(self, text=rtl("🛡 שחקן"), bg=PANEL_BG, fg=ACCENT,
                 font=("Arial", 13, "bold"), anchor="e").pack(fill="x", padx=10, pady=(10, 6))

        self._name_var = tk.StringVar(value="---")
        self._class_var = tk.StringVar(value="---")
        self._loc_var = tk.StringVar(value="---")

        for label, var in [(rtl("שם:"), self._name_var), (rtl("מקצוע:"), self._class_var), (rtl("מיקום:"), self._loc_var)]:
            row = tk.Frame(self, bg=PANEL_BG)
            row.pack(fill="x", padx=10, pady=2)
            tk.Label(row, textvariable=var, bg=PANEL_BG, fg=TEXT,
                     font=("Arial", 10), anchor="e", justify="right").pack(side="right")
            tk.Label(row, text=label, bg=PANEL_BG, fg=ACCENT,
                     font=("Arial", 10, "bold")).pack(side="right", padx=(0, 4))

        tk.Label(self, text=rtl("חיים:"), bg=PANEL_BG, fg=ACCENT,
                 font=("Arial", 10, "bold"), anchor="e").pack(fill="x", padx=10, pady=(10, 2))

        style = ttk.Style()
        style.configure("Health.Horizontal.TProgressbar", troughcolor=PANEL_BG,
                         background="#4caf50", thickness=14)
        self._health_bar = ttk.Progressbar(self, orient="horizontal",
                                            mode="determinate", maximum=100,
                                            style="Health.Horizontal.TProgressbar")
        self._health_bar.pack(fill="x", padx=10, pady=2)
        self._health_label = tk.Label(self, text="100/100", bg=PANEL_BG, fg=TEXT,
                                       font=("Arial", 9), anchor="e")
        self._health_label.pack(fill="x", padx=10)

        tk.Label(self, text=rtl("מלאי:"), bg=PANEL_BG, fg=ACCENT,
                 font=("Arial", 10, "bold"), anchor="e").pack(fill="x", padx=10, pady=(10, 2))
        self._inv = tk.Text(self, bg=BUTTON_BG, fg=TEXT, font=("Arial", 9),
                             height=7, wrap="word", state="disabled", relief="flat")
        self._inv.pack(fill="both", padx=10, pady=(0, 10), expand=True)

    def refresh(self, stats: dict) -> None:
        self._name_var.set(stats.get("name", "---"))
        self._class_var.set(stats.get("character_class", "---"))
        self._loc_var.set(stats.get("location", "---"))
        hp, max_hp = stats.get("health", 0), stats.get("max_health", 100)
        self._health_bar["value"] = int((hp / max_hp) * 100) if max_hp else 0
        self._health_label.config(text=f"{hp}/{max_hp}")
        items = stats.get("inventory", [])
        self._inv.config(state="normal")
        self._inv.delete("1.0", "end")
        self._inv.insert("end", rtl("\n".join(f"• {i}" for i in items)) if items else rtl("ריק"))
        self._inv.config(state="disabled")


class RightPanel(tk.Frame):
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, bg=PANEL_BG, width=210)
        self.pack_propagate(False)
        self._build()

    def _build(self) -> None:
        tk.Label(self, text=rtl("📊 סטטיסטיקה"), bg=PANEL_BG, fg=ACCENT,
                 font=("Arial", 13, "bold"), anchor="e").pack(fill="x", padx=10, pady=(10, 6))

        self._turns_var = tk.StringVar(value=rtl("תורות: 0"))
        self._cost_var = tk.StringVar(value=rtl("עלות: $0.000000"))
        self._tokens_var = tk.StringVar(value=rtl("קלט: 0 | פלט: 0"))
        for var in (self._turns_var, self._cost_var, self._tokens_var):
            tk.Label(self, textvariable=var, bg=PANEL_BG, fg=TEXT,
                     font=("Arial", 10), anchor="e").pack(fill="x", padx=10, pady=2)

        style = ttk.Style()
        style.configure("Budget.Horizontal.TProgressbar", troughcolor=PANEL_BG,
                         background=ACCENT, thickness=10)
        self._budget_bar = ttk.Progressbar(self, orient="horizontal",
                                            mode="determinate", maximum=100,
                                            style="Budget.Horizontal.TProgressbar")
        self._budget_bar.pack(fill="x", padx=10, pady=6)

        tk.Label(self, text=rtl("יומן אירועים:"), bg=PANEL_BG, fg=ACCENT,
                 font=("Arial", 10, "bold"), anchor="e").pack(fill="x", padx=10, pady=(6, 2))
        self._log = tk.Text(self, bg=BUTTON_BG, fg=TEXT, font=("Arial", 9),
                             wrap="word", state="disabled", relief="flat")
        self._log.pack(fill="both", padx=10, pady=(0, 10), expand=True)

    def refresh(self, stats: dict, cost: dict) -> None:
        self._turns_var.set(rtl(f"תורות: {stats.get('turn_count', 0)}"))
        usd = cost.get("total_cost_usd", 0.0)
        self._cost_var.set(rtl(f"עלות: ${usd:.6f}"))
        self._tokens_var.set(rtl(f"קלט: {cost.get('input_tokens', 0)} | פלט: {cost.get('output_tokens', 0)}"))
        self._budget_bar["value"] = min(100, int((usd / MAX_COST_USD) * 100))

    def log_event(self, msg: str) -> None:
        self._log.config(state="normal")
        self._log.insert("end", rtl(f"• {msg}") + "\n")
        self._log.see("end")
        self._log.config(state="disabled")
