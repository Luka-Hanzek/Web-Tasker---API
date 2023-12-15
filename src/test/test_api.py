import itertools

from fastapi import status
from rest.main import description
import rest.schemas

from database import database_filler

import base64


def _get_credentials(user):
    return base64.b64encode(f"{user['username']}:{user['password']}".encode('utf-8')).decode("utf-8")


_credentials = [_get_credentials(user) for user in database_filler.users]
user_credentials, admin_credentials = _credentials[:-1], _credentials[-1]


def test_root_path_doc(client, create_and_fill_database):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert description in response.content.decode('utf-8')


def test_get_current_user(client, create_and_fill_database):
    def coerce(value):
        if isinstance(value, rest.schemas.Role):
            return value.value
        return value

    excluded_keys = ['password']

    for credentials, user in zip(user_credentials + [admin_credentials], database_filler.users):
        response = client.get("/api/users/me", headers={"Authorization": f"Basic {credentials}"})
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {k: coerce(v) for k, v in user.items() if k not in excluded_keys}

    wrong_credentials = _get_credentials(dict(username='nonexistent', password='wrong_password'))
    response = client.get("/api/users/me", headers={"Authorization": f"Basic {wrong_credentials}"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_users(client, create_and_fill_database):
    response = client.get("/api/users", headers={"Authorization": f"Basic {admin_credentials}"})
    assert response.status_code == status.HTTP_200_OK
    for expected_user, actual_user in zip(database_filler.users, response.json()):
        assert expected_user['username'] == actual_user['username']


def test_update_user_info(client, create_and_fill_database):
    user = database_filler.users[0]
    credentials = _credentials[0]

    update_info = rest.schemas.UserUpdateInfo(bio='new bio',
                                              email='new@mail.com')
    response = client.patch(f"/api/users/{user['username']}",
                            headers={"Authorization": f"Basic {credentials}"},
                            json=update_info.model_dump())

    def coerce(value):
        if isinstance(value, rest.schemas.Role):
            return value.value
        return value
    excluded_keys = ['password']

    assert response.status_code == status.HTTP_200_OK
    user_expected = {k: coerce(v)
                     for k, v in user.items()
                     if k not in excluded_keys}
    # NOTE: Returned user may have additional data that is not checked
    user_actual = response.json()
    for k, v in user_expected.items():
        assert user_actual[k] == update_info.model_dump().get(k, v)

    response = client.patch(f"/api/users/{user['username']}",
                            headers={"Authorization": f"Basic {user_credentials[1]}"},
                            json=update_info.model_dump())
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_user_role(client, create_and_fill_database):
    new_role_info = rest.schemas.UserUpdateRole(role=rest.schemas.Role.ADMIN.value)
    response = client.patch(f"/api/users/{database_filler.users[1]['username']}",
                            headers={"Authorization": f"Basic {user_credentials[0]}"},
                            json=new_role_info.model_dump(mode='json'))
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = client.patch(f"/api/users/{database_filler.users[0]['username']}",
                            headers={"Authorization": f"Basic {admin_credentials}"},
                            json=new_role_info.model_dump(mode='json'))
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['role'] == rest.schemas.Role.ADMIN.value


def test_get_project(client, create_and_fill_database):
    user = database_filler.users[0]

    # All projects
    response = client.get(f"/api/users/{user['username']}/projects",
                          headers={"Authorization": f"Basic {user_credentials[0]}"})
    assert response.status_code == status.HTTP_200_OK
    projects_actual = response.json()
    assert len(projects_actual) == len(database_filler.projects[user['username']])

    user = database_filler.users[1]

    # Public projects
    response = client.get(f"/api/users/{user['username']}/projects",
                          headers={"Authorization": f"Basic {user_credentials[1]}"},
                          params={'visibility': 'public'})
    assert response.status_code == status.HTTP_200_OK
    projects_actual = response.json()
    assert len(projects_actual) == len([p for p in database_filler.projects[user['username']]
                                        if p['visibility'] == rest.schemas.ProjectVisibility.PUBLIC])
    assert projects_actual[0]['visibility'] == rest.schemas.ProjectVisibility.PUBLIC.value

    # Private projects
    response = client.get(f"/api/users/{user['username']}/projects",
                          headers={"Authorization": f"Basic {user_credentials[1]}"},
                          params={'visibility': 'private'})
    assert response.status_code == status.HTTP_200_OK
    projects_actual = response.json()
    assert len(projects_actual) == len([p for p in database_filler.projects[user['username']]
                                        if p['visibility'] == rest.schemas.ProjectVisibility.PRIVATE])
    assert projects_actual[0]['visibility'] == rest.schemas.ProjectVisibility.PRIVATE.value

    response = client.get(f"/api/users/{database_filler.users[0]['username']}/projects",
                          headers={"Authorization": f"Basic {user_credentials[1]}"},
                          params={'visibility': 'private'})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_project(client, create_and_fill_database):
    user = database_filler.users[0]
    new_project_info = rest.schemas.ProjectCreate(name='new project name',
                                                  description='new project description',
                                                  visibility=rest.schemas.ProjectVisibility.PUBLIC)
    response = client.post(f"/api/users/{user['username']}/projects",
                           headers={"Authorization": f"Basic {user_credentials[0]}"},
                           json=new_project_info.model_dump(mode='json'))
    assert response.status_code == status.HTTP_200_OK
    project_actual = response.json()
    for k, v in new_project_info.model_dump(mode='json').items():
        assert project_actual[k] == v

    response = client.post(f"/api/users/{user['username']}/projects",
                           headers={"Authorization": f"Basic {user_credentials[1]}"},
                           json=new_project_info.model_dump(mode='json'))
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_projects(client, create_and_fill_database):
    user = database_filler.users[0]
    response = client.get(f"/api/users/{user['username']}/projects",
                          headers={"Authorization": f"Basic {user_credentials[0]}"})
    assert response.status_code == status.HTTP_200_OK
    projects_actual = response.json()
    assert len(projects_actual) == len(database_filler.projects[user['username']])

    response = client.get(f"/api/users/{user['username']}/projects",
                          headers={"Authorization": f"Basic {user_credentials[1]}"},
                          params={'visibility': rest.schemas.ProjectVisibility.PRIVATE.value})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_task(client, create_and_fill_database):
    user = database_filler.users[0]
    response = client.get(f"/api/users/{user['username']}/projects",
                          headers={"Authorization": f"Basic {user_credentials[0]}"})
    project = response.json()[0]
    assert len(project['task_ids']) == len(database_filler.projects[user['username']])
    task = rest.schemas.TaskCreate(description='new task description')
    response = client.post(f"/api/users/{user['username']}/projects/{project['id']}/tasks",
                           headers={"Authorization": f"Basic {user_credentials[0]}"},
                           json=task.model_dump(mode='json'))
    assert response.status_code == status.HTTP_200_OK
    actual_task = response.json()
    assert actual_task['description'] == task.description
    response = client.get(f"/api/users/{user['username']}/projects",
                          headers={"Authorization": f"Basic {user_credentials[0]}"})
    project = response.json()[0]
    assert len(project['task_ids']) == len(database_filler.projects[user['username']]) + 1


def test_get_tasks(client, create_and_fill_database):
    user = database_filler.users[0]
    response = client.get(f"/api/users/{user['username']}/projects",
                          headers={"Authorization": f"Basic {user_credentials[0]}"})
    project = response.json()[0]
    response = client.get(f"/api/users/{user['username']}/projects/{project['id']}/tasks",
                          headers={"Authorization": f"Basic {user_credentials[0]}"})
    assert response.status_code == status.HTTP_200_OK
    tasks = response.json()
    assert len(tasks) == sum(len(x) for x in database_filler.tasks.keys()
                             if x[0] == user['username'] and x[1] == project['name'])
    response = client.get(f"/api/users/{user['username']}/projects/{project['id']}/tasks/{tasks[0]['id']}",
                          headers={"Authorization": f"Basic {user_credentials[0]}"})
    assert response.status_code == status.HTTP_200_OK
    task = response.json()
    assert task['id'] == tasks[0]['id']


def test_update_task(client, create_and_fill_database):
    user = database_filler.users[0]
    response = client.get(f"/api/users/{user['username']}/projects",
                          headers={"Authorization": f"Basic {user_credentials[0]}"})
    project = response.json()[0]
    response = client.get(f"/api/users/{user['username']}/projects/{project['id']}/tasks",
                          headers={"Authorization": f"Basic {user_credentials[0]}"})
    assert response.status_code == status.HTTP_200_OK
    task = response.json()[0]
    new_task_info = rest.schemas.TaskUpdate(description='new task description')
    response = client.patch(f"/api/users/{user['username']}/projects/{project['id']}/tasks/{task['id']}",
                            headers={"Authorization": f"Basic {user_credentials[0]}"},
                            json=new_task_info.model_dump(mode='json'))
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['description'] == new_task_info.description


def test_delete_task(client, create_and_fill_database):
    user = database_filler.users[0]
    response = client.get(f"/api/users/{user['username']}/projects",
                          headers={"Authorization": f"Basic {user_credentials[0]}"})
    project = response.json()[0]
    response = client.get(f"/api/users/{user['username']}/projects/{project['id']}/tasks",
                          headers={"Authorization": f"Basic {user_credentials[0]}"})
    assert response.status_code == status.HTTP_200_OK
    task = response.json()[0]

    response = client.delete(f"/api/users/{user['username']}/projects/{project['id']}/tasks/{task['id']}",
                             headers={"Authorization": f"Basic {user_credentials[0]}"})
    assert response.status_code == status.HTTP_200_OK

    response = client.get(f"/api/users/{user['username']}/projects/{project['id']}/tasks/{task['id']}",
                          headers={"Authorization": f"Basic {user_credentials[0]}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_start_task(client, create_and_fill_database):
    user = database_filler.users[0]
    response = client.get(f"/api/users/{user['username']}/projects",
                          headers={"Authorization": f"Basic {user_credentials[0]}"})
    project = response.json()[0]
    response = client.get(f"/api/users/{user['username']}/projects/{project['id']}/tasks",
                          headers={"Authorization": f"Basic {user_credentials[0]}"})
    assert response.status_code == status.HTTP_200_OK
    task = response.json()[0]

    assert task['start_timestamp'] is None
    assert task['end_timestamp'] is None

    url = f"/api/users/{user['username']}/projects/{project['id']}/tasks/{task['id']}/start"
    response = client.post(url,
                           headers={"Authorization": f"Basic {user_credentials[0]}"})
    assert response.status_code == status.HTTP_200_OK

    response = client.get(f"/api/users/{user['username']}/projects/{project['id']}/tasks",
                          headers={"Authorization": f"Basic {user_credentials[0]}"})
    assert response.status_code == status.HTTP_200_OK
    task = response.json()[0]
    assert task['start_timestamp'] is not None
    assert task['end_timestamp'] is None

    url = f"/api/users/{user['username']}/projects/{project['id']}/tasks/{task['id']}/stop"
    response = client.post(url,
                           headers={"Authorization": f"Basic {user_credentials[0]}"})
    assert response.status_code == status.HTTP_200_OK

    response = client.get(f"/api/users/{user['username']}/projects/{project['id']}/tasks",
                          headers={"Authorization": f"Basic {user_credentials[0]}"})
    assert response.status_code == status.HTTP_200_OK
    task = response.json()[0]

    assert task['start_timestamp'] is not None
    assert task['end_timestamp'] is not None
