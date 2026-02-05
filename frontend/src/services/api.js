import axios from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 5000,
})

export const fetchTodos = (filters = {}) => {
  const params = new URLSearchParams()
  if (filters.dog_name) params.append('dog_name', filters.dog_name)
  if (filters.completed !== null && filters.completed !== undefined) params.append('completed', filters.completed)
  if (filters.priority) params.append('priority', filters.priority)

  const queryString = params.toString()
  const url = queryString ? `${API_BASE_URL}/todos?${queryString}` : `${API_BASE_URL}/todos`
  return axios.get(url, { timeout: 5000 })
}

export const createTodo = (todoData) => {
  return api.post('/todos', todoData)
}

export const getTodo = (id) => {
  return api.get(`/todos/${id}`)
}

export const updateTodo = (id, todoData) => {
  return api.put(`/todos/${id}`, todoData)
}

export const deleteTodo = (id) => {
  return api.delete(`/todos/${id}`)
}

export const toggleTodo = (id) => {
  return api.patch(`/todos/${id}/toggle`)
}

export default api
