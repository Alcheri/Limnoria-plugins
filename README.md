<!-- OnJoin - Send a random (humorous) notice to a user entering an IRC channel. -->

# OnJoin

[![Tests](https://github.com/Alcheri/WorldTime/actions/workflows/tests.yml/badge.svg?branch=Limnoria-WorldTime)](https://github.com/Alcheri/WorldTime/actions/workflows/tests.yml)
[![Lint](https://github.com/Alcheri/WorldTime/actions/workflows/lint.yml/badge.svg?branch=Limnoria-WorldTime)](https://github.com/Alcheri/WorldTime/actions/workflows/lint.yml)
[![CodeQL](https://github.com/Alcheri/WorldTime/actions/workflows/codeql.yml/badge.svg?branch=Limnoria-WorldTime)](https://github.com/Alcheri/WorldTime/actions/workflows/codeql.yml)

Send a random (humorous) notice to a user entering an IRC channel.

## Configuring

* Enable in channel(s):

* `config channel #channel plugins.onjoin.enable True or False` (On or Off)
* `config plugins.onjoin.maxQuotes 1000` to retain at most the newest stored quotes
* `config plugins.onjoin.maxRecentQuotes 10` to cap how many quotes `recentquotes` may show

## Setting up

** No setting up required.

## Admin commands

- `addquote <text>` appends a quote to the shared quotes file. This requires the bot `admin` capability.
- `recentquotes [count]` shows the newest stored quotes, up to the configured maximum, with quote numbers you can use for deletion. This also requires the bot `admin` capability.
- `delquote <quote_number>` deletes a stored quote by its `recentquotes` number. This also requires the bot `admin` capability.

## Python Source Header Policy

- In Python 3 files, do not add `# -*- coding: utf-8 -*-` unless a non-default source encoding is required.
- Use `#!/usr/bin/env python3` only for executable scripts, not import-only modules.
