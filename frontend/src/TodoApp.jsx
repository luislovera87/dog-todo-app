import { useState, useEffect } from 'react'
import TodoForm from './components/TodoForm'
import TodoList from './components/TodoList'
import * as api from './services/api'
import { authService } from './services/auth'
import './App.css'

function TodoApp({ onLogout }) {
  const [todos, setTodos] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [hasError, setHasError] = useState(false)
  const [filters, setFilters] = useState({
    dog_name: '',
    completed: null,
    priority: '',
  })

  const loadTodos = async (filterObj = filters) => {
    setIsLoading(true)
    setHasError(false)
    try {
      const response = await api.fetchTodos(filterObj)
      setTodos(response.data)
    } catch (error) {
      console.error('Failed to load todos:', error)
      if (error.response?.status === 401) {
        authService.logout()
        onLogout()
        return
      }
      setHasError(true)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadTodos()
  }, [])

  const handleCreateTodo = async (todoData) => {
    setIsLoading(true)
    try {
      await api.createTodo(todoData)
      await loadTodos()
    } catch (error) {
      console.error('Failed to create todo:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const handleToggleTodo = async (id) => {
    setIsLoading(true)
    try {
      await api.toggleTodo(id)
      await loadTodos()
    } catch (error) {
      console.error('Failed to toggle todo:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteTodo = async (id) => {
    if (!confirm('Are you sure you want to delete this task?')) return

    setIsLoading(true)
    try {
      await api.deleteTodo(id)
      await loadTodos()
    } catch (error) {
      console.error('Failed to delete todo:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleEditTodo = (todo) => {
    console.log('Edit todo:', todo)
  }

  const handleFilterChange = (e) => {
    const { name, value } = e.target
    const newFilters = {
      ...filters,
      [name]: value || null,
    }
    setFilters(newFilters)
    loadTodos(newFilters)
  }

  const handleClearFilters = () => {
    setFilters({ dog_name: '', completed: null, priority: '' })
    loadTodos({ dog_name: '', completed: null, priority: '' })
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>🐾 Dog Todo App 🐾</h1>
        <p>Manage all your pup's tasks in one place!</p>
        <button onClick={onLogout} className="btn-logout">
          Logout
        </button>
      </header>

      <div className="app-content">
        <aside className="sidebar">
          <TodoForm onSubmit={handleCreateTodo} isLoading={isLoading} />

          <div className="filters">
            <h3>🔍 Filters</h3>
            <div className="filter-group">
              <label htmlFor="filter-dog">Dog Name</label>
              <input
                type="text"
                id="filter-dog"
                name="dog_name"
                value={filters.dog_name}
                onChange={handleFilterChange}
                placeholder="Filter by dog..."
              />
            </div>

            <div className="filter-group">
              <label htmlFor="filter-priority">Priority</label>
              <select
                id="filter-priority"
                name="priority"
                value={filters.priority}
                onChange={handleFilterChange}
              >
                <option value="">All Priorities</option>
                <option value="low">Nap-worthy (Low)</option>
                <option value="medium">Walk-worthy (Medium)</option>
                <option value="high">Treat-worthy (High)</option>
              </select>
            </div>

            <div className="filter-group">
              <label htmlFor="filter-completed">Status</label>
              <select
                id="filter-completed"
                name="completed"
                value={filters.completed === null ? '' : filters.completed}
                onChange={(e) => {
                  const value = e.target.value === '' ? null : e.target.value === 'true'
                  const newFilters = { ...filters, completed: value }
                  setFilters(newFilters)
                  loadTodos(newFilters)
                }}
              >
                <option value="">All Tasks</option>
                <option value="false">Incomplete</option>
                <option value="true">Completed</option>
              </select>
            </div>

            <button onClick={handleClearFilters} className="btn-clear-filters">
              Clear Filters
            </button>
          </div>
        </aside>

        <main className="todo-main">
          <TodoList
            todos={todos}
            onToggle={handleToggleTodo}
            onDelete={handleDeleteTodo}
            onEdit={handleEditTodo}
            isLoading={isLoading}
            hasError={hasError}
          />
        </main>
      </div>

      <footer className="app-footer">
        <p>Good dog! Keep managing those tasks! 🦴</p>
      </footer>
    </div>
  )
}

export default TodoApp
