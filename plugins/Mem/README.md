<!-- Reports memory usage and top allocations. -->

# Mem: Provides memory usage and allocation statistics

<!-- README_HEADER:start -->
[![Tests][tests-badge]][tests-link]
[![Lint][lint-badge]][lint-link]
[![CodeQL][codeql-badge]][codeql-link]
![Python][python-badge]
![Black][black-badge]
![Limnoria][limnoria-badge]
<!-- README_HEADER:end -->

Mem is a plugin for Limnoria that provides insights into memory usage and allocation patterns. It allows users to monitor the memory consumption of the bot and identify potential memory leaks or inefficient memory usage.

## Features

- Display current memory usage of the bot.
- Show top memory allocations to help identify which parts of the code are consuming the most memory.
- Provide detailed statistics on memory usage for debugging and optimization purposes.

## Installation

Navigate to your Limnoria plugin directory (usually ~/runbot/plugins) and clone the repository:

`git clone https://github.com/Alcheri/Mem.git`

Install the plugin’s dependencies:

`pip install --upgrade -r requirements.txt`

Load the plugin into your bot:

`/msg yourbot load Mem`

## Usage

Once the plugin is installed and loaded, you can use the following commands to interact with it:

- `!mem usage`: Displays the current memory usage of the bot.
- `!mem top`: Shows the top memory allocations.
- `!mem stats`: Provides detailed statistics on memory usage.

## Contributing

Contributions to the Mem plugin are welcome! If you have suggestions for improvements or want to report a bug, please open an issue or submit a pull request on the GitHub repository.

## License

This project is licensed under the BSD 3-Clause License. See the [LICENCE](LICENCE.md) file for details.

<!-- Badge reference definitions -->
[tests-badge]: https://github.com/Alcheri/Mem/actions/workflows/tests.yml/badge.svg
[tests-link]: https://github.com/Alcheri/Mem/actions/workflows/tests.yml

[lint-badge]: https://github.com/Alcheri/Mem/actions/workflows/lint.yml/badge.svg
[lint-link]: https://github.com/Alcheri/Mem/actions/workflows/lint.yml

[codeql-badge]: https://github.com/Alcheri/Mem/actions/workflows/codeql.yml/badge.svg
[codeql-link]: https://github.com/Alcheri/Mem/security/code-scanning

[python-badge]: https://img.shields.io/badge/python-3.11.2-blue.svg
[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[limnoria-badge]: https://img.shields.io/badge/limnoria-compatible-brightgreen.svg
