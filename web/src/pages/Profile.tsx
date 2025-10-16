import React, { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { apiGet, apiPut } from '../services/api'

const Profile: React.FC = () => {
  const { token, logout } = useAuth()
  const [me, setMe] = useState<any>(null)
  const [dogName, setDogName] = useState('')
  const [lat, setLat] = useState<number | ''>('')
  const [lng, setLng] = useState<number | ''>('')
  const [message, setMessage] = useState('')

  useEffect(() => {
    ;(async () => {
      const data = await apiGet<any>('/users/me', token!)
      setMe(data)
      setDogName(data.dog_name || '')
      setLat(data.location_lat ?? '')
      setLng(data.location_lng ?? '')
    })()
  }, [token])

  async function save() {
    const payload: any = { dog_name: dogName }
    if (lat !== '') payload.location_lat = lat
    if (lng !== '') payload.location_lng = lng
    const data = await apiPut<any>('/users/me', payload, token!)
    setMe(data)
    setMessage('Sauvegardé!')
    setTimeout(() => setMessage(''), 1500)
  }

  if (!me) return <div className="container">Chargement…</div>
  return (
    <div className="container">
      <h1>Mon profil</h1>
      <p>Email: {me.email}</p>
      <label>Nom du chien</label>
      <input value={dogName} onChange={e => setDogName(e.target.value)} />
      <label>Latitude approx.</label>
      <input type="number" value={lat} onChange={e => setLat(e.target.value === '' ? '' : Number(e.target.value))} />
      <label>Longitude approx.</label>
      <input type="number" value={lng} onChange={e => setLng(e.target.value === '' ? '' : Number(e.target.value))} />
      <div>
        <button onClick={save}>Enregistrer</button>
        <button onClick={logout} style={{ marginLeft: 8 }}>Se déconnecter</button>
      </div>
      {message && <p style={{ color: 'green' }}>{message}</p>}
    </div>
  )
}

export default Profile
