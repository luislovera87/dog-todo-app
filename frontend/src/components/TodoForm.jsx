import { useState } from 'react'

export default function TodoForm({ onSubmit, isLoading }) {
  const [formData, setFormData] = useState({
    task_name: '',
    dog_name: '',
    description: '',
    priority: 'medium',
    due_date: '',
  })
  const [error, setError] = useState('')

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!formData.task_name.trim() || !formData.dog_name.trim()) {
      setError('Task name and dog name are required')
      return
    }

    try {
      const submitData = {
        task_name: formData.task_name,
        dog_name: formData.dog_name,
        priority: formData.priority,
      }
      if (formData.description) submitData.description = formData.description
      if (formData.due_date) submitData.due_date = formData.due_date

      await onSubmit(submitData)
      setFormData({
        task_name: '',
        dog_name: '',
        description: '',
        priority: 'medium',
        due_date: '',
      })
    } catch (err) {
      let errorMsg = 'Failed to create todo'
      if (err.response?.status === 422) {
        errorMsg = 'Invalid input - please check your entries'
      } else if (err.code === 'ECONNABORTED') {
        errorMsg = 'Request timeout - is the backend running?'
      } else if (err.message === 'Network Error') {
        errorMsg = 'Network error - is the backend running at http://localhost:8000?'
      } else if (err.message) {
        errorMsg = err.message
      }
      setError(errorMsg)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="todo-form">
      <h2>🐾 New Task</h2>
      {error && <div className="error-message">{error}</div>}

      <div className="form-group">
        <label htmlFor="task_name">Task Name *</label>
        <input
          type="text"
          id="task_name"
          name="task_name"
          value={formData.task_name}
          onChange={handleChange}
          placeholder="e.g., Walk Buddy"
          disabled={isLoading}
        />
      </div>

      <div className="form-group">
        <label htmlFor="dog_name">Dog Name *</label>
        <input
          type="text"
          id="dog_name"
          name="dog_name"
          value={formData.dog_name}
          onChange={handleChange}
          placeholder="e.g., Buddy, Max, Luna"
          disabled={isLoading}
        />
      </div>

      <div className="form-group">
        <label htmlFor="description">Description</label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="Add details..."
          rows="3"
          disabled={isLoading}
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="priority">Priority</label>
          <select
            id="priority"
            name="priority"
            value={formData.priority}
            onChange={handleChange}
            disabled={isLoading}
          >
            <option value="low">Nap-worthy (Low)</option>
            <option value="medium">Walk-worthy (Medium)</option>
            <option value="high">Treat-worthy (High)</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="due_date">Due Date</label>
          <input
            type="datetime-local"
            id="due_date"
            name="due_date"
            value={formData.due_date}
            onChange={handleChange}
            disabled={isLoading}
          />
        </div>
      </div>

      <button type="submit" disabled={isLoading} className="btn-primary">
        {isLoading ? 'Creating...' : 'Fetch Task! 🐕'}
      </button>
    </form>
  )
}
