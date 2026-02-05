import pytest
from app import crud
from app.schemas import TodoCreate, TodoUpdate
from app.models import PriorityEnum
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

def test_create_todo(db):
    todo_data = TodoCreate(
        task_name="Training",
        dog_name="Charlie",
        priority=PriorityEnum.high,
    )
    result = crud.create_todo(db, todo_data)

    assert result.id is not None
    assert result.task_name == "Training"
    assert result.dog_name == "Charlie"

def test_get_todos_empty(db):
    todos = crud.get_todos(db)
    assert len(todos) == 0

def test_get_todos_multiple(db):
    for i in range(3):
        todo_data = TodoCreate(
            task_name=f"Task {i}",
            dog_name="Buddy",
        )
        crud.create_todo(db, todo_data)

    todos = crud.get_todos(db)
    assert len(todos) == 3

def test_get_todos_filter_by_dog(db):
    crud.create_todo(db, TodoCreate(task_name="Task1", dog_name="Buddy"))
    crud.create_todo(db, TodoCreate(task_name="Task2", dog_name="Max"))

    buddy_todos = crud.get_todos(db, dog_name="Buddy")
    assert len(buddy_todos) == 1
    assert buddy_todos[0].dog_name == "Buddy"

def test_get_todos_filter_by_completed(db):
    todo1 = crud.create_todo(db, TodoCreate(task_name="Task1", dog_name="Buddy"))
    todo2 = crud.create_todo(db, TodoCreate(task_name="Task2", dog_name="Buddy"))

    todo1.completed = True
    db.add(todo1)
    db.commit()

    incomplete = crud.get_todos(db, completed=False)
    assert len(incomplete) == 1
    assert incomplete[0].task_name == "Task2"

def test_get_todos_filter_by_priority(db):
    crud.create_todo(db, TodoCreate(task_name="Task1", dog_name="Buddy", priority=PriorityEnum.high))
    crud.create_todo(db, TodoCreate(task_name="Task2", dog_name="Buddy", priority=PriorityEnum.low))

    high_priority = crud.get_todos(db, priority=PriorityEnum.high)
    assert len(high_priority) == 1
    assert high_priority[0].priority == PriorityEnum.high

def test_get_todo(db):
    created = crud.create_todo(db, TodoCreate(task_name="Task", dog_name="Buddy"))
    retrieved = crud.get_todo(db, created.id)

    assert retrieved is not None
    assert retrieved.id == created.id

def test_get_todo_not_found(db):
    result = crud.get_todo(db, 999)
    assert result is None

def test_update_todo(db):
    todo = crud.create_todo(db, TodoCreate(task_name="Original", dog_name="Buddy"))
    update_data = TodoUpdate(task_name="Updated")

    updated = crud.update_todo(db, todo.id, update_data)
    assert updated.task_name == "Updated"
    assert updated.dog_name == "Buddy"

def test_update_todo_not_found(db):
    update_data = TodoUpdate(task_name="Updated")
    result = crud.update_todo(db, 999, update_data)
    assert result is None

def test_delete_todo(db):
    todo = crud.create_todo(db, TodoCreate(task_name="Task", dog_name="Buddy"))
    success = crud.delete_todo(db, todo.id)

    assert success is True
    assert crud.get_todo(db, todo.id) is None

def test_delete_todo_not_found(db):
    success = crud.delete_todo(db, 999)
    assert success is False

def test_toggle_todo_completion(db):
    todo = crud.create_todo(db, TodoCreate(task_name="Task", dog_name="Buddy"))
    assert todo.completed is False

    toggled = crud.toggle_todo_completion(db, todo.id)
    assert toggled.completed is True

    toggled2 = crud.toggle_todo_completion(db, todo.id)
    assert toggled2.completed is False

def test_toggle_todo_not_found(db):
    result = crud.toggle_todo_completion(db, 999)
    assert result is None
