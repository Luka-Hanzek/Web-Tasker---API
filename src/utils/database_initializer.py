from database import database_filler
from database.db_init import SessionLocal, Base, engine, get_db_path

import os


db_path = get_db_path()

if os.path.exists(db_path):
    os.remove(db_path)

session = SessionLocal()

Base.metadata.create_all(bind=engine)

database_filler.run(session)

session.close()
