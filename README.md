# URLtitle

![Python versions](https://img.shields.io/badge/Python-version-blue) ![Supported Python versions](https://img.shields.io/badge/3.9%2C%203.10%2C%203.11%2C%203.12%2C%203.13-blue.svg) [![Code style: black](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black) ![Build Status](https://github.com/Alcheri/My-Limnoria-Plugins/blob/master/img/status.svg) ![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg) [![CodeQL](https://github.com/Alcheri/Weather/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/Alcheri/Weather/actions/workflows/github-code-scanning/codeql) [![Lint](https://github.com/Alcheri/Weather/actions/workflows/black.yml/badge.svg)](https://github.com/Alcheri/Weather/actions/workflows/black.yml)

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

<br/><br/>
<p align="center">Copyright © MMXXIV, Barry Suridge</p>
