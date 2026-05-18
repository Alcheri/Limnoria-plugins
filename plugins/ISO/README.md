<!-- Convert alpha2 country codes to country name and vice versa. -->

<h1 align="center">ISO Plugin</h1>

<!-- README_HEADER:start -->
[![Tests][tests-badge]][tests-link]
[![Lint][lint-badge]][lint-link]
[![CodeQL][codeql-badge]][codeql-link]
![Python][python-badge]
![Black][black-badge]
![Limnoria][limnoria-badge]
<!-- README_HEADER:end -->


<p align="center">
    <em>Convert alpha2 country codes to country name and vice versa.</em>
</p>

## Install

Download ISO to the plugin dir, usually ~/runbot/plugins:

```plaintext
git clone https://github.com/Alcheri/ISO.git
```

To install additional requirements, run from /plugins/ISO folder:

```plaintext
pip install --upgrade -r requirements.txt 
```

Next, load the plugin:

```plaintext
/msg bot load ISO
```

## Setting up

**_None_**

## Using

```plaintext
<Barry> @country myanmar
<Borg>  MM Myanmar

<Barry> @country tr
<Borg>  TR Türkiye
```

<br/><br/>
<p align="center">Copyright © MMXXIV, Barry Suridge</p>

<!-- Badge reference definitions -->
[tests-badge]: https://github.com/Alcheri/ISO/actions/workflows/tests.yml/badge.svg
[tests-link]: https://github.com/Alcheri/ISO/actions/workflows/tests.yml

[lint-badge]: https://github.com/Alcheri/ISO/actions/workflows/lint.yml/badge.svg
[lint-link]: https://github.com/Alcheri/ISO/actions/workflows/lint.yml

[codeql-badge]: https://github.com/Alcheri/ISO/actions/workflows/codeql.yml/badge.svg
[codeql-link]: https://github.com/Alcheri/ISO/security/code-scanning

[python-badge]: https://img.shields.io/badge/python-3.9%2B-blue.svg
[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[limnoria-badge]: https://img.shields.io/badge/limnoria-compatible-brightgreen.svg
