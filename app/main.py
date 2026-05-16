import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

load_dotenv()

app = FastAPI(title="Habit Tracker")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return "<h1>Habit Tracker</h1>"
