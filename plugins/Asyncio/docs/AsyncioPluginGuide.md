<p align="center">
  <img src="../docs/images/puss-logo.svg" width="220" alt="Puss logo">
</p>

<h1 align="center">Asyncio Plugin</h1>

<p align="center">
  <em>Asynchronous AI Chat for Limnoria IRC</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.1-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.9%2B-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/limnoria-compatible-brightgreen.svg" alt="Limnoria">
  <img src="https://img.shields.io/badge/OpenAI-powered-8A2BE2.svg" alt="OpenAI">
  <img src="https://img.shields.io/badge/license-AGPLv3-green.svg" alt="Licence">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/async-safe-success.svg">
  <img src="https://img.shields.io/badge/context-isolated-success.svg">
  <img src="https://img.shields.io/badge/production-ready-blue.svg">
</p>

<hr style="width:65%; margin:auto;">

<p align="center">
Asyncio is a production-ready AI chat plugin for Limnoria IRC bots.  
It provides natural conversation with OpenAI models while ensuring  
safe multi-user behaviour, isolated memory, and stable long-running operation.
</p>

<hr style="width:65%; margin:auto;">

**Bot Name:** Puss  
**Plugin:** Asyncio — Asynchronous AI Chat for Limnoria IRC  
**Author:** Barry Suridge  
**Version:** 1.1  
**Date:** 2026-02-26

---

## 📖 Table of Contents

1. Commands Cheat Sheet  
2. Conversation Memory  
3. Plugin Configuration  
4. Best Practices  
5. Optional Tips  
6. Operator Notes  
7. Exporting to PDF  

---

# 1️⃣ Commands Cheat Sheet

| Command | Example Usage | Description |
|---------|---------------|-------------|
| 🗨️ **`!chat <message>`** | `!chat What is the acceleration due to gravity on Earth?` | Sends your message to the AI assistant. Moderation, cooldowns, and token limits apply automatically. |
| 🧹 **`!reset`** | `!reset` | Clears your conversation memory for the current channel or private message only. |

💡 **Tip:** Each channel and private message keeps its own conversation context.

---

# 2️⃣ Conversation Memory

The plugin maintains conversation history per **user AND channel**.

This ensures:

• Conversations in different channels stay separate  
• Private messages are treated as their own context  
• Users do not share memory with each other  
• History auto-trims to prevent growth  

### Example

In `#test`:
!chat Remember my favourite colour is blue
!chat What is my favourite colour?

Bot remembers.

In another channel:
!chat What is my favourite colour?

Bot does **not** remember.

---

# 3️⃣ Plugin Configuration (`@config`)

| Setting | Example | Description |
|---------|--------|-------------|
| 🔢 **`maxUserTokens`** | `@config plugins.Asyncio.maxUserTokens 2048` | Maximum tokens allowed per user input. |
| ⏱ **`cooldownSeconds`** | `@config plugins.Asyncio.cooldownSeconds 5` | Minimum delay between messages per user & channel. |
| 🐞 **`debugMode`** | `@config plugins.Asyncio.debugMode True` | Enables detailed logging for troubleshooting. |
| 🤖 **`botnick`** | `@config plugins.Asyncio.botnick Puss` | Bot name used in responses. |
| 🌐 **`language`** | `@config plugins.Asyncio.language British` | English style preference for AI responses. |

---

# 4️⃣ Best Practices

### ✅ Keep Messages Reasonably Concise

- Stay under `maxUserTokens`.
- Split very long content into multiple messages.

### ✅ Moderation-Friendly Input

- Avoid offensive, illegal, or harmful content.
- If a message is flagged, rephrase it.

### ✅ Understand Cooldowns

- Cooldowns apply per user AND per channel.
- Other users are unaffected.
- Other channels are unaffected.
- Private messages have their own cooldown.

### ✅ Reset When Needed

- Use `!reset` to start a fresh conversation.
- Only resets the current channel or PM.

### ✅ Debugging & Troubleshooting

- Enable `debugMode` for full logs.
- Check Limnoria logs if AI stops responding.

### ✅ Personalisation

- Adjust `botnick` and `language` to change style.

---

# 5️⃣ Optional Tips

- Encourage users to ask clear, structured questions.
- Avoid sending many queries rapidly (may hit API limits).
- Keep dependencies (`openai`, `dotenv`, etc.) updated.
- Restarting Limnoria clears all conversation memory.

---

# 6️⃣ Operator Notes

This plugin is designed for production IRC use.

It includes:

• Async-safe execution (non-blocking bot behaviour)  
• Built-in moderation filtering  
• Token length protection  
• Per-user + per-channel memory isolation  
• Automatic history trimming  
• Safe cooldown enforcement  

The design prevents:

• Cross-channel memory leakage  
• One user affecting another’s context  
• Excessive API usage  
• Runaway memory growth  

Optional future upgrades include:

• Persistent memory to disk  
• Admin control commands  
• Usage statistics  
• Channel enable/disable toggles  

---

# 7️⃣ Exporting to PDF

⚡ **Quick Command (Pandoc)**

```bash

pandoc AsyncioPluginGuide.md -o AsyncioPluginGuide.pdf \
    --pdf-engine=xelatex \
    -V geometry:margin=1in

© License

Copyright © MMXXIV Barry Suridge
All rights reserved.
