from pathlib import Path

from fastapi.templating import Jinja2Templates

from app.flash import consume_flashes
from app.format import days_ago, days_word

TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

templates.env.globals["consume_flashes"] = consume_flashes
templates.env.filters["days_ago"] = days_ago
templates.env.filters["days_word"] = days_word
