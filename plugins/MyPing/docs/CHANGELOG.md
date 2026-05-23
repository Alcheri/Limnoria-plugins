# Changelog

All notable changes to MyPing are documented in this file.

## Unreleased

### Added

- Moved supporting project documentation into the `docs/` directory.

### Changed

- Updated contribution terms.
- Normalised Black configuration and README badge references.
- Normalised README badges.
- Standardised GitHub support files and `.gitignore` entries.
- Applied Black formatting.
- Ignored the local `Documents/` directory.
- Set the package Python requirement to Python 3.10 or newer.

### Fixed

- Hardened MyPing subprocess handling.
- Avoided Supybot built-in shadowing in ping validation.
- Preserved IRC colours in MyPing replies.

## v1.0.2 - 2026-04-25

### Added

- Added deterministic tests that mock the ping subprocess.
- Added PEP 621 package metadata.
- Added GitHub Actions testing, Black linting, CodeQL, and README badges.

### Changed

- Updated README installation and usage guidance.
- Corrected copyright information.
- Stabilised Black linting and standardised CI workflows.
- Ignored Python cache artefacts and Supybot runtime directories.

### Fixed

- Cleaned up version guards and ping handling.
