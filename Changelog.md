# 📜 Changelog – Asyncio Limnoria Plugin

All notable changes to the Asyncio plugin will be documented in this file.

This project follows a simple versioning approach:

- Major updates for architectural changes
- Minor updates for new features
- Patch updates for bug fixes

---

## [1.1] – 2026-02-26

### ✨ Added

- Per-user **and** per-channel conversation memory
- Context-isolated cooldown tracking
- `!reset` command scoped to current channel/PM
- Automatic history trimming per context
- Improved moderation caching behaviour
- Safer Limnoria registry value handling helpers

### 🔧 Changed

- Memory model rewritten from global history → isolated contexts
- Cooldown logic rewritten to avoid registry Integer comparison issues
- Async execution model finalised using `threaded=True` + `asyncio.run()`
- Documentation fully rewritten to match real plugin behaviour

### 🐛 Fixed

- SSL connection issues causing delayed responses
- Async event loop deadlocks from incorrect coroutine handling
- TypeError caused by comparing float with Limnoria `Integer`
- Global history mixing users across channels
- Silent timeout behaviour when coroutine crashed internally

---

## [1.0] – 2026-02-25

### ✨ Initial Production Release

- Async chat command using OpenAI API
- Basic conversation memory support
- Moderation filtering implemented
- Token limit enforcement added
- Configurable bot name and language preference
- Debug logging option
- Retry logic for API rate limits

### ⚠️ Known Limitations (at time of release)

- Global conversation history shared across users
- Cooldown logic not context-aware
- Possible event-loop conflicts under heavy load

---

## Future Plans (Not Yet Implemented)

### 💡 Possible Enhancements

- Persistent memory storage (JSON or database)
- Admin commands (`!ai stats`, `!ai resetall`)
- Token usage tracking per user
- Channel enable/disable toggle
- Response style presets
- Multi-model support
- Operator dashboard logging

---

## About This File

This changelog exists to:

- Track plugin evolution clearly
- Help future debugging
- Provide upgrade notes for operators
- Document architectural decisions

---

**Maintained by:** Barry Suridge  
**Plugin:** Asyncio for Limnoria IRC
