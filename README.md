<!-- Reports memory usage and top allocations. -->

# Mem: Provides memory usage and allocation statistics

[![Tests](https://github.com/Alcheri/WorldTime/actions/workflows/tests.yml/badge.svg?branch=Limnoria-WorldTime)](https://github.com/Alcheri/WorldTime/actions/workflows/tests.yml)
[![Lint](https://github.com/Alcheri/WorldTime/actions/workflows/lint.yml/badge.svg?branch=Limnoria-WorldTime)](https://github.com/Alcheri/WorldTime/actions/workflows/lint.yml)
[![CodeQL](https://github.com/Alcheri/WorldTime/actions/workflows/codeql.yml/badge.svg?branch=Limnoria-WorldTime)](https://github.com/Alcheri/WorldTime/actions/workflows/codeql.yml)

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
