from sqlalchemy.orm import Session
from app.models import TodoItem, PriorityEnum, User
from app.schemas import TodoCreate, TodoUpdate
from typing import List, Optional
from app.security import hash_password, verify_password

def create_todo(db: Session, todo: TodoCreate) -> TodoItem:
    db_todo = TodoItem(
        task_name=todo.task_name,
        dog_name=todo.dog_name,
        description=todo.description,
        priority=todo.priority,
        due_date=todo.due_date,
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def get_todos(
    db: Session,
    dog_name: Optional[str] = None,
    completed: Optional[bool] = None,
    priority: Optional[PriorityEnum] = None,
) -> List[TodoItem]:
    query = db.query(TodoItem)
    if dog_name:
        query = query.filter(TodoItem.dog_name == dog_name)
    if completed is not None:
        query = query.filter(TodoItem.completed == completed)
    if priority:
        query = query.filter(TodoItem.priority == priority)
    return query.order_by(TodoItem.created_at.desc()).all()

def get_todo(db: Session, todo_id: int) -> Optional[TodoItem]:
    return db.query(TodoItem).filter(TodoItem.id == todo_id).first()

def update_todo(db: Session, todo_id: int, todo_update: TodoUpdate) -> Optional[TodoItem]:
    db_todo = get_todo(db, todo_id)
    if not db_todo:
        return None

    update_data = todo_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_todo, field, value)

    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def delete_todo(db: Session, todo_id: int) -> bool:
    db_todo = get_todo(db, todo_id)
    if not db_todo:
        return False
    db.delete(db_todo)
    db.commit()
    return True

def toggle_todo_completion(db: Session, todo_id: int) -> Optional[TodoItem]:
    db_todo = get_todo(db, todo_id)
    if not db_todo:
        return None
    db_todo.completed = not db_todo.completed
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def create_user(db: Session, username: str, password: str):
    """Create a new user with hashed password."""
    hashed_password = hash_password(password)
    db_user = User(username=username, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    """Retrieve a user by username."""
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: int):
    """Retrieve a user by ID."""
    return db.query(User).filter(User.id == user_id).first()
