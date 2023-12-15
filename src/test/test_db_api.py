from rest.schemas import (UserCreate, UserUpdateInfo, UserUpdateRole, ProjectCreate,
                          TaskCreate, Role, ProjectVisibility)

from database import crud


def test_create_user(db_session):
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword",
        "bio": "Test bio",
        "role": Role.BASIC,
    }
    user_create = UserCreate(**user_data)

    created_user = crud.create_user(db_session, user_create)

    assert created_user.username == user_data["username"]
    assert created_user.email == user_data["email"]
    assert created_user.bio == user_data["bio"]
    assert created_user.role == user_data["role"]


def test_get_user_by_username(db_session):
    existing_user = UserCreate(
        username="existing_user",
        email="existing@example.com",
        password="existing_password",
        bio="Existing bio",
        role=Role.BASIC,
    )
    db_user = crud.create_user(db_session, existing_user)

    retrieved_user = crud.get_user_by_username(db_session, db_user.username)

    assert retrieved_user.username == db_user.username
    assert retrieved_user.email == db_user.email
    assert retrieved_user.bio == db_user.bio
    assert retrieved_user.role == db_user.role


def test_update_user_info(db_session):
    existing_user = UserCreate(
        username="existing_user",
        email="existing@example.com",
        password="existing_password",
        bio="Existing bio",
        role=Role.BASIC,
    )
    db_user = crud.create_user(db_session, existing_user)

    update_info = UserUpdateInfo(email="new_email@example.com", bio="New bio")

    updated_user = crud.update_user_info(db_session, db_user.username, update_info)

    assert updated_user.email == update_info.email
    assert updated_user.bio == update_info.bio


def test_update_user_role(db_session):
    existing_user = UserCreate(
        username="existing_user",
        email="existing@example.com",
        password="existing_password",
        bio="Existing bio",
        role=Role.BASIC,
    )
    db_user = crud.create_user(db_session, existing_user)

    update_role = UserUpdateRole(role=Role.ADMIN)

    updated_user = crud.update_user_role(db_session, db_user.username, update_role)

    assert updated_user.role == update_role.role


def test_create_get_projects(db_session):
    user1 = UserCreate(
        username="user1",
        email="user1@example.com",
        password="password",
        bio="Existing bio",
        role=Role.BASIC,
    )
    db_user1 = crud.create_user(db_session, user1)

    project_data1 = {
        "name": "user1 project",
        "description": "Test description",
        "visibility": ProjectVisibility.PRIVATE,
        "owner_username": db_user1.username,
    }
    project_create = ProjectCreate(**project_data1)
    created_project1 = crud.create_project(db_session, db_user1.username, project_create)

    user2 = UserCreate(
        username="user2",
        email="user2@example.com",
        password="password",
        bio="Existing bio",
        role=Role.BASIC,
    )
    db_user2 = crud.create_user(db_session, user2)

    project_data2 = {
        "name": "user2 project",
        "description": "Test description",
        "visibility": ProjectVisibility.PUBLIC,
        "owner_username": db_user2.username,
    }
    project_create = ProjectCreate(**project_data2)
    created_project2 = crud.create_project(db_session, db_user2.username, project_create)

    projects = crud.get_projects(db_session, db_user1.username)
    assert len(projects) == 1
    assert projects[0].id == created_project1.id
    assert projects[0].name == project_data1["name"]
    assert projects[0].description == project_data1["description"]
    assert projects[0].visibility == project_data1["visibility"]
    assert projects[0].owner_username == project_data1["owner_username"]

    project = crud.get_project_by_id(db_session, created_project2.id)
    assert project.id == created_project2.id
    assert project.name == project_data2["name"]
    assert project.description == project_data2["description"]
    assert project.visibility == project_data2["visibility"]
    assert project.owner_username == project_data2["owner_username"]

    projects = crud.get_projects_by_owner_username_and_name(db_session,
                                                            db_user1.username,
                                                            created_project1.name)
    assert len(projects) == 1
    project = projects[0]
    assert project.id == created_project1.id
    assert project.name == project_data1["name"]
    assert project.description == project_data1["description"]
    assert project.visibility == project_data1["visibility"]
    assert project.owner_username == project_data1["owner_username"]

    project = crud.get_project_by_id_and_owner_username(db_session, created_project1.id,
                                                        db_user1.username)
    assert project.id == created_project1.id
    assert project.name == project_data1["name"]
    assert project.description == project_data1["description"]
    assert project.visibility == project_data1["visibility"]
    assert project.owner_username == project_data1["owner_username"]


def test_create_task(db_session):
    user = UserCreate(
        username="user1",
        email="user1@example.com",
        password="password",
        bio="Existing bio",
        role=Role.BASIC,
    )
    db_user = crud.create_user(db_session, user)

    project_data1 = {
        "name": "user1 project",
        "description": "Test description",
        "visibility": ProjectVisibility.PRIVATE,
        "owner_username": db_user.username,
    }
    project_create = ProjectCreate(**project_data1)
    created_project = crud.create_project(db_session, db_user.username, project_create)

    task_data = {
        "description": "Test Task",
    }
    task_create = TaskCreate(**task_data)

    created_task = crud.create_task(db_session, db_user.username, created_project.id, task_create)

    assert created_task.description == task_data["description"]
    assert created_task.owner_username == db_user.username
    assert created_task.project_id == created_project.id
    assert created_task.start_timestamp is None
    assert created_task.end_timestamp is None


def test_get_tasks_by_owner_username(db_session):
    user = UserCreate(
        username="user1",
        email="user1@example.com",
        password="password",
        bio="Existing bio",
        role=Role.BASIC,
    )
    db_user = crud.create_user(db_session, user)

    project_data = {
        "name": "user1 project",
        "description": "Test description",
        "visibility": ProjectVisibility.PRIVATE,
        "owner_username": db_user.username,
    }
    project_create = ProjectCreate(**project_data)
    created_project = crud.create_project(db_session, db_user.username, project_create)

    task_data = {
        "description": "Test Task",
    }
    task_create = TaskCreate(**task_data)

    created_task = crud.create_task(db_session, db_user.username, created_project.id, task_create)

    tasks = crud.get_tasks_by_owner_username(db_session, db_user.username)

    assert len(tasks) == 1
    assert tasks[0].id == created_task.id
    assert tasks[0].description == task_data["description"]
    assert tasks[0].owner_username == db_user.username
    assert tasks[0].start_timestamp is None
    assert tasks[0].end_timestamp is None


def test_start_stop_task(db_session):
    user = UserCreate(
        username="user1",
        email="user1@example.com",
        password="password",
        bio="Existing bio",
        role=Role.BASIC,
    )
    db_user = crud.create_user(db_session, user)

    project_data = {
        "name": "user1 project",
        "description": "Test description",
        "visibility": ProjectVisibility.PRIVATE,
        "owner_username": db_user.username,
    }
    project_create = ProjectCreate(**project_data)
    created_project = crud.create_project(db_session, db_user.username, project_create)

    task_data = {
        "description": "Test Task",
    }
    task_create = TaskCreate(**task_data)

    created_task = crud.create_task(db_session, db_user.username, created_project.id, task_create)

    tasks = crud.get_tasks_by_owner_username(db_session, db_user.username)

    assert tasks[0].start_timestamp is None
    assert tasks[0].end_timestamp is None

    crud.start_task(db_session, tasks[0].id)
    task = crud.get_task_by_id(db_session, tasks[0].id)
    assert task.start_timestamp is not None
    assert task.end_timestamp is None

    crud.stop_task(db_session, tasks[0].id)
    task = crud.get_task_by_id(db_session, tasks[0].id)
    assert task.start_timestamp is not None
    assert task.end_timestamp is not None
