<!-- This is a straightforward (simple) English Dictionary plugin for Limnoria. -->

<h1 align="center"> Dictionary </h1>

<!-- README_HEADER:start -->
[![Tests][tests-badge]][tests-link]
[![Lint][lint-badge]][lint-link]
[![CodeQL][codeql-badge]][codeql-link]
![Python][python-badge]
![Black][black-badge]
![Limnoria][limnoria-badge]
<!-- README_HEADER:end -->

<p align="center">
  <em>This is a straightforward (simple) English Dictionary plugin for Limnoria.</em>
</p>

## Installation

Navigate to your Limnoria plugin directory (usually ~/runbot/plugins) and clone the repository:

`git clone https://github.com/Alcheri/Dictionary.git`

Load the plugin into your bot:

`/msg yourbot load dictionary`

## Usage

>\<Barry\> @dict antidisestablishmentarianism
>
>\<Borg\> antidisestablishmentarianism (noun): A political philosophy opposed to the separation of a religious group (church) and a government (state), especially the belief held by those in 19th century England opposed to separating the Anglican church from the civil government or to refer to separation of church and state.
>

**Note:**

If Limnoria's Dict module is loaded then, unload it: `@unload dict`
<br/><br/>
<p align="center">Copyright © 2024 - 2026, Barry Suridge</p>

<!-- Badge reference definitions -->
[tests-badge]: https://github.com/Alcheri/Dictionary/actions/workflows/tests.yml/badge.svg
[tests-link]: https://github.com/Alcheri/Dictionary/actions/workflows/tests.yml

[lint-badge]: https://github.com/Alcheri/Dictionary/actions/workflows/lint.yml/badge.svg
[lint-link]: https://github.com/Alcheri/Dictionary/actions/workflows/lint.yml

[codeql-badge]: https://github.com/Alcheri/Dictionary/actions/workflows/codeql.yml/badge.svg
[codeql-link]: https://github.com/Alcheri/Dictionary/security/code-scanning

[python-badge]: https://img.shields.io/badge/python-3.9%2B-blue.svg
[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[limnoria-badge]: https://img.shields.io/badge/limnoria-compatible-brightgreen.svg
