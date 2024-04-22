import pytest

from fastapi import status, HTTPException
from db.models import Users
from test.utils import client, test_user, app, override_get_db, TestingSessionLocal
from routers.auth import get_db, authenticate_user, create_access_token, SECRET_KEY, ALGORITHM, get_current_user
from jose import jwt
from datetime import timedelta, datetime


app.dependency_overrides[get_db] = override_get_db

def test_create_user(test_user):
	data = {
		"username": "amarkanth",
		"email": "amarkanth.bollu@gmail.com",
		"first_name": "Amar",
		"last_name": "Kanth",
		"password": "1234",
		"role": "admin"
	}
	response = client.post("/auth/create_user", json=data)
	assert response.status_code == status.HTTP_201_CREATED

	db = TestingSessionLocal()
	model = db.query(Users).filter(Users.username == "amarkanth").first()
	assert model.username == data["username"]
	assert model.email == data["email"]
	assert model.first_name == data["first_name"]
	assert model.last_name == data["last_name"]
	assert model.role == data["role"]

def test_login_for_access_token(test_user):
	data = {
		"username": "codingwithrobytest",
		"password": "testpassword"
	}
	response = client.post("/auth/token", data=data)
	assert response.status_code == status.HTTP_200_OK
	assert 'access_token' in response.json()
	assert 'token_type' in response.json()

def test_login_with_invalid_user(test_user):
	data = {
		"username": "test_name",
		"password": "wrong_password"
	}
	response = client.post("/auth/token", data=data)
	assert response.status_code == 401
	assert response.json() == {'detail': 'Could not validate user.'}

def test_authenticate_user(test_user):
	db = TestingSessionLocal()

	user = authenticate_user(test_user.username, "testpassword", db)
	assert user is not None
	assert user.username == test_user.username

	non_exist_user = authenticate_user("wrong_username", "testpassword", db)
	assert non_exist_user is False

def test_create_access_token(test_user):
	token = create_access_token(test_user.username, test_user.id, test_user.role, timedelta(days=1))
	decode_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={'verify_signature': False})

	assert decode_token['sub'] == test_user.username
	assert decode_token['id'] == test_user.id
	assert decode_token['role'] == test_user.role

@pytest.mark.asyncio
async def test_get_current_user_with_valid_token(test_user):
	encode = {'sub': test_user.username, 'id': test_user.id, 'role': test_user.role}
	token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

	user = await get_current_user(token=token)
	assert user == {'username': test_user.username, 'id': test_user.id, 'user_role': test_user.role}

@pytest.mark.asyncio
async def test_get_current_user_missing_payload(test_user):
    encode = {'role': 'user'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == 'Could not validate user.'