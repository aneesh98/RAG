import { Link, useNavigate } from 'react-router-dom'
import { ArrowUpRight, Inbox, LoaderCircle, RotateCcw } from 'lucide-react'
import { date, label, type Ticket } from '../types'

export function Badge({ value, kind = 'status' }: { value: string; kind?: 'status' | 'priority' }) {
  return <span className={`badge ${kind} ${value.toLowerCase()}`}><span className="badge-dot"/>{label(value)}</span>
}
export function Loading() { return <div className="state" role="status"><LoaderCircle className="spin" size={25}/><p>Loading your workspace…</p></div> }
export function ErrorState({ message, retry }: { message: string; retry?: () => void }) {
  return <div className="state error-state" role="alert"><p>{message}</p>{retry && <button className="button secondary" onClick={retry}><RotateCcw size={16}/>Try again</button>}</div>
}
export function EmptyState({ title = 'No tickets found', description = 'Try adjusting your filters or create a new ticket.' }: { title?: string; description?: string }) {
  return <div className="state"><div className="empty-icon"><Inbox size={28}/></div><h3>{title}</h3><p>{description}</p></div>
}
export function TicketTable({ tickets }: { tickets: Ticket[] }) {
  const navigate = useNavigate()
  if (!tickets.length) return <EmptyState/>
  return <div className="table-scroll"><table><thead><tr><th>Ticket</th><th>Category</th><th>Priority</th><th>Status</th><th>Created by</th><th>Assigned to</th><th>Created</th><th><span className="sr-only">View</span></th></tr></thead>
    <tbody>{tickets.map(ticket => <tr key={ticket.id} onClick={e => { if (!(e.target as HTMLElement).closest('a')) navigate(`/tickets/${ticket.id}`) }} style={{ cursor: 'pointer' }}>
      <td><Link className="ticket-link" to={`/tickets/${ticket.id}`}><span className="ticket-id">#{String(ticket.id).padStart(4, '0')}</span><span className="ticket-title">{ticket.title}</span></Link></td>
      <td>{label(ticket.category)}</td><td><Badge kind="priority" value={ticket.priority}/></td><td><Badge value={ticket.status}/></td>
      <td>{ticket.creator.name}</td><td>{ticket.assignee?.name || <span className="muted">Unassigned</span>}</td><td className="nowrap">{date(ticket.created_at)}</td>
      <td><Link className="row-arrow" aria-label={`View ticket ${ticket.id}`} to={`/tickets/${ticket.id}`}><ArrowUpRight size={17}/></Link></td>
    </tr>)}</tbody></table></div>
}
