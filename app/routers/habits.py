from datetime import date

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Habit, HabitLog, User
from app.security import get_current_user
from app.templates import templates

router = APIRouter(prefix="/habits")


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
    color: str = Form("#22c55e"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    name = name.strip()
    description = description.strip()

    error = None
    if not name:
        error = "Название не может быть пустым"
    elif len(name) > 100:
        error = "Название слишком длинное (максимум 100 символов)"
    elif len(description) > 500:
        error = "Описание слишком длинное (максимум 500 символов)"

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
    return RedirectResponse("/", status_code=303)


@router.post("/{habit_id}/delete")
def delete_habit(
    habit_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    habit = db.get(Habit, habit_id)
    if not habit or habit.user_id != user.id:
        raise HTTPException(status_code=404)
    db.delete(habit)
    db.commit()
    return RedirectResponse("/", status_code=303)


@router.post("/{habit_id}/toggle")
def toggle_today(
    habit_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    habit = db.get(Habit, habit_id)
    if not habit or habit.user_id != user.id:
        raise HTTPException(status_code=404)

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
