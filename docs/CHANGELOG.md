# Changelog

## Unreleased - 2026-04-26

### Added

- Add per-user channel cooldowns for Google Maps lookups.
- Add focused tests for URL encoding, coordinate validation, output sanitising, and cooldown behaviour.
- Add pytest collection configuration for the repo test module.

### Changed

- Encode generated Google Maps directions URLs with structured URL encoding.
- Validate reverse geocode coordinates as numeric latitude and longitude values.
- Sanitise IRC replies by stripping control characters from provider-supplied output.
- Reduce logging of raw user input and full API response payloads.

### Security

- Reduce quota-abuse risk with a configurable per-user cooldown.
- Avoid exposing searched addresses and full provider responses in logs.
