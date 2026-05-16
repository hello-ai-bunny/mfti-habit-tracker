from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.db import init_db

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Habit Tracker", lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return "<h1>Habit Tracker</h1>"
