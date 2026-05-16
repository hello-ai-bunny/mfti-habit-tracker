# Habit Tracker

Веб-приложение для отслеживания привычек

## Стек

- **FastAPI** — веб-фреймворк
- **Jinja2** — серверный рендеринг шаблонов
- **SQLAlchemy** + **SQLite** — ORM и БД
- **passlib[bcrypt]** — хеширование паролей
- **Starlette SessionMiddleware** — сессии в куках
- **Bootstrap 5** — стили 

## Запуск

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env

python -m app.main
```

Открыть http://localhost:8000

## Возможности


## Структура проекта

```
habit-tracker/
├── app/
│   ├── main.py            
│   └── ...
├── requirements.txt
├── .env.example
└── README.md
```
