import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware

from app.db import init_db
from app.models import User
from app.routers import auth
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


@app.get("/")
def index(request: Request, user: User | None = Depends(get_optional_user)):
    return templates.TemplateResponse(
        request, "index.html", {"user": user}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
