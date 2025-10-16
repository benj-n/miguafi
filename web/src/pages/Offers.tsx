import React, { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { apiGet, apiPost, apiDeleteVoid } from '../services/api'
import { toIso } from '../env'
import { useToast } from '../context/ToastContext'

const Offers: React.FC = () => {
  const { token } = useAuth()
  const [start, setStart] = useState('')
  const [end, setEnd] = useState('')
  const [info, setInfo] = useState('')
  const [mine, setMine] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(10)
  const [sort, setSort] = useState('-start_at')
  const { push } = useToast()

  async function submit() {
    setInfo('')
    await apiPost('/availability/offers', { start_at: toIso(start), end_at: toIso(end) }, token!)
    push('Offre créée', { type: 'success' })
    setStart('')
    setEnd('')
    loadMine()
  }

  async function loadMine() {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize), sort })
    const data = await apiGet<{ items: any[]; total: number; page: number; page_size: number }>(`/availability/offers/mine?${params}`, token!)
    setMine(data.items)
    setTotal(data.total)
  }

  useEffect(() => { loadMine() }, [token, page, sort])

  async function remove(id: number) {
    await apiDeleteVoid(`/availability/offers/${id}`, token!)
    push('Offre supprimée', { type: 'success' })
    loadMine()
  }

  return (
    <div className="container">
      <h1>Offres</h1>
  <label htmlFor="offer-start">Début</label>
  <input id="offer-start" type="datetime-local" value={start} onChange={e => setStart(e.target.value)} />
  <label htmlFor="offer-end">Fin</label>
  <input id="offer-end" type="datetime-local" value={end} onChange={e => setEnd(e.target.value)} />
      <button onClick={submit}>Publier une offre</button>
      <h2>Mes offres</h2>
      <div style={{ margin: '8px 0' }}>
        Tri:
        <select value={sort} onChange={e => setSort(e.target.value)} style={{ marginLeft: 8 }}>
          <option value="-start_at">Début décroissant</option>
          <option value="start_at">Début croissant</option>
        </select>
      </div>
      <ul>
        {mine.map(o => (
          <li key={o.id} className="list-item">
            <span>{new Date(o.start_at).toLocaleString()} → {new Date(o.end_at).toLocaleString()}</span>
            <button onClick={() => remove(o.id)} className="danger">Supprimer</button>
          </li>
        ))}
      </ul>
      <div className="pager">
        <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>Précédent</button>
        <span>Page {page} / {Math.max(1, Math.ceil(total / pageSize))}</span>
        <button onClick={() => setPage(p => (p < Math.ceil(total / pageSize) ? p + 1 : p))} disabled={page >= Math.ceil(total / pageSize)}>Suivant</button>
      </div>
    </div>
  )
}

export default Offers
