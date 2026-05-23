# Changelog

All notable changes to WorldTime are documented in this file.

## Unreleased

### Changed

- Normalised README badges.
- Set the package Python requirement to Python 3.10 or newer.

## v1.1.0 - 2026-04-28

### Added

- Added PEP 621 package metadata.
- Added README status badges and improved WorldTime plugin description.
- Added GitHub Actions testing, Black linting, CodeQL, and Dependabot workflow support.
- Added licence documentation for upstream and maintained contributions.

### Changed

- Aligned Python 3.11 support.
- Refactored README code snippets.
- Standardised GitHub support files and `.gitignore` entries.
- Moved supporting project documentation into the `docs/` directory.
- Updated contribution terms.
- Normalised Black configuration.
- Ignored Supybot runtime directories and the local `Documents/` directory.

### Fixed

- Hardened WorldTime lookups and storage.
- Fixed package metadata.
- Replaced the placeholder docstring, added API key guard behaviour, removed deprecated sensor parameters, and widened exception handling.
