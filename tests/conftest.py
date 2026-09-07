from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app


@pytest.fixture()
def application(tmp_path: Path) -> Flask:
    return create_app(
        {
            "DATABASE": str(tmp_path / "test.sqlite3"),
            "SECRET_KEY": "test-key",
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
        }
    )


@pytest.fixture()
def client(application: Flask) -> FlaskClient:
    return application.test_client()
