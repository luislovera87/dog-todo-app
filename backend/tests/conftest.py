import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from fastapi.testclient import TestClient
from app.schemas import TodoCreate

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

@pytest.fixture(scope="function")
def db(test_db):
    """Provide a database session for tests."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def test_client(test_db):
    return TestClient(app)

@pytest.fixture
def sample_todo():
    return TodoCreate(
        task_name="Walk Buddy",
        dog_name="Buddy",
        description="Morning walk in the park",
        priority="high",
    )
