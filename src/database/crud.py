import datetime

import sqlalchemy.exc
from sqlalchemy.orm import Session
from sqlalchemy import and_

from typing import Optional

from . import models
import rest.schemas
from utils import password_hasher


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: rest.schemas.UserCreate):
    hashed_password = password_hasher.hash_password(user.password)
    db_user = models.User(username=user.username,
                          email=user.email,
                          bio=user.bio,
                          role=user.role,
                          hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_info(db: Session, username: str, user_info: rest.schemas.UserUpdateInfo):
    db_user = get_user_by_username(username)
    if user_info.email is not None:
        db_user.email = user_info.email
    if user_info.bio is not None:
        db_user.bio = user_info.bio

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_role(db: Session, username: str, user: rest.schemas.UserUpdateRole):
    db_user = get_user_by_username(db, username)
    db_user.role = user.role
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_projects(db: Session, username: str,
                 project_visibility: Optional[rest.schemas.ProjectVisibility] = None):
    conditions = [
        models.Project.owner_username == username,
        models.Project.visibility == project_visibility if project_visibility is not None else True
    ]
    return db.query(models.Project).filter(and_(*conditions)).all()


def get_project_by_id(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()


def create_project(db: Session, username: str, project: rest.schemas.ProjectCreate):
    db_project = models.Project(name=project.name,
                                description=project.description,
                                visibility=project.visibility,
                                owner_username=username)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def create_task(db: Session, username: str, project_id: int, task: rest.schemas.TaskCreate):
    task_db = models.Task(description=task.description,
                          owner_username=username,
                          project_id=project_id)
    db.add(task_db)
    db.commit()
    db.refresh(task_db)
    return task_db


def get_tasks_by_owner_username(db: Session, username: str,
                                project_visibility: Optional[rest.schemas.ProjectVisibility] = None):
    if project_visibility is None:
        return db.query(models.Task).filter(models.Task.owner_username == username).all()
    return db.query(models.Task).join(models.Project).filter(
        and_(
            models.Task.owner_username == username,
            models.Project.visibility == project_visibility
        )
    ).all()


def get_tasks_by_project_id(db: Session, project_id: int,
                            project_visibility: Optional[rest.schemas.ProjectVisibility] = None):
    if project_visibility is None:
        return db.query(models.Task).filter(models.Task.project_id == project_id).all()
    return db.query(models.Task).join(models.Project).filter(
        and_(
            models.Task.project_id == project_id,
            models.Project.visibility == project_visibility
        )
    ).all()


def get_tasks_by_owner_username_and_project_id(db: Session, username: str, project_id: int,
                                               project_visibility: Optional[rest.schemas.ProjectVisibility] = None):
    conditions = [
        models.Task.owner_username == username,
        models.Task.project_id == project_id
    ]
    if project_visibility is None:
        return db.query(models.Task).filter(and_(*conditions)).all()
    return db.query(models.Task).join(models.Project).filter(
        and_(
            *conditions,
            models.Project.visibility == project_visibility
        )
    ).all()


def get_task_by_id(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def update_task_info(db: Session, task_id: int, task_info: rest.schemas.TaskUpdate):
    db_task = get_task_by_id(db, task_id)
    if task_info.description is not None:
        db_task.description = task_info.description
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int):
    try:
        db_task = get_task_by_id(db, task_id)
        db.delete(db_task)
        db.commit()
    except sqlalchemy.exc.DatabaseError:
        return False
    return True


def start_task(db: Session, task_id: int):
    try:
        now = datetime.datetime.now()
        db_task = get_task_by_id(db, task_id)
        db_task.start_timestamp = now
        db.add(db_task)
        db.commit()
    except sqlalchemy.exc.DatabaseError:
        return False
    return True


def stop_task(db: Session, task_id: int):
    try:
        now = datetime.datetime.now()
        db_task = get_task_by_id(db, task_id)
        db_task.end_timestamp = now
        db.add(db_task)
        db.commit()
    except sqlalchemy.exc.DatabaseError:
        return False
    return True
