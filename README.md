# Habit Tracker

Веб-приложение для отслеживания привычек: создание привычек, отметка выполнения, хитмап и статистика.


## Стек

FastAPI · Jinja2 · SQLAlchemy 2.0 · SQLite · bcrypt · Starlette sessions · Bootstrap 5 · pytest

## Запуск

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/Mac

pip install -r requirements.txt
cp .env.example .env           

python -m app.main
```

Открыть `http://localhost:8000`

## Тесты

```bash
pytest
```

## Структура

```
app/
├── main.py            # FastAPI, middleware, 404
├── db.py              # engine, SessionLocal
├── models.py          # User, Habit, HabitLog
├── security.py        # bcrypt, get_current_user
├── stats.py           # стрики, хитмап
├── routers/           # auth, habits, stats
├── static/style.css
└── templates/
tests/
```
