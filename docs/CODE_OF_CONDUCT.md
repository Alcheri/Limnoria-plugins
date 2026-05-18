# Code of Conduct

## Purpose

Asyncio is an AI chat plugin for Limnoria IRC bots. It can process user prompts,
send content to the OpenAI API, remember short conversation context, and reply in
shared IRC channels.

This Code of Conduct sets expectations for respectful community behaviour and
responsible AI use around this project.

## Community Standards

Contributors, operators, and users are expected to:

- Treat other people with respect and patience.
- Give and accept technical feedback constructively.
- Avoid harassment, intimidation, personal attacks, and discriminatory language.
- Avoid publishing private information without explicit permission.
- Keep discussion focused on improving the plugin and its safe operation.

Unacceptable behaviour includes abuse, harassment, sustained disruption, and
conduct that would reasonably make other people feel unsafe or unwelcome.

## Responsible AI Use

AI output can be wrong, incomplete, biased, or unsafe. Contributors and
operators must not present Asyncio's responses as authoritative professional
advice or as a substitute for human judgement.

Contributions should preserve safeguards that reduce misuse, including:

- input moderation before model calls where the implementation supports it;
- per-user and per-channel memory boundaries;
- cooldowns and token limits that reduce spam and runaway use;
- clear reply handling that remains safe for IRC channels.

Changes that weaken these protections should explain the operational trade-off
and include appropriate tests or review notes.

## Privacy And Data Handling

Prompts and context may be sent to an external AI provider. Operators should make
that clear to their users and avoid feeding sensitive personal data, secrets,
credentials, private messages, or confidential operational details into the
plugin.

Contributors should avoid adding logging that records raw prompts, secrets, API
keys, access tokens, hostmasks, or private channel content unless it is clearly
needed for debugging and disabled by default.

## Safety, Moderation, And Abuse Prevention

Asyncio should not be used to harass people, automate abuse, bypass channel
rules, impersonate trusted users, generate malicious instructions, or flood IRC
channels.

Safety-related reports may involve:

- moderation bypasses;
- memory leakage between users or channels;
- output that exposes secrets or private content;
- prompts that cause unsafe or abusive replies;
- denial-of-service behaviour caused by repeated AI requests.

Report security-sensitive issues privately as described in
[Security Policy](SECURITY.md). General conduct concerns may be reported to
@Alcheri on GitHub.

## Operator Responsibilities

Operators are responsible for configuring the plugin appropriately for their IRC
network and community. This includes access controls, channel policy, rate
limits, logging settings, and provider API credentials.

Operators should review the relevant provider policies before enabling the
plugin in public or semi-public channels:

- [OpenAI Usage Policies](https://openai.com/policies/usage-policies/)
- [OpenAI Privacy Policy](https://openai.com/policies/privacy-policy/)

## Enforcement

Project maintainers may remove comments, reject contributions, close issues,
block users, or decline support when behaviour conflicts with this Code of
Conduct or creates avoidable safety risk.

Enforcement should be proportionate, documented where practical, and mindful of
the privacy and security of people reporting concerns.

## Attribution

The community standards and enforcement structure are informed by the
[Contributor Covenant](https://www.contributor-covenant.org/), version 2.0, and
adapted for an AI-enabled Limnoria plugin.
