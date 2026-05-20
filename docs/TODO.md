
# TODO: Dungeon Master

## Phase 1: Infrastructure & State
- [x] Create `pyproject.toml` and `.env-example`.
- [x] Implement `src/config.py` (load constraints).
- [x] Implement `src/gatekeeper.py` to prevent API budget overruns.
- [x] Implement `src/state.py` (Player dataclass, save/load to JSON).

## Phase 2: AI Agent & Logic
- [ ] Implement `WebSearchTool` for real-time data fetching.
- [ ] Implement `src/agent.py` with system prompt for a Hebrew DM.
- [ ] Add FinOps History Truncation (keep only the last 5 interactions).

## Phase 3: SDK Layer
- [ ] Implement `src/sdk.py` to wrap the Agent and State Manager.
- [ ] Ensure all SDK methods interacting with LLMs are non-blocking (async/threading).

## Phase 4: Hebrew GUI (Graphical User Interface)
- [ ] Implement `src/gui.py` skeleton (Right-to-Left alignment).
- [ ] Build Left Panel: Player Name, Class, Health Bars, Location, Inventory.
- [ ] Build Right Panel: Stats, Turns, API Cost counter, Event Log.
- [ ] Build Center Panel: Story text, chat bubbles, auto-scroll to bottom.
- [ ] Build Input Area: Text field, Send button, quick command buttons.
- [ ] Add loading animation during LLM thinking.

## Phase 5: Testing & Constraints
- [ ] Write 15+ pytest unit tests in `tests/`.
- [ ] Run `uv run ruff check .` and fix all styling errors.
- [ ] Ensure no file exceeds 150 lines.
