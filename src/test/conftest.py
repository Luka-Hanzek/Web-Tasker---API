import pytest

from fastapi.testclient import TestClient

from rest.main import app, get_db
from database.db_init import Base
from database import database_filler

from db import TestSessionLocal, engine, get_test_db


@pytest.fixture()
def db_session(create_database):
    gen = get_test_db()
    db = next(gen)
    yield db
    try:
        next(gen)
    except StopIteration:
        pass


@pytest.fixture()
def create_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def create_and_fill_database():
    Base.metadata.create_all(bind=engine)
    db = TestSessionLocal()
    database_filler.run(db)
    yield
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


app.dependency_overrides[get_db] = get_test_db
