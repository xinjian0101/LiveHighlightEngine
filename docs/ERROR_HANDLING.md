# Error Handling

The command-line interface should fail clearly when input cannot be processed.

## Input errors

Examples include malformed JSON, a non-object record, missing `start` or `end`, non-numeric timestamps, and unreadable files.

Recommended behavior:

- include the source line number when available;
- stop before writing a partial final report;
- avoid printing full sensitive records;
- return a non-zero process status;
- keep the original input unchanged.

## Validation errors

Events should be reviewed for negative timestamps, `end` not greater than `start`, non-finite signal values, and unreasonable duration.

The current MVP clamps signal values but does not yet enforce every schema rule. Future validation should distinguish warnings from blocking errors.

## Configuration errors

A configuration loader should reject unknown profile versions, missing weights, negative thresholds, weight totals outside an accepted tolerance, and unsupported output formats.

## Output errors

Write output through a temporary file and replace the destination only after serialization succeeds. This avoids leaving a truncated report after interruption.

## Diagnostic record

A machine-readable diagnostic may contain:

```json
{
  "error_code": "invalid_event",
  "message": "end must be greater than start",
  "line": 14,
  "field": "end"
}
```

## Stability rule

Documented error codes should remain stable even when human-readable messages improve.
