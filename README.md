# Wikipedia

![Python versions](https://img.shields.io/badge/Python-version-blue) ![Supported Python versions](https://img.shields.io/badge/3.10%2C%203.11%2C%203.12%2C%203.13-blue.svg) ![Build Status](./local/status.svg) ![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg) [![CodeQL](https://github.com/Alcheri/Wikipedia/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/Alcheri/Wikipedia/actions/workflows/github-code-scanning/codeql)

## Introduction

This is a Limnoria plugin to query and search Wikipedia.

## Install

Go into your Limnoria plugin dir, usually ~/runbot/plugins and run:

```plaintext
git clone https://github.com/Alcheri/Wikipedia.git
```

To install additional requirements, run from plugins/Wikipedia:

```plaintext
pip install --upgrade -r requirements.txt 
```

Next, load the plugin:

```plaintext
/msg bot load Wikipedia
```

## Configuring

* **_config channel #channel plugins.Wikipedia.enabled True or False (On or Off)_**

## Example Usage

```plaintext
<Barry> @wiki monty python
<Borg> Monty Python (also collectively known as the Pythons)[2][3] were a British comedy troupe formed in 1969 consisting of Graham Chapman, John Cleese, Terry Gilliam, Eric Idle, Terry Jones, and Michael Palin.
```

**_Inspired by: [andrewtryder/Wikipedia](https://github.com/andrewtryder/Wikipedia)_**
