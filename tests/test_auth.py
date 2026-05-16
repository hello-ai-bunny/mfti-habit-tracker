def test_index_anonymous_shows_landing(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Начать" in r.text


def test_register_success_redirects_and_logs_in(client):
    r = client.post(
        "/register",
        data={
            "username": "alice",
            "password": "secret123",
            "password_confirm": "secret123",
        },
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers["location"] == "/"

    home = client.get("/")
    assert "alice" in home.text


def test_register_short_password(client):
    r = client.post(
        "/register",
        data={"username": "alice", "password": "12", "password_confirm": "12"},
    )
    assert r.status_code == 400
    assert "от 6 символов" in r.text


def test_register_password_mismatch(client):
    r = client.post(
        "/register",
        data={
            "username": "alice",
            "password": "secret123",
            "password_confirm": "different",
        },
    )
    assert r.status_code == 400
    assert "не совпадают" in r.text


def test_register_short_username(client):
    r = client.post(
        "/register",
        data={
            "username": "a",
            "password": "secret123",
            "password_confirm": "secret123",
        },
    )
    assert r.status_code == 400


def test_register_duplicate_username(client):
    payload = {
        "username": "alice",
        "password": "secret123",
        "password_confirm": "secret123",
    }
    client.post("/register", data=payload, follow_redirects=False)
    r = client.post("/register", data=payload)
    assert r.status_code == 400
    assert "уже существует" in r.text


def test_login_success(client):
    client.post(
        "/register",
        data={
            "username": "alice",
            "password": "secret123",
            "password_confirm": "secret123",
        },
        follow_redirects=False,
    )
    client.post("/logout", follow_redirects=False)

    r = client.post(
        "/login",
        data={"username": "alice", "password": "secret123"},
        follow_redirects=False,
    )
    assert r.status_code == 303


def test_login_wrong_password(client):
    client.post(
        "/register",
        data={
            "username": "alice",
            "password": "secret123",
            "password_confirm": "secret123",
        },
        follow_redirects=False,
    )
    client.post("/logout", follow_redirects=False)

    r = client.post("/login", data={"username": "alice", "password": "wrong"})
    assert r.status_code == 400
    assert "Неверное" in r.text


def test_login_unknown_user(client):
    r = client.post("/login", data={"username": "nobody", "password": "whatever"})
    assert r.status_code == 400


def test_logout_clears_session(auth_client):
    r = auth_client.post("/logout", follow_redirects=False)
    assert r.status_code == 303

    home = auth_client.get("/")
    assert "Начать" in home.text


def test_register_when_logged_in_redirects(auth_client):
    r = auth_client.get("/register", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/"


def test_login_when_logged_in_redirects(auth_client):
    r = auth_client.get("/login", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/"
