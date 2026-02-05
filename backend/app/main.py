from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.models import PriorityEnum
from app.schemas import TodoCreate, TodoUpdate, TodoResponse
from app import crud

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

@app.get("/api/todos", response_model=list[TodoResponse])
def list_todos(
    db: Session = Depends(get_db),
    dog_name: str = Query(None),
    completed: bool = Query(None),
    priority: PriorityEnum = Query(None),
):
    return crud.get_todos(db, dog_name=dog_name, completed=completed, priority=priority)

@app.get("/api/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = crud.get_todo(db, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo

@app.post("/api/todos", response_model=TodoResponse, status_code=201)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    return crud.create_todo(db, todo)

@app.put("/api/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo_update: TodoUpdate, db: Session = Depends(get_db)):
    db_todo = crud.update_todo(db, todo_id, todo_update)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo

@app.delete("/api/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    success = crud.delete_todo(db, todo_id)
    if not success:
        raise HTTPException(status_code=404, detail="Todo not found")
    return None

@app.patch("/api/todos/{todo_id}/toggle", response_model=TodoResponse)
def toggle_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = crud.toggle_todo_completion(db, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo
