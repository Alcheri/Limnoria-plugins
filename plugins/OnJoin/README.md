<!-- OnJoin - Send a random (humorous) notice to a user entering an IRC channel. -->

# OnJoin

<!-- README_HEADER:start -->
[![Tests][tests-badge]][tests-link]
[![Lint][lint-badge]][lint-link]
[![CodeQL][codeql-badge]][codeql-link]
![Python][python-badge]
![Black][black-badge]
![Limnoria][limnoria-badge]
<!-- README_HEADER:end -->

Send a random (humorous) notice to a user entering an IRC channel.

## Configuring

* Enable in channel(s):

* `config channel #channel plugins.onjoin.enable True or False` (On or Off)
* `config plugins.onjoin.maxQuotes 1000` to retain at most the newest stored quotes
* `config plugins.onjoin.maxRecentQuotes 10` to cap how many quotes `recentquotes` may show

## Installation

From your Limnoria plugins directory (for example, ~/runbot/plugins):

`git clone https://github.com/Alcheri/OnJoin.git`

Load the plugin:

`/msg yourbot load OnJoin`

## Admin commands

- `addquote <text>` appends a quote to the shared quotes file. This requires the bot `admin` capability.
- `recentquotes [count]` shows the newest stored quotes, up to the configured maximum, with quote numbers you can use for deletion. This also requires the bot `admin` capability.
- `delquote <quote_number>` deletes a stored quote by its `recentquotes` number. This also requires the bot `admin` capability.

## Python Source Header Policy

- In Python 3 files, do not add `# -*- coding: utf-8 -*-` unless a non-default source encoding is required.
- Use `#!/usr/bin/env python3` only for executable scripts, not import-only modules.

<!-- Badge reference definitions -->
[tests-badge]: https://github.com/Alcheri/OnJoin/actions/workflows/tests.yml/badge.svg
[tests-link]: https://github.com/Alcheri/OnJoin/actions/workflows/tests.yml

[lint-badge]: https://github.com/Alcheri/OnJoin/actions/workflows/lint.yml/badge.svg
[lint-link]: https://github.com/Alcheri/OnJoin/actions/workflows/lint.yml

[codeql-badge]: https://github.com/Alcheri/OnJoin/actions/workflows/codeql.yml/badge.svg
[codeql-link]: https://github.com/Alcheri/OnJoin/security/code-scanning

[python-badge]: https://img.shields.io/badge/python-3.11.2-blue.svg
[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[limnoria-badge]: https://img.shields.io/badge/limnoria-compatible-brightgreen.svg
