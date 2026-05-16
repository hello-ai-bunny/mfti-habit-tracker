from datetime import date, timedelta

from app.models import HabitLog


def test_stats_page_empty(auth_client):
    r = auth_client.get("/stats")
    assert r.status_code == 200
    assert "Пока нет привычек" in r.text or "Здесь пока пусто" in r.text


def test_stats_page_shows_summary(auth_client):
    auth_client.post("/habits/new", data={"name": "A"}, follow_redirects=False)
    auth_client.post("/habits/new", data={"name": "B"}, follow_redirects=False)
    auth_client.post("/habits/1/toggle", follow_redirects=False)

    r = auth_client.get("/stats")
    assert r.status_code == 200
    assert ">1<" in r.text
    assert "/2<" in r.text
    assert "A" in r.text
    assert "B" in r.text


def test_stats_page_aggregates_correctly(client, db_session):
    client.post(
        "/register",
        data={
            "username": "tester",
            "password": "secret123",
            "password_confirm": "secret123",
        },
        follow_redirects=False,
    )
    client.post("/habits/new", data={"name": "H1"}, follow_redirects=False)
    client.post("/habits/new", data={"name": "H2"}, follow_redirects=False)

    today = date.today()
    for i in range(3):
        db_session.add(HabitLog(habit_id=1, date=today - timedelta(days=i)))
    db_session.add(HabitLog(habit_id=2, date=today - timedelta(days=10)))
    db_session.commit()

    r = client.get("/stats")
    assert r.status_code == 200
    assert ">2<" in r.text 
    assert ">4<" in r.text  


def test_stats_page_anonymous_redirects(client):
    r = client.get("/stats", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/login"


def test_navbar_has_stats_link_when_logged_in(auth_client):
    r = auth_client.get("/")
    assert 'href="/stats"' in r.text


def test_navbar_no_stats_link_for_anonymous(client):
    r = client.get("/")
    assert 'href="/stats"' not in r.text


def test_dashboard_has_visible_detail_button(auth_client):
    auth_client.post("/habits/new", data={"name": "X"}, follow_redirects=False)
    r = auth_client.get("/")
    assert "Подробнее" in r.text
