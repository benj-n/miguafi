import React, { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { apiGet, apiPostVoid, apiPutVoid } from '../services/api'
import { useToast } from '../context/ToastContext'

const Notifications: React.FC = () => {
  const { token } = useAuth()
  const [items, setItems] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(10)
  const [unreadOnly, setUnreadOnly] = useState(false)
  const { push } = useToast()

  useEffect(() => {
    ;(async () => {
      const params = new URLSearchParams({ page: String(page), page_size: String(pageSize), unread_only: String(unreadOnly) })
      const data = await apiGet<{ items: any[]; total: number }>(`/notifications/me?${params}`, token!)
      setItems(data.items)
      setTotal(data.total)
    })()
  }, [token, page, unreadOnly])

  async function markRead(id: number) {
    await apiPutVoid(`/notifications/${id}/read`, token!)
    push('Notification lue', { type: 'success' })
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize), unread_only: String(unreadOnly) })
    const data = await apiGet<{ items: any[]; total: number }>(`/notifications/me?${params}`, token!)
    setItems(data.items)
    setTotal(data.total)
  }

  async function markAll() {
    await apiPostVoid('/notifications/me/read-all', token!)
    push('Toutes les notifications marquées comme lues', { type: 'success' })
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize), unread_only: String(unreadOnly) })
    const data = await apiGet<{ items: any[]; total: number }>(`/notifications/me?${params}`, token!)
    setItems(data.items)
    setTotal(data.total)
  }

  return (
    <div className="container">
      <h1>Notifications</h1>
      <div style={{ marginBottom: 8, display: 'flex', gap: 8, alignItems: 'center' }}>
        <button onClick={markAll}>Tout marquer comme lu</button>
        <label style={{ display: 'inline-flex', gap: 6, alignItems: 'center' }}>
          <input type="checkbox" checked={unreadOnly} onChange={e => { setPage(1); setUnreadOnly(e.target.checked) }} /> Unread only
        </label>
      </div>
      <ul>
        {items.map(n => (
          <li key={n.id} className="list-item">
            <span>
              {n.message} — {new Date(n.created_at).toLocaleString()} {n.is_read ? '(lu)' : ''}
            </span>
            {!n.is_read && <button onClick={() => markRead(n.id)}>Marquer lu</button>}
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

export default Notifications
