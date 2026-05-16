def _create(client, name="Original", description="orig desc", color="#111111"):
    return client.post(
        "/habits/new",
        data={"name": name, "description": description, "color": color},
        follow_redirects=False,
    )


def test_edit_form_renders(auth_client):
    _create(auth_client, name="Original")
    r = auth_client.get("/habits/1/edit")
    assert r.status_code == 200
    assert "Редактировать привычку" in r.text
    assert "Original" in r.text


def test_edit_updates_fields(auth_client):
    _create(auth_client, name="Old", description="old", color="#111111")
    r = auth_client.post(
        "/habits/1/edit",
        data={"name": "New name", "description": "new desc", "color": "#abcdef"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers["location"] == "/habits/1"

    detail = auth_client.get("/habits/1")
    assert "New name" in detail.text
    assert "new desc" in detail.text
    assert "#abcdef" in detail.text


def test_edit_empty_name_returns_400(auth_client):
    _create(auth_client)
    r = auth_client.post(
        "/habits/1/edit",
        data={"name": "", "description": "", "color": "#000000"},
    )
    assert r.status_code == 400
    assert "не может быть пустым" in r.text


def test_edit_404_for_nonexistent(auth_client):
    r = auth_client.get("/habits/999/edit")
    assert r.status_code == 404


def test_edit_404_for_others_habit(client):
    client.post(
        "/register",
        data={
            "username": "alice",
            "password": "secret123",
            "password_confirm": "secret123",
        },
        follow_redirects=False,
    )
    _create(client, name="alice habit")
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
    r = client.get("/habits/1/edit")
    assert r.status_code == 404


def test_edit_anonymous_redirects(client):
    r = client.get("/habits/1/edit", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/login"
