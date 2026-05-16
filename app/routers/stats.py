from datetime import date, timedelta

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Habit, HabitLog, User
from app.security import get_current_user
from app.stats import (
    build_heatmap,
    current_streak,
    done_in_last_n_days,
    longest_streak,
)
from app.templates import templates

router = APIRouter()


@router.get("/stats")
def stats_page(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    habits = db.scalars(
        select(Habit)
        .where(Habit.user_id == user.id, Habit.archived.is_(False))
        .order_by(Habit.created_at.desc())
    ).all()

    today = date.today()

    # Логи всех привычек юзера за один заход — без N+1
    logs_by_habit: dict[int, set[date]] = {h.id: set() for h in habits}
    if habits:
        rows = db.execute(
            select(HabitLog.habit_id, HabitLog.date).where(
                HabitLog.habit_id.in_([h.id for h in habits])
            )
        ).all()
        for habit_id, d in rows:
            logs_by_habit[habit_id].add(d)

    habit_stats = []
    for h in habits:
        dates = logs_by_habit[h.id]
        habit_stats.append(
            {
                "habit": h,
                "streak": current_streak(dates, today),
                "longest": longest_streak(dates),
                "total": len(dates),
                "today_done": today in dates,
                "week_done": done_in_last_n_days(dates, today, 7),
                "heatmap": build_heatmap(dates, today, days_back=83),  # ~12 недель
            }
        )

    # Агрегированные цифры
    total_habits = len(habits)
    today_done_count = sum(1 for s in habit_stats if s["today_done"])
    total_marks = sum(s["total"] for s in habit_stats)
    best_streak_overall = max((s["longest"] for s in habit_stats), default=0)

    # Активных дней за неделю (хоть одна привычка отмечена)
    all_dates: set[date] = set()
    for dates in logs_by_habit.values():
        all_dates |= dates
    active_days_week = sum(
        1 for i in range(7) if (today - timedelta(days=i)) in all_dates
    )

    # Общий хитмап: интенсивность = сколько привычек отмечено в этот день
    counts_by_date: dict[date, int] = {}
    for dates in logs_by_habit.values():
        for d in dates:
            counts_by_date[d] = counts_by_date.get(d, 0) + 1
    combined_heatmap = build_heatmap(all_dates, today, days_back=119)
    max_count_per_day = max(counts_by_date.values(), default=1)

    return templates.TemplateResponse(
        request,
        "stats.html",
        {
            "user": user,
            "habit_stats": habit_stats,
            "total_habits": total_habits,
            "today_done_count": today_done_count,
            "total_marks": total_marks,
            "best_streak_overall": best_streak_overall,
            "active_days_week": active_days_week,
            "combined_heatmap": combined_heatmap,
            "counts_by_date": counts_by_date,
            "max_count_per_day": max_count_per_day,
        },
    )
