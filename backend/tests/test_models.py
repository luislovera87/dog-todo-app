import pytest
from app.models import TodoItem, PriorityEnum
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_todo_item(db_session):
    todo = TodoItem(
        task_name="Feed Max",
        dog_name="Max",
        priority=PriorityEnum.high,
    )
    db_session.add(todo)
    db_session.commit()

    assert todo.id is not None
    assert todo.task_name == "Feed Max"
    assert todo.dog_name == "Max"
    assert todo.completed is False
    assert todo.priority == PriorityEnum.high

def test_todo_item_defaults(db_session):
    todo = TodoItem(
        task_name="Test",
        dog_name="TestDog",
    )
    db_session.add(todo)
    db_session.commit()

    assert todo.completed is False
    assert todo.priority == PriorityEnum.medium
    assert todo.created_at is not None
    assert todo.updated_at is not None

def test_todo_item_with_description(db_session):
    todo = TodoItem(
        task_name="Groom",
        dog_name="Luna",
        description="Bath and nail trim",
    )
    db_session.add(todo)
    db_session.commit()

    assert todo.description == "Bath and nail trim"
