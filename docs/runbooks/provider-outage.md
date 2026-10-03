# Provider outage runbook

## Symptom

The pipeline shows provider timeouts, repeated fallback behavior, or a sudden rise in failed model calls.

## Immediate checks

1. Confirm the provider is available for the configured model.
2. Confirm the API key is still valid and has not expired.
3. Check for quota exhaustion or rate-limit warnings.
4. Inspect whether the code is still routing to the expected provider tier.

## Actions

- If the primary provider is down, confirm fallback logic is active and logged.
- If the fallback provider is also unavailable, pause non-critical runs.
- If a provider is rate-limited, reduce batch size or retry only after an interval.
- If the issue is repetitive, inspect `pipeline/config.py` and provider routing logic before re-running large batches.

## Validation

- the fallback chain should be explicit and traceable
- logs must record which provider was attempted and why it failed
- no silent retries should hide the underlying failure condition

## Ownership

The pipeline owner or platform maintainer should review provider health before production reruns.
