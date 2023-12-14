from sqlalchemy import Enum, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from .db_init import Base
from rest.schemas import user, project, task


class User(Base):
    __tablename__ = 'users'

    username = Column(String, primary_key=True)
    email = Column(String, unique=True)
    age = Column(Integer, nullable=False)
    hashed_password = Column(String)
    role = Column(Enum(user.Role), nullable=False)

    projects = relationship('Project', back_populates='owner')
    tasks = relationship('Task', back_populates='owner')

    @property
    def project_ids(self):
        return [project.id for project in self.projects]

    @property
    def task_ids(self):
        return [task.id for task in self.tasks]


class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    visibility = Column(Enum(project.ProjectVisibility), nullable=False)
    owner_username = Column(Integer, ForeignKey('users.username'))

    owner = relationship('User', back_populates='projects')
    tasks = relationship('Task', back_populates='project')

    @property
    def task_ids(self):
        return [task.id for task in self.tasks]


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    start_timestamp = Column(DateTime, nullable=True)
    end_timestamp = Column(DateTime, nullable=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    owner_username = Column(Integer, ForeignKey('users.username'))

    project = relationship('Project', back_populates='tasks')
    owner = relationship('User', back_populates='tasks')
