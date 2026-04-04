# Limnoria plugin for WorldTime

Retrieve current time and time zone information for various locations.

Forked from [reticulatingspline/WorldTime](https://github.com/reticulatingspline/WorldTime).

## Install

Go into your Limnoria plugin dir, usually ~/runbot/plugins and run:

```plaintext
gh repo clone Alcheri/WorldTime
```

To install additional requirements, run from /plugins/WorldTime folder:

```plaintext
pip install --upgrade -r requirements.txt 
```

Next, load the plugin:

```plaintext
/msg bot load WorldTime
```

Enable Google [Geocoding](https://console.cloud.google.com/apis/library/geocoding-backend.googleapis.com) and [Time Zone](https://console.cloud.google.com/apis/library/timezone-backend.googleapis.com) APIs. Set your [API Key](https://console.cloud.google.com/apis/credentials) using the command below

* **_config plugins.worldtime.mapsapikey <your_key_here_**

## Example Usage
<!-- LaTeX text formatting (colour) -->
\<spline\> @worldtime New York, NY\
\<myybot\> ${\texttt{New York, NY, USA}}$ :: Current local time is: Sat, 09:38 (Eastern Daylight Time)

\<spline\> @worldtime 90210\
\<myybot\> ${\texttt{Beverly Hills, CA 90210, USA}}$ :: Current local time is: Sat, 06:38 (Pacific Daylight Time)

* **_aka add \<new alias\> worldtime $*_**

    Add an alias to your bot for ease of use.

```plaintext
@wt set [location] -- Sets your current ident@host to [location]

@wt unset -- Removes your current ident@host
```

## Licensing

This project contains code originally published under the MIT Licence by the
upstream author. The original licence text is preserved verbatim in
`LICENSE.txt` as required by the MIT Licence.

All modifications, additions, and ongoing maintenance performed by Barry
Suridge are licensed under the terms described in `LICENCE.md`.

In summary:

- `LICENSE.txt` — original upstream MIT Licence (unchanged)
- `LICENCE.md` — licence applying to Barry Suridge’s contributions
