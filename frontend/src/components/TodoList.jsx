import TodoItem from './TodoItem'

export default function TodoList({ todos, onToggle, onDelete, onEdit, isLoading, hasError }) {
  if (hasError) {
    return (
      <div className="todo-list">
        <div className="error-state">
          <p>⚠️ Failed to load tasks. Is the backend running?</p>
          <p>Start the backend: <code>cd backend && uvicorn app.main:app --reload</code></p>
        </div>
      </div>
    )
  }

  if (todos.length === 0) {
    return (
      <div className="todo-list">
        <div className="empty-state">
          <p>🐕 No tasks to chase!</p>
          <p>Create a new task above to get started.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="todo-list">
      {todos.map(todo => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={onToggle}
          onDelete={onDelete}
          onEdit={onEdit}
          isLoading={isLoading}
        />
      ))}
    </div>
  )
}
