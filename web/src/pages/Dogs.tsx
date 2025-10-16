import React, { useEffect, useMemo, useState } from 'react'
import Navbar from '../components/Navbar'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { apiDeleteVoid, apiGet, apiPost, apiPut, apiUpload, apiPostVoid } from '../services/api'

type Dog = {
  id: number
  name: string
  photo_url?: string | null
  created_at: string
}

const namePattern = /^[A-Z0-9]{1,98}[0-9]{2}$/

const Dogs: React.FC = () => {
  const { token } = useAuth()
  const { push } = useToast()
  const [dogs, setDogs] = useState<Dog[]>([])
  const [newName, setNewName] = useState('')
  const [editing, setEditing] = useState<{ id: number, name: string } | null>(null)
  const [coOwnerUserId, setCoOwnerUserId] = useState('')

  const load = async () => {
    if (!token) return
    const data = await apiGet<Dog[]>(`/dogs/me`, token)
    setDogs(data)
  }

  useEffect(() => { load() }, [token])

  const canCreate = useMemo(() => namePattern.test(newName), [newName])

  const createDog = async () => {
    if (!token) return
    if (!canCreate) { push('Nom invalide (MAJUSCULES/CHIFFRES et se termine par 2 chiffres)'); return }
    const created = await apiPost<Dog>(`/dogs/`, { name: newName }, token)
    push('Chien créé')
    setNewName('')
    setDogs([created, ...dogs])
  }

  const saveEdit = async () => {
    if (!token || !editing) return
    if (!namePattern.test(editing.name)) { push('Nom invalide'); return }
    const updated = await apiPut<Dog>(`/dogs/${editing.id}`, { name: editing.name }, token)
    push('Chien mis à jour')
    setDogs(dogs.map(d => d.id === updated.id ? updated : d))
    setEditing(null)
  }

  const removeDog = async (id: number) => {
    if (!token) return
    await apiDeleteVoid(`/dogs/${id}`, token)
    push('Chien supprimé')
    setDogs(dogs.filter(d => d.id !== id))
  }

  const addCoOwner = async (dogId: number) => {
    if (!token) return
    if (!coOwnerUserId) { push('ID utilisateur requis'); return }
    await apiPostVoid(`/dogs/${dogId}/coowners/${coOwnerUserId}`, token)
    push('Co-propriétaire ajouté')
    setCoOwnerUserId('')
  }

  const removeCoOwner = async (dogId: number) => {
    if (!token) return
    if (!coOwnerUserId) { push('ID utilisateur requis'); return }
    await apiDeleteVoid(`/dogs/${dogId}/coowners/${coOwnerUserId}`, token)
    push('Co-propriétaire retiré')
    setCoOwnerUserId('')
  }

  const uploadPhoto = async (dogId: number, file: File | null) => {
    if (!token || !file) return
    // Client-side validation: image/* mime and size limit (e.g., 5MB)
    if (!file.type.startsWith('image/')) { push('Fichier image requis'); return }
    const maxBytes = 5 * 1024 * 1024
    if (file.size > maxBytes) { push('Image trop volumineuse (max 5 Mo)'); return }
    const fd = new FormData()
    fd.append('file', file, file.name)
    const updated = await apiUpload<Dog>(`/dogs/${dogId}/photo`, fd, token)
    push('Photo mise à jour')
    setDogs(dogs.map(d => d.id === updated.id ? updated : d))
  }

  return (
    <div>
      <Navbar />
      <div className="container">
        <h2>Mes chiens</h2>

        <div className="card" style={{ marginBottom: 16 }}>
          <h3>Créer un chien</h3>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <input
              aria-label="Nom du chien"
              placeholder="Nom (ex: REX21)"
              value={newName}
              onChange={e => setNewName(e.target.value.toUpperCase())}
            />
            <button disabled={!canCreate} onClick={createDog}>Créer</button>
            <small>Format: MAJUSCULES/CHIFFRES et se termine par 2 chiffres</small>
          </div>
        </div>

        <div className="list">
          {dogs.map(dog => (
            <div key={dog.id} className="list-item">
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
                {dog.photo_url ? (
                  <img src={dog.photo_url} alt={dog.name} style={{ width: 64, height: 64, objectFit: 'cover', borderRadius: 6 }} />
                ) : (
                  <div style={{ width: 64, height: 64, background: '#eee', display: 'inline-block', borderRadius: 6 }} />
                )}
                {editing?.id === dog.id ? (
                  <>
                    <input
                      value={editing.name}
                      onChange={e => setEditing({ id: dog.id, name: e.target.value.toUpperCase() })}
                    />
                    <button onClick={saveEdit}>Sauver</button>
                    <button className="danger" onClick={() => setEditing(null)}>Annuler</button>
                  </>
                ) : (
                  <>
                    <strong>{dog.name}</strong>
                    <button onClick={() => setEditing({ id: dog.id, name: dog.name })}>Modifier</button>
                  </>
                )}

                <label style={{ marginLeft: 12 }}>
                  Photo:
                  <input type="file" accept="image/*" onChange={e => uploadPhoto(dog.id, e.target.files?.[0] ?? null)} />
                </label>

                <button className="danger" onClick={() => removeDog(dog.id)}>Supprimer</button>

                <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                  <input
                    aria-label="ID co-propriétaire"
                    placeholder="ID utilisateur (8 chiffres)"
                    value={coOwnerUserId}
                    onChange={e => setCoOwnerUserId(e.target.value)}
                    style={{ width: 180 }}
                  />
                  <button onClick={() => addCoOwner(dog.id)}>Ajouter co-propriétaire</button>
                  <button onClick={() => removeCoOwner(dog.id)}>Retirer co-propriétaire</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Dogs
