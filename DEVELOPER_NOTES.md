# 🛠 Asyncio Plugin – Developer Notes

This document explains the architectural decisions behind the Asyncio Limnoria plugin.

It exists to:

- Preserve architectural intent
- Prevent regression during refactors
- Document production-learned lessons
- Guide safe feature expansion

This is an internal engineering document — not user-facing documentation.

---

# 🎯 Design Principles

The plugin prioritises:

1. Stability over cleverness
2. IRC-safe behaviour under load
3. Strict user/channel isolation
4. Protection against runaway API usage
5. Compatibility with Limnoria’s threading model
6. Minimal external dependencies

Implementation choices favour reliability over theoretical elegance.

---

# 🧠 Conversation Memory Model

## ❌ Rejected: Global Shared History

Early implementations used one shared conversation history.

This caused:

- Cross-user context contamination
- Multi-channel behavioural drift
- Unbounded memory growth
- Unpredictable response context

## ✅ Adopted: Context-Keyed Memory

History is keyed using:

    context_key = f"{channel}:{nick}"

Properties:

- Same user in different channels → separate conversations
- Private messages → isolated context
- No shared state between users
- Bounded memory per context

This model is deterministic and IRC-safe.

---

# ⏱ Cooldown Architecture

Cooldowns use the same context key:

    USER_COOLDOWNS[context_key]

Design guarantees:

- Spam control without affecting other users
- No cross-channel interference
- Cooldown enforcement occurs BEFORE any API call

This prevents unnecessary API usage and protects rate limits.

---

# 🔄 Async Execution Strategy

## ❌ Rejected: Direct Limnoria Event Loop Integration

Attempting to attach coroutines to Limnoria’s internal loop caused:

- Deadlocks
- Hanging commands
- Coroutine lifecycle corruption
- Plugin conflicts

## ✅ Adopted: Threaded Plugin + asyncio.run()

The plugin uses:

    threaded = True
    asyncio.run(...)

Design rationale:

- Limnoria manages threads safely
- Each command receives a clean event loop
- Prevents coroutine reuse errors
- Dramatically simplifies debugging

Trade-off:

Slight per-call overhead in exchange for reliability and isolation.

This is intentional.

---

# 🔢 Token Counting Strategy

## ❌ Rejected: tiktoken Dependency

Issues encountered:

- Model encoding breakage on version changes
- Increased dependency surface
- Unnecessary precision for IRC use
- Fragility under model evolution

## ✅ Adopted: Approximate Token Counting

Implementation:

    len(text.split())

Why acceptable:

- Token limits are protective, not billing-critical
- Overestimation is safer than underestimation
- Zero external dependencies
- Model-agnostic behaviour

Precision is not required for IRC safety.

---

# 🛡 Moderation Strategy

Moderation characteristics:

- Cached using lru_cache
- Executed in background thread
- Fail-open if moderation API fails
- Applied only to user input (not history)

Why fail-open?

- Prevents moderation outages from disabling the bot
- Maintains IRC reliability
- Avoids blocking legitimate usage

Reliability takes precedence over strict enforcement.

---

# 📦 Limnoria Registry Handling

Limnoria registry values may return custom wrapper types.

Direct comparisons caused errors such as:

    TypeError: '<' not supported between instances of 'float' and 'Integer'

## Rule

All registry reads must pass through converters:

    _to_int()
    _to_bool()

No direct comparison of raw registry values is permitted.

---

# 🧹 History Trimming Policy

History is trimmed on every request:

    [system] + last N messages

Design goals:

- Prevent unbounded memory growth
- Keep context relevant
- Avoid excessive token usage
- Ensure predictable behaviour

Trimming is automatic and silent.

---

# 🗃 Persistence Policy (Deferred)

Persistent storage was intentionally postponed.

Reasons:

- Avoid file corruption risks
- Avoid concurrency complexity
- Preserve restart safety
- Keep core architecture simple

Persistence can be introduced later without redesigning the memory model.

---

# ⚙️ Error Handling Philosophy

The plugin follows:

- Log extensively
- Fail safely
- Never crash the bot
- Provide user-friendly fallback messages

Contract:

- Users see minimal, clear error messages
- Full stack traces are logged (debug mode)
- Only command layer may reply to IRC

---

# 🚫 Architectural Anti-Patterns

The following must NOT be reintroduced:

- Global shared history
- Direct event loop manipulation
- Blocking I/O inside command handlers
- Direct registry comparisons
- Deep-layer irc.reply() calls
- Shared mutable global state across contexts

These are known failure sources.

---

# 🚀 v1.2 Architectural Change Proposal

v1.2 is a structural hardening release.

Objectives:

1. Formalise service separation
2. Introduce structured internal layering
3. Improve observability and debugging
4. Prepare for optional persistence
5. Strengthen error classification
6. Reduce implicit global state

User-facing behaviour must remain unchanged.

---

## 🧩 Layered Architecture (Proposed)

    plugin.py      → IRC command interface only
    core.py        → Conversation orchestration
    services.py    → External API interactions
    memory.py      → Context memory handling
    cooldown.py    → Cooldown tracking
    errors.py      → Exception hierarchy
    utils.py       → Pure helper functions

Rules:

- plugin.py must not call APIs directly
- services.py must not call irc.reply()
- memory.py must not contain business logic
- core.py orchestrates but does not perform raw I/O

---

## 🛡 Structured Exception Hierarchy

Proposed:

    PluginError
    ├── ConfigurationError
    ├── RateLimitError
    ├── ModerationError
    ├── MemoryError
    ├── ServiceError
        ├── APIConnectionError
        ├── APITimeoutError
        └── APIResponseError

Only PluginError subclasses may propagate upward.

---

## 🧠 Memory Engine Abstraction

Encapsulate memory:

    class ConversationMemory:
        get_context()
        append()
        trim()
        clear()

Removes global mutable state and prepares for persistence.

---

## ⏱ Cooldown Manager Abstraction

    class CooldownManager:
        is_allowed()
        record()

Prevents scattered cooldown logic.

---

## 📊 Observability Improvements

Debug-mode metrics:

- API latency
- Context count
- Average history length

Must not alter behaviour.

---

## 🗃 Optional Persistence (Experimental)

- JSON snapshotting
- Atomic file replace
- Disabled by default
- Must never block command thread
- Fail gracefully on corruption

---

## 🔄 Async Strategy Stability

threaded = True + asyncio.run() remains unchanged in v1.2.

No coroutine objects may escape scope.

---

## 🚫 Explicit Non-Goals for v1.2

- No direct event loop integration
- No global shared memory
- No heavy dependency additions
- No behaviour change

---

# 🧪 v1.2 Implementation Checklist

## Phase 1 – Structural Refactor

- [ ] Extract ConversationMemory to memory.py
- [ ] Extract CooldownManager to cooldown.py
- [ ] Implement errors.py hierarchy
- [ ] Replace raw dictionary access
- [ ] Preserve identical behaviour

## Phase 2 – Layer Enforcement

- [ ] Remove API calls from plugin.py
- [ ] Remove IRC references from services.py
- [ ] Ensure core.py orchestrates cleanly
- [ ] Confirm no blocking I/O exists

## Phase 3 – Observability

- [ ] Add debug timing metrics
- [ ] Log context statistics
- [ ] Confirm zero overhead when disabled

## Phase 4 – Optional Persistence

- [ ] Add config flag
- [ ] Implement atomic JSON write
- [ ] Ensure background execution
- [ ] Confirm restart recovery
- [ ] Confirm corruption safety

---

# 🧪 Regression Test Matrix

Before tagging v1.2:

Multi-Channel Isolation  
Cooldown Behaviour  
Failure Modes  
Memory Trimming  
Restart Behaviour  

No regression is acceptable.

---

# 📌 Versioning Philosophy

v1.1 → Production-stable architecture  
v1.2 → Structural refinement and internal hardening  
v1.3 → Optional capability expansion  
v2.0 → Major architectural shift only  

---

# 🧑‍💻 Author Notes

This plugin evolved through real IRC production usage.

Decisions reflect resolution of:

- Hanging bots
- Cross-user memory contamination
- Rate-limit storms
- Registry type crashes
- Coroutine lifecycle bugs

The current architecture reflects what has proven reliable under real-world IRC load.

---

Maintained by: Barry Suridge  
Plugin: Asyncio for Limnoria IRC  
Status: Production-stable architecture
