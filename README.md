<!-- Limnoria plugin to query and summarize Wikipedia articles. -->

# Wikipedia

Limnoria plugin to query and summarize Wikipedia articles.

## Requirements

- Python 3.10+
- Limnoria
- requests
- beautifulsoup4

## Install

From your Limnoria plugins directory:

```bash
git clone https://github.com/Alcheri/Wikipedia.git
```

Install plugin dependencies:

```bash
cd Wikipedia
pip install --upgrade -r requirements.txt
```

Load the plugin:

```text
/msg bot load Wikipedia
```

## Configuration

Enable in a channel:

```text
/msg bot config channel #channel plugins.Wikipedia.enabled True
```

Disable in a channel:

```text
/msg bot config channel #channel plugins.Wikipedia.enabled False
```

## Usage

```text
@wiki monty python
```

Example response:

```text
Monty Python (also collectively known as the Pythons) were a British comedy troupe formed in 1969.
```

## Behavior Notes

- Returns a short summary (up to 2 paragraphs), truncated for IRC-friendly length.
- Detects disambiguation pages and asks for a more specific topic.
- Returns a friendly message when no article is found.
- Honors channel enable/disable config, and can still be used in private messages.

## Testing

Run isolated Wikipedia plugin tests in WSL (without loading other plugins):

```bash
wsl -e bash -lc 'set -euo pipefail; cd /home/barry/supyplugins; source .venv-wsl/bin/activate; TMPDIR=$(mktemp -d); cp -a Wikipedia "$TMPDIR"/Wikipedia; supybot-test --plugins-dir="$TMPDIR" --disable-multiprocessing --no-network Wikipedia; STATUS=$?; rm -rf "$TMPDIR"; exit $STATUS'
```

Expected result:

- 3 tests run
- 0 failures

## Licensing

This project contains code originally published under the MIT Licence by the
upstream author. The original licence text is preserved verbatim in
`LICENSE.txt` as required by the MIT Licence.

All modifications, additions, and ongoing maintenance performed by Barry
Suridge are licensed under the terms described in `LICENCE.md`.

In summary:

- `LICENSE.txt` — original upstream MIT Licence (unchanged)
- `LICENCE.md` — licence applying to Barry Suridge’s contributions
