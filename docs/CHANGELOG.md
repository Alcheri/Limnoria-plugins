# Changelog

All notable changes to MessagesLog are documented in this file.

## Unreleased

### Added

- Moved supporting project documentation into the `docs/` directory.

### Changed

- Updated the contribution agreement.
- Modernised `pyproject.toml` build-system and Black configuration.
- Normalised README badges.
- Standardised GitHub support files and `.gitignore` entries.
- Ignored the local `Documents/` directory.
- Set the package Python requirement to Python 3.10 or newer.

## v1.0.0 - 2026-04-23

### Added

- Initial MessagesLog plugin implementation for reading Limnoria `messages.log`.
- Added configuration for log path, default line count, and maximum line count.
- Added GitHub Actions testing, Black linting, Dependabot, CodeQL, and CI badges.
- Added pytest-compatible tests.

### Changed

- Sent `messageslog tail` output by notice.
- Stabilised Black linting.

### Fixed

- Gated `messageslog tail` to admins.
