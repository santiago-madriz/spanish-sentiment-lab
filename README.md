# Spanish Sentiment Lab

[![Quality](https://github.com/santiago-madriz/spanish-sentiment-lab/actions/workflows/quality.yml/badge.svg)](https://github.com/santiago-madriz/spanish-sentiment-lab/actions/workflows/quality.yml)

A small Flask application used to demonstrate API, data, security, and web quality engineering. It classifies Spanish course feedback as positive, negative, or neutral through both a browser workflow and a JSON API.

The application uses OpenAI when `OPENAI_API_KEY` is configured and falls back to a transparent keyword baseline for reproducible offline development. Both engines share the same `Analyzer` contract and quality checks.

## Product experience

- Responsive dark interface for browsing courses and analyzing feedback
- Clear positive, negative, and neutral result states
- Visible analyzer status so local and AI-backed results are not confused
- Per-course comment history backed by SQLite
- Accessible forms, validation feedback, focus states, and mobile layouts

## What this demonstrates

- API contract and negative-path testing with `pytest`
- SQLite constraints, parameterized queries, and connection lifecycle management
- CSRF protection for state-changing browser requests
- Input normalization, required-field checks, and length boundaries
- Accessible templates, clear focus states, and semantic landmarks
- Optional OpenAI-backed classification behind the same injectable analyzer contract
- Static analysis, type checks, coverage thresholds, and dependency review in CI
- Container-ready configuration without committed credentials

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
flask --app app run
```

Open `http://127.0.0.1:5000`. The SQLite database is created under `instance/`.

To enable AI analysis, copy `.env.example`, export `OPENAI_API_KEY`, and optionally set `OPENAI_MODEL`. Never commit the key. Without it, the UI clearly identifies the local deterministic engine.

### API example

```bash
curl --request POST http://127.0.0.1:5000/api/sentiment \
  --header 'Content-Type: application/json' \
  --data '{"text":"Excelente curso"}'
```

### Quality checks

```bash
ruff check .
mypy app.py
pytest
pip-audit --skip-editable
```

## Modernization notes

Version 2 replaces a student prototype that depended on a local MySQL password, generated external images during page loads, and converted user-named audio files through a shell. Those paths made the application hard to reproduce and created avoidable security risks. The current scope keeps the useful sentiment domain while making every dependency and boundary testable.

See [Architecture](docs/ARCHITECTURE.md), [Test Strategy](docs/TEST_STRATEGY.md), and [Security](SECURITY.md).

## Limitations

The baseline classifier is an educational seam, not a production sentiment model. It does not understand context, negation, sarcasm, dialect, or demographic variation. Do not use its output for decisions about people.

## License

[MIT](LICENSE)
