from __future__ import annotations

import json
import os
import re
import secrets
import sqlite3
from collections.abc import Mapping
from pathlib import Path
from typing import Protocol, cast
from urllib.request import Request, urlopen

from flask import (
    Flask,
    Response,
    current_app,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask.typing import ResponseReturnValue
from flask_wtf.csrf import CSRFProtect  # type: ignore[import-untyped]

csrf = CSRFProtect()


class Analyzer(Protocol):
    def classify(self, text: str) -> str: ...


class SpanishKeywordAnalyzer:
    """Deterministic classifier used to keep the demo reproducible.

    It is deliberately not presented as an ML model. Production deployments can
    inject a trained analyzer that implements the same ``classify`` contract.
    """

    positive_words = {
        "bueno",
        "buena",
        "excelente",
        "encanta",
        "fascina",
        "genial",
        "gusta",
        "útil",
    }
    negative_words = {
        "difícil",
        "malo",
        "mala",
        "odio",
        "pésimo",
        "pésima",
        "terrible",
    }

    def classify(self, text: str) -> str:
        words = set(re.findall(r"[a-záéíóúüñ]+", text.casefold()))
        score = len(words & self.positive_words) - len(words & self.negative_words)
        if score > 0:
            return "positive"
        if score < 0:
            return "negative"
        return "neutral"


class OpenAIAnalyzer:
    """Spanish sentiment classifier backed by the OpenAI Responses API."""

    endpoint = "https://api.openai.com/v1/responses"

    def __init__(self, api_key: str, model: str = "gpt-4.1-mini") -> None:
        self.api_key = api_key
        self.model = model

    def classify(self, text: str) -> str:
        body = json.dumps(
            {
                "model": self.model,
                "instructions": (
                    "Clasifica el sentimiento del comentario en español. Responde únicamente "
                    "con una de estas palabras exactas: positive, negative, neutral."
                ),
                "input": text,
                "max_output_tokens": 16,
                "store": False,
            }
        ).encode("utf-8")
        request_data = Request(  # noqa: S310
            self.endpoint,
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urlopen(request_data, timeout=15) as response:  # noqa: S310
            payload = json.loads(response.read().decode("utf-8"))
        output_text = payload.get("output_text", "")
        if not output_text:
            output_text = "".join(
                str(content.get("text", ""))
                for item in payload.get("output", [])
                if isinstance(item, dict)
                for content in item.get("content", [])
                if isinstance(content, dict) and content.get("type") == "output_text"
            )
        result = str(output_text).strip().casefold()
        if result not in {"positive", "negative", "neutral"}:
            raise ValueError("AI analyzer returned an unsupported sentiment")
        return result


def _default_analyzer() -> Analyzer:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if api_key:
        return OpenAIAnalyzer(api_key, os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))
    return SpanishKeywordAnalyzer()


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        database = Path(current_app.config["DATABASE"])
        database.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(database)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return cast(sqlite3.Connection, g.db)


def close_db(_: BaseException | None = None) -> None:
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_db() -> None:
    schema_path = Path(current_app.root_path) / "schema.sql"
    connection = get_db()
    connection.executescript(schema_path.read_text(encoding="utf-8"))
    connection.commit()


def _sentiment_summary(course_id: int) -> dict[str, float | int]:
    counts = {"positive": 0, "negative": 0, "neutral": 0}
    rows = get_db().execute(
        """
        SELECT sentiment, COUNT(*) AS count
        FROM comments
        WHERE course_id = ?
        GROUP BY sentiment
        """,
        (course_id,),
    )
    for row in rows:
        counts[row["sentiment"]] = row["count"]

    total = sum(counts.values())
    percentages = {
        label: round((count / total) * 100, 1) if total else 0.0
        for label, count in counts.items()
    }
    return {"total": total, **percentages}


def _read_text(payload: Mapping[str, object]) -> str:
    value = payload.get("text", "")
    return value.strip() if isinstance(value, str) else ""


def create_app(test_config: Mapping[str, object] | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.getenv("DATABASE_PATH", str(Path(app.instance_path) / "sentiment.sqlite3")),
        MAX_COMMENT_LENGTH=1000,
        SECRET_KEY=os.getenv("SECRET_KEY") or secrets.token_hex(32),
    )
    if test_config:
        app.config.from_mapping(test_config)

    app.extensions["sentiment_analyzer"] = app.config.get(
        "SENTIMENT_ANALYZER", _default_analyzer()
    )
    app.teardown_appcontext(close_db)
    csrf.init_app(app)

    with app.app_context():
        init_db()

    @app.get("/")
    def index() -> str:
        courses = get_db().execute("SELECT id, name FROM courses ORDER BY id").fetchall()
        summaries = {course["id"]: _sentiment_summary(course["id"]) for course in courses}
        return render_template("index.html", courses=courses, summaries=summaries)

    @app.route("/course/<int:course_id>", methods=["GET", "POST"])
    def course(course_id: int) -> ResponseReturnValue:
        connection = get_db()
        selected_course = connection.execute(
            "SELECT id, name FROM courses WHERE id = ?", (course_id,)
        ).fetchone()
        if selected_course is None:
            return render_template("404.html"), 404

        if request.method == "POST":
            comment = request.form.get("comment", "").strip()
            limit = current_app.config["MAX_COMMENT_LENGTH"]
            if not comment:
                flash("Escriba un comentario antes de enviarlo.", "error")
            elif len(comment) > limit:
                flash(f"El comentario no puede superar {limit} caracteres.", "error")
            else:
                analyzer: Analyzer = current_app.extensions["sentiment_analyzer"]
                sentiment = analyzer.classify(comment)
                connection.execute(
                    "INSERT INTO comments (course_id, content, sentiment) VALUES (?, ?, ?)",
                    (course_id, comment, sentiment),
                )
                connection.commit()
                flash("Comentario analizado y guardado.", "success")
                return redirect(url_for("course", course_id=course_id))

        comments = connection.execute(
            """
            SELECT content, sentiment, created_at
            FROM comments
            WHERE course_id = ?
            ORDER BY id DESC
            """,
            (course_id,),
        ).fetchall()
        return render_template(
            "course.html",
            course=selected_course,
            comments=comments,
            max_comment_length=current_app.config["MAX_COMMENT_LENGTH"],
            ai_enabled=isinstance(
                current_app.extensions["sentiment_analyzer"], OpenAIAnalyzer
            ),
        )

    @app.get("/api/health")
    def health() -> Response:
        get_db().execute("SELECT 1").fetchone()
        return jsonify(status="ok", service="spanish-sentiment-lab")

    @app.post("/api/sentiment")
    @csrf.exempt
    def sentiment_api() -> ResponseReturnValue:
        if not request.is_json:
            return jsonify(error="Content-Type must be application/json"), 415
        text = _read_text(request.get_json(silent=True) or {})
        if not text:
            return jsonify(error="text is required"), 400
        if len(text) > current_app.config["MAX_COMMENT_LENGTH"]:
            return jsonify(error="text exceeds the maximum length"), 422

        analyzer: Analyzer = current_app.extensions["sentiment_analyzer"]
        return jsonify(sentiment=analyzer.classify(text), text_length=len(text))

    @app.errorhandler(404)
    def not_found(_: object) -> ResponseReturnValue:
        return render_template("404.html"), 404

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
