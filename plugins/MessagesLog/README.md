<!-- Access Limnoria's messages.log -->

# Messages.log plugin for Limnoria

<!-- README_HEADER:start -->
[![Tests][tests-badge]][tests-link]
[![Lint][lint-badge]][lint-link]
[![CodeQL][codeql-badge]][codeql-link]
![Python][python-badge]
![Black][black-badge]
![Limnoria][limnoria-badge]
<!-- README_HEADER:end -->

Reads the tail of `~/runbot/logs/messages.log` (configurable) with:

- `messageslog tail`
- `messageslog tail 50`
- `messageslog truncate`

The commands can be run in-channel by users with the `admin` capability. Log
lines are sent to the requesting user via IRC notice, and the channel receives a
short confirmation message with the number of lines sent. `truncate` clears the
configured log file in place without creating a backup.

Config keys:

- `supybot.plugins.MessagesLog.logFilePath` (default: `~/runbot/logs/messages.log`)
- `supybot.plugins.MessagesLog.lineCount` (default: `20`)
- `supybot.plugins.MessagesLog.maxLineCount` (default: `100`)

<!-- Badge reference definitions -->
[tests-badge]: https://github.com/Alcheri/MessagesLog/actions/workflows/tests.yml/badge.svg
[tests-link]: https://github.com/Alcheri/MessagesLog/actions/workflows/tests.yml

[lint-badge]: https://github.com/Alcheri/MessagesLog/actions/workflows/lint.yml/badge.svg
[lint-link]: https://github.com/Alcheri/MessagesLog/actions/workflows/lint.yml

[codeql-badge]: https://github.com/Alcheri/MessagesLog/actions/workflows/codeql.yml/badge.svg
[codeql-link]: https://github.com/Alcheri/MessagesLog/security/code-scanning

[python-badge]: https://img.shields.io/badge/python-3.11.2-blue.svg
[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[limnoria-badge]: https://img.shields.io/badge/limnoria-compatible-brightgreen.svg
