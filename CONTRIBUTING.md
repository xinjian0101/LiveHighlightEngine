# Contributing

Contributions should improve reliability, reproducibility, and local-first operation.

## Development principles

- Keep the scoring core deterministic.
- Avoid hidden network requests.
- Treat event input as untrusted data.
- Separate adapters from scoring logic.
- Preserve backward compatibility for documented event fields.
- Add fixtures for every new input adapter.

## Change checklist

1. Explain the user problem.
2. Document the affected event or configuration fields.
3. Add positive, negative, and boundary tests.
4. Compare benchmark metrics before and after scoring changes.
5. Update the changelog.
6. Record any compatibility impact.

## Scoring changes

A scoring pull request should include the old and new weight profile, benchmark dataset version, thresholds tested, precision, recall, F1, boundary error, and a short trade-off analysis.

## Adapter changes

Adapters should normalize external data into the documented event schema. They must not silently invent timestamps or signal values.

## Commit style

Use concise prefixes such as `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, and `ci:`.

## Review standard

A change is ready when its behavior is documented, its fixtures are reproducible, and failure cases produce clear messages.
