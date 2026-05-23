# Changelog

All notable changes to Dictionary are documented in this file.

## Unreleased

### Added

- Added supporting project documentation under `docs/`.

### Changed

- Updated contribution terms.
- Removed repo-local Ruff configuration from `pyproject.toml`.
- Fixed package metadata and validation.
- Normalised README badge references.
- Standardised GitHub support files and `.gitignore` entries.
- Ignored the local `Documents/` directory.

### Fixed

- Hardened Dictionary lookup output.

## v1.0.0 - 2026-04-16

### Added

- Added the initial Dictionary plugin implementation.
- Added quoted phrase lookup support and 404 handling.
- Added deterministic test scaffolding for Supybot test discovery.
- Added PEP 621 package metadata.
- Added GitHub Actions testing, Black linting, CodeQL, and README badges.

### Changed

- Updated the plugin version to `1.0.0`.
- Normalised the request user agent.
- Migrated package metadata away from `setup.py`.
- Standardised CI workflows and Black lint checks.

### Fixed

- Hardened test import handling.
- Removed obsolete setup metadata and redundant workflow files.
