import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { apiGet } from '../services/api'

const Navbar: React.FC = () => {
  const { token, logout } = useAuth()
  const [email, setEmail] = useState<string>('')

  useEffect(() => {
    let ignore = false
    if (token) {
      apiGet<any>('/users/me', token).then(u => {
        if (!ignore) setEmail(u.email)
      }).catch(() => {})
    }
    return () => { ignore = true }
  }, [token])

  return (
    <nav style={{ padding: '8px 12px', background: '#0ea5e9', color: 'white' }}>
      <Link to="/profile" style={{ color: 'white', marginRight: 12 }}>Profil</Link>
      <Link to="/offers" style={{ color: 'white', marginRight: 12 }}>Offres</Link>
      <Link to="/requests" style={{ color: 'white', marginRight: 12 }}>Demandes</Link>
      <Link to="/notifications" style={{ color: 'white', marginRight: 12 }}>Notifications</Link>
  <Link to="/dogs" style={{ color: 'white', marginRight: 12 }}>Chiens</Link>

      <span style={{ float: 'right' }}>
        {email && <span style={{ marginRight: 12 }}>{email}</span>}
        <button onClick={logout} style={{ background: 'white', color: '#0ea5e9', border: 'none', padding: '6px 10px', borderRadius: 4, cursor: 'pointer' }}>Se déconnecter</button>
      </span>
    </nav>
  )
}

export default Navbar
