from database import db_init
from rest import schemas
from database import crud

import os

database_path = db_init.get_db_path()
if os.path.exists(database_path):
    os.remove(database_path)

db_init.Base.metadata.create_all(bind=db_init.engine)



users = [
    dict(username='username01',
         email='username01@gmail.com',
         age=21,
         role=schemas.Role.BASIC,
         password='username01_password'),
    dict(username='username02',
         email='username02@gmail.com',
         age=25,
         role=schemas.Role.BASIC,
         password='username02_password'),
    dict(username='admin',
         email='admin@gmail.com',
         age=50,
         role=schemas.Role.ADMIN,
         password='admin')
]

session = db_init.SessionLocal()

for user in users:
    user_schema = schemas.UserCreate(**user)
    crud.create_user(session, user_schema)


projects = dict(
    username01=[
        dict(name='username01_project01',
             description='username01_project01 description',
             visibility=schemas.ProjectVisibility.PRIVATE),
        dict(name='username01_project02',
             description='username01_project02 description',
             visibility=schemas.ProjectVisibility.PRIVATE),
    ],
    username02=[
        dict(name='username02_project01',
             description='username02_project01 description',
             visibility=schemas.ProjectVisibility.PUBLIC),
        dict(name='username02_project02',
             description='username02_project02 description',
             visibility=schemas.ProjectVisibility.PRIVATE),
    ],
    admin=[
        dict(name='admin_project01',
             description='admin_project01 description',
             visibility=schemas.ProjectVisibility.PRIVATE),
        dict(name='username01_project02',
             description='admin_project02 description',
             visibility=schemas.ProjectVisibility.PRIVATE),
    ]
)

for username, user_projects in projects.items():
    for user_project in user_projects:
        create_project_schema = schemas.ProjectCreate(**user_project)
        crud.create_project(session, username, create_project_schema)

session.close()
