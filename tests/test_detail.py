from datetime import date, timedelta

from app.models import HabitLog


def _register_and_create(client, habit_name="Test"):
    client.post(
        "/register",
        data={
            "username": "tester",
            "password": "secret123",
            "password_confirm": "secret123",
        },
        follow_redirects=False,
    )
    client.post(
        "/habits/new",
        data={"name": habit_name, "color": "#22c55e"},
        follow_redirects=False,
    )


def test_detail_page_renders(auth_client):
    auth_client.post(
        "/habits/new",
        data={"name": "Run", "description": "morning run", "color": "#22c55e"},
        follow_redirects=False,
    )
    r = auth_client.get("/habits/1")
    assert r.status_code == 200
    assert "Run" in r.text
    assert "morning run" in r.text
    assert "Текущий стрик" in r.text
    assert "Хитмап" in r.text


def test_detail_empty_stats(auth_client):
    auth_client.post(
        "/habits/new", data={"name": "X"}, follow_redirects=False
    )
    r = auth_client.get("/habits/1")
    assert ">0<" in r.text 
    assert "Отметить сегодня" in r.text


def test_detail_streak_after_toggle(auth_client):
    auth_client.post(
        "/habits/new", data={"name": "X"}, follow_redirects=False
    )
    auth_client.post("/habits/1/toggle", follow_redirects=False)
    r = auth_client.get("/habits/1")
    assert "Сделано сегодня" in r.text
    assert ">1<" in r.text


def test_detail_streak_with_backfilled_logs(client, db_session):
    """Вставляем логи задним числом и проверяем что стрик считается верно."""
    _register_and_create(client, habit_name="Habit")

    today = date.today()
    for i in range(5):
        db_session.add(HabitLog(habit_id=1, date=today - timedelta(days=i)))
    db_session.commit()

    r = client.get("/habits/1")
    assert r.status_code == 200
    assert ">5<" in r.text


def test_detail_404_for_nonexistent(auth_client):
    r = auth_client.get("/habits/999")
    assert r.status_code == 404


def test_detail_404_for_others_habit(client):
    client.post(
        "/register",
        data={
            "username": "alice",
            "password": "secret123",
            "password_confirm": "secret123",
        },
        follow_redirects=False,
    )
    client.post("/habits/new", data={"name": "alice"}, follow_redirects=False)
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
    r = client.get("/habits/1")
    assert r.status_code == 404


def test_detail_redirect_anonymous(client):
    r = client.get("/habits/1", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/login"


def test_dashboard_links_to_detail(auth_client):
    auth_client.post(
        "/habits/new", data={"name": "Linked"}, follow_redirects=False
    )
    r = auth_client.get("/")
    assert 'href="/habits/1"' in r.text
