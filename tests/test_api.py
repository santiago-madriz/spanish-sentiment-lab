import pytest
from flask.testing import FlaskClient

import app as app_module


def test_health_contract(client: FlaskClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "service": "spanish-sentiment-lab",
        "status": "ok",
    }


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Excelente curso, me encanta", "positive"),
        ("Curso terrible y difícil", "negative"),
        ("La clase empieza a las ocho", "neutral"),
    ],
)
def test_sentiment_contract(client: FlaskClient, text: str, expected: str) -> None:
    response = client.post("/api/sentiment", json={"text": text})

    assert response.status_code == 200
    assert response.get_json() == {"sentiment": expected, "text_length": len(text)}


@pytest.mark.parametrize(
    ("kwargs", "status", "error"),
    [
        ({"data": "plain text"}, 415, "Content-Type must be application/json"),
        ({"json": {}}, 400, "text is required"),
        ({"json": {"text": " "}}, 400, "text is required"),
        ({"json": {"text": "x" * 1001}}, 422, "text exceeds the maximum length"),
    ],
)
def test_api_validation(
    client: FlaskClient, kwargs: dict[str, object], status: int, error: str
) -> None:
    response = client.post("/api/sentiment", **kwargs)

    assert response.status_code == status
    assert response.get_json() == {"error": error}


class FakeOpenAIResponse:
    def __init__(self, result: str) -> None:
        self.result = result

    def __enter__(self) -> "FakeOpenAIResponse":
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def read(self) -> bytes:
        return (
            '{"output":[{"content":[{"type":"output_text","text":"'
            + self.result
            + '"}]}]}'
        ).encode()


def test_openai_analyzer_reads_responses_output(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        app_module,
        "urlopen",
        lambda *_args, **_kwargs: FakeOpenAIResponse("positive"),
    )

    assert app_module.OpenAIAnalyzer("test-key").classify("Me encantó") == "positive"


def test_openai_analyzer_rejects_unknown_label(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        app_module,
        "urlopen",
        lambda *_args, **_kwargs: FakeOpenAIResponse("mixed"),
    )

    with pytest.raises(ValueError, match="unsupported sentiment"):
        app_module.OpenAIAnalyzer("test-key").classify("Ambivalente")
