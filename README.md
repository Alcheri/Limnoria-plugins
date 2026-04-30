<!-- Retrieve current time and time zone information for various locations. -->

# Limnoria plugin for WorldTime

[![Tests](https://github.com/Alcheri/WorldTime/actions/workflows/tests.yml/badge.svg?branch=Limnoria-WorldTime)](https://github.com/Alcheri/WorldTime/actions/workflows/tests.yml)
[![Lint](https://github.com/Alcheri/WorldTime/actions/workflows/lint.yml/badge.svg?branch=Limnoria-WorldTime)](https://github.com/Alcheri/WorldTime/actions/workflows/lint.yml)
[![CodeQL](https://github.com/Alcheri/WorldTime/actions/workflows/codeql.yml/badge.svg?branch=Limnoria-WorldTime)](https://github.com/Alcheri/WorldTime/actions/workflows/codeql.yml)

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
