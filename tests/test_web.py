from flask.testing import FlaskClient


def test_course_catalog_has_accessible_landmarks(client: FlaskClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert b"<main" in response.data
    assert "Inteligencia Artificial" in response.text


def test_comment_can_be_classified_and_persisted(client: FlaskClient) -> None:
    response = client.post(
        "/course/1",
        data={"comment": "Excelente curso"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Comentario analizado y guardado." in response.text
    assert "Excelente curso" in response.text
    assert "positive" in response.text


def test_empty_comment_is_rejected(client: FlaskClient) -> None:
    response = client.post("/course/1", data={"comment": " "})

    assert response.status_code == 200
    assert "Escriba un comentario" in response.text


def test_unknown_course_returns_custom_404(client: FlaskClient) -> None:
    response = client.get("/course/999")

    assert response.status_code == 404
    assert "Ese curso no existe" in response.text
