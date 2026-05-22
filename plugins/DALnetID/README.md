<!-- DALnetID plugin for Limnoria -->

## DALnetID for Limnoria

<!-- README_HEADER:start -->
[![Tests][tests-badge]][tests-link]
[![Lint][lint-badge]][lint-link]
[![CodeQL][codeql-badge]][codeql-link]
![Python][python-badge]
![Black][black-badge]
![Limnoria][limnoria-badge]
<!-- README_HEADER:end -->

<em>DALnetID identifies your bot to DALnet's NickServ.</em>

See [docs/TODO.md](docs/TODO.md) for small future expansion ideas.

``/msg <yourbot> config plugins.DALnetID.nickservPassword [BotNickServPassword]``

``/msg <yourbot> config plugins.DALnetID.allowedNetworks DALnet``

``@id``

```plaintext
@Barry @id
@Borg Barry: Identifying to NickServ...
@Borg Barry: The operation succeeded.
```

<!-- Badge reference definitions -->
[tests-badge]: https://github.com/Alcheri/DALnetID/actions/workflows/tests.yml/badge.svg
[tests-link]: https://github.com/Alcheri/DALnetID/actions/workflows/tests.yml

[lint-badge]: https://github.com/Alcheri/DALnetID/actions/workflows/lint.yml/badge.svg
[lint-link]: https://github.com/Alcheri/DALnetID/actions/workflows/lint.yml

[codeql-badge]: https://github.com/Alcheri/DALnetID/actions/workflows/codeql.yml/badge.svg
[codeql-link]: https://github.com/Alcheri/DALnetID/security/code-scanning

[python-badge]: https://img.shields.io/badge/python-3.11.2-blue.svg
[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[limnoria-badge]: https://img.shields.io/badge/limnoria-compatible-brightgreen.svg
