from fastapi import status
from routers.todos import get_db, get_current_user
from db.models import Todos
from test.utils import client, app, override_get_db, override_get_current_user, test_todo, TestingSessionLocal


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_read_all_todos(test_todo):
    expected_response = [{'complete': False, 'title': 'Learn to code!', 
    'description': 'Need to learn everyday!', 'id': 1, 'priority': 5, 'owner_id': 1}]
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response


def test_read_todo(test_todo):
    expected_response = {'complete': False, 'title': 'Learn to code!', 
    'description': 'Need to learn everyday!', 'id': 1, 'priority': 5, 'owner_id': 1}
    response = client.get("todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response


def test_read_todo_not_found(test_todo):
    response = client.get("todo/99")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}


def test_create_todo(test_todo):
    request_data={
        'title': 'New Todo!',
        'description':'New todo description',
        'priority': 5,
        'complete': False,
    }

    response = client.post('/todo/', json=request_data)
    assert response.status_code == 201

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')


def test_update_todo(test_todo):
    request_data={
        'title':'Change the title of the todo already saved!',
        'description': 'Need to learn everyday!',
        'priority': 5,
        'complete': False,
    }

    response = client.put('/todo/1', json=request_data)
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == 'Change the title of the todo already saved!'


def test_update_todo_not_found(test_todo):
    request_data={
        'title':'Change the title of the todo already saved!',
        'description': 'Need to learn everyday!',
        'priority': 5,
        'complete': False,
    }

    response = client.put('/todo/999', json=request_data)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}


def test_delete_todo(test_todo):
    response = client.delete('/todo/1')
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_delete_todo_not_found():
    response = client.delete('/todo/999')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}