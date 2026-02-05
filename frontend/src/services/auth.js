const API_URL = '/api/auth'

export const authService = {
  register: async (username, password) => {
    const response = await fetch(`${API_URL}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Registration failed')
    }
    return await response.json()
  },

  login: async (username, password) => {
    const response = await fetch(`${API_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Login failed')
    }
    return await response.json()
  },

  logout: () => {
    localStorage.removeItem('token')
  },

  getToken: () => localStorage.getItem('token'),

  setToken: (token) => localStorage.setItem('token', token),

  isAuthenticated: () => !!localStorage.getItem('token'),
}
