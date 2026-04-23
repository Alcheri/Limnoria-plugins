<!-- Access Limnoria's messages.log -->

# Messages.log plugin for Limnoria

Reads the tail of `~/runbot/logs/messages.log` (configurable) with:

- `messageslog tail`
- `messageslog tail 50`

Config keys:

- `supybot.plugins.MessagesLog.logFilePath` (default: `~/runbot/logs/messages.log`)
- `supybot.plugins.MessagesLog.lineCount` (default: `20`)
- `supybot.plugins.MessagesLog.maxLineCount` (default: `100`)
