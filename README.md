# 🐾 Dog Todo App

A full-stack todo application for managing dog-related tasks. Built with React 18 + Vite on the frontend and FastAPI + SQLAlchemy on the backend.

## Features

✨ **Core Features**:
- Create, read, update, and delete dog-related tasks
- Mark tasks as complete with a checkbox (🐾)
- Filter tasks by dog name, priority, or completion status
- Set priority levels: Nap-worthy (low), Walk-worthy (medium), Treat-worthy (high)
- Optional due dates and descriptions
- Dog-themed UI with playful emojis and paw print decorations
- Real-time updates across the app

🎨 **UI Features**:
- Dog avatars with emojis (Buddy 🐕, Max 🐶, Luna 🐕, etc.)
- Color-coded priority badges
- Responsive design (desktop and mobile)
- Playful language ("Good dog!", "Fetch your tasks!", "No tasks to chase!")
- Animated paw print decoration

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework with automatic API documentation
- **SQLAlchemy** - ORM for database operations
- **SQLite** - File-based database (dog_todos.db)
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server
- **Pytest** - Unit testing framework with coverage reporting

### Frontend
- **React 18** - UI library with functional components and hooks
- **Vite** - Fast build tool and dev server (HMR)
- **Axios** - HTTP client for API communication
- **CSS** - Dog-themed styling with gradients and animations

## Project Structure

```
claude-sandbox/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app and routes
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── crud.py              # Database operations
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── config.py            # Configuration
│   │   └── __init__.py
│   ├── tests/
│   │   ├── test_models.py       # Model tests
│   │   ├── test_crud.py         # CRUD tests
│   │   ├── test_api.py          # API endpoint tests
│   │   ├── conftest.py          # Pytest fixtures
│   │   └── __init__.py
│   ├── venv/                    # Python virtual environment
│   ├── requirements.txt         # Python dependencies
│   └── dog_todos.db             # SQLite database (created at runtime)
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── TodoForm.jsx     # Form for creating todos
│   │   │   ├── TodoItem.jsx     # Individual todo display
│   │   │   ├── TodoList.jsx     # List container
│   │   │   └── DogAvatar.jsx    # Dog emoji component
│   │   ├── services/
│   │   │   └── api.js           # Axios API client
│   │   ├── App.jsx              # Main component
│   │   ├── App.css              # Component styles
│   │   ├── main.jsx             # React entry point
│   │   ├── index.css            # Global styles
│   │   └── vite.svg
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   ├── node_modules/            # Dependencies
│   └── dist/                    # Build output (created at runtime)
│
├── README.md                    # This file
├── CLAUDE.md                    # Claude Code instructions
└── .gitignore                   # Git ignore rules
```

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd /home/circawolf/projects/claude-sandbox/backend
   ```

2. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Verify dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the backend server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The backend will be available at:
   - API: `http://localhost:8000`
   - Interactive API docs: `http://localhost:8000/docs`
   - Alternative docs: `http://localhost:8000/redoc`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd /home/circawolf/projects/claude-sandbox/frontend
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173`

### Running Tests

In a new terminal, run the backend tests:

```bash
cd /home/circawolf/projects/claude-sandbox/backend
source venv/bin/activate
pytest -v --cov=app
```

Expected output: All tests pass with >80% coverage

## API Endpoints

All endpoints are prefixed with `/api`.

### Todos

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/todos` | List all todos with optional filters |
| `GET` | `/todos/{id}` | Get a specific todo |
| `POST` | `/todos` | Create a new todo |
| `PUT` | `/todos/{id}` | Update an existing todo |
| `DELETE` | `/todos/{id}` | Delete a todo |
| `PATCH` | `/todos/{id}/toggle` | Toggle completion status |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check endpoint |

### Query Parameters

Use query parameters to filter todos:

```bash
# Filter by dog name
curl http://localhost:8000/api/todos?dog_name=Buddy

# Filter by completion status
curl http://localhost:8000/api/todos?completed=false

# Filter by priority
curl http://localhost:8000/api/todos?priority=high

# Combine filters
curl "http://localhost:8000/api/todos?dog_name=Buddy&completed=false&priority=high"
```

### Request/Response Examples

**Create a Todo:**
```bash
curl -X POST http://localhost:8000/api/todos \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "Walk Buddy",
    "dog_name": "Buddy",
    "description": "30-minute walk in the park",
    "priority": "high",
    "due_date": "2025-02-10T15:00:00"
  }'
```

**Response (201 Created):**
```json
{
  "id": 1,
  "task_name": "Walk Buddy",
  "dog_name": "Buddy",
  "description": "30-minute walk in the park",
  "completed": false,
  "priority": "high",
  "due_date": "2025-02-10T15:00:00",
  "created_at": "2025-02-04T10:30:00",
  "updated_at": "2025-02-04T10:30:00"
}
```

**List Todos:**
```bash
curl http://localhost:8000/api/todos
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "task_name": "Walk Buddy",
    "dog_name": "Buddy",
    "description": "30-minute walk in the park",
    "completed": false,
    "priority": "high",
    "due_date": "2025-02-10T15:00:00",
    "created_at": "2025-02-04T10:30:00",
    "updated_at": "2025-02-04T10:30:00"
  }
]
```

## Data Model

**TodoItem** table schema:

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| id | Integer | No | Auto-increment | Primary key |
| task_name | String | No | - | Task description |
| dog_name | String | No | - | Name of the dog |
| description | String | Yes | NULL | Optional details |
| completed | Boolean | No | false | Completion status |
| priority | Enum | No | "medium" | low, medium, high |
| due_date | DateTime | Yes | NULL | Optional deadline |
| created_at | DateTime | No | now() | Timestamp |
| updated_at | DateTime | No | now() | Updated timestamp |

Priority levels:
- `low` - "Nap-worthy" 😴
- `medium` - "Walk-worthy" 🚶
- `high` - "Treat-worthy" 🍖

## Development Workflow

### Terminal 1: Backend
```bash
cd /home/circawolf/projects/claude-sandbox/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Frontend
```bash
cd /home/circawolf/projects/claude-sandbox/frontend
npm run dev
```

### Terminal 3: Tests
```bash
cd /home/circawolf/projects/claude-sandbox/backend
source venv/bin/activate
pytest -v --cov=app --cov-report=html
# View coverage report: open htmlcov/index.html
```

## Verification Steps

### 1. Backend Health
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok"}
```

### 2. Create a Todo
```bash
curl -X POST http://localhost:8000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"task_name":"Give Max his medication","dog_name":"Max","priority":"high"}'
```

### 3. Visit Frontend
Open your browser and navigate to `http://localhost:5173`

### 4. Test CRUD Operations
1. Fill out the form and create a task
2. Verify it appears in the list
3. Check the checkbox to mark it complete
4. Use filters to find tasks by dog name or priority
5. Delete a task to verify it's removed

### 5. View Database
```bash
sqlite3 /home/circawolf/projects/claude-sandbox/backend/dog_todos.db
sqlite> SELECT * FROM todos;
sqlite> .exit
```

## Testing

### Run All Tests
```bash
cd /home/circawolf/projects/claude-sandbox/backend
source venv/bin/activate
pytest -v
```

### Test Coverage
```bash
pytest -v --cov=app --cov-report=term-missing
```

### Run Specific Test File
```bash
pytest tests/test_api.py -v
```

### Watch Mode
```bash
pytest-watch tests/ -- -v
```

## Troubleshooting

### Backend Won't Start
- Ensure Python 3.8+ is installed
- Check virtual environment is activated: `source venv/bin/activate`
- Verify dependencies: `pip install -r requirements.txt`
- Try removing `dog_todos.db` and starting fresh

### Frontend Shows "Cannot GET /health"
- Backend must be running on `http://localhost:8000`
- Check that CORS is configured in FastAPI
- Verify no firewall is blocking port 8000

### Tests Fail
- Ensure you're in the backend directory: `cd backend`
- Activate venv: `source venv/bin/activate`
- Remove test database: `rm test.db`
- Run tests: `pytest -v`

### Database Errors
- Remove the database file: `rm dog_todos.db`
- Restart the backend server

## Build and Deployment

### Build Frontend
```bash
cd /home/circawolf/projects/claude-sandbox/frontend
npm run build
# Output: dist/
```

### Production Backend
```bash
cd /home/circawolf/projects/claude-sandbox/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Sample Data

To populate with sample data, create a script or use the API:

```bash
# Walk Buddy
curl -X POST http://localhost:8000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"task_name":"Morning walk","dog_name":"Buddy","priority":"high"}'

# Feed Max
curl -X POST http://localhost:8000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"task_name":"Dinner time","dog_name":"Max","priority":"medium"}'

# Groom Luna
curl -X POST http://localhost:8000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"task_name":"Bath and brushing","dog_name":"Luna","priority":"high"}'
```

## Performance Notes

- Database queries include ordering by creation date (newest first)
- Filtering is performed server-side for efficiency
- Frontend uses React hooks for state management
- Vite provides fast HMR during development
- SQLite is suitable for single-user/small-scale use; consider PostgreSQL for production

## Future Enhancements

- User authentication and authorization
- Multi-user support
- Calendar view for due dates
- Recurring tasks
- Task categories/tags
- Search functionality
- Email/SMS reminders
- Mobile app (React Native)
- Dark mode toggle
- Drag-and-drop reordering
- Analytics dashboard

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run tests: `pytest -v`
4. Commit: `git commit -m "Add feature description"`
5. Push and create a PR

## License

MIT License

## Support

For issues, questions, or feedback:
1. Check the Troubleshooting section
2. Review API documentation at http://localhost:8000/docs
3. Check test files for usage examples

Happy doggy task managing! 🐾🦴
