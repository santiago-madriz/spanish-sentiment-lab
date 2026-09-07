# Test Strategy

## Risk model

| Risk | Control | Automated evidence |
| --- | --- | --- |
| API accepts malformed input | Media-type, required-value, and boundary validation | Parameterized negative API tests |
| Stored data is invalid or orphaned | SQLite checks and foreign keys | Web persistence tests plus schema constraints |
| Model change breaks consumers | Stable analyzer and response contracts | Positive, negative, and neutral contract tests |
| Form can be submitted cross-origin | CSRF token on state-changing browser route | Framework protection enabled; disabled only in isolated tests |
| Dependencies drift or become vulnerable | Bounded versions and dependency review | Dependabot and CI installation from clean environment |
| Coverage hides an untested branch | Enforced threshold and branch-oriented cases | `pytest-cov` fails below 90% |

## Pyramid

1. **Classifier and validation checks** are deterministic and fast.
2. **Flask integration tests** exercise routing, persistence, errors, and HTML contracts with a temporary database.
3. **A short manual exploratory charter** covers keyboard flow, screen-reader labels, mobile layout, and unexpected Spanish phrasing before a release.

## Exit criteria

- lint and type checks pass;
- test coverage remains at or above 90%;
- no credential-like value is committed;
- error responses retain their documented status codes;
- any new analyzer includes evaluation data and failure-mode tests.
