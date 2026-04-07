"""
Test suite — Incredible India Flask Tourism App
Run: pytest tests/ --cov=app --cov-report=term-missing -v
"""

import json
import os
import sys
import pytest

# Make app importable from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app as flask_app
from app import app, STATES, QUIZ_QUESTIONS, _hash, _load, _save


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def client(tmp_path):
    """Test client with isolated temp data directory."""
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"
    app.config["WTF_CSRF_ENABLED"] = False

    # Redirect data files to temp dir
    flask_app.USERS_FILE = str(tmp_path / "users.json")
    flask_app.DATA_FILE  = str(tmp_path / "userdata.json")

    with app.test_client() as c:
        yield c


@pytest.fixture
def logged_in_client(client, tmp_path):
    """Client with a pre-registered and logged-in user."""
    flask_app.USERS_FILE = str(tmp_path / "users.json")
    _save(flask_app.USERS_FILE, {
        "testuser": {
            "pw": _hash("password123"),
            "email": "test@example.com",
            "joined": "2024-01-01T00:00:00",
        }
    })
    client.post("/login", data={"username": "testuser", "password": "password123"})
    return client


# ── Health & Routing ──────────────────────────────────────────────────────────

class TestHealth:
    def test_health_returns_200(self, client):
        r = client.get("/health")
        assert r.status_code == 200

    def test_health_returns_ok_json(self, client):
        r = client.get("/health")
        data = json.loads(r.data)
        assert data["status"] == "ok"
        assert "app" in data

    def test_root_redirects_to_login(self, client):
        r = client.get("/")
        assert r.status_code == 302
        assert "/login" in r.headers["Location"]

    def test_home_requires_login(self, client):
        r = client.get("/home")
        assert r.status_code == 302

    def test_profile_requires_login(self, client):
        r = client.get("/profile")
        assert r.status_code == 302

    def test_quiz_requires_login(self, client):
        r = client.get("/quiz")
        assert r.status_code == 302


# ── Auth ──────────────────────────────────────────────────────────────────────

class TestAuth:
    def test_login_page_loads(self, client):
        r = client.get("/login")
        assert r.status_code == 200
        assert b"Login" in r.data

    def test_signup_page_loads(self, client):
        r = client.get("/signup")
        assert r.status_code == 200

    def test_signup_creates_user(self, client, tmp_path):
        flask_app.USERS_FILE = str(tmp_path / "users.json")
        r = client.post("/signup", data={
            "username": "newuser",
            "password": "secret99",
            "email": "new@example.com",
        })
        assert r.status_code in [200, 302]
        users = _load(flask_app.USERS_FILE, {})
        assert "newuser" in users
        assert users["newuser"]["pw"] == _hash("secret99")

    def test_signup_rejects_short_username(self, client, tmp_path):
        flask_app.USERS_FILE = str(tmp_path / "users.json")
        r = client.post("/signup", data={"username": "ab", "password": "secret99"})
        users = _load(flask_app.USERS_FILE, {})
        assert "ab" not in users

    def test_signup_rejects_short_password(self, client, tmp_path):
        flask_app.USERS_FILE = str(tmp_path / "users.json")
        r = client.post("/signup", data={"username": "validuser", "password": "abc"})
        users = _load(flask_app.USERS_FILE, {})
        assert "validuser" not in users

    def test_signup_rejects_duplicate_username(self, client, tmp_path):
        flask_app.USERS_FILE = str(tmp_path / "users.json")
        _save(flask_app.USERS_FILE, {"alice": {"pw": _hash("pass123"), "email": ""}})
        r = client.post("/signup", data={"username": "alice", "password": "pass999"})
        users = _load(flask_app.USERS_FILE, {})
        assert users["alice"]["pw"] == _hash("pass123")  # not overwritten

    def test_login_valid_credentials(self, client, tmp_path):
        flask_app.USERS_FILE = str(tmp_path / "users.json")
        _save(flask_app.USERS_FILE, {"bob": {"pw": _hash("mypassword"), "email": ""}})
        r = client.post("/login", data={"username": "bob", "password": "mypassword"})
        assert r.status_code == 302
        assert "/home" in r.headers["Location"]

    def test_login_invalid_password(self, client, tmp_path):
        flask_app.USERS_FILE = str(tmp_path / "users.json")
        _save(flask_app.USERS_FILE, {"bob": {"pw": _hash("mypassword"), "email": ""}})
        r = client.post("/login", data={"username": "bob", "password": "wrongpass"})
        assert r.status_code == 200  # stays on login page

    def test_login_unknown_user(self, client, tmp_path):
        flask_app.USERS_FILE = str(tmp_path / "users.json")
        r = client.post("/login", data={"username": "ghost", "password": "anything"})
        assert r.status_code == 200

    def test_guest_login(self, client):
        r = client.get("/guest")
        assert r.status_code == 302

    def test_logout(self, logged_in_client):
        r = logged_in_client.get("/logout")
        assert r.status_code == 302
        # After logout, home should redirect to login
        r2 = logged_in_client.get("/home")
        assert r2.status_code == 302


# ── Pages (authenticated) ─────────────────────────────────────────────────────

class TestPages:
    def test_home_loads(self, logged_in_client):
        r = logged_in_client.get("/home")
        assert r.status_code == 200
        assert b"Incredible India" in r.data

    def test_home_shows_states_and_uts(self, logged_in_client):
        r = logged_in_client.get("/home")
        assert b"Rajasthan" in r.data
        assert b"Kerala" in r.data
        assert b"Sikkim" in r.data
        assert b"Delhi" in r.data
        assert b"Ladakh" in r.data

    def test_state_detail_loads(self, logged_in_client):
        r = logged_in_client.get("/state/Goa")
        assert r.status_code == 200
        assert b"Goa" in r.data
        assert b"Beaches" in r.data

    def test_state_detail_unknown_redirects(self, logged_in_client):
        r = logged_in_client.get("/state/FakeState")
        assert r.status_code == 302

    def test_profile_loads(self, logged_in_client):
        r = logged_in_client.get("/profile")
        assert r.status_code == 200
        assert b"testuser" in r.data

    def test_quiz_page_loads(self, logged_in_client):
        r = logged_in_client.get("/quiz")
        assert r.status_code == 200
        assert b"Quiz" in r.data


# ── API Endpoints ─────────────────────────────────────────────────────────────

class TestAPI:
    def test_random_returns_valid_state(self, logged_in_client):
        r = logged_in_client.get("/api/random")
        assert r.status_code == 200
        data = json.loads(r.data)
        assert "name" in data
        assert data["name"] in STATES

    def test_favourite_add(self, logged_in_client, tmp_path):
        flask_app.DATA_FILE = str(tmp_path / "userdata.json")
        r = logged_in_client.post("/api/favourite",
            json={"name": "Rajasthan"},
            content_type="application/json")
        assert r.status_code == 200
        data = json.loads(r.data)
        assert data["added"] is True

    def test_favourite_toggle_remove(self, logged_in_client, tmp_path):
        flask_app.DATA_FILE = str(tmp_path / "userdata.json")
        logged_in_client.post("/api/favourite", json={"name": "Kerala"})
        r = logged_in_client.post("/api/favourite", json={"name": "Kerala"})
        data = json.loads(r.data)
        assert data["added"] is False

    def test_visited_add(self, logged_in_client, tmp_path):
        flask_app.DATA_FILE = str(tmp_path / "userdata.json")
        r = logged_in_client.post("/api/visited",
            json={"name": "Goa"},
            content_type="application/json")
        assert r.status_code == 200
        data = json.loads(r.data)
        assert data["added"] is True
        assert "total" in data

    def test_favourite_requires_auth(self, client):
        client.get("/guest")  # login as guest
        r = client.post("/api/favourite", json={"name": "Goa"})
        assert r.status_code == 403

    def test_visited_invalid_state(self, logged_in_client, tmp_path):
        flask_app.DATA_FILE = str(tmp_path / "userdata.json")
        r = logged_in_client.post("/api/visited", json={"name": "FakeState"})
        assert r.status_code == 404


# ── Data Integrity ────────────────────────────────────────────────────────────

class TestStateData:
    def test_exactly_36_states_and_uts(self):
        assert len(STATES) == 36, f"Expected 36 (states+UTs), got {len(STATES)}"

    def test_all_states_have_required_fields(self):
        required = ["emoji", "tag", "color", "overview",
                    "food", "food_note", "places", "places_note",
                    "best_time", "facts"]
        for name, state in STATES.items():
            for field in required:
                assert field in state, f"State '{name}' is missing field '{field}'"

    def test_all_states_have_non_empty_content(self):
        for name, state in STATES.items():
            assert state["overview"].strip(), f"State '{name}' has empty overview"
            assert len(state["food"]) > 0,    f"State '{name}' has no food items"
            assert len(state["places"]) > 0,  f"State '{name}' has no places"
            assert len(state["facts"]) > 0,   f"State '{name}' has no facts"

    def test_all_states_have_emoji(self):
        for name, state in STATES.items():
            assert state["emoji"], f"State '{name}' missing emoji"

    def test_all_states_have_color(self):
        for name, state in STATES.items():
            assert state["color"].startswith("#"), f"State '{name}' has invalid color"


class TestQuizData:
    def test_minimum_15_questions(self):
        assert len(QUIZ_QUESTIONS) >= 15

    def test_each_question_has_answer_in_options(self):
        for q in QUIZ_QUESTIONS:
            assert q["ans"] in q["options"], \
                f"Answer '{q['ans']}' not in options {q['options']} for: {q['q']}"

    def test_each_question_has_4_options(self):
        for q in QUIZ_QUESTIONS:
            assert len(q["options"]) == 4, f"Question should have 4 options: {q['q']}"

    def test_no_duplicate_questions(self):
        questions = [q["q"] for q in QUIZ_QUESTIONS]
        assert len(questions) == len(set(questions)), "Duplicate quiz questions found"


# ── Utilities ─────────────────────────────────────────────────────────────────

class TestUtilities:
    def test_hash_is_deterministic(self):
        assert _hash("hello") == _hash("hello")

    def test_hash_different_inputs(self):
        assert _hash("abc") != _hash("def")

    def test_hash_length(self):
        assert len(_hash("anything")) == 64  # sha256 hex = 64 chars

    def test_load_missing_file_returns_default(self, tmp_path):
        result = _load(str(tmp_path / "nonexistent.json"), {"default": True})
        assert result == {"default": True}

    def test_save_and_load_roundtrip(self, tmp_path):
        path = str(tmp_path / "test.json")
        data = {"key": "value", "num": 42, "list": [1, 2, 3]}
        _save(path, data)
        loaded = _load(path, {})
        assert loaded == data