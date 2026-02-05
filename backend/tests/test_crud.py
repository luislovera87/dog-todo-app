import pytest
from app import crud
from app.schemas import TodoCreate, TodoUpdate
from app.models import PriorityEnum, User, TodoItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def user_with_db(db):
    """Create a test user and return user with db."""
    user = crud.create_user(db, "testuser", "testpass")
    return user, db

def create_todo_for_user(db, user, task_name, dog_name, priority=None, description=None):
    """Helper to create a todo with user_id."""
    todo = TodoItem(
        task_name=task_name,
        dog_name=dog_name,
        priority=priority or PriorityEnum.medium,
        description=description,
        user_id=user.id
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo

def test_create_todo(user_with_db):
    user, db = user_with_db
    result = create_todo_for_user(db, user, "Training", "Charlie", PriorityEnum.high)

    assert result.id is not None
    assert result.task_name == "Training"
    assert result.dog_name == "Charlie"

def test_get_todos_empty(user_with_db):
    user, db = user_with_db
    todos = crud.get_todos(db)
    assert len(todos) == 0

def test_get_todos_multiple(user_with_db):
    user, db = user_with_db
    for i in range(3):
        create_todo_for_user(db, user, f"Task {i}", "Buddy")

    todos = crud.get_todos(db)
    assert len(todos) == 3

def test_get_todos_filter_by_dog(user_with_db):
    user, db = user_with_db
    create_todo_for_user(db, user, "Task1", "Buddy")
    create_todo_for_user(db, user, "Task2", "Max")

    buddy_todos = crud.get_todos(db, dog_name="Buddy")
    assert len(buddy_todos) == 1
    assert buddy_todos[0].dog_name == "Buddy"

def test_get_todos_filter_by_completed(user_with_db):
    user, db = user_with_db
    todo1 = create_todo_for_user(db, user, "Task1", "Buddy")
    todo2 = create_todo_for_user(db, user, "Task2", "Buddy")

    todo1.completed = True
    db.add(todo1)
    db.commit()

    incomplete = crud.get_todos(db, completed=False)
    assert len(incomplete) == 1
    assert incomplete[0].task_name == "Task2"

def test_get_todos_filter_by_priority(user_with_db):
    user, db = user_with_db
    create_todo_for_user(db, user, "Task1", "Buddy", PriorityEnum.high)
    create_todo_for_user(db, user, "Task2", "Buddy", PriorityEnum.low)

    high_priority = crud.get_todos(db, priority=PriorityEnum.high)
    assert len(high_priority) == 1
    assert high_priority[0].priority == PriorityEnum.high

def test_get_todo(user_with_db):
    user, db = user_with_db
    created = create_todo_for_user(db, user, "Task", "Buddy")
    retrieved = crud.get_todo(db, created.id)

    assert retrieved is not None
    assert retrieved.id == created.id

def test_get_todo_not_found(user_with_db):
    user, db = user_with_db
    result = crud.get_todo(db, 999)
    assert result is None

def test_update_todo(user_with_db):
    user, db = user_with_db
    todo = create_todo_for_user(db, user, "Original", "Buddy")
    update_data = TodoUpdate(task_name="Updated")

    updated = crud.update_todo(db, todo.id, update_data)
    assert updated.task_name == "Updated"
    assert updated.dog_name == "Buddy"

def test_update_todo_not_found(user_with_db):
    user, db = user_with_db
    update_data = TodoUpdate(task_name="Updated")
    result = crud.update_todo(db, 999, update_data)
    assert result is None

def test_delete_todo(user_with_db):
    user, db = user_with_db
    todo = create_todo_for_user(db, user, "Task", "Buddy")
    success = crud.delete_todo(db, todo.id)

    assert success is True
    assert crud.get_todo(db, todo.id) is None

def test_delete_todo_not_found(user_with_db):
    user, db = user_with_db
    success = crud.delete_todo(db, 999)
    assert success is False

def test_toggle_todo_completion(user_with_db):
    user, db = user_with_db
    todo = create_todo_for_user(db, user, "Task", "Buddy")
    assert todo.completed is False

    toggled = crud.toggle_todo_completion(db, todo.id)
    assert toggled.completed is True

    toggled2 = crud.toggle_todo_completion(db, todo.id)
    assert toggled2.completed is False

def test_toggle_todo_not_found(user_with_db):
    user, db = user_with_db
    result = crud.toggle_todo_completion(db, 999)
    assert result is None
