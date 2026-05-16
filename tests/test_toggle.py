def _create_habit(client, name="Test"):
    return client.post(
        "/habits/new",
        data={"name": name, "description": "", "color": "#22c55e"},
        follow_redirects=False,
    )


def test_toggle_creates_log_for_today(auth_client):
    _create_habit(auth_client)

    home = auth_client.get("/")
    assert "Отметить сегодня" in home.text
    assert "Сделано сегодня" not in home.text

    r = auth_client.post("/habits/1/toggle", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/"

    home = auth_client.get("/")
    assert "✓ Сделано сегодня" in home.text


def test_toggle_twice_removes_log(auth_client):
    _create_habit(auth_client)

    auth_client.post("/habits/1/toggle", follow_redirects=False)
    auth_client.post("/habits/1/toggle", follow_redirects=False)

    home = auth_client.get("/")
    assert "Отметить сегодня" in home.text
    assert "Сделано сегодня" not in home.text


def test_toggle_nonexistent_habit(auth_client):
    r = auth_client.post("/habits/999/toggle")
    assert r.status_code == 404


def test_anonymous_cannot_toggle(client):
    r = client.post("/habits/1/toggle", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/login"


def test_user_cannot_toggle_others_habit(client):
    client.post(
        "/register",
        data={
            "username": "alice",
            "password": "secret123",
            "password_confirm": "secret123",
        },
        follow_redirects=False,
    )
    _create_habit(client, name="alice habit")
    client.post("/logout", follow_redirects=False)

    client.post(
        "/register",
        data={
            "username": "bob",
            "password": "secret123",
            "password_confirm": "secret123",
        },
        follow_redirects=False,
    )
    r = client.post("/habits/1/toggle", follow_redirects=False)
    assert r.status_code == 404


def test_toggle_independent_between_habits(auth_client):
    _create_habit(auth_client, name="Habit A")
    _create_habit(auth_client, name="Habit B")

    auth_client.post("/habits/1/toggle", follow_redirects=False)

    home = auth_client.get("/")
    assert home.text.count("✓ Сделано сегодня") == 1
    assert home.text.count("Отметить сегодня") == 1
