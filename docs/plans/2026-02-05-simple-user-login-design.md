# Simple User/Password Login System Design

**Date**: 2026-02-05
**Feature**: Multi-user authentication with registration and login
**Status**: Approved Design

## Overview

Add user authentication to the Dog Todo App so each user can create an account, log in with a username/password, and see only their own todos. Auto-logout after 24 hours of inactivity.

## Key Requirements

- Multiple users, each with own account
- Registration (signup) + Login flow
- Clean database start (fresh slate)
- Private todos per user
- Auto-logout after 24 hours of inactivity
- Minimal password requirements (any password, just needs to exist)

---

## Architecture & Authentication Flow

**Authentication Method**: JWT (JSON Web Tokens)
- User registers with username/password → hashed password stored in database
- User logs in → backend validates credentials, returns JWT token (24-hour expiry)
- Frontend stores JWT in localStorage, includes it in all API requests
- Backend validates JWT on every request; if expired → user auto-logs out
- Token refresh not needed for this simple version (auto-logout on expiry)

**Key Components**:
- New `User` database model (id, username, password_hash, created_at)
- New API endpoints: POST `/auth/register`, POST `/auth/login`, POST `/auth/logout`
- Todos get a `user_id` foreign key (todos are now scoped to users)
- GET `/api/todos` only returns logged-in user's todos

**Tech Stack**:
- Backend: `python-jose` for JWT handling, `passlib` for password hashing
- Frontend: Store token in localStorage, add Authorization header to requests
- 24-hour JWT expiry triggers auto-logout when token expires

**Database Changes**:
- New `User` table with username (unique), password_hash
- Add `user_id` to existing `TodoItem` table (foreign key)
- Existing todos: deleted (clean slate approach)

---

## Frontend Components & UI

**New Pages/Components**:
- `LoginPage.jsx` - Form with username/password inputs, "Login" button, link to register
- `RegisterPage.jsx` - Form with username/password inputs, "Create Account" button, link to login
- `ProtectedRoute.jsx` - Wrapper component that redirects to login if no valid token
- Update `App.jsx` - Add routing logic to show login/register OR todo app based on auth state

**User Experience**:
- App starts at login page (no token in localStorage)
- User either logs in with existing account or clicks "Create Account" to register
- After successful login/register → redirected to todo app
- Token auto-saves to localStorage on login
- If token expires (24 hours) → user redirected to login page on next action
- "Logout" button in header clears token and redirects to login

**Error Handling on Frontend**:
- Display "Username already exists" on duplicate registration
- Display "Invalid username or password" on failed login (don't say which is wrong)
- Show loading state while API request is in progress
- Disable form submission while loading

**Layout**:
- Login/Register pages: centered form, simple design matching dog theme
- After login: existing todo app with added logout button in header

---

## Backend Changes (Database & API)

**New Database Model** (`User`):
- `id` - Integer primary key
- `username` - String, unique, required
- `password_hash` - String (hashed with passlib), required
- `created_at` - DateTime, auto-generated

**Updated Database Model** (`TodoItem`):
- Add `user_id` - Foreign key to User table, required
- Existing todos in database: will be cleared (clean slate approach)

**New API Endpoints**:
- `POST /auth/register` - Accept {username, password}, create user, return JWT token
- `POST /auth/login` - Accept {username, password}, validate, return JWT token
- `POST /auth/logout` - Clear token on backend (optional; mostly frontend-driven)
- `GET /auth/me` - Return current user info (optional, for verification)

**JWT Configuration**:
- Secret key stored in environment variable
- 24-hour expiration time
- Include user_id in token payload
- Backend middleware validates token on every `/api/todos` request

**Updated CRUD** (`get_todos`):
- Filter todos by current user_id from JWT
- Users can only see/modify their own todos

**Dependencies to Add**:
- python-jose (JWT)
- passlib (password hashing)
- python-multipart (form data)

---

## Data Flow & Session Management

**Registration Flow**:
1. User enters username/password → POST `/auth/register`
2. Backend: check username not taken, hash password with passlib, create User record
3. Backend: generate JWT token (user_id + 24h expiry), return to frontend
4. Frontend: save token to localStorage, redirect to todo app

**Login Flow**:
1. User enters username/password → POST `/auth/login`
2. Backend: find user by username, compare password hash with passlib
3. Backend: if match, generate JWT token, return to frontend
4. Frontend: save token to localStorage, redirect to todo app

**Request/Response with Auth**:
1. Frontend adds `Authorization: Bearer <token>` header to all `/api/todos` requests
2. Backend middleware validates token signature and expiry
3. If valid: extract user_id, attach to request, proceed
4. If invalid/expired: return 401 Unauthorized
5. Frontend catches 401, clears localStorage, redirects to login

**Session Persistence**:
- Token stays in localStorage across page reloads
- On app start: check if token exists and is valid
- If expired: automatically redirect to login on first API call
- No refresh token needed (24h is acceptable for auto-logout)

**Logout Flow**:
1. User clicks logout button
2. Frontend: clear token from localStorage, redirect to login
3. Optional: POST `/auth/logout` to backend (mostly for audit/cleanup)

---

## Error Handling & Edge Cases

**Error Scenarios**:
- **Username already exists**: Return 409 Conflict during registration, show error to user
- **Invalid credentials**: Return 401 Unauthorized during login, show generic "Invalid username or password"
- **Expired token**: Return 401 on API call, frontend auto-redirects to login
- **Missing token**: Return 401 if Authorization header missing on protected routes
- **Invalid token**: Return 401 if signature is tampered with or invalid

**Edge Cases**:
- User registers, closes browser, comes back next day → token expired, redirected to login ✓
- User logs out → localStorage cleared, redirect to login ✓
- User tries to access `/todos` without logging in → 401 error, redirect to login ✓
- User tries to access another user's todo via direct API call → filtered by user_id, returns empty ✓
- Username with spaces/special chars → allowed (just needs to exist)
- Very long password → allowed, hashed normally by passlib

**API Response Format**:
```json
// Successful login/register
{ "access_token": "eyJ0eXAi...", "token_type": "bearer" }

// Error
{ "detail": "Invalid username or password" }
```

**Frontend Error Display**:
- Show user-friendly error messages
- Don't expose internal details
- Show loading spinners during auth requests

---

## Testing Strategy

**Backend Tests** (add to `backend/tests/test_auth.py`):
- Test user registration: valid credentials, duplicate username, empty fields
- Test user login: valid credentials, invalid username, invalid password
- Test JWT token: valid token accepted, expired token rejected, missing token rejected
- Test todo filtering: user only sees own todos, cannot access other user's todos
- Test logout: token properly cleared

**Frontend Tests** (optional):
- Login form: submit button works, displays errors on failed login
- Register form: submit button works, displays errors on duplicate username
- Protected route: redirects to login if no token
- API requests: Authorization header sent with token

**Manual Testing Checklist**:
- Register new user → token saved, redirected to todo app
- Add todo as user A → todo appears
- Log out → token cleared, redirected to login
- Log in as different user B → user B sees empty todo list (user A's todos invisible)
- Wait 24+ hours (or manually expire token) → auto-logout on next action
- Try accessing `/api/todos` without token → 401 error, redirected to login
- Try registering duplicate username → error shown
- Try logging in with wrong password → generic error shown

**Test Coverage Goal**: >80% on new auth code

---

## Implementation Order

1. Backend database models and migrations
2. Backend auth endpoints (register, login, logout, me)
3. Backend JWT middleware for todo endpoints
4. Update todo CRUD to filter by user_id
5. Frontend login/register pages
6. Frontend authentication state management (token in localStorage)
7. Frontend protected routes and redirects
8. Frontend logout button and session handling
9. Testing and integration verification

---

## Files to Create/Modify

**Backend**:
- `backend/app/models.py` - Add User model, update TodoItem with user_id
- `backend/app/schemas.py` - Add UserCreate, UserResponse, Token schemas
- `backend/app/crud.py` - Add create_user, get_user_by_username
- `backend/app/main.py` - Add auth routes, JWT middleware, update todo routes
- `backend/app/security.py` - NEW: JWT and password hashing utilities
- `backend/tests/test_auth.py` - NEW: Authentication tests

**Frontend**:
- `frontend/src/pages/LoginPage.jsx` - NEW: Login form
- `frontend/src/pages/RegisterPage.jsx` - NEW: Registration form
- `frontend/src/components/ProtectedRoute.jsx` - NEW: Route protection wrapper
- `frontend/src/services/auth.js` - NEW: Authentication API calls
- `frontend/src/App.jsx` - Update with routing and auth state
- `frontend/src/services/api.js` - Update to include JWT in requests

**Configuration**:
- `backend/requirements.txt` - Add python-jose, passlib, python-multipart
- `backend/.env.example` - Add JWT_SECRET_KEY example

---

## Success Criteria

- [ ] Users can register with unique username
- [ ] Users can log in with valid credentials
- [ ] JWT tokens stored in localStorage persist across page reloads
- [ ] Tokens expire after 24 hours of creation
- [ ] Users only see their own todos
- [ ] Logout clears token and redirects to login
- [ ] Invalid/expired tokens redirect to login on any API call
- [ ] Error messages are user-friendly
- [ ] >80% test coverage for auth code
