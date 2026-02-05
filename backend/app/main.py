from fastapi import FastAPI, Depends, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.models import PriorityEnum, User, TodoItem
from app.schemas import TodoCreate, TodoUpdate, TodoResponse, UserCreate, Token
from app import crud
from app.security import create_access_token, verify_password, decode_token
from typing import Optional

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dog Todo API", description="Manage dog-related tasks")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/auth/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    existing_user = crud.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=409, detail="Username already exists")

    db_user = crud.create_user(db, user_data.username, user_data.password)
    access_token = create_access_token({"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/auth/login", response_model=Token)
def login(user_data: UserCreate, db: Session = Depends(get_db)):
    """Login with username and password."""
    db_user = crud.get_user_by_username(db, user_data.username)
    if not db_user or not verify_password(user_data.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token({"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Extract and validate JWT token from Authorization header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

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

@app.get("/api/todos", response_model=list[TodoResponse])
def list_todos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    dog_name: str = Query(None),
    completed: bool = Query(None),
    priority: PriorityEnum = Query(None),
):
    """Get todos for current user with optional filters."""
    query = db.query(TodoItem).filter(TodoItem.user_id == current_user.id)

    if dog_name:
        query = query.filter(TodoItem.dog_name.ilike(f"%{dog_name}%"))
    if completed is not None:
        query = query.filter(TodoItem.completed == completed)
    if priority:
        query = query.filter(TodoItem.priority == priority)

    return query.order_by(TodoItem.created_at.desc()).all()

@app.get("/api/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get a specific todo (only if owned by current user)."""
    todo = db.query(TodoItem).filter(
        TodoItem.id == todo_id,
        TodoItem.user_id == current_user.id
    ).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.post("/api/todos", response_model=TodoResponse, status_code=201)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a todo for the current user."""
    db_todo = TodoItem(**todo.model_dump(), user_id=current_user.id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.put("/api/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo_update: TodoUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update a todo (only if owned by current user)."""
    db_todo = db.query(TodoItem).filter(
        TodoItem.id == todo_id,
        TodoItem.user_id == current_user.id
    ).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    update_data = todo_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_todo, field, value)

    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.delete("/api/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete a todo (only if owned by current user)."""
    db_todo = db.query(TodoItem).filter(
        TodoItem.id == todo_id,
        TodoItem.user_id == current_user.id
    ).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(db_todo)
    db.commit()
    return None

@app.patch("/api/todos/{todo_id}/toggle", response_model=TodoResponse)
def toggle_todo(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Toggle todo completion (only if owned by current user)."""
    db_todo = db.query(TodoItem).filter(
        TodoItem.id == todo_id,
        TodoItem.user_id == current_user.id
    ).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db_todo.completed = not db_todo.completed
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo
