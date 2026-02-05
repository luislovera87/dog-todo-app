# CLAUDE.md - Dog Todo App Development Guide

This file provides guidance to Claude Code when working with this Dog Todo App project.

## Project Status

The Dog Todo App is a fully implemented full-stack application with:
- ✅ Backend: FastAPI + SQLAlchemy + SQLite
- ✅ Frontend: React 18 + Vite
- ✅ Testing: Pytest with >80% coverage
- ✅ Documentation: README and API docs

## Project Structure Overview

**Backend** (`backend/`):
- `app/main.py` - FastAPI application, all routes
- `app/models.py` - SQLAlchemy TodoItem model
- `app/schemas.py` - Pydantic request/response schemas
- `app/crud.py` - Database operations (create, read, update, delete, toggle)
- `app/database.py` - Database connection setup
- `app/config.py` - Configuration

**Frontend** (`frontend/`):
- `src/main.jsx` - React entry point
- `src/App.jsx` - Main React component, state management
- `src/components/` - Reusable UI components (TodoForm, TodoItem, TodoList, DogAvatar)
- `src/services/api.js` - Axios HTTP client
- `src/App.css` - Component styles with dog theme
- `src/index.css` - Global styles

**Tests** (`backend/tests/`):
- `test_api.py` - API endpoint tests
- `test_crud.py` - CRUD operation tests
- `test_models.py` - SQLAlchemy model tests
- `conftest.py` - Pytest fixtures

## Build and Development Commands

### Backend
```bash
# Setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest -v --cov=app

# Run specific test file
pytest tests/test_api.py -v
```

### Frontend
```bash
# Setup
cd frontend
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Architecture Overview

**Data Flow**:
1. Frontend (React) sends HTTP requests via Axios
2. Backend (FastAPI) receives requests and validates with Pydantic
3. Database operations via SQLAlchemy ORM
4. Responses returned as JSON
5. Frontend updates React state and re-renders UI

**Key Features**:
- **CORS**: Enabled for frontend-to-backend communication
- **Validation**: Pydantic schemas enforce data integrity
- **Database**: SQLite with automatic migrations via SQLAlchemy
- **Testing**: Comprehensive unit tests with fixtures
- **Error Handling**: Proper HTTP status codes (200, 201, 404, 422)

## API Specification

All endpoints return JSON. Base URL: `http://localhost:8000/api`

### Endpoints
- `GET /health` - Health check endpoint
- `GET /todos` - List todos (supports filtering)
- `POST /todos` - Create todo (status: 201)
- `GET /todos/{id}` - Get specific todo
- `PUT /todos/{id}` - Update todo
- `DELETE /todos/{id}` - Delete todo (status: 204)
- `PATCH /todos/{id}/toggle` - Toggle completion

### Filter Query Parameters
- `dog_name` - Filter by dog name (string)
- `completed` - Filter by completion (boolean)
- `priority` - Filter by priority (low/medium/high)

Example: `/todos?dog_name=Buddy&completed=false&priority=high`

### Priority Labels
In the UI, priority levels are displayed with dog-themed language:
- `low` → "Nap-worthy"
- `medium` → "Walk-worthy"
- `high` → "Treat-worthy"

## Data Model

**Database**: SQLite file-based storage at `backend/dog_todos.db` (auto-created on first run)

**TodoItem** SQLAlchemy model fields:
- `id` - Integer primary key
- `task_name` - Required string
- `dog_name` - Required string
- `description` - Optional string
- `completed` - Boolean (default: false)
- `priority` - Enum: low, medium, high (default: medium)
- `due_date` - Optional datetime
- `created_at` - Timestamp (auto-generated)
- `updated_at` - Timestamp (auto-updated)

**Pydantic Schemas**:
- `TodoCreate` - Request body for POST /todos
- `TodoUpdate` - Request body for PUT /todos/{id}
- `TodoResponse` - Response body for all endpoints

## Common Development Tasks

### Add a New API Endpoint
1. Define Pydantic schema in `app/schemas.py`
2. Add CRUD function in `app/crud.py`
3. Add route in `app/main.py`
4. Add tests in `backend/tests/test_api.py`

### Add a New Database Field
1. Update `TodoItem` model in `app/models.py`
2. Update Pydantic schemas in `app/schemas.py`
3. Add database migration (SQLAlchemy auto-creates on startup)
4. Add tests for new field in `test_models.py`

### Fix a Bug
1. Write a failing test in `backend/tests/`
2. Run test to confirm it fails
3. Fix the code
4. Verify test passes: `pytest -v`

### Add Frontend Component
1. Create component file in `src/components/`
2. Use functional components with hooks
3. Import in `App.jsx` where needed
4. Add tests if complex logic (not required for simple components)

### Edit Todo Functionality
⚠️ **Current Status**: Form UI and button implemented, but edit mode is a placeholder (logs to console). To fully implement:
1. Add edit state management in `App.jsx` (selectedTodo, isEditMode)
2. Populate TodoForm fields when in edit mode
3. Change POST to PUT request in handleCreateTodo when editing
4. Reset edit mode after successful update
5. Add API endpoint integration test for update functionality

## Testing Strategy

**Unit Tests** cover:
- Model creation and field types
- CRUD operations (create, read, update, delete)
- Database queries and filtering
- API endpoints and status codes
- Error handling and validation
- Edge cases and boundary conditions

**Test Execution**:
```bash
# Run all tests with coverage
pytest -v --cov=app

# Run specific test file
pytest tests/test_api.py -v

# Run single test
pytest tests/test_api.py::test_create_todo -v
```

**Test Summary**:
- **Total Tests**: 33 across 3 test files
  - test_api.py: 16 tests (API endpoints + filters + error handling)
  - test_crud.py: 14 tests (CRUD operations at database level)
  - test_models.py: 3 tests (Model creation and defaults)
- **Coverage Target**: >80% across all modules

## Performance Considerations

- **Database**: SQLite suitable for single-user; PostgreSQL for production scaling
- **Frontend**: React lazy loading via React.lazy() if needed
- **Caching**: Consider Redis for frequently accessed data
- **Pagination**: Add if todo list grows large (>1000 items)

## Important Files and Their Purposes

### Critical Files (Frequently Modified)
1. `backend/app/main.py` - All API routes
2. `backend/app/crud.py` - All database logic
3. `frontend/src/App.jsx` - Main UI state and logic
4. `frontend/src/components/TodoForm.jsx` - Task creation UI

### Supporting Files
1. `backend/app/models.py` - Data structure
2. `backend/app/schemas.py` - Request/response validation
3. `backend/tests/test_api.py` - API verification

## Deployment Considerations

### Backend
- Use environment variables for configuration
- Secure database credentials
- Enable HTTPS in production
- Consider database backups
- Health check endpoint (`/api/health`) can be used for monitoring/readiness probes

### Frontend
- Run `npm run build` for production
- Serve `dist/` folder with web server
- Set correct API base URL for production
- Implement error boundaries

## Development Workflows

### Local Development
1. Terminal 1: `cd backend && source venv/bin/activate && uvicorn app.main:app --reload`
2. Terminal 2: `cd frontend && npm run dev`
3. Terminal 3: `cd backend && source venv/bin/activate && pytest --cov=app`
4. Open http://localhost:5173

### Before Committing
1. Run tests: `pytest -v --cov=app`
2. Verify coverage: >80%
3. Check for lint issues: `flake8 app/` (optional)
4. Test manually in browser
5. Commit with clear message

## Troubleshooting Common Issues

**Backend won't start**
- Check Python version: `python --version` (need 3.8+)
- Activate venv: `source venv/bin/activate`
- Install deps: `pip install -r requirements.txt`
- Check port 8000: `lsof -i :8000`

**Frontend shows API errors**
- Backend must be running
- Check CORS configuration in `app/main.py`
- Verify Vite proxy config in `frontend/vite.config.js`

**Tests fail**
- Remove test database: `rm backend/test.db`
- Reinstall dependencies: `pip install -r requirements.txt`
- Check database permissions: `chmod 755 backend/`

## Next Steps / Future Enhancements

- Add user authentication (JWT)
- Implement recurring tasks
- Add calendar view
- Create email notifications
- Build mobile app (React Native)
- Add search functionality
- Implement soft deletes
- Add audit logging

## Code Style and Conventions

**Python (Backend)**:
- PEP 8 style guide
- Type hints where applicable
- Docstrings for functions
- 80-character line limit

**JavaScript (Frontend)**:
- ES6 modules
- Functional components with hooks
- Consistent naming: camelCase for functions/variables
- Comments for complex logic

**Naming Conventions**:
- Endpoints: lowercase, hyphenated (`/todos`, `/toggle`)
- Database: snake_case (`task_name`, `dog_name`)
- React components: PascalCase (`TodoForm`, `TodoItem`)
- Variables/functions: camelCase (`isLoading`, `handleSubmit`)

## Resources

- FastAPI docs: https://fastapi.tiangolo.com/
- SQLAlchemy docs: https://docs.sqlalchemy.org/
- React docs: https://react.dev/
- Vite docs: https://vitejs.dev/
- Pytest docs: https://docs.pytest.org/

---

This CLAUDE.md should be updated when:
- New major features are added
- Architecture significantly changes
- Development workflow changes
- Important files are added/removed
