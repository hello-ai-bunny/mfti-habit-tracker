def test_404_renders_pretty_page(client):
    r = client.get("/this-route-does-not-exist")
    assert r.status_code == 404
    assert "404" in r.text
    assert "Страница не найдена" in r.text
    assert "На главную" in r.text


def test_404_for_nonexistent_habit_renders_page(auth_client):
    r = auth_client.get("/habits/9999")
    assert r.status_code == 404
    assert "Страница не найдена" in r.text


def test_static_css_is_served(client):
    r = client.get("/static/style.css")
    assert r.status_code == 200
    assert "habit-card" in r.text
