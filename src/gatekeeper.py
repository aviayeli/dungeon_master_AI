from __future__ import annotations
from dataclasses import dataclass, field
from src.config import INPUT_COST_PER_MTOK, OUTPUT_COST_PER_MTOK, MAX_COST_USD


class BudgetExceededError(Exception):
    pass


@dataclass
class _Gatekeeper:
    total_input_tokens: int = field(default=0)
    total_output_tokens: int = field(default=0)
    total_cost_usd: float = field(default=0.0)

    def record_usage(self, input_tokens: int, output_tokens: int) -> None:
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost_usd += (
            input_tokens * INPUT_COST_PER_MTOK / 1_000_000
            + output_tokens * OUTPUT_COST_PER_MTOK / 1_000_000
        )

    def check_budget(self) -> None:
        if self.total_cost_usd >= MAX_COST_USD:
            raise BudgetExceededError(
                f"עלות ה-API ({self.total_cost_usd:.4f}$) חרגה מהתקציב המותר ({MAX_COST_USD}$)"
            )

    def reset(self) -> None:
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost_usd = 0.0


_instance: _Gatekeeper | None = None


def get_gatekeeper() -> _Gatekeeper:
    global _instance
    if _instance is None:
        _instance = _Gatekeeper()
    return _instance
