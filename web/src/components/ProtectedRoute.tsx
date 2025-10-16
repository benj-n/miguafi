import React from 'react'
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import Navbar from './Navbar'
import { useAuth } from '../context/AuthContext'

const ProtectedRoute: React.FC = () => {
  const { token, loading } = useAuth()
  const location = useLocation()
  if (!token) return <Navigate to="/login" replace state={{ from: location }} />
  return (
    <>
      <Navbar />
      {loading && <div style={{ height: 4, background: '#0ea5e9', width: '100%', opacity: 0.7 }} />}
      <Outlet />
    </>
  )
}

export default ProtectedRoute
