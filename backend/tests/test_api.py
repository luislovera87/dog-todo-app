import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import crud
from app.security import create_access_token

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

def create_test_user(db, username="testuser", password="testpass"):
    """Helper to create a test user and return token."""
    user = crud.create_user(db, username, password)
    token = create_access_token({"sub": str(user.id)})
    return user, token

def get_auth_headers(token):
    """Helper to create Authorization header from token."""
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function")
def test_db():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield engine

    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()

@pytest.fixture
def client(test_db):
    return TestClient(app)

@pytest.fixture
def client_with_user(test_db):
    """Provide client with authenticated user."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db)
    db = TestingSessionLocal()

    client = TestClient(app)
    user, token = create_test_user(db, "testuser", "testpass")
    headers = get_auth_headers(token)

    db.close()
    return client, headers, user

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_todo(client_with_user):
    """Test creating a todo with authentication."""
    client, headers, user = client_with_user
    todo_data = {
        "task_name": "Walk Buddy",
        "dog_name": "Buddy",
        "priority": "high",
    }
    response = client.post("/api/todos", json=todo_data, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert data["task_name"] == "Walk Buddy"
    assert data["dog_name"] == "Buddy"
    assert data["priority"] == "high"
    assert data["completed"] is False
    assert data["user_id"] == user.id
    assert "id" in data

def test_create_todo_without_token(client):
    """Test that creating todo requires authentication."""
    response = client.post("/api/todos", json={"task_name": "Task", "dog_name": "Dog"})
    assert response.status_code == 401

def test_create_todo_validation_error(client_with_user):
    """Test validation error with auth."""
    client, headers, user = client_with_user
    response = client.post("/api/todos", json={"dog_name": "Buddy"}, headers=headers)
    assert response.status_code == 422

def test_list_todos_empty(client_with_user):
    """Test listing empty todos list."""
    client, headers, user = client_with_user
    response = client.get("/api/todos", headers=headers)
    assert response.status_code == 200
    assert response.json() == []

def test_list_todos_without_token(client):
    """Test that listing todos requires authentication."""
    response = client.get("/api/todos")
    assert response.status_code == 401

def test_list_todos(client_with_user):
    """Test listing todos for user (only sees own todos)."""
    client, headers, user = client_with_user
    client.post("/api/todos", json={"task_name": "Task1", "dog_name": "Buddy"}, headers=headers)
    client.post("/api/todos", json={"task_name": "Task2", "dog_name": "Max"}, headers=headers)

    response = client.get("/api/todos", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_list_todos_filter_by_dog(client_with_user):
    """Test filtering todos by dog name."""
    client, headers, user = client_with_user
    client.post("/api/todos", json={"task_name": "Task1", "dog_name": "Buddy"}, headers=headers)
    client.post("/api/todos", json={"task_name": "Task2", "dog_name": "Max"}, headers=headers)

    response = client.get("/api/todos?dog_name=Buddy", headers=headers)
    assert response.status_code == 200
    todos = response.json()
    assert len(todos) == 1
    assert todos[0]["dog_name"] == "Buddy"

def test_list_todos_filter_by_completed(client_with_user):
    """Test filtering todos by completion status."""
    client, headers, user = client_with_user
    todo1_resp = client.post("/api/todos", json={"task_name": "Task1", "dog_name": "Buddy"}, headers=headers)
    todo1_id = todo1_resp.json()["id"]
    client.post("/api/todos", json={"task_name": "Task2", "dog_name": "Buddy"}, headers=headers)

    client.patch(f"/api/todos/{todo1_id}/toggle", headers=headers)

    response = client.get("/api/todos?completed=true", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_todo(client_with_user):
    """Test getting a specific todo."""
    client, headers, user = client_with_user
    create_resp = client.post("/api/todos", json={"task_name": "Task", "dog_name": "Buddy"}, headers=headers)
    todo_id = create_resp.json()["id"]

    response = client.get(f"/api/todos/{todo_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["task_name"] == "Task"

def test_get_todo_not_found(client_with_user):
    """Test getting nonexistent todo returns 404."""
    client, headers, user = client_with_user
    response = client.get("/api/todos/999", headers=headers)
    assert response.status_code == 404

def test_update_todo(client_with_user):
    """Test updating a todo."""
    client, headers, user = client_with_user
    create_resp = client.post("/api/todos", json={"task_name": "Original", "dog_name": "Buddy"}, headers=headers)
    todo_id = create_resp.json()["id"]

    response = client.put(f"/api/todos/{todo_id}", json={"task_name": "Updated"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["task_name"] == "Updated"

def test_update_todo_not_found(client_with_user):
    """Test updating nonexistent todo returns 404."""
    client, headers, user = client_with_user
    response = client.put("/api/todos/999", json={"task_name": "Updated"}, headers=headers)
    assert response.status_code == 404

def test_delete_todo(client_with_user):
    """Test deleting a todo."""
    client, headers, user = client_with_user
    create_resp = client.post("/api/todos", json={"task_name": "Task", "dog_name": "Buddy"}, headers=headers)
    todo_id = create_resp.json()["id"]

    response = client.delete(f"/api/todos/{todo_id}", headers=headers)
    assert response.status_code == 204

    get_resp = client.get(f"/api/todos/{todo_id}", headers=headers)
    assert get_resp.status_code == 404

def test_delete_todo_not_found(client_with_user):
    """Test deleting nonexistent todo returns 404."""
    client, headers, user = client_with_user
    response = client.delete("/api/todos/999", headers=headers)
    assert response.status_code == 404

def test_toggle_todo(client_with_user):
    """Test toggling todo completion."""
    client, headers, user = client_with_user
    create_resp = client.post("/api/todos", json={"task_name": "Task", "dog_name": "Buddy"}, headers=headers)
    todo_id = create_resp.json()["id"]

    response = client.patch(f"/api/todos/{todo_id}/toggle", headers=headers)
    assert response.status_code == 200
    assert response.json()["completed"] is True

    response2 = client.patch(f"/api/todos/{todo_id}/toggle", headers=headers)
    assert response2.json()["completed"] is False

def test_toggle_todo_not_found(client_with_user):
    """Test toggling nonexistent todo returns 404."""
    client, headers, user = client_with_user
    response = client.patch("/api/todos/999/toggle", headers=headers)
    assert response.status_code == 404
