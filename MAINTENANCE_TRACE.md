# Maintenance Trace

This file records visible maintenance work applied to LiveHighlightEngine.

## Maintenance cycle 1

- Expanded the repository entry point.
- Added architecture, configuration, examples, tests, and roadmap material.
- Preserved the original command-line behavior.

## Maintenance cycle 2

- Added an event schema.
- Added scoring calibration guidance.
- Added ClipBench regression integration.

## Maintenance cycle 3

- Added a broader manual-review scoring profile.
- Added contribution standards.
- Added an error-handling contract.

## Maintenance cycle 4 — English-only documentation

### Iteration 61

- Replaced the Chinese README with a complete English project guide.
- Converted the input and output examples to English.
- Preserved the existing CLI, field names, and implementation boundaries.

### Iteration 62

- Updated the changelog with the English-only user-facing documentation policy.
- Consolidated all documented capabilities and limitations.

### Iteration 63

- Updated this trace with the fourth maintenance cycle.
- Confirmed that compatibility-sensitive API field names remain unchanged.

## Validation record

| Check | Result |
|---|---|
| Existing CLI command retained | pass |
| Existing JSONL fields retained | pass |
| Local-first positioning retained | pass |
| English README completed | pass |
| English examples completed | pass |
| Unimplemented behavior remains labeled as planned | pass |

## Maintenance policy

1. Every behavior-changing commit must include or update a test.
2. Scoring changes must record the configuration and benchmark revision.
3. Output schema changes require compatibility notes.
4. Performance claims require a reproducible fixture.
5. Candidate output must remain reviewable and explainable.
6. User-facing documentation and examples are maintained in English.

## Known open items

- No large public benchmark result is currently published.
- No automatic video decoding or media-command execution is included.
- Rule-based scoring is not claimed to be optimal across every content category.
