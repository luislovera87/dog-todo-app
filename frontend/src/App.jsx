import { useEffect, useState } from 'react'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProtectedRoute from './components/ProtectedRoute'
import TodoApp from './TodoApp'
import { authService } from './services/auth'

export default function App() {
  const [path, setPath] = useState(window.location.pathname)

  useEffect(() => {
    const handlePopState = () => setPath(window.location.pathname)
    window.addEventListener('popstate', handlePopState)
    return () => window.removeEventListener('popstate', handlePopState)
  }, [])

  const navigate = (to, { replace = false } = {}) => {
    if (replace) {
      window.history.replaceState({}, '', to)
    } else {
      window.history.pushState({}, '', to)
    }
    setPath(to)
  }

  const handleLogout = () => {
    authService.logout()
    navigate('/login', { replace: true })
  }

  if (path === '/login') {
    return (
      <LoginPage
        onNavigate={navigate}
        onAuthSuccess={() => navigate('/', { replace: true })}
      />
    )
  }

  if (path === '/register') {
    return (
      <RegisterPage
        onNavigate={navigate}
        onAuthSuccess={() => navigate('/', { replace: true })}
      />
    )
  }

  return (
    <ProtectedRoute onUnauthenticated={() => navigate('/login', { replace: true })}>
      <TodoApp onLogout={handleLogout} />
    </ProtectedRoute>
  )
}
