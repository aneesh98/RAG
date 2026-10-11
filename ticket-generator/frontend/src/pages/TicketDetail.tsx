import { useEffect, useState, type FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, CalendarDays, LoaderCircle, Save, UserRound } from 'lucide-react'
import { api } from '../services/api'
import { date, label, priorities, statuses, type Ticket, type Status, type Priority } from '../types'
import { useWorkspace } from '../components/Workspace'
import { Badge, ErrorState, Loading } from '../components/Common'

export default function TicketDetail() {
  const { id = '' } = useParams(); const { user, users, notify } = useWorkspace()
  const [ticket, setTicket] = useState<Ticket | null>(null); const [error, setError] = useState(''); const [saveError, setSaveError] = useState(''); const [retry, setRetry] = useState(0)
  const [status, setStatus] = useState<Status>('OPEN'); const [priority, setPriority] = useState<Priority>('MEDIUM'); const [assigned, setAssigned] = useState(''); const [busy, setBusy] = useState(false)
  function populate(t: Ticket) { setTicket(t); setStatus(t.status); setPriority(t.priority); setAssigned(t.assigned_to ? String(t.assigned_to) : '') }
  useEffect(() => {
    const controller = new AbortController(); setTicket(null); setError(''); setSaveError('')
    api.ticket(user.id, id, controller.signal).then(populate).catch(e => { if (!controller.signal.aborted) setError(e.message) })
    return () => controller.abort()
  }, [id, user.id, retry])
  async function save(e: FormEvent) {
    e.preventDefault(); if (!ticket) return; setBusy(true); setSaveError('')
    try { populate(await api.update(user.id, ticket.id, { status, priority, assigned_to: assigned ? Number(assigned) : null })); notify('Ticket updated successfully.') }
    catch (e) { setSaveError(e instanceof Error ? e.message : 'Unable to update ticket') }
    finally { setBusy(false) }
  }
  const changed = ticket && (ticket.status !== status || ticket.priority !== priority || (ticket.assigned_to ? String(ticket.assigned_to) : '') !== assigned)
  return <><Link className="back-link" to="/tickets"><ArrowLeft size={16}/>Back to tickets</Link>
    {error ? <ErrorState message={error} retry={() => setRetry(v => v + 1)}/> : !ticket ? <Loading/> : <>
      <div className="page-heading detail-heading"><div><p className="eyebrow">TICKET #{String(ticket.id).padStart(4, '0')}</p><h1>{ticket.title}</h1><p>Created {date(ticket.created_at)} by {ticket.creator.name}</p></div><Badge value={ticket.status}/></div>
      <div className="detail-layout"><div><section className="panel detail-section"><h2>Description</h2><p className="description">{ticket.description}</p></section><section className="panel detail-section"><h2>People & timeline</h2><div className="info-grid"><div><UserRound size={18}/><span><small>Submitted by</small><strong>{ticket.creator.name}</strong><a href={`mailto:${ticket.creator.email}`}>{ticket.creator.email}</a></span></div><div><UserRound size={18}/><span><small>Assigned agent</small><strong>{ticket.assignee?.name || 'Unassigned'}</strong>{ticket.assignee && <a href={`mailto:${ticket.assignee.email}`}>{ticket.assignee.email}</a>}</span></div><div><CalendarDays size={18}/><span><small>Created</small><strong>{new Date(ticket.created_at).toLocaleString()}</strong></span></div><div><CalendarDays size={18}/><span><small>Last updated</small><strong>{new Date(ticket.updated_at).toLocaleString()}</strong></span></div></div></section></div>
      <aside><section className="panel detail-section"><h2>Ticket information</h2><dl className="metadata"><div><dt>Category</dt><dd>{label(ticket.category)}</dd></div><div><dt>Priority</dt><dd><Badge value={ticket.priority} kind="priority"/></dd></div><div><dt>Status</dt><dd><Badge value={ticket.status}/></dd></div></dl></section>
      {user.role === 'SUPPORT_AGENT' ? <form className="panel management" onSubmit={save}><h2>Manage ticket</h2><p className="muted">Keep this request moving forward.</p><fieldset disabled={busy}><label>Status<select value={status} onChange={e => setStatus(e.target.value as Status)}>{statuses.map(v => <option key={v} value={v}>{label(v)}</option>)}</select></label><label>Priority<select value={priority} onChange={e => setPriority(e.target.value as Priority)}>{priorities.map(v => <option key={v} value={v}>{label(v)}</option>)}</select></label><label>Assigned agent<select value={assigned} onChange={e => setAssigned(e.target.value)}><option value="">Unassigned</option>{users.filter(u => u.role === 'SUPPORT_AGENT').map(u => <option key={u.id} value={u.id}>{u.name}</option>)}</select></label></fieldset>{saveError && <div className="inline-error" role="alert">{saveError}</div>}<button disabled={busy || !changed} className="button primary full">{busy ? <LoaderCircle className="spin" size={17}/> : <Save size={17}/>} {busy ? 'Saving…' : 'Save changes'}</button></form> : <div className="read-only-note">Your IT team manages the status, priority, and assignment of this request.</div>}
      </aside></div>
    </>}
  </>
}
