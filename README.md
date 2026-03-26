# Limnoria-plugins

A curated collection of Limnoria (Supybot) plugins maintained by **@Alcheri**.

This repository exists primarily to work with Limnoria’s built-in **PluginDownloader** plugin, which expects a single Git repository containing **multiple plugin directories** under a common path (here: `plugins/`).

## Repository layout

Plugins are stored under `plugins/<PluginName>/`, for example:

```
plugins/
  WorldTime/
  LocalControl/
  ...
```

Each plugin directory contains the normal Limnoria plugin structure (typically `__init__.py`, `plugin.py`, `config.py`, etc.).

## Installing via Limnoria PluginDownloader

Once this repository is registered in Limnoria’s PluginDownloader index, you can:

- List configured repositories:
  - `@plugindownloader repolist`
- List plugins from this repository:
  - `@plugindownloader repolist Alcheri`
- Install a plugin:
  - `@plugindownloader install Alcheri WorldTime`
- Show plugin info (first paragraph of the plugin’s README, if present):
  - `@plugindownloader info Alcheri WorldTime`

## Development model

Most plugins are developed in their own repositories under branches named:

- `Limnoria-<PluginName>`

This repository is a **bundle for distribution/discovery** via PluginDownloader.

If you want to contribute to a specific plugin, prefer sending PRs to that plugin’s own repository (when applicable).

## Keeping things simple (no private mirrors)

Private repositories used for deployment or local workflow are intentionally **not mirrored** into this bundle repository.  
Only publicly distributable plugins are included.

## Maintenance (git subtree)

This repository can be maintained using `git subtree`, keeping each plugin under `plugins/<PluginName>/` while preserving history.

### One-time add (example)

```bash
git remote add worldtime https://github.com/Alcheri/WorldTime.git
git fetch worldtime Limnoria-WorldTime
git subtree add --prefix=plugins/WorldTime worldtime Limnoria-WorldTime
```

### Updating an existing subtree (example)

```bash
git fetch worldtime Limnoria-WorldTime
git subtree pull --prefix=plugins/WorldTime worldtime Limnoria-WorldTime
```

## Licensing

Each plugin may have its own licence. Check each plugin directory for a `LICENCE`/`LICENCE.md` file.

If a plugin directory includes a `LICENCE.md`, that file governs the plugin.
