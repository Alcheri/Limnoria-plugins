# Changelog

## 1.2.0 - 2026-04-26

### Added

- Add per-user channel cooldowns for DNS lookups.
- Add `allowInsecureGeoIP` to make plaintext GeoIP providers opt-in.
- Add focused regression tests for provider security, output sanitising, and cooldown behaviour.
- Add modular `core.py`, `services.py`, and `cooldown.py` helpers while keeping `plugin.py` focused on Limnoria orchestration.

### Changed

- Require Python 3.10 or newer.
- Change the default GeoIP provider order to `ipstack,ipapi`.
- Round latitude and longitude output to four decimal places.
- Redact provider request query strings before logging request failures.
- Sanitise provider-supplied text before sending IRC replies.

### Security

- Remove ipstack plaintext HTTP fallback so API keys are only sent over HTTPS.
- Disable the plaintext `ip-api` provider by default.
