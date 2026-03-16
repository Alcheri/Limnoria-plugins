📦 Version 1.2 — Refinement & Power Features
🧩 1. Quality of Life Improvements
!history

Display recent conversation history for the current context.

Purpose:

Improve transparency

Help debug memory behaviour

Demonstrate context isolation

`!token_usage`

Display approximate:

Current prompt token count

Current history length

Configured maximum token limit

Purpose:

Help users avoid exceeding limits

Improve operational clarity

🧠 2. Memory Enhancements
Configurable maxHistoryLength

Introduce new registry setting:

`@config plugins.Asyncio.maxHistoryLength 12`

Replace hardcoded history trimming with configurable value.

Optional Persistent Memory (Advanced / Optional)

Add:

`@config plugins.Asyncio.persistentMemory False`

If enabled:

Save context histories to disk

Reload on bot restart

⚠ This would be opt-in only to preserve lightweight default behaviour.

🧮 3. Math Mode Improvements

Current behaviour:

Auto-detection

`≤ 6 lines`

Plain text output

Potential refinements:

More precise detection heuristic

Enforced numbered steps

Optional compact mode:

`@config plugins.Asyncio.mathCompact True`

🌐 4. Rate Limit Intelligence

Enhance current exponential backoff to:

Differentiate quota exhaustion vs temporary 429

Provide clearer user feedback

Optional short-term global cooldown during API instability

🛠 5. Administrative Controls

Introduce admin-only commands:

`!ai stats`\
`!ai resetall`\
`!ai clearcache`

For:

Clearing moderation cache

Resetting all context histories

Inspecting memory usage

⚙ 6. Performance Improvements

Replace naive token estimation with tiktoken

Smarter history trimming (token-based instead of message-count-based)

Output truncation detection warning

🧪 Proposed Milestones
v1.2-alpha

`maxHistoryLength`

`!history`

v1.2-beta

`!token_usage`

Improved math formatting

v1.2 (Stable)

Admin tools

Refined rate-limit handling

Optional persistent memory

🔮 Longer-Term Ideas (v1.3+)

Plugin metrics dashboard

Optional structured logging mode

Docker deployment example

CI linting workflow

Context summarisation for long-running sessions

Model selection via config

🏁 Release Philosophy

Asyncio will prioritise:

Stability over rapid feature expansion

Explicit configuration over hidden behaviour

Predictable performance over complexity

Each release must remain production-ready.

Maintainer: Barry Suridge
Project: Asyncio Limnoria AI Plugin
License: MIT



