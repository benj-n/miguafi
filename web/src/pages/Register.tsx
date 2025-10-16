import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { API_BASE } from '../env'

const Register: React.FC = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [dogName, setDogName] = useState('')
  const [photoUrl, setPhotoUrl] = useState('')
  const [lat, setLat] = useState<number | ''>('')
  const [lng, setLng] = useState<number | ''>('')
  const [error, setError] = useState('')
  const [ok, setOk] = useState('')
  const navigate = useNavigate()

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(''); setOk('')
    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          password,
          dog_name: dogName || undefined,
          dog_photo_url: photoUrl || undefined,
          location_lat: lat === '' ? undefined : lat,
          location_lng: lng === '' ? undefined : lng,
        })
      })
      if (!res.ok) throw new Error(await res.text())
      setOk('Compte créé, vous pouvez vous connecter.')
      setTimeout(() => navigate('/login'), 1000)
    } catch (e: any) {
      setError(e.message || 'Erreur')
    }
  }

  return (
    <div className="container">
      <h1>Inscription</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {ok && <p style={{ color: 'green' }}>{ok}</p>}
      <form onSubmit={onSubmit}>
        <label>Courriel</label>
        <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
        <label>Mot de passe</label>
        <input type="password" value={password} onChange={e => setPassword(e.target.value)} required minLength={8} />

        <h3>Profil</h3>
        <label>Nom du chien</label>
        <input value={dogName} onChange={e => setDogName(e.target.value)} />
        <label>URL photo du chien</label>
        <input value={photoUrl} onChange={e => setPhotoUrl(e.target.value)} />
        <label>Latitude approx.</label>
        <input type="number" value={lat} onChange={e => setLat(e.target.value === '' ? '' : Number(e.target.value))} />
        <label>Longitude approx.</label>
        <input type="number" value={lng} onChange={e => setLng(e.target.value === '' ? '' : Number(e.target.value))} />
        <button type="submit">Créer un compte</button>
      </form>
      <p><Link to="/login">Déjà inscrit ? Se connecter</Link></p>
    </div>
  )
}

export default Register
