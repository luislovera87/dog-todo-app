import { useEffect } from 'react'

export default function ProtectedRoute({ children, onUnauthenticated }) {
  const token = localStorage.getItem('token')

  useEffect(() => {
    if (!token) {
      onUnauthenticated?.()
    }
  }, [token, onUnauthenticated])

  if (!token) return null

  return children
}
