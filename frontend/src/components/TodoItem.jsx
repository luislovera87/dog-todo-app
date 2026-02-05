import DogAvatar from './DogAvatar'

export default function TodoItem({ todo, onToggle, onDelete, onEdit, isLoading }) {
  const priorityLabel = {
    low: 'Nap-worthy',
    medium: 'Walk-worthy',
    high: 'Treat-worthy',
  }

  return (
    <div className={`todo-item ${todo.completed ? 'completed' : ''} priority-${todo.priority}`}>
      <div className="todo-content">
        <div className="todo-header">
          <input
            type="checkbox"
            checked={todo.completed}
            onChange={() => onToggle(todo.id)}
            disabled={isLoading}
            className="todo-checkbox"
          />
          <span className="todo-task">
            <DogAvatar dogName={todo.dog_name} />
            {todo.task_name}
          </span>
        </div>
        <div className="todo-meta">
          <span className="dog-name">{todo.dog_name}</span>
          <span className="priority-badge">{priorityLabel[todo.priority]}</span>
        </div>
        {todo.description && (
          <p className="todo-description">{todo.description}</p>
        )}
        {todo.due_date && (
          <p className="todo-due-date">
            📅 {new Date(todo.due_date).toLocaleDateString()}
          </p>
        )}
      </div>
      <div className="todo-actions">
        <button
          onClick={() => onEdit(todo)}
          disabled={isLoading}
          className="btn-edit"
          title="Edit"
        >
          ✏️
        </button>
        <button
          onClick={() => onDelete(todo.id)}
          disabled={isLoading}
          className="btn-delete"
          title="Delete"
        >
          🗑️
        </button>
      </div>
    </div>
  )
}
