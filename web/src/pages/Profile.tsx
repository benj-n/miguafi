import React, { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { apiGet, apiPut } from '../services/api'
import MapPicker, { LatLng as LatLngT } from '../components/MapPicker'

const Profile: React.FC = () => {
  const { token, logout } = useAuth()
  const [me, setMe] = useState<any>(null)
  const [coord, setCoord] = useState<LatLngT | null>(null)
  const [message, setMessage] = useState('')

  useEffect(() => {
    ;(async () => {
      const data = await apiGet<any>('/users/me', token!)
      setMe(data)
      if (typeof data.location_lat === 'number' && typeof data.location_lng === 'number') {
        setCoord({ lat: data.location_lat, lng: data.location_lng })
      } else {
        setCoord(null)
      }
    })()
  }, [token])

  async function save() {
  const payload: any = {}
    if (coord) { payload.location_lat = coord.lat; payload.location_lng = coord.lng }
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
  <h3>Localisation</h3>
  <p>Cliquez sur la carte pour ajuster vos coordonnées.</p>
  <MapPicker value={coord} onChange={setCoord} />
      <div>
        <button onClick={save}>Enregistrer</button>
        <button onClick={logout} style={{ marginLeft: 8 }}>Se déconnecter</button>
      </div>
      {message && <p style={{ color: 'green' }}>{message}</p>}
    </div>
  )
}

export default Profile
