import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

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

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_todo(client):
    todo_data = {
        "task_name": "Walk Buddy",
        "dog_name": "Buddy",
        "priority": "high",
    }
    response = client.post("/api/todos", json=todo_data)

    assert response.status_code == 201
    data = response.json()
    assert data["task_name"] == "Walk Buddy"
    assert data["dog_name"] == "Buddy"
    assert data["priority"] == "high"
    assert data["completed"] is False
    assert "id" in data

def test_create_todo_validation_error(client):
    response = client.post("/api/todos", json={"dog_name": "Buddy"})
    assert response.status_code == 422

def test_list_todos_empty(client):
    response = client.get("/api/todos")
    assert response.status_code == 200
    assert response.json() == []

def test_list_todos(client):
    client.post("/api/todos", json={"task_name": "Task1", "dog_name": "Buddy"})
    client.post("/api/todos", json={"task_name": "Task2", "dog_name": "Max"})

    response = client.get("/api/todos")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_list_todos_filter_by_dog(client):
    client.post("/api/todos", json={"task_name": "Task1", "dog_name": "Buddy"})
    client.post("/api/todos", json={"task_name": "Task2", "dog_name": "Max"})

    response = client.get("/api/todos?dog_name=Buddy")
    assert response.status_code == 200
    todos = response.json()
    assert len(todos) == 1
    assert todos[0]["dog_name"] == "Buddy"

def test_list_todos_filter_by_completed(client):
    todo1_resp = client.post("/api/todos", json={"task_name": "Task1", "dog_name": "Buddy"})
    todo1_id = todo1_resp.json()["id"]
    client.post("/api/todos", json={"task_name": "Task2", "dog_name": "Buddy"})

    client.patch(f"/api/todos/{todo1_id}/toggle")

    response = client.get("/api/todos?completed=true")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_todo(client):
    create_resp = client.post("/api/todos", json={"task_name": "Task", "dog_name": "Buddy"})
    todo_id = create_resp.json()["id"]

    response = client.get(f"/api/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["task_name"] == "Task"

def test_get_todo_not_found(client):
    response = client.get("/api/todos/999")
    assert response.status_code == 404

def test_update_todo(client):
    create_resp = client.post("/api/todos", json={"task_name": "Original", "dog_name": "Buddy"})
    todo_id = create_resp.json()["id"]

    response = client.put(f"/api/todos/{todo_id}", json={"task_name": "Updated"})
    assert response.status_code == 200
    assert response.json()["task_name"] == "Updated"

def test_update_todo_not_found(client):
    response = client.put("/api/todos/999", json={"task_name": "Updated"})
    assert response.status_code == 404

def test_delete_todo(client):
    create_resp = client.post("/api/todos", json={"task_name": "Task", "dog_name": "Buddy"})
    todo_id = create_resp.json()["id"]

    response = client.delete(f"/api/todos/{todo_id}")
    assert response.status_code == 204

    get_resp = client.get(f"/api/todos/{todo_id}")
    assert get_resp.status_code == 404

def test_delete_todo_not_found(client):
    response = client.delete("/api/todos/999")
    assert response.status_code == 404

def test_toggle_todo(client):
    create_resp = client.post("/api/todos", json={"task_name": "Task", "dog_name": "Buddy"})
    todo_id = create_resp.json()["id"]

    response = client.patch(f"/api/todos/{todo_id}/toggle")
    assert response.status_code == 200
    assert response.json()["completed"] is True

    response2 = client.patch(f"/api/todos/{todo_id}/toggle")
    assert response2.json()["completed"] is False

def test_toggle_todo_not_found(client):
    response = client.patch("/api/todos/999/toggle")
    assert response.status_code == 404
