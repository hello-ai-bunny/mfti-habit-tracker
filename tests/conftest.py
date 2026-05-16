import os

os.environ.setdefault("SECRET_KEY", "test-secret-key")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app


@pytest.fixture
def db_engine():
    """In-memory SQLite, общий между client и db_session фикстурами."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """Прямой доступ к сессии БД для тестов, которые вставляют данные напрямую."""
    SessionLocal = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_engine):
    """TestClient, использующий ту же in-memory БД, что и db_session."""
    SessionLocal = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def auth_client(client):
    """Клиент, уже зарегистрированный и залогиненный как `tester`."""
    response = client.post(
        "/register",
        data={
            "username": "tester",
            "password": "secret123",
            "password_confirm": "secret123",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    return client
