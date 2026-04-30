<!-- Access Limnoria's messages.log -->

# Messages.log plugin for Limnoria

[![Tests](https://github.com/Alcheri/WorldTime/actions/workflows/tests.yml/badge.svg?branch=Limnoria-WorldTime)](https://github.com/Alcheri/WorldTime/actions/workflows/tests.yml)
[![Lint](https://github.com/Alcheri/WorldTime/actions/workflows/lint.yml/badge.svg?branch=Limnoria-WorldTime)](https://github.com/Alcheri/WorldTime/actions/workflows/lint.yml)
[![CodeQL](https://github.com/Alcheri/WorldTime/actions/workflows/codeql.yml/badge.svg?branch=Limnoria-WorldTime)](https://github.com/Alcheri/WorldTime/actions/workflows/codeql.yml)

Reads the tail of `~/runbot/logs/messages.log` (configurable) with:

- `messageslog tail`
- `messageslog tail 50`

The command can be run in-channel. Log lines are sent to the requesting user
via IRC notice, and the channel receives a short confirmation message with the
number of lines sent.

Config keys:

- `supybot.plugins.MessagesLog.logFilePath` (default: `~/runbot/logs/messages.log`)
- `supybot.plugins.MessagesLog.lineCount` (default: `20`)
- `supybot.plugins.MessagesLog.maxLineCount` (default: `100`)
