# Simple User/Password Login Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add user registration, login, and JWT authentication to the Dog Todo App so each user has a private account and can only see their own todos.

**Architecture:** JWT-based stateless authentication with token stored in localStorage on frontend. Backend validates tokens on every request. Users filtered by user_id on all todo operations. 24-hour token expiry for auto-logout.

**Tech Stack:**
- Backend: python-jose (JWT), passlib (password hashing), python-multipart
- Frontend: localStorage for token storage, Authorization headers on requests
- Database: New User model, updated TodoItem with user_id foreign key

---

## Phase 1: Backend Setup & Dependencies

### Task 1: Add Python dependencies

**Files:**
- Modify: `backend/requirements.txt`

**Step 1: Add new dependencies to requirements.txt**

Add these lines to `backend/requirements.txt`:
```
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```

**Step 2: Verify file changes**

Run: `grep -E "python-jose|passlib|python-multipart" backend/requirements.txt`

Expected output: All three packages listed

**Step 3: Commit**

```bash
cd /home/circawolf/projects/claude-sandbox
git add backend/requirements.txt
git commit -m "deps: add JWT and password hashing libraries

- python-jose for JWT token generation/validation
- passlib for secure password hashing
- python-multipart for form data handling"
```

---

## Phase 2: Backend Database Models

### Task 2: Create User model

**Files:**
- Modify: `backend/app/models.py`

**Step 1: Add User model to models.py**

Read the current file first, then add this User model before the TodoItem model:

```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to todos
    todos = relationship("TodoItem", back_populates="owner")
```

**Step 2: Update TodoItem model to add user_id**

In the TodoItem class, add this field after the `updated_at` field:

```python
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    owner = relationship("User", back_populates="todos")
```

**Step 3: Verify imports**

Check that `backend/app/models.py` has these imports at the top:
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime
```

**Step 4: Commit**

```bash
git add backend/app/models.py
git commit -m "feat: add User model and user_id to TodoItem

- New User table with username (unique) and password_hash
- TodoItem now has user_id foreign key
- Relationship between User and TodoItem for ORM access"
```

---

## Phase 3: Backend Authentication Schemas

### Task 3: Add Pydantic schemas for auth

**Files:**
- Modify: `backend/app/schemas.py`

**Step 1: Add auth schemas**

Add these schemas at the end of `backend/app/schemas.py`:

```python
class UserCreate(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)

class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

**Step 2: Verify file**

Check that schemas.py imports datetime: `grep "from datetime import" backend/app/schemas.py`

If not present, add to imports: `from datetime import datetime`

**Step 3: Commit**

```bash
git add backend/app/schemas.py
git commit -m "feat: add auth schemas (UserCreate, UserResponse, Token)"
```

---

## Phase 4: Backend Security Utilities

### Task 4: Create security.py module

**Files:**
- Create: `backend/app/security.py`

**Step 1: Create security.py with password and JWT utilities**

Create new file `backend/app/security.py`:

```python
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
import os

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

**Step 2: Test imports**

Run: `python -c "from backend.app.security import hash_password, verify_password, create_access_token, decode_token; print('All imports successful')"`

Expected: "All imports successful"

**Step 3: Commit**

```bash
git add backend/app/security.py
git commit -m "feat: add security utilities for JWT and password hashing

- hash_password/verify_password for bcrypt operations
- create_access_token/decode_token for JWT handling
- 24-hour token expiry configuration"
```

---

## Phase 5: Backend CRUD for Users

### Task 5: Add user CRUD functions

**Files:**
- Modify: `backend/app/crud.py`

**Step 1: Add user creation and lookup functions**

Add these functions to `backend/app/crud.py`:

```python
from backend.app.security import hash_password, verify_password


def create_user(db: Session, username: str, password: str):
    """Create a new user with hashed password."""
    hashed_password = hash_password(password)
    db_user = models.User(username=username, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str):
    """Retrieve a user by username."""
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_id(db: Session, user_id: int):
    """Retrieve a user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()
```

**Step 2: Add import at top of crud.py**

Verify that `backend/app/crud.py` imports Session:
```python
from sqlalchemy.orm import Session
```

**Step 3: Commit**

```bash
git add backend/app/crud.py
git commit -m "feat: add user CRUD functions

- create_user: Create user with bcrypt-hashed password
- get_user_by_username: Lookup user for login
- get_user_by_id: Lookup user by ID from token"
```

---

## Phase 6: Backend Authentication Tests

### Task 6: Write tests for auth utilities

**Files:**
- Create: `backend/tests/test_auth.py`

**Step 1: Create test_auth.py with security tests**

Create new file `backend/tests/test_auth.py`:

```python
import pytest
from backend.app.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
)


def test_hash_password():
    """Test password hashing."""
    password = "testpass123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)


def test_verify_password_wrong():
    """Test password verification with wrong password."""
    password = "testpass123"
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
```

**Step 2: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_auth.py -v`

Expected: All tests PASS

**Step 3: Commit**

```bash
git add backend/tests/test_auth.py
git commit -m "test: add security utilities tests

- Password hashing and verification
- Token creation and decoding
- Invalid token handling"
```

---

## Phase 7: Backend User Registration Tests

### Task 7: Write tests for user registration

**Files:**
- Modify: `backend/tests/test_auth.py`

**Step 1: Add registration test fixtures and tests**

Add these to `backend/tests/test_auth.py`:

```python
from backend.app import crud, models


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
```

**Step 2: Run tests**

Run: `cd backend && python -m pytest tests/test_auth.py::test_create_user -v`

Expected: PASS

**Step 3: Run all auth tests**

Run: `cd backend && python -m pytest tests/test_auth.py -v`

Expected: All tests PASS (11 total)

**Step 4: Commit**

```bash
git add backend/tests/test_auth.py
git commit -m "test: add user creation and retrieval tests"
```

---

## Phase 8: Backend Auth API Endpoints

### Task 8: Add registration endpoint

**Files:**
- Modify: `backend/app/main.py`

**Step 1: Add register endpoint to main.py**

Add these imports at the top of `backend/app/main.py`:
```python
from backend.app.security import create_access_token, verify_password
from fastapi.security import HTTPBearer, HTTPAuthCredentials
```

Add this endpoint before the `/api/todos` routes:

```python
@app.post("/api/auth/register", response_model=schemas.Token)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    existing_user = crud.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=409, detail="Username already exists")

    db_user = crud.create_user(db, user_data.username, user_data.password)
    access_token = create_access_token({"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
```

**Step 2: Test registration endpoint**

Run: `cd backend && python -m pytest tests/test_api.py -v` (existing tests should still pass)

Expected: All existing tests PASS

**Step 3: Commit**

```bash
git add backend/app/main.py
git commit -m "feat: add POST /api/auth/register endpoint

- Accept username and password
- Hash password, create user record
- Return JWT token on success
- Return 409 if username already exists"
```

---

## Task 9: Add login endpoint

**Files:**
- Modify: `backend/app/main.py`

**Step 1: Add login endpoint**

Add this endpoint to `backend/app/main.py`:

```python
@app.post("/api/auth/login", response_model=schemas.Token)
def login(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Login with username and password."""
    db_user = crud.get_user_by_username(db, user_data.username)
    if not db_user or not verify_password(user_data.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token({"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
```

**Step 2: Test login endpoint**

Run: `cd backend && python -m pytest tests/test_api.py -v`

Expected: All existing tests PASS

**Step 3: Commit**

```bash
git add backend/app/main.py
git commit -m "feat: add POST /api/auth/login endpoint

- Validate username/password against stored hash
- Return JWT token on success
- Return 401 on invalid credentials"
```

---

## Task 10: Add JWT middleware for protected routes

**Files:**
- Modify: `backend/app/main.py`

**Step 1: Create dependency for token validation**

Add this function to `backend/app/main.py`:

```python
def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> models.User:
    """Extract and validate JWT token from Authorization header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

    from backend.app.security import decode_token
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = crud.get_user_by_id(db, int(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user
```

**Step 2: Update get_todos endpoint to require auth**

Find the existing `@app.get("/api/todos")` endpoint and update it:

```python
@app.get("/api/todos")
def get_todos(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    dog_name: Optional[str] = None,
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
):
    """Get todos for current user with optional filters."""
    query = db.query(models.TodoItem).filter(models.TodoItem.user_id == current_user.id)

    if dog_name:
        query = query.filter(models.TodoItem.dog_name.ilike(f"%{dog_name}%"))
    if completed is not None:
        query = query.filter(models.TodoItem.completed == completed)
    if priority:
        query = query.filter(models.TodoItem.priority == priority)

    return query.order_by(models.TodoItem.created_at.desc()).all()
```

**Step 3: Update all other todo endpoints to require auth**

For each endpoint (`POST /todos`, `GET /todos/{id}`, `PUT /todos/{id}`, `DELETE /todos/{id}`, `PATCH /todos/{id}/toggle`), add `current_user: models.User = Depends(get_current_user)` parameter and ensure operations filter by `current_user.id`.

Example for POST /todos:
```python
@app.post("/api/todos", status_code=201, response_model=schemas.TodoResponse)
def create_todo(
    todo: schemas.TodoCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Create a todo for the current user."""
    db_todo = models.TodoItem(**todo.dict(), user_id=current_user.id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo
```

For GET /todos/{todo_id}:
```python
@app.get("/api/todos/{todo_id}", response_model=schemas.TodoResponse)
def get_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get a specific todo (only if owned by current user)."""
    todo = db.query(models.TodoItem).filter(
        models.TodoItem.id == todo_id,
        models.TodoItem.user_id == current_user.id
    ).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo
```

Similar pattern for PUT, DELETE, PATCH.

**Step 4: Run tests**

Run: `cd backend && python -m pytest tests/test_api.py -v`

Note: Existing tests will fail because they don't include JWT tokens. We'll fix this next.

**Step 5: Commit**

```bash
git add backend/app/main.py
git commit -m "feat: add JWT middleware and protect todo endpoints

- get_current_user dependency validates Bearer token
- All todo endpoints require valid JWT token
- Todos filtered by current_user.id
- Returns 401 for missing/invalid/expired tokens"
```

---

## Phase 9: Update Backend Tests for Auth

### Task 11: Update existing API tests for authentication

**Files:**
- Modify: `backend/tests/test_api.py`

**Step 1: Add test helpers for auth**

Add this at the top of `backend/tests/test_api.py`:

```python
def create_test_user(db, username="testuser", password="testpass"):
    """Helper to create a test user and return token."""
    from backend.app import crud
    from backend.app.security import create_access_token

    user = crud.create_user(db, username, password)
    token = create_access_token({"sub": str(user.id)})
    return user, token


def get_auth_headers(token):
    """Helper to create Authorization header from token."""
    return {"Authorization": f"Bearer {token}"}
```

**Step 2: Update test_create_todo**

Find the existing `test_create_todo` function and update it:

```python
def test_create_todo(client, db):
    """Test creating a todo with authentication."""
    user, token = create_test_user(db)
    headers = get_auth_headers(token)

    response = client.post(
        "/api/todos",
        json={
            "task_name": "Walk the dog",
            "dog_name": "Buddy",
            "priority": "high",
        },
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["task_name"] == "Walk the dog"
    assert data["dog_name"] == "Buddy"
    assert data["priority"] == "high"
    assert data["user_id"] == user.id
```

**Step 3: Update test_get_todos**

Update the existing `test_get_todos`:

```python
def test_get_todos(client, db):
    """Test listing todos (filtered by user)."""
    user1, token1 = create_test_user(db, "user1", "pass1")
    user2, token2 = create_test_user(db, "user2", "pass2")

    # Create todos for user1
    client.post(
        "/api/todos",
        json={"task_name": "Task 1", "dog_name": "Buddy"},
        headers=get_auth_headers(token1),
    )
    client.post(
        "/api/todos",
        json={"task_name": "Task 2", "dog_name": "Max"},
        headers=get_auth_headers(token1),
    )

    # Create todo for user2
    client.post(
        "/api/todos",
        json={"task_name": "Task 3", "dog_name": "Luna"},
        headers=get_auth_headers(token2),
    )

    # User1 should only see their 2 todos
    response = client.get("/api/todos", headers=get_auth_headers(token1))
    assert response.status_code == 200
    todos = response.json()
    assert len(todos) == 2
    assert todos[0]["dog_name"] in ["Buddy", "Max"]
```

**Step 4: Add tests for auth errors**

Add these new tests:

```python
def test_get_todos_without_token(client):
    """Test that todos endpoint requires authentication."""
    response = client.get("/api/todos")
    assert response.status_code == 401
    assert "authorization" in response.json()["detail"].lower()


def test_get_todos_with_invalid_token(client):
    """Test that invalid token is rejected."""
    response = client.get(
        "/api/todos",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401


def test_create_todo_without_token(client):
    """Test that creating todo requires authentication."""
    response = client.post(
        "/api/todos",
        json={"task_name": "Task", "dog_name": "Dog"}
    )
    assert response.status_code == 401
```

**Step 5: Run tests**

Run: `cd backend && python -m pytest tests/test_api.py -v`

Expected: All tests PASS (or show which ones need updating)

**Step 6: Commit**

```bash
git add backend/tests/test_api.py
git commit -m "test: update API tests for JWT authentication

- Add auth helpers for creating test users and tokens
- Update all todo endpoint tests to include Authorization header
- Add tests for 401 errors when auth is missing/invalid
- Verify todo filtering by user_id"
```

---

## Phase 10: Frontend Setup

### Task 12: Create login and register pages

**Files:**
- Create: `frontend/src/pages/LoginPage.jsx`
- Create: `frontend/src/pages/RegisterPage.jsx`

**Step 1: Create LoginPage.jsx**

Create new file `frontend/src/pages/LoginPage.jsx`:

```jsx
import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })

      const data = await response.json()

      if (!response.ok) {
        setError(data.detail || 'Login failed')
        return
      }

      localStorage.setItem('token', data.access_token)
      navigate('/')
    } catch (err) {
      setError('Network error - is the backend running?')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-form">
        <h1>🐕 Dog Todo</h1>
        <h2>Login</h2>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              disabled={isLoading}
            />
          </div>

          <button type="submit" disabled={isLoading} className="btn-primary">
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <p className="auth-link">
          Don't have an account? <Link to="/register">Sign up here</Link>
        </p>
      </div>
    </div>
  )
}
```

**Step 2: Create RegisterPage.jsx**

Create new file `frontend/src/pages/RegisterPage.jsx`:

```jsx
import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'

export default function RegisterPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })

      const data = await response.json()

      if (!response.ok) {
        setError(data.detail || 'Registration failed')
        return
      }

      localStorage.setItem('token', data.access_token)
      navigate('/')
    } catch (err) {
      setError('Network error - is the backend running?')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-form">
        <h1>🐕 Dog Todo</h1>
        <h2>Create Account</h2>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Choose a username"
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Choose a password"
              disabled={isLoading}
            />
          </div>

          <button type="submit" disabled={isLoading} className="btn-primary">
            {isLoading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <p className="auth-link">
          Already have an account? <Link to="/login">Login here</Link>
        </p>
      </div>
    </div>
  )
}
```

**Step 3: Commit**

```bash
git add frontend/src/pages/LoginPage.jsx frontend/src/pages/RegisterPage.jsx
git commit -m "feat: add login and register pages

- LoginPage: username/password form with login flow
- RegisterPage: username/password form with registration flow
- Both save token to localStorage and redirect to home"
```

---

### Task 13: Create ProtectedRoute component

**Files:**
- Create: `frontend/src/components/ProtectedRoute.jsx`

**Step 1: Create ProtectedRoute.jsx**

Create new file `frontend/src/components/ProtectedRoute.jsx`:

```jsx
import { Navigate } from 'react-router-dom'

export default function ProtectedRoute({ children }) {
  const token = localStorage.getItem('token')

  if (!token) {
    return <Navigate to="/login" replace />
  }

  return children
}
```

**Step 2: Commit**

```bash
git add frontend/src/components/ProtectedRoute.jsx
git commit -m "feat: add ProtectedRoute component

- Redirects to /login if no token in localStorage
- Wraps todo app to require authentication"
```

---

### Task 14: Create auth service

**Files:**
- Create: `frontend/src/services/auth.js`

**Step 1: Create auth.js**

Create new file `frontend/src/services/auth.js`:

```js
const API_URL = '/api/auth'

export const authService = {
  register: async (username, password) => {
    const response = await fetch(`${API_URL}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Registration failed')
    }
    return await response.json()
  },

  login: async (username, password) => {
    const response = await fetch(`${API_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Login failed')
    }
    return await response.json()
  },

  logout: () => {
    localStorage.removeItem('token')
  },

  getToken: () => localStorage.getItem('token'),

  setToken: (token) => localStorage.setItem('token', token),

  isAuthenticated: () => !!localStorage.getItem('token'),
}
```

**Step 2: Commit**

```bash
git add frontend/src/services/auth.js
git commit -m "feat: add auth service for API calls

- login/register functions for API requests
- getToken/setToken/logout for token management
- isAuthenticated for checking auth status"
```

---

## Phase 11: Frontend App Routing & State Management

### Task 15: Update App.jsx for routing and auth

**Files:**
- Modify: `frontend/src/App.jsx`
- Modify: `frontend/src/main.jsx`

**Step 1: Install React Router**

Add react-router-dom to `frontend/package.json` dependencies if not present, then run:
```bash
cd frontend && npm install
```

**Step 2: Update main.jsx with Router**

Replace `frontend/src/main.jsx` with:

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
```

**Step 3: Create new App.jsx structure**

Replace `frontend/src/App.jsx` with:

```jsx
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProtectedRoute from './components/ProtectedRoute'
import TodoApp from './TodoApp'
import { authService } from './services/auth'

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    // Check if user is already logged in
    const token = authService.getToken()
    if (token) {
      setIsAuthenticated(true)
    }
  }, [])

  const handleLogout = () => {
    authService.logout()
    setIsAuthenticated(false)
    navigate('/login')
  }

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <TodoApp onLogout={handleLogout} />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
```

**Step 4: Create TodoApp.jsx (rename from App.jsx logic)**

Move the existing todo app logic to `frontend/src/TodoApp.jsx`:

```jsx
import { useState, useEffect } from 'react'
import TodoForm from './components/TodoForm'
import TodoList from './components/TodoList'
import './App.css'
import { apiService } from './services/api'

export default function TodoApp({ onLogout }) {
  const [todos, setTodos] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [hasError, setHasError] = useState(false)
  const [filters, setFilters] = useState({ dog_name: '', completed: null, priority: '' })

  useEffect(() => {
    fetchTodos()
  }, [filters])

  const fetchTodos = async () => {
    setIsLoading(true)
    setHasError(false)
    try {
      const data = await apiService.fetchTodos(filters)
      setTodos(data)
    } catch (error) {
      setHasError(true)
      console.error('Failed to fetch todos:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateTodo = async (todo) => {
    try {
      const newTodo = await apiService.createTodo(todo)
      setTodos([newTodo, ...todos])
    } catch (error) {
      console.error('Failed to create todo:', error)
    }
  }

  const handleToggleTodo = async (id) => {
    try {
      const updated = await apiService.toggleTodo(id)
      setTodos(todos.map(t => (t.id === id ? updated : t)))
    } catch (error) {
      console.error('Failed to toggle todo:', error)
    }
  }

  const handleDeleteTodo = async (id) => {
    try {
      await apiService.deleteTodo(id)
      setTodos(todos.filter(t => t.id !== id))
    } catch (error) {
      console.error('Failed to delete todo:', error)
    }
  }

  const handleEditTodo = (todo) => {
    console.log('Edit todo:', todo)
  }

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters)
  }

  const handleClearFilters = () => {
    setFilters({ dog_name: '', completed: null, priority: '' })
  }

  return (
    <div className="app-container">
      <div className="app-header">
        <h1>🐾 Dog Todo App</h1>
        <p>Manage your dog's tasks with ease!</p>
        <button onClick={onLogout} className="btn-logout">
          Logout
        </button>
      </div>
      <div className="app-content">
        <div className="sidebar">
          <TodoForm onSubmit={handleCreateTodo} isLoading={isLoading} />
        </div>
        <div className="todo-main">
          <TodoList
            todos={todos}
            onToggle={handleToggleTodo}
            onDelete={handleDeleteTodo}
            onEdit={handleEditTodo}
            isLoading={isLoading}
            hasError={hasError}
          />
        </div>
      </div>
    </div>
  )
}
```

**Step 5: Update api.js to include auth header**

Modify `frontend/src/services/api.js` to add Authorization header to all requests:

```js
import axios from 'axios'
import { authService } from './auth'

const client = axios.create({
  baseURL: '/api',
  timeout: 5000,
})

// Add Authorization header to all requests
client.interceptors.request.use((config) => {
  const token = authService.getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 errors by redirecting to login
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      authService.logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const apiService = {
  fetchTodos: async (filters = {}) => {
    const params = new URLSearchParams()
    if (filters.dog_name) params.append('dog_name', filters.dog_name)
    if (filters.completed !== null && filters.completed !== undefined) {
      params.append('completed', filters.completed)
    }
    if (filters.priority) params.append('priority', filters.priority)
    const { data } = await client.get(`/todos?${params}`)
    return data
  },

  createTodo: async (todo) => {
    const { data } = await client.post('/todos', todo)
    return data
  },

  getTodo: async (id) => {
    const { data } = await client.get(`/todos/${id}`)
    return data
  },

  updateTodo: async (id, todo) => {
    const { data } = await client.put(`/todos/${id}`, todo)
    return data
  },

  deleteTodo: async (id) => {
    await client.delete(`/todos/${id}`)
  },

  toggleTodo: async (id) => {
    const { data } = await client.patch(`/todos/${id}/toggle`)
    return data
  },
}
```

**Step 6: Add auth styling to App.css**

Add these styles to `frontend/src/App.css`:

```css
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5e6d3 0%, #e8d5b7 100%);
}

.auth-form {
  background: white;
  border-radius: 15px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.auth-form h1 {
  text-align: center;
  color: #8b6f47;
  font-size: 2rem;
  margin: 0 0 0.5rem 0;
}

.auth-form h2 {
  text-align: center;
  color: #8b6f47;
  font-size: 1.5rem;
  margin: 0 0 1.5rem 0;
}

.auth-form .form-group {
  margin-bottom: 1rem;
}

.auth-form .form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #333;
  font-weight: 500;
}

.auth-form .form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  box-sizing: border-box;
}

.auth-form .btn-primary {
  width: 100%;
  padding: 0.75rem;
  background: linear-gradient(135deg, #8b6f47 0%, #a0826d 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  margin-top: 1rem;
}

.auth-form .btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.auth-link {
  text-align: center;
  margin-top: 1rem;
  color: #666;
}

.auth-link a {
  color: #8b6f47;
  text-decoration: none;
  font-weight: bold;
}

.auth-link a:hover {
  text-decoration: underline;
}

.btn-logout {
  background: #d9534f;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.9rem;
  margin-top: 1rem;
}

.btn-logout:hover {
  background: #c9302c;
}

.app-header {
  position: relative;
}
```

**Step 7: Create pages directory**

```bash
mkdir -p frontend/src/pages
```

**Step 8: Run frontend dev server**

Run: `cd frontend && npm run dev`

Expected: App starts on http://localhost:5173

**Step 9: Commit**

```bash
git add frontend/src/main.jsx frontend/src/App.jsx frontend/src/TodoApp.jsx
git add frontend/src/services/api.js frontend/package.json
git commit -m "feat: add routing and authentication to frontend

- React Router setup with /login, /register, / routes
- ProtectedRoute wrapper for authenticated pages
- JWT token in localStorage with axios interceptors
- Auto-redirect to login on 401 responses
- Logout button in header
- API requests include Authorization header"
```

---

## Phase 12: Frontend Integration Testing

### Task 16: Manual end-to-end testing

**Files:** None (manual testing)

**Testing Checklist:**

1. **Registration Flow**
   - [ ] Navigate to http://localhost:5173/register
   - [ ] Enter new username and password
   - [ ] Click "Create Account"
   - [ ] Should redirect to todo app homepage
   - [ ] Token should be in localStorage (check DevTools)

2. **Login Flow**
   - [ ] Log out (click logout button)
   - [ ] Should redirect to /login
   - [ ] Try logging in with registered credentials
   - [ ] Should succeed and show todos

3. **Todo Operations with Auth**
   - [ ] Create a todo
   - [ ] Toggle completion
   - [ ] Delete a todo
   - [ ] All operations should work

4. **Multi-user Isolation**
   - [ ] Open app in private/incognito window
   - [ ] Register different username
   - [ ] Create a todo
   - [ ] Both users should see empty lists (no shared todos)

5. **Token Expiry**
   - [ ] Edit token in localStorage to old date
   - [ ] Try to create a todo
   - [ ] Should redirect to login

6. **Error Handling**
   - [ ] Try registering duplicate username → should show error
   - [ ] Try logging in with wrong password → should show error
   - [ ] Try accessing /api/todos without token → should fail

---

## Phase 13: Cleanup & Documentation

### Task 17: Update CLAUDE.md for auth feature

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Update Authentication section in CLAUDE.md**

Add new section after "API Specification":

```markdown
## Authentication

**Login & Registration**:
- `POST /auth/register` - Create new user account
- `POST /auth/login` - Login with username/password
- `POST /auth/logout` - Logout (frontend token removal)
- `GET /auth/me` - Get current user info (optional)

**JWT Token**:
- 24-hour expiration (auto-logout on inactivity)
- Stored in browser localStorage
- Sent in Authorization header: `Bearer <token>`
- Invalid/expired tokens return 401, redirect to login

**Frontend Routes**:
- `/login` - Login page
- `/register` - Registration page
- `/` - Todo app (protected, requires login)
```

**Step 2: Update Data Model section**

Add new User model to the data model section:

```markdown
**User** SQLAlchemy model fields:
- `id` - Integer primary key
- `username` - String, unique, required
- `password_hash` - String (bcrypt), required
- `created_at` - Timestamp (auto-generated)

**TodoItem updated**:
- `user_id` - Foreign key to User (added)
- Todos now scoped per user (filtering by user_id)
```

**Step 3: Update dependencies section**

Add to requirements:

```markdown
**Authentication**:
- python-jose==3.3.0 (JWT tokens)
- passlib[bcrypt]==1.7.4 (password hashing)
- python-multipart==0.0.6 (form data)

**Frontend**:
- react-router-dom (routing for auth pages)
```

**Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md for authentication feature

- Add auth endpoints documentation
- Update data model with User table
- Document JWT token handling
- Add new dependencies"
```

---

## Summary

**Files Modified**: 12
**Files Created**: 10
**Total Commits**: 17

**Key Components**:
1. Backend auth: 3 endpoints (register, login, logout)
2. Backend security: JWT + bcrypt utilities
3. Frontend auth: Login, Register, ProtectedRoute
4. Frontend routing: React Router with protected routes
5. Frontend API: Axios with JWT interceptors
6. Database: User model + user_id on todos

**Test Coverage**:
- Security utilities: password hashing, token creation/validation
- User CRUD: creation, lookup, duplicate handling
- API auth: protected endpoints, 401 errors, user isolation
- Frontend: routing, error display, auth redirects

**What's NOT Included** (scope creep):
- ❌ Email verification
- ❌ Password reset/recovery
- ❌ Remember me functionality
- ❌ Social login
- ❌ Rate limiting
- ❌ Session persistence across devices
