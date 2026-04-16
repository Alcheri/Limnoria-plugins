# Asyncio Moderation: `omni-moderation-latest`

This document describes how the Asyncio Limnoria plugin uses OpenAI moderation in production, with practical details tied to the current implementation in `plugin.py`.

## Purpose

The plugin moderates user input before sending it to chat completions.  
Goals:

- reduce unsafe prompt content reaching the chat model
- keep IRC interaction responsive
- avoid bot outages if moderation is temporarily unavailable

## Where Moderation Runs

Moderation is executed in `execute_chat_with_input_moderation(...)` after cooldown and token checks, but before chat generation.

Current order:

1. Cooldown gate
2. Token-length gate
3. Moderation check (`omni-moderation-latest`)
4. Chat completion request

If moderation flags input, the request stops and the user gets:

`I'm sorry, but your input has been flagged as inappropriate.`

## Model and API Call

The plugin calls:

```python
openai_client.moderations.create(
    model="omni-moderation-latest",
    input=text
)
```

Only `response.results[0].flagged` is currently used for allow/block behavior.

## Async + Caching Strategy

Moderation is wrapped in a synchronous helper and executed with:

`asyncio.to_thread(...)`

This keeps the plugin responsive and avoids blocking command handling.

A local LRU cache is applied:

`@lru_cache(maxsize=512)`

Implications:

- repeated identical inputs are fast (cache hit)
- reduced moderation API traffic for duplicates
- cache lives in-process (clears on bot restart)

## Retry and Failure Behavior

`check_moderation_flag(...)` retries up to 3 times when rate-limited (`429` / `Too Many Requests`), using exponential backoff with small jitter.

If moderation fails for other reasons, the plugin logs the error and continues with **fail-open** behavior.

Fail-open means:

- moderation errors do not block all chat usage
- input is treated as unflagged when moderation cannot decide

This is a reliability-first tradeoff suitable for IRC uptime.

## Inputs Skipped From Moderation

The plugin returns "not flagged" immediately when input is:

- empty/whitespace
- starts with `!`
- shorter than 5 characters

This avoids spending moderation calls on command-like or trivial inputs.

## Operational Notes

- Moderation decisions are based on the input message only.
- Conversation history is not separately moderated in this layer.
- Logs include moderation warnings/errors for diagnostics.
- User-facing output stays minimal to avoid noisy channel behavior.

## Security and Product Tradeoffs

Current policy balances safety and availability:

- **Safety**: flagged content is blocked before chat generation.
- **Availability**: moderation outages/rate limits should not take the bot offline.

If stricter enforcement is needed later, fail-open can be changed to fail-closed, or category-level decisions can be added using richer moderation fields.

## Summary

Asyncio uses `omni-moderation-latest` as a lightweight pre-filter with:

- async thread offloading
- duplicate-input caching
- bounded retry on rate limit
- fail-open fallback

This design keeps moderation useful without making the IRC bot brittle.
