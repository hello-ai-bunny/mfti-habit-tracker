from datetime import date

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.flash import flash
from app.models import Habit, HabitLog, User
from app.security import get_current_user
from app.stats import (
    build_heatmap,
    current_streak,
    done_in_last_n_days,
    longest_streak,
)
from app.templates import templates

router = APIRouter(prefix="/habits")


def _validate_habit_input(name: str, description: str) -> str | None:
    if not name:
        return "Название не может быть пустым"
    if len(name) > 100:
        return "Название слишком длинное (максимум 100 символов)"
    if len(description) > 500:
        return "Описание слишком длинное (максимум 500 символов)"
    return None


def _load_owned_habit(habit_id: int, user: User, db: Session) -> Habit:
    habit = db.get(Habit, habit_id)
    if not habit or habit.user_id != user.id:
        raise HTTPException(status_code=404)
    return habit


@router.get("/new")
def new_habit_form(
    request: Request,
    user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        request,
        "habits/new.html",
        {"user": user, "error": None},
    )


@router.post("/new")
def create_habit(
    request: Request,
    name: str = Form(""),
    description: str = Form(""),
    color: str = Form("#4f46e5"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    name = name.strip()
    description = description.strip()

    error = _validate_habit_input(name, description)
    if error:
        return templates.TemplateResponse(
            request,
            "habits/new.html",
            {
                "user": user,
                "error": error,
                "name": name,
                "description": description,
                "color": color,
            },
            status_code=400,
        )

    habit = Habit(
        user_id=user.id,
        name=name,
        description=description,
        color=color,
    )
    db.add(habit)
    db.commit()
    flash(request, f"Привычка «{habit.name}» создана", "success")
    return RedirectResponse("/", status_code=303)


@router.get("/{habit_id}/edit")
def edit_habit_form(
    habit_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    habit = _load_owned_habit(habit_id, user, db)
    return templates.TemplateResponse(
        request,
        "habits/edit.html",
        {"user": user, "habit": habit, "error": None},
    )


@router.post("/{habit_id}/edit")
def edit_habit(
    habit_id: int,
    request: Request,
    name: str = Form(""),
    description: str = Form(""),
    color: str = Form("#4f46e5"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    habit = _load_owned_habit(habit_id, user, db)
    name = name.strip()
    description = description.strip()

    error = _validate_habit_input(name, description)
    if error:
        habit.name = name
        habit.description = description
        habit.color = color
        return templates.TemplateResponse(
            request,
            "habits/edit.html",
            {"user": user, "habit": habit, "error": error},
            status_code=400,
        )

    habit.name = name
    habit.description = description
    habit.color = color
    db.commit()
    flash(request, "Привычка обновлена", "success")
    return RedirectResponse(f"/habits/{habit_id}", status_code=303)


@router.post("/{habit_id}/delete")
def delete_habit(
    habit_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    habit = _load_owned_habit(habit_id, user, db)
    habit_name = habit.name
    db.delete(habit)
    db.commit()
    flash(request, f"Привычка «{habit_name}» удалена", "info")
    return RedirectResponse("/", status_code=303)


@router.get("/{habit_id}")
def habit_detail(
    habit_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    habit = _load_owned_habit(habit_id, user, db)

    logged_dates: set[date] = set(
        db.scalars(
            select(HabitLog.date).where(HabitLog.habit_id == habit_id)
        ).all()
    )
    today = date.today()

    days_since_creation = max(1, (today - habit.created_at.date()).days + 1)
    active_percent = round(len(logged_dates) / days_since_creation * 100)

    return templates.TemplateResponse(
        request,
        "habits/detail.html",
        {
            "user": user,
            "habit": habit,
            "today_done": today in logged_dates,
            "streak": current_streak(logged_dates, today),
            "longest": longest_streak(logged_dates),
            "total": len(logged_dates),
            "week_done": done_in_last_n_days(logged_dates, today, 7),
            "month_done": done_in_last_n_days(logged_dates, today, 30),
            "heatmap_weeks": build_heatmap(logged_dates, today, days_back=119),
            "days_since_creation": days_since_creation,
            "active_percent": active_percent,
        },
    )


@router.post("/{habit_id}/toggle")
def toggle_today(
    habit_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    habit = _load_owned_habit(habit_id, user, db)
    today = date.today()
    existing = db.scalar(
        select(HabitLog).where(
            HabitLog.habit_id == habit_id,
            HabitLog.date == today,
        )
    )
    if existing:
        db.delete(existing)
    else:
        db.add(HabitLog(habit_id=habit_id, date=today))
    db.commit()
    return RedirectResponse("/", status_code=303)
