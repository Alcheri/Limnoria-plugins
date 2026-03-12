<h1 align="center">URLtitle</h1>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9%2B-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/limnoria-compatible-brightgreen.svg" alt="Limnoria">
  <img src="https://img.shields.io/badge/License-BSD_3--Clause-blue.svg" alt="License">
</p>

# Description

A simple plugin that detects URLs in a channel and returns the page title.

## Install

Go into your Limnoria plugin dir, usually ~/runbot/plugins and run:

```plaintext
git clone https://github.com/Alcheri/URLtitle.git
```

To install additional requirements, run from /plugins/URLtitle:

```plaintext
pip install --upgrade -r requirements.txt 
```

Next, load the plugin:

```plaintext
/msg bot load URLtitle
```

## Configuring

* **config channel #channel plugins.URLtitle.enabled True or False (On or Off)**

    Should plugin work in this channel?

* **supybot.plugins.URLtitle.userAgent**

  User-Agent header sent when fetching URLs. Default is a plugin-specific
  Limnoria URLtitle identifier.

<br/><br/>
<p align="center">Copyright © MMXXIV, Barry Suridge</p>
