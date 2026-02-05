import pytest
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
)
from app import crud, models


def test_hash_password():
    """Test password hashing."""
    password = "secure_pass_123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)


def test_verify_password_wrong():
    """Test password verification with wrong password."""
    password = "secure_pass_123"
    hashed = hash_password(password)
    assert not verify_password("wrongpass", hashed)


def test_create_and_decode_token():
    """Test JWT token creation and decoding."""
    data = {"sub": "user123"}
    token = create_access_token(data)
    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user123"


def test_decode_invalid_token():
    """Test decoding an invalid token."""
    decoded = decode_token("invalid.token.here")
    assert decoded is None


def test_token_contains_expiry():
    """Test that token contains expiry time."""
    data = {"sub": "user123"}
    token = create_access_token(data)
    decoded = decode_token(token)
    assert "exp" in decoded


def test_create_user(db):
    """Test creating a new user."""
    user = crud.create_user(db, username="testuser", password="testpass")
    assert user.username == "testuser"
    assert user.password_hash != "testpass"
    assert user.id is not None


def test_create_duplicate_user(db):
    """Test that duplicate usernames raise integrity error."""
    crud.create_user(db, username="testuser", password="pass1")
    with pytest.raises(Exception):  # SQLAlchemy IntegrityError
        crud.create_user(db, username="testuser", password="pass2")


def test_get_user_by_username(db):
    """Test retrieving user by username."""
    created = crud.create_user(db, username="findme", password="pass")
    found = crud.get_user_by_username(db, "findme")
    assert found is not None
    assert found.username == "findme"


def test_get_user_by_username_not_found(db):
    """Test retrieving nonexistent user."""
    result = crud.get_user_by_username(db, "nonexistent")
    assert result is None


def test_get_user_by_id(db):
    """Test retrieving user by ID."""
    created = crud.create_user(db, username="byid", password="pass")
    found = crud.get_user_by_id(db, created.id)
    assert found is not None
    assert found.id == created.id
