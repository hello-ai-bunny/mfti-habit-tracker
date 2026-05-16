from datetime import date, timedelta
from typing import TypedDict


class HeatmapCell(TypedDict):
    date: date
    logged: bool
    in_range: bool
    is_today: bool


def current_streak(logged_dates: set[date], today: date) -> int:
    """Сколько дней подряд привычка отмечалась.
    """
    streak = 0
    d = today
    while d in logged_dates:
        streak += 1
        d -= timedelta(days=1)
    return streak


def longest_streak(logged_dates: set[date]) -> int:
    """Самый длинный стрик за всё время логов."""
    if not logged_dates:
        return 0
    sorted_dates = sorted(logged_dates)
    longest = 1
    current = 1
    for prev, curr in zip(sorted_dates, sorted_dates[1:]):
        if (curr - prev).days == 1:
            current += 1
            longest = max(longest, current)
        else:
            current = 1
    return longest


def done_in_last_n_days(logged_dates: set[date], today: date, n: int) -> int:
    """Количество отметок в последние n дней."""
    return sum(
        1 for i in range(n) if (today - timedelta(days=i)) in logged_dates
    )


def build_heatmap(
    logged_dates: set[date],
    today: date,
    days_back: int = 119,
) -> list[list[HeatmapCell]]:
    """Сетка по неделям для хитмапа.

    Возвращает список колонок-недель.
    Каждая колонка — список из 7 ячеек.
    """
    start = today - timedelta(days=days_back)
    start_monday = start - timedelta(days=start.weekday())

    weeks: list[list[HeatmapCell]] = []
    current = start_monday
    while current <= today:
        week: list[HeatmapCell] = []
        for i in range(7):
            d = current + timedelta(days=i)
            week.append(
                HeatmapCell(
                    date=d,
                    logged=d in logged_dates,
                    in_range=start <= d <= today,
                    is_today=d == today,
                )
            )
        weeks.append(week)
        current += timedelta(days=7)
    return weeks
