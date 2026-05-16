import os
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from app.db import get_db, init_db
from app.models import Habit, HabitLog, User
from app.routers import auth, habits, stats
from app.security import get_optional_user
from app.stats import current_streak
from app.templates import templates

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Habit Tracker", lifespan=lifespan)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "123"),
)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(auth.router)
app.include_router(habits.router)
app.include_router(stats.router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code in (301, 302, 303, 307, 308):
        return Response(status_code=exc.status_code, headers=exc.headers or {})
    if exc.status_code == 404:
        return templates.TemplateResponse(
            request, "404.html", {"user": None}, status_code=404
        )
    raise exc


@app.get("/")
def index(
    request: Request,
    sort: str = "created",
    user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    if user is None:
        return templates.TemplateResponse(request, "index.html", {"user": None})

    query = select(Habit).where(
        Habit.user_id == user.id, Habit.archived.is_(False)
    )
    if sort == "name":
        query = query.order_by(Habit.name.asc())
    else:
        query = query.order_by(Habit.created_at.desc())

    user_habits = list(db.scalars(query).all())

    today = date.today()
    habit_ids = [h.id for h in user_habits]
    today_done: set[int] = set()
    streak_by_habit: dict[int, int] = {}
    days_since_by_habit: dict[int, int] = {}

    if habit_ids:
        today_done = set(
            db.scalars(
                select(HabitLog.habit_id).where(
                    HabitLog.date == today,
                    HabitLog.habit_id.in_(habit_ids),
                )
            ).all()
        )

        log_rows = db.execute(
            select(HabitLog.habit_id, HabitLog.date).where(
                HabitLog.habit_id.in_(habit_ids)
            )
        ).all()
        dates_by_habit: dict[int, set[date]] = {hid: set() for hid in habit_ids}
        for hid, d in log_rows:
            dates_by_habit[hid].add(d)
        streak_by_habit = {
            hid: current_streak(dates_by_habit[hid], today) for hid in habit_ids
        }
        days_since_by_habit = {
            h.id: (today - h.created_at.date()).days for h in user_habits
        }

    if sort == "streak":
        user_habits.sort(key=lambda h: streak_by_habit.get(h.id, 0), reverse=True)

    return templates.TemplateResponse(
        request,
        "habits/dashboard.html",
        {
            "user": user,
            "habits": user_habits,
            "today_done": today_done,
            "streak_by_habit": streak_by_habit,
            "days_since_by_habit": days_since_by_habit,
            "sort": sort,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
