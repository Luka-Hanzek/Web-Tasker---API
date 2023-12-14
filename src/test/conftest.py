import fastapi
import pytest

from sqlalchemy import create_engine, StaticPool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from rest.main import app, get_db


DATABASE_URL = 'sqlite:///:memory:'


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_test_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = get_test_db
