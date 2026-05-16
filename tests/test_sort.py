from datetime import date, timedelta

from app.models import HabitLog


def test_default_sort_by_created_desc(client, db_session):
    """С разными created_at: новые сверху."""
    client.post(
        "/register",
        data={
            "username": "tester",
            "password": "secret123",
            "password_confirm": "secret123",
        },
        follow_redirects=False,
    )
    # Создаём через API, затем выставим явные created_at через db_session
    client.post("/habits/new", data={"name": "Older"}, follow_redirects=False)
    client.post("/habits/new", data={"name": "Newer"}, follow_redirects=False)

    from app.models import Habit

    older = db_session.get(Habit, 1)
    newer = db_session.get(Habit, 2)
    from datetime import datetime, timedelta as td

    base = datetime(2026, 1, 1, 12, 0, 0)
    older.created_at = base
    newer.created_at = base + td(days=10)
    db_session.commit()

    # съесть flashes от создания
    client.get("/")
    r = client.get("/")
    # Newer создана позже → должна быть выше
    assert r.text.index("Newer") < r.text.index("Older")


def test_sort_by_name(client, db_session):
    client.post(
        "/register",
        data={
            "username": "tester",
            "password": "secret123",
            "password_confirm": "secret123",
        },
        follow_redirects=False,
    )
    client.post("/habits/new", data={"name": "Zebra"}, follow_redirects=False)
    client.post("/habits/new", data={"name": "Alpha"}, follow_redirects=False)
    # съесть flashes
    client.get("/")
    r = client.get("/?sort=name")
    assert r.text.index("Alpha") < r.text.index("Zebra")


def test_sort_by_streak(client, db_session):
    client.post(
        "/register",
        data={
            "username": "tester",
            "password": "secret123",
            "password_confirm": "secret123",
        },
        follow_redirects=False,
    )
    client.post("/habits/new", data={"name": "Low"}, follow_redirects=False)
    client.post("/habits/new", data={"name": "High"}, follow_redirects=False)

    today = date.today()
    # High → 5 дней подряд, Low → 1 день
    for i in range(5):
        db_session.add(HabitLog(habit_id=2, date=today - timedelta(days=i)))
    db_session.add(HabitLog(habit_id=1, date=today))
    db_session.commit()

    # съесть flashes
    client.get("/")
    r = client.get("/?sort=streak")
    assert r.text.index("High") < r.text.index("Low")
