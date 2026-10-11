import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, CheckCheck, Clock3, Layers, Plus, Timer } from 'lucide-react'
import { api } from '../services/api'
import type { Stats, Ticket } from '../types'
import { useWorkspace } from '../components/Workspace'
import { ErrorState, Loading, TicketTable } from '../components/Common'

export default function Dashboard() {
  const { user } = useWorkspace()
  const [data, setData] = useState<{ stats: Stats; tickets: Ticket[] } | null>(null)
  const [error, setError] = useState('')
  const [retry, setRetry] = useState(0)
  useEffect(() => {
    const controller = new AbortController(); setError(''); setData(null)
    Promise.all([api.stats(user.id, controller.signal), api.tickets(user.id, { page_size: 5 }, controller.signal)])
      .then(([stats, tickets]) => setData({ stats, tickets: tickets.items }))
      .catch(e => { if (!controller.signal.aborted) setError(e.message) })
    return () => controller.abort()
  }, [user.id, retry])
  return <><div className="page-heading"><div><p className="eyebrow">YOUR SUPPORT WORKSPACE</p><h1>Overview</h1><p>A clear view of {user.role === 'EMPLOYEE' ? 'your IT requests' : 'your team’s support queue'}.</p></div>{user.role === 'EMPLOYEE' && <Link to="/tickets/new" className="button primary"><Plus size={17}/>Create ticket</Link>}</div>
    <section className="welcome"><div><span className="welcome-label">LET’S KEEP THINGS RUNNING</span><h2>Hello, {user.name.split(' ')[0]}.</h2><p>{user.role === 'EMPLOYEE' ? 'From a quick question to a hardware fix, your IT team is here to help.' : 'Your next resolution starts here. Keep every request moving forward.'}</p></div><div className="welcome-art" aria-hidden="true"><div className="art-circle"><CheckCheck size={48}/></div><span className="art-star">✦</span></div></section>
    {error ? <ErrorState message={error} retry={() => setRetry(v => v + 1)}/> : !data ? <Loading/> : <>
      <div className="stats-grid">{[
        { title: 'Total tickets', count: data.stats.total, icon: Layers, color: 'gray', sub: 'All requests in your scope' },
        { title: 'Open', count: data.stats.open, icon: Clock3, color: 'amber', sub: 'Waiting for a helping hand' },
        { title: 'In progress', count: data.stats.in_progress, icon: Timer, color: 'blue', sub: 'Your IT team is on it' },
        { title: 'Resolved', count: data.stats.resolved, icon: CheckCheck, color: 'green', sub: 'Ready to get back to work' },
      ].map(({ title, count, icon: Icon, color, sub }) => <div className="stat-card" key={title}><div className="stat-top"><span>{title}</span><span className={`stat-icon ${color}`}><Icon size={18}/></span></div><strong>{count}</strong><p>{sub}</p></div>)}</div>
      <section className="panel"><div className="panel-heading"><div><h2>Recent tickets</h2><p>The latest requests, all in one place.</p></div><Link className="text-link" to="/tickets">View all tickets<ArrowRight size={16}/></Link></div><TicketTable tickets={data.tickets}/></section>
      <div className="dashboard-note"><span className="small-dot"/> Every request has a place. Track progress and stay in the loop.</div>
    </>}
  </>
}
