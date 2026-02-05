import pytest
from app.models import TodoItem, PriorityEnum, User
from app import crud
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

@pytest.fixture
def user_with_session(db_session):
    """Create a test user."""
    user = crud.create_user(db_session, "testuser", "testpass")
    return user, db_session

def test_create_todo_item(user_with_session):
    user, db_session = user_with_session
    todo = TodoItem(
        task_name="Feed Max",
        dog_name="Max",
        priority=PriorityEnum.high,
        user_id=user.id,
    )
    db_session.add(todo)
    db_session.commit()

    assert todo.id is not None
    assert todo.task_name == "Feed Max"
    assert todo.dog_name == "Max"
    assert todo.completed is False
    assert todo.priority == PriorityEnum.high
    assert todo.user_id == user.id

def test_todo_item_defaults(user_with_session):
    user, db_session = user_with_session
    todo = TodoItem(
        task_name="Test",
        dog_name="TestDog",
        user_id=user.id,
    )
    db_session.add(todo)
    db_session.commit()

    assert todo.completed is False
    assert todo.priority == PriorityEnum.medium
    assert todo.created_at is not None

def test_todo_item_with_description(user_with_session):
    user, db_session = user_with_session
    todo = TodoItem(
        task_name="Groom",
        dog_name="Luna",
        description="Bath and nail trim",
        user_id=user.id,
    )
    db_session.add(todo)
    db_session.commit()

    assert todo.description == "Bath and nail trim"
    assert todo.user_id == user.id
