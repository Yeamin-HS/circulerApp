"""The API contract is frozen (ADR-010). These tests fail when it drifts.

To change the contract on purpose:
    UPDATE_OPENAPI=1 .venv/bin/pytest tests/test_contract.py
then regenerate the frontend types (`npm run types` in frontend/) and note the change in
IMPLEMENTATION.md.
"""

import json
import os
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

SNAPSHOT = Path(__file__).parents[2] / "docs" / "openapi.json"

ENDPOINTS = {
    ("POST", "/auth/register"),
    ("POST", "/auth/login"),
    ("GET", "/me"),
    ("DELETE", "/me"),
    ("POST", "/me/consent"),
    ("POST", "/me/cv"),
    ("PUT", "/me/profile"),
    ("GET", "/me/profile"),
    ("POST", "/circulars"),
    ("GET", "/circulars"),
    ("GET", "/circulars/{circular_id}"),
    ("GET", "/circulars/{circular_id}/eligibility"),
    ("POST", "/circulars/{circular_id}/ask"),
    ("GET", "/chunks/{chunk_id}"),
    ("GET", "/health"),
}
PUBLIC = {"/auth/register", "/auth/login", "/health"}


def test_openapi_matches_snapshot() -> None:
    current = json.dumps(app.openapi(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if os.environ.get("UPDATE_OPENAPI"):
        SNAPSHOT.write_text(current, encoding="utf-8")
    assert current == SNAPSHOT.read_text(encoding="utf-8"), "API contract changed; see ADR-010"


def test_endpoint_list_is_exact() -> None:
    paths = app.openapi()["paths"]
    found = {(method.upper(), path) for path, ops in paths.items() for method in ops}
    assert found == ENDPOINTS


def test_every_private_route_requires_a_token(client: TestClient) -> None:
    for method, path in sorted(ENDPOINTS):
        if path in PUBLIC:
            continue
        response = client.request(method, path.format(circular_id=1, chunk_id=1))
        assert response.status_code == 401, (method, path)
        assert response.json()["error"]["code"] == "unauthorized"


def test_errors_share_one_shape(client: TestClient, token: str) -> None:
    invalid = client.post("/auth/register", json={"email": "not-an-email", "password": "x"})
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "validation_error"

    stub = client.get("/me/profile", headers={"Authorization": f"Bearer {token}"})
    assert stub.status_code == 501
    assert stub.json()["error"]["code"] == "not_implemented"

    missing = client.get("/no-such-route")
    assert missing.status_code == 404
    assert set(missing.json()["error"]) == {"code", "message", "retry_after"}


def test_fact_card_schema_holds_every_labelled_circular() -> None:
    """The 15 hand-labelled circulars (Story 1.2) must fit the frozen FactCard."""
    from app.core.schemas import FactCard

    def wrap(value: object) -> dict:
        return {"value": value, "evidence": []}

    labels = sorted((Path(__file__).parents[2] / "eval" / "labels").glob("*.json"))
    assert len(labels) >= 15
    for path in labels:
        card = json.loads(path.read_text(encoding="utf-8"))["fact_card"]
        posts = [
            {k: wrap(v) for k, v in post.items()} | {"grade": wrap(None)} for post in card["posts"]
        ]
        top = {k: wrap(v) for k, v in card.items() if k != "posts"}
        FactCard.model_validate(top | {"posts": posts})
