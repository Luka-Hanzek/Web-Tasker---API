from database import db_init
from rest import schemas
from database import crud
from database import models

from collections import defaultdict
from typing import List, Dict, Tuple

import os


database_path = db_init.get_db_path()
if os.path.exists(database_path):
    os.remove(database_path)

db_init.Base.metadata.create_all(bind=db_init.engine)



users = [
    dict(username='username01',
         email='username01@gmail.com',
         bio='username01 bio',
         role=schemas.Role.BASIC,
         password='username01_password'),
    dict(username='username02',
         email='username02@gmail.com',
         bio='username02 bio',
         role=schemas.Role.BASIC,
         password='username02_password'),
    dict(username='admin',
         email='admin@gmail.com',
         bio='admin bio',
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

user_projects_models: Dict[str, List[models.Project]] = defaultdict(list)

for username, user_projects in projects.items():
    for project in user_projects:
        create_project_schema = schemas.ProjectCreate(**project)
        project = crud.create_project(session, username, create_project_schema)
        user_projects_models[username].append(project)


tasks = {
    ('username01', user_projects_models['username01'][0].id): [
        dict(description=f'owner: username01\n'
                         f'project name: {user_projects_models["username01"][0].name}\n\n'
                         'Do this do that'),
        dict(description=f'owner: username01\n'
                         f'project name: {user_projects_models["username01"][1].name}\n\n'
                         'Do this do that')
    ]
}

for (username, project_id), user_tasks in tasks.items():
    for user_task in user_tasks:
        create_task_schema = schemas.TaskCreate(**user_task)
        project = crud.create_task(session, username, project_id, create_project_schema)

session.close()
