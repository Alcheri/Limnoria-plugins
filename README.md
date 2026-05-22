<!-- Retrieve current time and time zone information for various locations. -->

# Limnoria plugin for WorldTime

<!-- README_HEADER:start -->
[![Tests][tests-badge]][tests-link]
[![Lint][lint-badge]][lint-link]
[![CodeQL][codeql-badge]][codeql-link]
![Python][python-badge]
![Black][black-badge]
![Limnoria][limnoria-badge]
<!-- README_HEADER:end -->

Retrieve current time and time zone information for various locations.

Forked from [reticulatingspline/WorldTime](https://github.com/reticulatingspline/WorldTime).

## Install

Go into your Limnoria plugin dir, usually ~/runbot/plugins and run:

GitHub CLI: `gh repo clone Alcheri/WorldTime` or SSH: `git clone git@github.com:Alcheri/WorldTime.git`

To install additional requirements, run from /plugins/WorldTime folder:

`pip install --upgrade -r requirements.txt`

Next, load the plugin:

`/msg bot load WorldTime`

Enable Google [Geocoding](https://console.cloud.google.com/apis/library/geocoding-backend.googleapis.com) and [Time Zone](https://console.cloud.google.com/apis/library/timezone-backend.googleapis.com) APIs. Set your [API Key](https://console.cloud.google.com/apis/credentials) using the command below

* **_config plugins.worldtime.mapsapikey <your_key_here_**

* **_config channel #channel plugins.WorldTime.cooldownSeconds 5_**

    Sets the per-user `worldtime` lookup cooldown for the channel.

* **_config plugins.WorldTime.maxResponseBytes 262144_**

    Sets the maximum Google API response size WorldTime will read.

Security notes:

* `--nick` lookups are public and use locations that users have stored with
  `set`.
* Stored locations and direct lookup locations are capped and sanitised before
  use.
* Replies preserve intentional IRC formatting while stripping unsafe control
  characters.

## Example Usage

```plaintext
<spline> @worldtime New York, NY
<myybot> New York, NY, USA :: Current local time is: Sat, 09:38 (Eastern Daylight Time)
<spline> @worldtime 90210
<myybot> Beverly Hills, CA 90210, USA :: Current local time is: Sat, 06:38 (Pacific Daylight Time)
```

Add an alias to your bot for ease of use.

`aka add [--channel <#channel>] <name> <command>`

`@wt set [location] -- Sets your current ident@host to [location]`

`@wt unset -- Removes your current ident@host`

## Licensing

This project contains code originally published under the MIT Licence by the
upstream author. The original licence text is preserved verbatim in
`LICENSE.txt` as required by the MIT Licence.

All modifications, additions, and ongoing maintenance performed by Barry
Suridge are licensed under the terms described in `LICENCE.md`.

In summary:

- `LICENSE.txt` — original upstream MIT Licence (unchanged)
- `LICENCE.md` — licence applying to Barry Suridge’s contributions

<!-- Badge reference definitions -->
[tests-badge]: https://github.com/Alcheri/WorldTime/actions/workflows/tests.yml/badge.svg
[tests-link]: https://github.com/Alcheri/WorldTime/actions/workflows/tests.yml

[lint-badge]: https://github.com/Alcheri/WorldTime/actions/workflows/lint.yml/badge.svg
[lint-link]: https://github.com/Alcheri/WorldTime/actions/workflows/lint.yml

[codeql-badge]: https://github.com/Alcheri/WorldTime/actions/workflows/codeql.yml/badge.svg
[codeql-link]: https://github.com/Alcheri/WorldTime/security/code-scanning

[python-badge]: https://img.shields.io/badge/python-3.11.2-blue.svg
[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[limnoria-badge]: https://img.shields.io/badge/limnoria-compatible-brightgreen.svg
