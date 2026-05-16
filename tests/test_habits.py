def _create_habit(client, name="Test", description="", color="#22c55e"):
    return client.post(
        "/habits/new",
        data={"name": name, "description": description, "color": color},
        follow_redirects=False,
    )


def test_dashboard_empty_for_new_user(auth_client):
    r = auth_client.get("/")
    assert r.status_code == 200
    assert "У тебя пока нет привычек" in r.text


def test_create_habit_appears_on_dashboard(auth_client):
    r = _create_habit(auth_client, name="Бегать", description="по утрам")
    assert r.status_code == 303
    assert r.headers["location"] == "/"

    home = auth_client.get("/")
    assert "Бегать" in home.text
    assert "по утрам" in home.text


def test_create_habit_empty_name(auth_client):
    r = auth_client.post("/habits/new", data={"name": ""})
    assert r.status_code == 400
    assert "не может быть пустым" in r.text


def test_create_habit_whitespace_only_name(auth_client):
    r = auth_client.post("/habits/new", data={"name": "   "})
    assert r.status_code == 400


def test_create_habit_too_long_name(auth_client):
    r = auth_client.post("/habits/new", data={"name": "x" * 101})
    assert r.status_code == 400


def test_create_habit_too_long_description(auth_client):
    r = auth_client.post(
        "/habits/new",
        data={"name": "ok", "description": "x" * 501},
    )
    assert r.status_code == 400


def test_delete_own_habit(auth_client):
    _create_habit(auth_client, name="To delete")
    r = auth_client.post("/habits/1/delete", follow_redirects=False)
    assert r.status_code == 303

    home = auth_client.get("/")
    assert "To delete" not in home.text


def test_delete_nonexistent_habit(auth_client):
    r = auth_client.post("/habits/999/delete")
    assert r.status_code == 404


def test_anonymous_cannot_get_new_form(client):
    r = client.get("/habits/new", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/login"


def test_anonymous_cannot_create(client):
    r = client.post(
        "/habits/new",
        data={"name": "x"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers["location"] == "/login"


def test_anonymous_cannot_delete(client):
    r = client.post("/habits/1/delete", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/login"


def test_user_cannot_delete_others_habit(client):
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

    r = client.post("/habits/1/delete", follow_redirects=False)
    assert r.status_code == 404


def test_user_cannot_see_others_habits_on_dashboard(client):
    client.post(
        "/register",
        data={
            "username": "alice",
            "password": "secret123",
            "password_confirm": "secret123",
        },
        follow_redirects=False,
    )
    _create_habit(client, name="alice secret habit")
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
    home = client.get("/")
    assert "alice secret habit" not in home.text
    assert "У тебя пока нет привычек" in home.text
