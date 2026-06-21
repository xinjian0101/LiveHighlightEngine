# Security Policy

## Supported versions

Security fixes are applied to the current `main` branch. Older commits and unmaintained forks are not guaranteed to receive fixes.

## Reporting a vulnerability

Do not publish credentials, private recordings, personal information, internal paths, or working exploit details in a public issue.

Use GitHub private vulnerability reporting when it is available for this repository. If private reporting is unavailable, open a minimal public issue stating that a security concern exists without including sensitive details.

Include:

- affected commit;
- affected component;
- impact summary;
- minimal synthetic reproduction;
- operating system and Python version;
- whether untrusted JSONL, configuration, or output paths are involved.

## Security boundaries

LiveHighlightEngine does not execute FFmpeg, decode media, or upload source files. Integrators remain responsible for validating adapter inputs, protecting local paths, controlling output locations, and reviewing downstream execution.

## Out of scope

- exposed secrets already committed by third parties;
- security of unrelated media players or FFmpeg runners;
- unsupported local modifications;
- social-engineering requests;
- claims without a reproducible affected code path.

## Disclosure

Allow maintainers reasonable time to reproduce, correct, test, and document a confirmed issue before public disclosure.
