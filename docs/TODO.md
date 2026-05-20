
# TODO: Dungeon Master

## Phase 1: Infrastructure & State
- [x] Create `pyproject.toml` and `.env-example`.
- [x] Implement `src/config.py` (load constraints).
- [x] Implement `src/gatekeeper.py` to prevent API budget overruns.
- [x] Implement `src/state.py` (Player dataclass, save/load to JSON).

## Phase 2: AI Agent & Logic
- [x] Implement `WebSearchTool` for real-time data fetching.
- [x] Implement `src/agent.py` with system prompt for a Hebrew DM.
- [x] Add FinOps History Truncation (keep only the last 5 interactions).

## Phase 3: SDK Layer
- [x] Implement `src/sdk.py` to wrap the Agent and State Manager.
- [x] Ensure all SDK methods interacting with LLMs are non-blocking (async/threading).

## Phase 4: Hebrew GUI (Graphical User Interface)
- [x] Implement `src/gui.py` skeleton (Right-to-Left alignment) — modularized as `gui_panels.py`, `gui_center.py`, `gui_main.py`.
- [x] Build Left Panel: Player Name, Class, Health Bars, Location, Inventory.
- [x] Build Right Panel: Stats, Turns, API Cost counter, Event Log.
- [x] Build Center Panel: Story text, chat bubbles, auto-scroll to bottom.
- [x] Build Input Area: Text field, Send button, quick command buttons.
- [x] Add loading animation during LLM thinking.

## Phase 5: Testing & Constraints
- [x] Write 15+ pytest unit tests in `tests/`.
- [x] Run `uv run ruff check .` and fix all styling errors.
- [x] Ensure no file exceeds 150 lines.
