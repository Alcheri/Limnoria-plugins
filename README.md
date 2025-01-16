# Limnoria plugin for WorldTime

Retrieve current time and time zone information for various locations.

Forked from https://github.com/reticulatingspline/WorldTime

## Install

Go into your Limnoria plugin dir, usually ~/runbot/plugins and run:

```plaintext
https://github.com/Alcheri/WorldTime.git
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

![Python versions](https://img.shields.io/badge/Python-version-blue) ![Supported Python versions](https://img.shields.io/badge/3.11%2C%203.12%2C%203.13-blue.svg) [![Code style: black](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black) ![Build Status](https://github.com/Alcheri/My-Limnoria-Plugins/blob/master/img/status.svg) ![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg) [![CodeQL](https://github.com/Alcheri/Weather/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/Alcheri/Weather/actions/workflows/github-code-scanning/codeql) [![Lint](https://github.com/Alcheri/Weather/actions/workflows/black.yml/badge.svg)](https://github.com/Alcheri/Weather/actions/workflows/black.yml)
