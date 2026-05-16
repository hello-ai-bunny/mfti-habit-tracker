from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User
from app.security import hash_password, verify_password
from app.templates import templates

router = APIRouter()


@router.get("/register")
def register_form(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(
        request, "auth/register.html", {"error": None}
    )


@router.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    db: Session = Depends(get_db),
):
    username = username.strip()
    error = None
    if len(username) < 3:
        error = "Имя пользователя должно быть от 3 символов"
    elif len(password) < 6:
        error = "Пароль должен быть от 6 символов"
    elif len(password.encode("utf-8")) > 72:
        error = "Пароль слишком длинный (максимум 72 байта)"
    elif password != password_confirm:
        error = "Пароли не совпадают"
    elif db.scalar(select(User).where(User.username == username)):
        error = "Пользователь с таким именем уже существует"

    if error:
        return templates.TemplateResponse(
            request,
            "auth/register.html",
            {"error": error, "username": username},
            status_code=400,
        )

    user = User(username=username, password_hash=hash_password(password))
    db.add(user)
    db.commit()

    request.session["user_id"] = user.id
    return RedirectResponse("/", status_code=303)


@router.get("/login")
def login_form(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(
        request, "auth/login.html", {"error": None}
    )


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.scalar(select(User).where(User.username == username.strip()))
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {"error": "Неверное имя пользователя или пароль", "username": username},
            status_code=400,
        )

    request.session["user_id"] = user.id
    return RedirectResponse("/", status_code=303)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
