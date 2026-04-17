<!-- Google Maps -->

<h1 align="center">Google Maps</h1>

<!-- README_HEADER:start -->
<p align="center">
  <a href="https://github.com/Alcheri/GoogleMaps/actions/workflows/tests.yml">
    <img src="https://github.com/Alcheri/GoogleMaps/actions/workflows/tests.yml/badge.svg" alt="Tests">
  </a>
  <a href="https://github.com/Alcheri/GoogleMaps/actions/workflows/lint.yml">
    <img src="https://github.com/Alcheri/GoogleMaps/actions/workflows/lint.yml/badge.svg" alt="Lint">
  </a>
  <a href="https://github.com/Alcheri/GoogleMaps/security/code-scanning">
    <img src="https://github.com/Alcheri/GoogleMaps/actions/workflows/codeql.yml/badge.svg" alt="CodeQL">
  </a>
  <img src="https://img.shields.io/badge/python-3.9%2B-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black">
  <img src="https://img.shields.io/badge/limnoria-compatible-brightgreen.svg" alt="Limnoria">
  <img src="https://img.shields.io/badge/License-BSD_3--Clause-blue.svg" alt="License">
</p>
<!-- README_HEADER:end -->


## Setting up

* Step 1: Create a [Google Account](https://accounts.google.com)
* Step 2: Generate a New API Key.
* Step 3: Review Pricing and Usage Terms.

**Google** gives each account US$200/month of free credit.

## Install

Go into your Limnoria plugin directory, usually ~/runbot/plugins and run:

```plaintext
git clone https://github.com/Alcheri/GoogleMaps.git
```

To install additional requirements, run from /plugins/GoogleMaps:

```plaintext
pip install --upgrade -r requirements.txt 
```

Next, load the plugin:

```plaintext
/msg bot load GoogleMaps
```

## Configuring

* **_config channel #channel plugins.GoogleMaps.enabled True or False (On or Off)_**
* **_config plugins.GoogleMaps.googlemapsAPI [Your_API_key]_**

## Using

```plaintext
<Barry> @map --address 1275 Grevillea Rd Wendouree VIC
<Borg> Google Maps: 1275 Grevillea Rd, Wendouree VIC 3355, Australia [ID: ChIJcSzC6YxD0WoRWtgRRJh8D2U] -37.5283674 143.8164991 ['premise']

<Barry> @map --reverse -- -37.5283674, 143.8164991
<Borg>  Location: 1275 Grevillea Rd, Wendouree VIC 3355, Australia Coordinates: -37.5283674, 143.8164991 Type: premise Place ID: ChIJcSzC6YxD0WoRWtgRRJh8D2

<Barry> @map --directions Sydney Opera House | Bondi Beach
<Borg>  Route from Bennelong Point, Sydney NSW 2000, Australia to Bondi Beach, NSW 2026, Australia: Distance: 9.1 km, Duration: 17 mins. Directions: https://www.google.com/maps/dir/?api=1&origin=Sydney+Opera+House&destination=Bondi+Beach
```

**Notes:**
>The syntax of the commands are somewhat specific as a result of what is required by Google Maps.\
>Reverse geocoding requires two minus signs (--) (when using negative latitudes) and a comma to separate latitude from longitude.\
>Directions requires a pipe (|) to separate departure point from destination.  
<br>

<p align="center">Copyright © MMXXIV, Barry Suridge</p>

## Python Source Header Policy

- In Python 3 files, do not add `# -*- coding: utf-8 -*-` unless a non-default source encoding is required.
- Use `#!/usr/bin/env python3` only for executable scripts, not import-only modules.
