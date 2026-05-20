
# PLAN: Dungeon Master Architecture

## 1. High-Level Architecture (SDK Pattern)
The system is strictly divided into layers to prevent GUI freezing and ensure modularity:
- **GUI Layer (Frontend):** Hebrew layout. Runs on the main UI thread. Calls ONLY the SDK.
- **SDK Layer (`sdk.py`):** The single entry point for all business logic. Exposes async/threaded methods to the GUI so it never blocks.
- **Business Logic & AI:** Contains the DM Agent, State Manager, and Tool executor.
- **FinOps Gatekeeper:** Intercepts all LLM/API calls to enforce token/cost limits per session.

## 2. Component Breakdown
- `config/settings.py`: Hardcoded constraints and `.env` loaders.
- `src/gatekeeper.py`: Singleton tracking costs and rate limits.
- `src/state.py`: Manages save/load (JSON) and player stats (Health, Inventory).
- `src/agent.py`: The LLM Dungeon Master. Implements History Truncation (FinOps) to only send the last N messages.
- `src/gui.py`: Tkinter/CustomTkinter Right-to-Left interface with 3 panels (Left: Stats, Center: Story/Chat, Right: Logs/API Cost).
- `src/tools.py`: Web Search Tool integration.

## 3. Asynchronous Flow
User types command -> GUI calls `SDK.process_turn_async()` -> SDK spawns a thread/async task -> Agent calls LLM -> Result updates GUI via a thread-safe callback.
