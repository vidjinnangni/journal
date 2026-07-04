"""Smoke tests for the Flask app.

These don't aim for full coverage: they just make sure the app boots and
the main routes render without error, so CI has something to run against.
"""

import pytest

from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def test_index_ok(client):
    response = client.get("/")
    assert response.status_code == 200


def test_sitemap_ok(client):
    response = client.get("/sitemap.xml")
    assert response.status_code == 200


def test_robots_ok(client):
    response = client.get("/robots.txt")
    assert response.status_code == 200


def test_unknown_page_returns_404(client):
    response = client.get("/this-page-does-not-exist")
    assert response.status_code == 404


def test_about_page_ok(client):
    # Ships with the repo under pages/about/index.md.
    response = client.get("/about")
    assert response.status_code == 200


def test_existing_post_ok(client):
    # Ships with the repo under posts/2026-01-15-bienvenue/index.md.
    response = client.get("/post/2026-01-15-bienvenue")
    assert response.status_code == 200
