import contextlib

from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

DATABASE_URL = 'sqlite:///:memory:'


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_test_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextlib.contextmanager
def db_session():
    gen = get_test_db()
    db = next(gen)
    yield db
    try:
        next(gen)
    except StopIteration:
        pass
