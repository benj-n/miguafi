import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { API_BASE } from '../env'
import MapPicker, { LatLng as LatLngT } from '../components/MapPicker'
// MapPicker will be added; to keep page functional without leaflet deps at test time, we lazy-init simple inputs when MapPicker is unavailable.

const Register: React.FC = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [dogName, setDogName] = useState('')
  const dogNamePattern = /^[A-Z0-9]{1,98}[0-9]{2}$/
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [coord, setCoord] = useState<LatLngT | null>(null)
  const [error, setError] = useState('')
  const [ok, setOk] = useState('')
  const [progress, setProgress] = useState<number>(0)
  const [submitting, setSubmitting] = useState(false)
  const navigate = useNavigate()

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(''); setOk(''); setProgress(0)

    // Validate file (optional)
    if (file) {
      if (!file.type.startsWith('image/')) { setError('Le fichier doit être une image'); return }
      const maxBytes = 10 * 1024 * 1024
      if (file.size > maxBytes) { setError('Image trop volumineuse (max 10 Mo)'); return }
    }

    try {
      const fd = new FormData()
      fd.append('email', email)
      fd.append('password', password)
      if (dogName) fd.append('dog_name', dogName.toUpperCase())
      if (coord) {
        fd.append('location_lat', String(coord.lat))
        fd.append('location_lng', String(coord.lng))
      }
      if (file) fd.append('file', file, file.name)

      setSubmitting(true)
      await new Promise<void>((resolve, reject) => {
        const xhr = new XMLHttpRequest()
        xhr.open('POST', `${API_BASE}/auth/register-multipart`)
        xhr.upload.onprogress = (evt) => {
          if (evt.lengthComputable) setProgress(Math.round((evt.loaded / evt.total) * 100))
        }
        xhr.onload = () => {
          if (xhr.status >= 200 && xhr.status < 300) resolve()
          else reject(new Error(xhr.responseText || 'Erreur'))
        }
        xhr.onerror = () => reject(new Error('Erreur réseau'))
        xhr.send(fd)
      })

      setOk('Compte créé, vous pouvez vous connecter.')
      setTimeout(() => navigate('/login'), 1000)
    } catch (e: any) {
      setError(e.message || 'Erreur')
    } finally {
      setSubmitting(false)
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
   <label>Nom du chien (optionnel)</label>
   <input value={dogName} onChange={e => setDogName(e.target.value.toUpperCase())} placeholder="ex: REX21"
     pattern={dogName ? dogNamePattern.source : undefined}
     title="MAJUSCULES/CHIFFRES et se termine par 2 chiffres" />
        <label>Photo du chien (optionnel)</label>
        <input type="file" accept="image/*" onChange={e => {
          const f = e.target.files?.[0] || null
          setFile(f)
          if (f) setPreview(URL.createObjectURL(f))
          else setPreview(null)
        }} />
        {preview && (
          <div style={{ marginTop: 8 }}>
            <img src={preview} alt="aperçu" style={{ maxHeight: 240, objectFit: 'contain', borderRadius: 6 }} />
          </div>
        )}
        <h3>Localisation</h3>
        <p>Cliquez sur la carte pour définir vos coordonnées.</p>
        <MapPicker value={coord} onChange={setCoord} />
        <button type="submit" disabled={submitting}>
          {submitting ? 'Création en cours…' : 'Créer un compte'}
        </button>
        {submitting && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 8 }}>
            <span className="spinner" aria-label="chargement" />
            <span>Envoi en cours… {progress}%</span>
          </div>
        )}
      </form>
      <p><Link to="/login">Déjà inscrit ? Se connecter</Link></p>
    </div>
  )
}

export default Register
