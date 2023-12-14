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


def get_projects(db: Session, username: str, project_visibility: rest.schemas.ProjectVisibility):
    filter = and_(models.Project.owner_username == username,
                  models.Project.visibility == project_visibility)
    return db.query(models.Project).filter(filter).all()


def create_project(db: Session, username: str, project: rest.schemas.ProjectCreate):
    db_project = models.Project(name=project.name,
                                description=project.description,
                                visibility=project.visibility,
                                owner_username=username)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project
