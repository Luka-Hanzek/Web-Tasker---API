""" Sources:
    Basic auth: https://fastapi.tiangolo.com/advanced/security/http-basic-auth/#__tabbed_2_1

    WARNING: Currently using only SHA256 for password hashing without salting -> NOT SECURE
             Should use proper password hashing with bcrypt!!

"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from typing import Annotated, Optional, List

from sqlalchemy.orm import Session

import uvicorn

import database.db_init
import database.models

from database.db_init import SessionLocal
from database import crud

from utils import password_hasher

from rest.schemas import *


database.models.Base.metadata.create_all(bind=database.db_init.engine)

app = FastAPI()

security = HTTPBasic()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_user(credentials: Annotated[HTTPBasicCredentials, Depends(security)],
                db: Annotated[Session, Depends(get_db)]) -> Optional[User]:
    user = crud.get_user_by_username(db, credentials.username)
    if user is not None and \
            password_hasher.hash_password(credentials.password) == user.hashed_password:
        return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Incorrect username or password",
                        headers={"WWW-Authenticate": "Basic"})


class RoleChecker:
    def __init__(self, role: Role):
        self.role = role

    def __call__(self, db: Annotated[Session, Depends(get_db)],
                 credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
        user = crud.get_user_by_username(db, credentials.username)
        if user.role != self.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized"
            )
        return user


# Custom route for Swagger UI documentation
@app.get("/")
def custom_swagger_ui_html():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Swagger UI")


@app.get("/users/me")
def get_current_user(user: Annotated[User, Depends(verify_user)],
                     db: Annotated[Session, Depends(get_db)]) -> User:
    return crud.get_user_by_username(db, user.username)


@app.get("/users")
def get_users(user: Annotated[User, Depends(verify_user)],
              db: Annotated[Session, Depends(get_db)]) -> List[UserGetIdentity]:
    return crud.get_users(db)


@app.get("/users/{username}")
def get_user(user: Annotated[User, Depends(verify_user)],
              username: str,
              db: Annotated[Session, Depends(get_db)]) -> User:
    db_user = crud.get_user_by_username(db, username)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user


@app.patch("/users/{username}")
def update_user_info(user: Annotated[User, Depends(verify_user)],
                     username: str,
                     user_info: UserUpdateInfo,
                     db: Annotated[Session, Depends(get_db)]) -> UserGet:
    if username == user.username or user.role == Role.ADMIN:
        return crud.update_user_info(db, user.username, user_info)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
        )


@app.patch("/users/{user_id}/role", dependencies=[Depends(RoleChecker(Role.ADMIN))])
async def update_user_role(user: Annotated[User, Depends(verify_user)],
                           user_role_update: UserUpdateRole,
                           db: Annotated[Session, Depends(get_db)]):
    crud.update_user_role(db, user.username, user_role_update)


@app.post("/users/{username}/projects")
def create_project(username: str,
                   user: Annotated[User, Depends(verify_user)],
                   project_info: ProjectCreate,
                   db: Annotated[Session, Depends(get_db)]):
    if username != user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
        )
    project = crud.create_project(db, user.username, project_info)
    return project


@app.get("/users/{username}/projects")
def get_projects(username: str,
                 user: Annotated[User, Depends(verify_user)],
                 db: Annotated[Session, Depends(get_db)],
                 visibility: Optional[ProjectVisibility] = None):
    projects = []
    if visibility == ProjectVisibility.PRIVATE:
        if username != user.username and user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized"
            )
        projects.extend(crud.get_projects(db, username, ProjectVisibility.PRIVATE))
    elif visibility == ProjectVisibility.PUBLIC:
        projects.extend(crud.get_projects(db, username, ProjectVisibility.PUBLIC))
    elif visibility is None:
        if user.username == username or user.role == Role.ADMIN:
            projects.extend(crud.get_projects(db, username))
        projects.extend(crud.get_projects(db, username, ProjectVisibility.PUBLIC))
    return projects


@app.get("/users/{username}/projects/{project_id}")
def get_project(username: str,
                project_id: int,
                user: Annotated[User, Depends(verify_user)],
                db: Annotated[Session, Depends(get_db)],
                visibility: Optional[ProjectVisibility] = None):
    project = crud.get_project_by_id_and_owner_username(db, project_id, username)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    # We raise 404 to not revel whether private projects exists or not
    if username != user.username and project.visibility == ProjectVisibility.PRIVATE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project


@app.post("/users/{username}/projects/{project_id}/tasks")
def create_task(username: str,
                project_id: int,
                task: TaskCreate,
                user: Annotated[User, Depends(verify_user)],
                db: Annotated[Session, Depends(get_db)]):
    project = crud.get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    # We raise 404 to not revel whether private projects exists or not
    if username != user.username and project.visibility == ProjectVisibility.PRIVATE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    crud.create_task(db, user.username, project.id, task)


@app.get("/users/{username}/projects/{project_id}/tasks/{task_id}")
def get_task(username: str,
             project_id: int,
             task_id: int,
             user: Annotated[User, Depends(verify_user)],
             db: Annotated[Session, Depends(get_db)]):
    project = crud.get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    # We raise 404 to not revel whether private projects exists or not
    if username != user.username and project.visibility == ProjectVisibility.PRIVATE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    task = crud.get_task_by_id(db, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@app.get("/users/{username}/projects/{project_id}/tasks")
def get_tasks(username: str,
              project_id: int,
              user: Annotated[User, Depends(verify_user)],
              db: Annotated[Session, Depends(get_db)]):
    project = crud.get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    # We raise 404 to not revel whether private projects exists or not
    if username != user.username and project.visibility == ProjectVisibility.PRIVATE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return crud.get_tasks_by_project_id(db, project_id)


@app.patch("/users/{username}/projects/{project_id}/tasks/{task_id}")
def update_task(username: str,
                project_id: int,
                task_id: int,
                task_update_info: TaskUpdate,
                user: Annotated[User, Depends(verify_user)],
                db: Annotated[Session, Depends(get_db)]):
    project = crud.get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    # We raise 404 to not revel whether private projects exists or not
    if username != user.username and project.visibility == ProjectVisibility.PRIVATE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    task = crud.get_task_by_id(db, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return crud.update_task_info(db, task_id, task_update_info)


@app.delete("/users/{username}/projects/{project_id}/tasks")
def delete_task(username: str,
                project_id: int,
                task_id: int,
                user: Annotated[User, Depends(verify_user)],
                db: Annotated[Session, Depends(get_db)]):
    project = crud.get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    # We raise 404 to not revel whether private projects exists or not
    if username != user.username and project.visibility == ProjectVisibility.PRIVATE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    task = crud.get_task_by_id(db, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    sucess = crud.delete_task(db, task_id)
    if not sucess:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Task could not be deleted"
        )
    raise HTTPException(
        status_code=status.HTTP_200_OK
    )


@app.post("/users/{username}/projects/{project_id}/tasks/{task_id}/start")
def start_task(username: str,
                project_id: int,
                task_id: int,
                user: Annotated[User, Depends(verify_user)],
                db: Annotated[Session, Depends(get_db)]):
    project = crud.get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    # We raise 404 to not revel whether private projects exists or not
    if username != user.username and project.visibility == ProjectVisibility.PRIVATE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    task = crud.get_task_by_id(db, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    if task.start_timestamp is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task already started"
        )
    sucess = crud.start_task(db, task_id)
    if not sucess:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Task could not be started"
        )
    raise HTTPException(
        status_code=status.HTTP_200_OK
    )


@app.post("/users/{username}/projects/{project_id}/tasks/{task_id}/stop")
def stop_task(username: str,
              project_id: int,
              task_id: int,
              user: Annotated[User, Depends(verify_user)],
              db: Annotated[Session, Depends(get_db)]):
    project = crud.get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    # We raise 404 to not revel whether private projects exists or not
    if username != user.username and project.visibility == ProjectVisibility.PRIVATE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    task = crud.get_task_by_id(db, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    if task.start_timestamp is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot stop task that wasn't started"
        )
    if task.end_timestamp is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task already stopped"
        )
    sucess = crud.stop_task(db, task_id)
    if not sucess:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Task could not be stopped"
        )
    raise HTTPException(
        status_code=status.HTTP_200_OK
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
