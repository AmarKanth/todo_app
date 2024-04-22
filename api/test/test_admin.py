from fastapi import status
from test.utils import client, app, override_get_db, override_get_current_user, test_todo, TestingSessionLocal
from routers.admin import get_db, get_current_user
from db.models import Todos


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_read_all_todos_by_admin(test_todo):
	expected_response = [{'complete': False, 'title': 'Learn to code!', 
	'description': 'Need to learn everyday!', 'id': 1, 'priority': 5, 'owner_id': 1}]
	response = client.get("/admin/todo")
	assert response.status_code == status.HTTP_200_OK
	assert response.json() == expected_response


def test_delete_todo_by_admin(test_todo):
	response = client.delete("/admin/todo/1")
	assert response.status_code == 204

	db = TestingSessionLocal()
	model = db.query(Todos).filter(Todos.id == 1).first()
	assert model is None


def test_delete_todo_not_found_by_admin(test_todo):
	response = client.delete("/admin/todo/9999")
	assert response.status_code == 404
	assert response.json() == {'detail': 'Todo not found.'}