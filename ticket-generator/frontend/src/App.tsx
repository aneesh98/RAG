import { useEffect, useState } from 'react'
import { BrowserRouter, Link, NavLink, Route, Routes, useLocation, Navigate } from 'react-router-dom'
import { Check, CircleHelp, LayoutDashboard, Menu, Plus, ShieldCheck, Ticket, X } from 'lucide-react'
import { api } from './services/api'
import { label, type User } from './types'
import { Workspace } from './components/Workspace'
import { ErrorState, Loading } from './components/Common'
import Dashboard from './pages/Dashboard'
import Tickets from './pages/Tickets'
import CreateTicket from './pages/CreateTicket'
import TicketDetail from './pages/TicketDetail'

function Shell() {
  const [users, setUsers] = useState<User[]>([]); const [userId, setUserId] = useState(() => Number(localStorage.getItem('deskflow-user') || 1))
  const [error, setError] = useState(''); const [retry, setRetry] = useState(0); const [menu, setMenu] = useState(false)
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)
  const location = useLocation()
  useEffect(() => { setMenu(false) }, [location.pathname])
  useEffect(() => {
    const controller = new AbortController(); setError('')
    api.users(controller.signal).then(data => { setUsers(data); if (!data.some(u => u.id === userId)) setUserId(data[0]?.id || 1) }).catch(e => { if (!controller.signal.aborted) setError(e.message) })
    return () => controller.abort()
  }, [retry])
  useEffect(() => { localStorage.setItem('deskflow-user', String(userId)); setToast(null) }, [userId])
  useEffect(() => { if (toast) { const timer = setTimeout(() => setToast(null), 6000); return () => clearTimeout(timer) } }, [toast])
  const user = users.find(u => u.id === userId)
  if (error) return <main className="startup"><h1>Deskflow</h1><ErrorState message={`Unable to connect to the helpdesk API. ${error}`} retry={() => setRetry(v => v + 1)}/></main>
  if (!user) return <main className="startup"><h1>Deskflow</h1>{users.length ? <ErrorState message="No selected user is available."/> : <Loading/>}</main>
  const title = location.pathname === '/' ? 'Dashboard' : location.pathname === '/tickets/new' ? 'Create ticket' : location.pathname === '/tickets' ? user.role === 'EMPLOYEE' ? 'My tickets' : 'All tickets' : 'Ticket details'
  return <Workspace.Provider value={{ user, users, notify: (message, type = 'success') => setToast({ message, type }) }}><div className="app-shell">
    {menu && <button aria-label="Close navigation" className="sidebar-overlay" onClick={() => setMenu(false)}/>}
    <aside className={`sidebar ${menu ? 'visible' : ''}`}><Link className="brand" to="/"><span className="brand-symbol"><Ticket size={23}/></span>deskflow<span className="brand-period">.</span></Link><p className="brand-subtitle">IT SUPPORT, SIMPLIFIED</p><span className="nav-caption">WORKSPACE</span><nav><NavLink to="/" end><LayoutDashboard size={19}/>Dashboard</NavLink><NavLink to="/tickets"><Ticket size={19}/>{user.role === 'EMPLOYEE' ? 'My tickets' : 'All tickets'}</NavLink>{user.role === 'EMPLOYEE' && <Link className="nav-create" to="/tickets/new"><Plus size={18}/>Create ticket</Link>}</nav>
    <div className="sidebar-bottom"><div className="support-note"><CircleHelp size={22}/><h3>A little help, a lot less hassle.</h3><p>One place for every IT request.</p></div><div className="sidebar-user"><span className="avatar">{user.name.split(' ').map(n => n[0]).join('')}</span><div><strong>{user.name}</strong><small>{label(user.role)}</small></div><span className="online-dot"/></div></div></aside>
    <div className="main-shell"><header className="topbar"><div className="breadcrumb"><button className="icon-button mobile-menu" aria-label="Open navigation" onClick={() => setMenu(true)}><Menu size={21}/></button><span>Workspace</span><span className="breadcrumb-slash">/</span><strong>{title}</strong></div><div className="demo-selector"><span className="demo-tag">DEMO USER</span><select aria-label="Switch demo user" value={userId} onChange={e => setUserId(Number(e.target.value))}>{users.map(u => <option key={u.id} value={u.id}>{u.name} · {label(u.role)}</option>)}</select></div></header>
    <div className="demo-banner"><ShieldCheck size={15}/><span>Development demo · The user selector allows impersonation. This is not secure authentication.</span></div>
    <main className="page-content"><Routes><Route path="/" element={<Dashboard key={user.id}/>}/><Route path="/tickets" element={<Tickets key={user.id}/>}/><Route path="/tickets/new" element={<CreateTicket key={user.id}/>}/><Route path="/tickets/:id" element={<TicketDetail key={user.id}/>}/><Route path="*" element={<Navigate to="/" replace/>}/></Routes></main><footer className="app-footer"><span>Deskflow · Internal IT Helpdesk</span><span>Less friction. More flow.</span></footer></div>
    {toast && <div className={`toast ${toast.type}`} role={toast.type === 'error' ? 'alert' : 'status'}><Check size={19}/><span>{toast.message}</span><button aria-label="Dismiss notification" onClick={() => setToast(null)}><X size={17}/></button></div>}
  </div></Workspace.Provider>
}
export default function App() { return <BrowserRouter><Shell/></BrowserRouter> }
