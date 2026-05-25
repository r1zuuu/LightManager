import pytest
import sqlalchemy
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from webapp.main import app
from webapp.db import Base, get_db
from webapp import models

# Tworzymy osobną bazę testową działającą tylko w pamięci RAM
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=sqlalchemy.pool.StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    # Dla każdego testu czyścimy i tworzymy nową bazę
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session, mocker):
    # ZMockowanie mqtt_manager'a żeby nie wyrzucał żądań do publicznego brokera w trakcie testów
    mocker.patch(
        "webapp.services.switch_service.mqtt_manager.request_registration",
        return_value=True,
    )
    mocker.patch(
        "webapp.services.switch_service.mqtt_manager.publish", return_value=True
    )

    # Nadpisanie bazy danych z oryginalnej na testową
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client
