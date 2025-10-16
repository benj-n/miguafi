import React, { useState } from 'react'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const Login: React.FC = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const location = useLocation() as any
  const { login, loading } = useAuth()

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    try {
      await login(email, password)
      const dest = location.state?.from?.pathname || '/profile'
      navigate(dest)
    } catch (e: any) {
      setError(e.message || 'Erreur de connexion')
    }
  }

  return (
    <div className="container">
      <h1>Connexion</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <form onSubmit={onSubmit}>
        <label>Courriel</label>
        <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
        <label>Mot de passe</label>
        <input type="password" value={password} onChange={e => setPassword(e.target.value)} required minLength={8} />
        <button type="submit" disabled={loading || !email || password.length < 8}>
          {loading ? 'Connexion…' : 'Se connecter'}
        </button>
      </form>
      <p>
        Pas de compte? <a href="/register">Créer un compte</a>
      </p>
      <p>
        <Link to="/">Accueil</Link>
      </p>
    </div>
  )
}

export default Login
