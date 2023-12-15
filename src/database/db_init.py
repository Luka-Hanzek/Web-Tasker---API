from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os
from pathlib import Path


def get_db_path():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    parent_path = Path(dir_path).parent
    return str(parent_path.joinpath("database.db"))

engine = create_engine(
    f"sqlite:///{get_db_path()}", connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
