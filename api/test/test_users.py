from fastapi import status
from test.utils import client, app, override_get_db, override_get_current_user, test_user, TestingSessionLocal
from routers.users import get_db, get_current_user


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user 


def test_get_user(test_user):
    response = client.get("/user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'codingwithrobytest'
    assert response.json()['email'] == 'codingwithrobytest@email.com'
    assert response.json()['first_name'] == 'Eric'
    assert response.json()['last_name'] == 'Roby'
    assert response.json()['role'] == 'admin'


def test_change_password_success(test_user):
	data = {"password": "testpassword", "new_password": "newpassword"}
	response = client.put("/user/password", json=data)
	assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_password_invalid_current_password(test_user):
	data = {"password": "wrong_password", "new_password": "newpassword"}
	response = client.put("/user/password", json=data)
	assert response.status_code == status.HTTP_401_UNAUTHORIZED
	assert response.json() == {'detail': 'Error on password change'}