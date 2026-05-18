<!-- Returns the ping result of <hostname | ip or IPv6> using Python's shlex library. -->

<h1 align="center">An alternative to Limnorias' PING function </h1>

<!-- README_HEADER:start -->
[![Tests][tests-badge]][tests-link]
[![Lint][lint-badge]][lint-link]
[![CodeQL][codeql-badge]][codeql-link]
![Python][python-badge]
![Black][black-badge]
![Limnoria][limnoria-badge]
<!-- README_HEADER:end -->

<p align="center">
    <em>
        Returns the ping result of <hostname | ip or IPv6> using Python's shlex library.
    </em>
</p>

# Install

Download the plugin:

```plaintext
git clone https://github.com/Alcheri/MyPing.git
```

Next, load the plugin:

```plaintext
/msg bot load MyPing
```

# Configuring

* **_config channel #channel plugins.MyPing.enable True or False (On or Off_**

# Setting up

To stop conflict with Limnorias' core 'ping' function do the following:

\<Barry\> defaultplugin --remove ping Misc\
\<Borg\> defaultplugin ping MyPing

# Using
<!-- LaTeX text formatting (colour) -->
\<Barry\> @ping Mini-Me\
\<Borg\>  ${\texttt{\color{red}its.all.good.in.bazzas.club}}$ is Reachable ~ Time elapsed: ${\texttt{\color{teal}(0.0, 0.0)}}$ seconds/milliseconds Packet Loss: ${\texttt{\color{teal}0\%}}$

\<Barry\> @ping 167.88.114.11\
\<Borg\>  ${\texttt{\color{red}167.88.114.11}}$ is Reachable ~ Time elapsed: ${\texttt{\color{teal}(0.0, 362.0)}}$ seconds/milliseconds Packet Loss: ${\texttt{\color{teal}0\%}}$

\<Barry\> @ping 2a01:4f9:c011:33a2::20\
\<Borg\>  ${\texttt{\color{red}2a01:4f9:c011:33a2::20}}$ is Reachable ~ Time elapsed: ${\texttt{\color{teal}(0.0, 167.0)}}$ seconds/milliseconds Packet Loss: ${\texttt{\color{teal}0\%}}$

<br><br>
<p align="center">Copyright © 2020 - 2026, Barry Suridge</p>

<!-- Badge reference definitions -->
[tests-badge]: https://github.com/Alcheri/MyPing/actions/workflows/tests.yml/badge.svg
[tests-link]: https://github.com/Alcheri/MyPing/actions/workflows/tests.yml

[lint-badge]: https://github.com/Alcheri/MyPing/actions/workflows/lint.yml/badge.svg
[lint-link]: https://github.com/Alcheri/MyPing/actions/workflows/lint.yml

[codeql-badge]: https://github.com/Alcheri/MyPing/actions/workflows/codeql.yml/badge.svg
[codeql-link]: https://github.com/Alcheri/MyPing/security/code-scanning

[python-badge]: https://img.shields.io/badge/python-3.9%2B-blue.svg
[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[limnoria-badge]: https://img.shields.io/badge/limnoria-compatible-brightgreen.svg
