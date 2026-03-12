# Weather: several bugs and code quality issues

**Labels:** `bug`, `enhancement`

---

## Summary

A review of `plugin.py` and `config.py` found two security concerns, one potential `NameError`,
two architectural inefficiencies, and a handful of minor quality issues.

---

## Bugs

### 1. API keys leaked to debug log *(security)*

`google_maps()` and `openweather()` both pass the full `params` dict — which includes the API
key — to `log.debug`. Anyone with access to the bot's log files can harvest the keys.

```python
# google_maps()
log.debug(f"Using Google Maps API with {url} and params: {params}")
# openweather()
log.debug(f"Weather: using URL {url} with params {params} (openweather)")
```

**Fix:** log only the URL, or redact the key: `{**params, 'key': '***'}`.

---

### 2. `ident_host` possibly undefined in `except KeyError`

If `"user" in optlist` and `irc.state.nickToHostmask()` raises (nick not in channel), execution
falls to the `except KeyError` block, which references `ident_host` — a name that was never
assigned. This raises a `NameError` instead of giving the user a helpful message.

```python
try:
    if "user" in optlist:
        host = irc.state.nickToHostmask(optlist["user"])  # may raise
    else:
        host = msg.prefix
    ident_host = host.split("!")[1]   # ident_host assigned here
    location = self.db[ident_host]
except KeyError:
    irc.error(...% ircutils.bold("*!" + ident_host), ...)  # NameError if nickToHostmask raised
```

**Steps to reproduce:**

```
@weather --user SomeNickNotInChannel
# Expected: "Nickname not found" error
# Actual:   NameError / unhandled exception in the bot log
```

---

## Architecture

### 3. `asyncio.run()` creates a fresh event loop per command

`weather()` and `google()` each call `asyncio.run(process_…())`, which creates and immediately
tears down a new event loop on every invocation. This is wasteful and will raise
`RuntimeError: This event loop is already running` in certain bot environments. Limnoria plugins
that use async I/O should set `threaded = True` and use a persistent loop or
`concurrent.futures`.

### 4. New `aiohttp.ClientSession` created per request

`fetch_data()` opens a `ClientSession` inside the call. The
[aiohttp docs](https://docs.aiohttp.org/en/stable/client_advanced.html#persistent-session)
explicitly warn against this — sessions are intended to be long-lived and reused across requests.
A session should be created once (e.g., in `__init__`) and closed in `die()`.

---

## Minor quality issues

### 5. Placeholder class docstring

```python
class Weather(callbacks.Plugin):
    """
    Add the help for "@plugin help Weather" here
    This should describe *how* to use this plugin.
    """
```

This was never replaced with real content.

### 6. `help` command overrides Limnoria's built-in

Defining a command named `help` shadows the framework's built-in `help` dispatcher — users will
get the custom docstring output instead of the standard plugin help listing.

### 7. Unused `apikeys` config group

`config.py` registers `conf.registerGroup(Weather, "apikeys")` but no values are ever nested
under it. Either use it or remove it to avoid confusion.

### 8. File I/O without explicit encoding

`load_db()` and `flush_db()` open `Weather.json` without `encoding="utf-8"`, making behaviour
platform-dependent on Windows.
