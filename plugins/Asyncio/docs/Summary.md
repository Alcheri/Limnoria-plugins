# Summary of Asyncio IRC Plugin

• Asyncio is a Limnoria IRC plugin that provides OpenAI-backed chat with an intentionally conservative architecture:
  `plugin.py` is the only IRC-facing layer, `core/` handles orchestration and response shaping, `services/` isolates OpenAI

  Functionally, the repo is built around the chat and reset commands. It supports per-channel/per-user memory isolation,
  input moderation, cooldown protection, approximate token limits, IRC-safe reply chunking, and a special maths mode
  that forces short step-by-step answers. OpenAI model selection is resilient: it uses a fallback chain and records the
  active model at runtime.

  Structurally, this repo has already been refactored away from a monolithic plugin into bounded modules:

- `plugin.py`: Limnoria command entrypoint, reply handling, error reporting
- `core/chat.py`: main request flow, moderation gate, token check, model call orchestration
- `core/text.py`: maths detection, output cleanup, IRC chunk splitting
- `services/openai_client.py`: client setup and chat-model fallback logic
- `services/moderation.py`: moderation with caching and retry/fail-open behaviour
- `state/memory.py` and `state/runtime.py: conversation history and OpenAI runtime state
- `config/__init__.py` and `config/runtime.py`: Limnoria registry definitions and safe config extraction

Operationally, the design prioritises reliability over sophistication. It uses threaded = True with asyncio.run(...)
per command rather than trying to share an event loop with Limnoria, and it keeps all state in memory rather than
persisting it. The test layout is lightweight but deliberate: test.py remains as the Limnoria entrypoint, with focused
unit tests under tests/ for chat flow, text processing, moderation, OpenAI client behaviour, and memory handling.

Overall, this is a production-oriented, modular AI chat plugin for Limnoria that aims for stability, safe concurrency
boundaries, and predictable IRC behaviour rather than aggressive feature breadth.

---

Maintained by: Barry Suridge Plugin: Asyncio for Limnoria IRC Status: Production-stable architecture, v1.0 released 2024-06-01
