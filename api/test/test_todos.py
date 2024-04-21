from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from main import app
from db.connection import Base
from db.models import Todos, Users
from routers.auth import bcrypt_context
from routers.todos import get_db, get_current_user

from fastapi.testclient import TestClient
from fastapi import status

import pytest


SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass = StaticPool,
)


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {'username': 'codingwithrobytest', 'id': 1, 'user_role': 'admin'}


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


client = TestClient(app)

def test_read_all_todos():
	response = client.get("/")
	assert response.status_code == status.HTTP_200_OK


# @pytest.fixture
# def test_todo():
#     todo = Todos(
#         title="Learn to code!",
#         description="Need to learn everyday!",
#         priority=5,
#         complete=False,
#         owner_id=1,
#     )

#     db = TestingSessionLocal()
#     db.add(todo)
#     db.commit()
#     yield todo
#     with engine.connect() as connection:
#         connection.execute(text("DELETE FROM todos;"))
#         connection.commit()


# @pytest.fixture
# def test_user():
#     user = Users(
#         username="codingwithrobytest",
#         email="codingwithrobytest@email.com",
#         first_name="Eric",
#         last_name="Roby",
#         hashed_password=bcrypt_context.hash("testpassword"),
#         role="admin",
#         phone_number="(111)-111-1111"
#     )
#     db = TestingSessionLocal()
#     db.add(user)
#     db.commit()
#     yield user
#     with engine.connect() as connection:
#         connection.execute(text("DELETE FROM users;"))
#         connection.commit()