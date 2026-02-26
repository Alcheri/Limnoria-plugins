# 🛠 Asyncio Plugin – Developer Notes

This document explains the architectural decisions behind the Asyncio Limnoria plugin.

It is intended for:

- Future maintenance of the plugin
- Refactoring work
- Debugging production issues
- Adding new features safely

---

## 🎯 Design Goals

The plugin was designed with the following priorities:

1. **Stability over cleverness**
2. **IRC-safe behaviour under load**
3. **Isolation between users and channels**
4. **Protection against runaway API usage**
5. **Compatibility with Limnoria’s architecture**
6. **Minimal external dependencies**

This means some implementation choices favour reliability rather than theoretical elegance.

---

## 🧠 Conversation Memory Model

### ❌ Rejected Approach: Global History

Early versions used one shared conversation history.

Problems:

- Users contaminated each other’s context
- Multi-channel bots behaved unpredictably
- One user could influence responses to others
- Memory growth became unbounded

### ✅ Final Approach: Context-Keyed Memory

The plugin now stores history using:
context_key = f"{channel}:{nick}"

This ensures:

- Same user in different channels → separate conversations
- Private messages → independent context
- Users never share memory
- History stays relevant

This model is simple, predictable, and IRC-friendly.

---

## ⏱ Cooldown Design

Cooldowns are tracked using the same context key:
USER_COOLDOWNS[context_key]

Why:

- Prevents spam without blocking other users
- Prevents one channel from affecting another
- Works naturally with Limnoria’s multi-channel behaviour

Cooldown enforcement happens **before any API call** to prevent unnecessary usage.

---

## 🔄 Async Execution Strategy

### ❌ Rejected Approach: Native async event loop integration

Directly attaching to Limnoria’s event loop caused:

- Deadlocks
- Hanging commands
- Difficult-to-debug coroutine states
- Conflicts with other plugins

### ✅ Final Approach: Threaded plugin + `asyncio.run()`

The plugin uses:

Why:

- Prevents spam without blocking other users
- Prevents one channel from affecting another
- Works naturally with Limnoria’s multi-channel behaviour

Cooldown enforcement happens **before any API call** to prevent unnecessary usage.

---

## 🔄 Async Execution Strategy

### ❌ Rejected Approach: Native async event loop integration

Directly attaching to Limnoria’s event loop caused:

- Deadlocks
- Hanging commands
- Difficult-to-debug coroutine states
- Conflicts with other plugins

### ✅ Final Approach: Threaded plugin + `asyncio.run()`

The plugin uses:
threaded = True
asyncio.run(...)

Reasons:

- Limnoria handles threading safely
- Each command gets a clean event loop
- Prevents coroutine reuse errors
- Simplifies debugging dramatically

This trades a tiny bit of overhead for much higher reliability.

---

## 🔢 Token Counting Strategy

### ❌ Rejected: tiktoken dependency

Problems encountered:

- Model name changes broke encoding lookup
- Extra dependency complexity
- Unnecessary precision for IRC usage
- More fragile under version changes

### ✅ Final Approach: Approximate token counting

The plugin uses:

Reasons:

- Limnoria handles threading safely
- Each command gets a clean event loop
- Prevents coroutine reuse errors
- Simplifies debugging dramatically

This trades a tiny bit of overhead for much higher reliability.

---

## 🔢 Token Counting Strategy

### ❌ Rejected: tiktoken dependency

Problems encountered:

- Model name changes broke encoding lookup
- Extra dependency complexity
- Unnecessary precision for IRC usage
- More fragile under version changes

### ✅ Final Approach: Approximate token counting

The plugin uses:
len(text.split())

Why this is acceptable:

- Token limits are only protective, not billing-critical
- Overestimation is safer than underestimation
- No dependency required
- Works consistently across models

---

## 🛡 Moderation Strategy

Moderation is:

- Cached using `lru_cache`
- Executed in a background thread
- Fail-open if moderation API fails

Why fail-open?

- Prevents moderation outages from breaking the bot
- Avoids blocking legitimate users
- Maintains reliability in production IRC environments

Moderation is intentionally applied **only to user input**, not history.

---

## 📦 Limnoria Config Handling

Limnoria registry values sometimes return custom types.

Direct comparisons caused errors like:
TypeError: '<' not supported between instances of 'float' and 'Integer'

### Solution

All config reads go through helper converters:
_to_int()
_to_bool()

This ensures values are always native Python types.

---

## 🧹 History Trimming

History is automatically trimmed:
[system] + last N messages

Why:

- Prevents memory growth
- Keeps responses focused
- Avoids sending excessive tokens
- Keeps behaviour predictable

This trimming happens silently on each request.

---

## 🧾 Why No Persistent Storage Yet

Persistent memory was intentionally deferred.

Reasons:

- Avoid file corruption risks
- Avoid concurrency issues
- Keep plugin restart-safe
- Keep initial architecture simple

Persistent storage can be added later without changing the core logic.

---

## ⚙️ Error Handling Philosophy

The plugin prefers:

- Logging over crashing
- User-friendly fallback messages
- Safe defaults instead of hard failures

If something goes wrong:

- User sees a simple message
- Logs contain full stack trace (when debug enabled)

---

## 🧭 Future Architecture Directions

Planned safe extensions:

- JSON-based persistent memory
- Admin control commands
- Token usage tracking
- Channel-level enable/disable
- Response style presets

All of these can be added without breaking the existing structure.

---

## 📘 Maintenance Tips

If modifying the plugin:

1. Never reintroduce global history
2. Keep context_key logic intact
3. Always convert registry values to native types
4. Avoid deep integration with Limnoria event loop
5. Test in multi-channel environment before release

---

## 🧑‍💻 Author Notes

This plugin evolved through real IRC usage rather than theoretical design.

Many decisions were made to fix real-world issues:

- Hanging bots
- Cross-user memory bleed
- Rate limit storms
- Registry type crashes

The current structure reflects what actually works reliably in production.

---

**Maintained by:** Barry Suridge  
**Plugin:** Asyncio for Limnoria IRC
