import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app.db import get_db, init_db
from app.models import Habit, User
from app.routers import auth, habits
from app.security import get_optional_user
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

app.include_router(auth.router)
app.include_router(habits.router)


@app.get("/")
def index(
    request: Request,
    user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    if user is None:
        return templates.TemplateResponse(request, "index.html", {"user": None})

    user_habits = db.scalars(
        select(Habit)
        .where(Habit.user_id == user.id, Habit.archived.is_(False))
        .order_by(Habit.created_at.desc())
    ).all()

    return templates.TemplateResponse(
        request,
        "habits/dashboard.html",
        {"user": user, "habits": user_habits},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
