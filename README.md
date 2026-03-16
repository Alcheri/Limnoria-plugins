<h1 align="center">MyDNS</h1>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9%2B-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/limnoria-compatible-brightgreen.svg" alt="Limnoria">
  <img src="https://img.shields.io/badge/License-BSD_3--Clause-blue.svg" alt="License">
</p>

<p align="center">
  Alternative DNS lookup plugin for Limnoria with GeoIP enrichment.
</p>

## Features

* Resolves hostnames, URLs, nick hostmasks, IPv4, and IPv6.
* Performs reverse DNS for IP addresses.
* Uses multiple GeoIP providers and selects the most complete result.
* Prefers globally-routable addresses when multiple DNS answers are available.
* Displays country flags using Unicode emoji derived from country code.

## Installation

From your Limnoria plugins directory (for example, ~/runbot/plugins):

```bash
git clone https://github.com/Alcheri/MyDNS.git
```

Install dependencies from the plugin directory:

```bash
pip install --upgrade -r requirements.txt
```

If needed, unload the built-in Internet plugin to avoid command overlap:

```text
/msg yourbot unload Internet
```

Load the plugin:

```text
/msg yourbot load MyDNS
```

## Configuration

Optional API key (recommended for better provider coverage):

```text
config plugins.MyDNS.ipstackAPI your_api_key_here
```

Provider order (comma-separated). Default:

```text
config plugins.MyDNS.geoipProviderOrder ipstack,ipapi,ip-api
```

Example with free providers first:

```text
config plugins.MyDNS.geoipProviderOrder ipapi,ip-api,ipstack
```

Enable per channel:

```text
config channel #channel plugins.MyDNS.enable True
```

Disable per channel:

```text
config channel #channel plugins.MyDNS.enable False
```

## Usage

```text
@dns <hostname | URL | nick | IPv4 | IPv6>
```

## Example

```text
<Barry> @dns example.com
<Borg> DNS: example.com resolves to [93.184.216.34] LOC: City: Los Angeles State: California Long: -118.2437 Lat: 34.0522 Country Code: US Country: United States 🇺🇸 Post/Zip Code: 90012

<Barry> @dns 203.7.22.140
<Borg> DNS: <203-7-22-140> [203-7-22-140.dyn.iinet.net.au <> 203.7.22.140] LOC: City: Ballarat State: Victoria Long: 143.8470 Lat: -37.5633 Country Code: AU Country: Australia 🇦🇺 Post/Zip Code: 3350
```

## Accuracy Notes

* GeoIP is approximate and may differ from the host's physical location.
* Private, loopback, link-local, and unroutable IPs cannot be geolocated reliably.
* Best quality usually comes from globally-routable public IP addresses.
* Results can vary between providers and over time.
* Provider order is configurable with plugins.MyDNS.geoipProviderOrder.
* Some IRC clients may not render flag emoji; country code is still shown.

## Troubleshooting

If lookups fail or seem inaccurate:

1. Confirm the plugin is loaded.

```text
/msg yourbot list MyDNS
```

1. Confirm the plugin is enabled in the current channel.

```text
config channel #channel plugins.MyDNS.enable
```

1. Reload after changes.

```text
/msg yourbot reload MyDNS
```

1. Add or verify your ipstack API key.

```text
config plugins.MyDNS.ipstackAPI your_api_key_here
```

Copyright © MMXXVI, Barry Suridge


