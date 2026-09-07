# Architecture

## Request flow

```text
Browser form ──CSRF + validation──┐
                                  ├── Analyzer contract ── deterministic baseline
JSON API ──media type + schema────┘
                  │
                  └── SQLite repository ── constraints + foreign keys
```

`create_app` is the composition root. Runtime configuration, the database path, and the analyzer can be replaced in tests without changing route behavior.

## Decisions

| Decision | Quality benefit | Trade-off |
| --- | --- | --- |
| SQLite default | Zero-service setup and isolated test databases | Not intended for high-write distributed workloads |
| Analyzer protocol | Model can change without rewriting routes or contract tests | Implementations must normalize their output |
| Deterministic baseline | Fast, explainable tests with no credentials or network | Lower linguistic accuracy than a trained model |
| Server-rendered pages | Small browser surface and native semantics | Less client-side interactivity |

## Extension seam

A production analyzer needs only this contract:

```python
class Analyzer(Protocol):
    def classify(self, text: str) -> str: ...
```

Before replacing the baseline, add a versioned Spanish evaluation set, define acceptable per-class precision and recall, and test timeout/error behavior for any remote dependency.
