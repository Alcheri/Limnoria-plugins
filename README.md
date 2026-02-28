<!-- README Header -->
<p align="center">
  <img src="docs/images/puss-logo.svg" width="220" alt="Puss logo">
</p>

<h1 align="center">Asyncio Plugin (ChatGPT)</h1>

<p align="center">
  <em>Asynchronous AI Chat for Limnoria IRC</em>
</p>

<p align="center">
  <a href="https://github.com/Alcheri/Asyncio/releases/latest">
    <img src="https://img.shields.io/github/v/release/Alcheri/Asyncio?sort=semver" alt="Latest Release">
  </a>
  <img src="https://img.shields.io/badge/python-3.9%2B-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/limnoria-compatible-brightgreen.svg" alt="Limnoria">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
</p>

<p align="center">
  <a href="https://github.com/Alcheri/Asyncio/releases/latest">
    <img src="https://img.shields.io/badge/Download-Latest%20Release-brightgreen?style=for-the-badge" alt="Download Latest Release">
  </a>
</p>

<hr style="width:65%; margin:auto;">

<p align="center">
  Asyncio is a production-ready AI chat plugin for Limnoria IRC bots.<br>
  It provides safe multi-user behaviour with per-channel memory isolation,<br>
  moderation, cooldowns, and a math mode that answers in ≤ 6 lines.
</p>

<div align="center">

[Manual](docs/AsyncioPluginGuide.md) •
[Roadmap](docs/ROADMAP.md) •
[Changelog](CHANGELOG.md) •
[Developer Notes](DEVELOPER_NOTES.md) •
[Architecture](docs/architecture.md)

</div>

<hr style="width:65%; margin:auto;">

## Overview

Asyncio brings modern asynchronous AI chat to Limnoria. It supports natural conversation, math queries, multi-user concurrency, and safe behaviour across channels. The plugin is designed for reliability, clarity, and minimal configuration.

## Prerequisites

Before installing, ensure you have:

- A valid OpenAI account — [OpenAI Platform]( https://platform.openai.com)
- A newly generated API key
- Awareness of OpenAI pricing and usage terms
- A `.env` file in your bot’s root directory (`~/runbot`) containing:

```plaintext
OPENAI_API_KEY="your_api_key_here"
```
Python requirements:

* `Python 3.9+`
* `asyncio`
* `openai`
* `python-dotenv`

# Installation

Navigate to your Limnoria plugin directory (usually ~/runbot/plugins) and clone the repository:

`git clone https://github.com/Alcheri/Asyncio.git`

Install the plugin’s dependencies:

`pip install --upgrade -r requirements.txt`

Load the plugin into your bot:

`/msg yourbot load Asyncio`

Configuration

The plugin exposes several settings through Limnoria’s configuration system:

* `supybot.plugins.Asyncio.botnick` — the bot’s speaking name\
_Default_: "Assistant"

* `supybot.plugins.Asyncio.language` — response dialect\
_Options_: American, Australian, British, Canadian\
_Default_: British

Usage Examples

```plaintext
@chat good morning
Puss Good morning, SomeNick! How can I help you today?

@chat Tell me a joke
Puss Processing your message...
Puss Sure thing! Why did the kangaroo cross the road?
Puss Because it was the chicken’s day off! 🦘😄

@chat What is 3 ** 3?
Puss Processing your message...
Puss 3 ** 3 means 3 raised to the power of 3.
Puss 3 * 3 * 3 = 27
Puss Final answer: 27
```

Solving word problems

```plaintext
@chat A farm has chickens and cows. There are 50 heads and 130 legs. How many of each?

Puss Processing your message...
Puss Let the number of chickens be C and cows be W.
Puss C + W = 50
Puss 2C + 4W = 130
Puss Solving gives C = 35 and W = 15.
Puss Final answer: 35 chickens and 15 cows.
```

The plugin handles arithmetic, algebra, and natural-language math queries, always returning concise, readable answers.

Notes

* `asyncio` provides the asynchronous event loop used for concurrent chat handling.
* `openai` is the official Python client for the OpenAI API.
* `python-dotenv` securely loads environment variables from `.env`.

<br><br>

<p align="center">Copyright © MMXXVI, Barry Suridge</p>
