import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ChevronLeft, ChevronRight, Plus, Search, SlidersHorizontal, X } from 'lucide-react'
import { api } from '../services/api'
import { categories, priorities, statuses, label, type TicketPage } from '../types'
import { useWorkspace } from '../components/Workspace'
import { ErrorState, Loading, TicketTable } from '../components/Common'

export default function Tickets() {
  const { user } = useWorkspace()
  const [search, setSearch] = useState(''); const [debounced, setDebounced] = useState('')
  const [status, setStatus] = useState(''); const [category, setCategory] = useState(''); const [priority, setPriority] = useState('')
  const [page, setPage] = useState(1); const [size, setSize] = useState(10)
  const [data, setData] = useState<TicketPage | null>(null); const [error, setError] = useState(''); const [retry, setRetry] = useState(0)
  useEffect(() => { const timer = setTimeout(() => { setDebounced(search); setPage(1) }, 300); return () => clearTimeout(timer) }, [search])
  useEffect(() => {
    const controller = new AbortController(); setError(''); setData(null)
    api.tickets(user.id, { search: debounced, status, category, priority, page, page_size: size }, controller.signal)
      .then(setData).catch(e => { if (!controller.signal.aborted) setError(e.message) })
    return () => controller.abort()
  }, [user.id, debounced, status, category, priority, page, size, retry])
  const filtered = !!(search || status || category || priority)
  return <><div className="page-heading"><div><p className="eyebrow">TICKET DIRECTORY</p><h1>{user.role === 'EMPLOYEE' ? 'My tickets' : 'All tickets'}</h1><p>{user.role === 'EMPLOYEE' ? 'Keep track of every request from start to finish.' : 'Manage incoming requests and keep your team moving.'}</p></div>{user.role === 'EMPLOYEE' && <Link to="/tickets/new" className="button primary"><Plus size={17}/>Create ticket</Link>}</div>
    <section className="panel"><div className="filter-bar"><div className="search-box"><Search size={18}/><input aria-label="Search tickets" placeholder="Search title or description…" value={search} onChange={e => setSearch(e.target.value)}/></div><SlidersHorizontal size={17} className="filter-icon"/>
      {([{ name: 'Status', plural: 'statuses', options: statuses, value: status, setter: setStatus }, { name: 'Category', plural: 'categories', options: categories, value: category, setter: setCategory }, { name: 'Priority', plural: 'priorities', options: priorities, value: priority, setter: setPriority }]).map(f => <select key={f.name} aria-label={`Filter by ${f.name.toLowerCase()}`} value={f.value} onChange={e => { f.setter(e.target.value); setPage(1) }}><option value="">All {f.plural}</option>{f.options.map(v => <option value={v} key={v}>{label(v)}</option>)}</select>)}
      {filtered && <button className="icon-button" title="Clear filters" aria-label="Clear filters" onClick={() => { setSearch(''); setDebounced(''); setStatus(''); setCategory(''); setPriority(''); setPage(1) }}><X size={17}/></button>}
    </div>
    {error ? <ErrorState message={error} retry={() => setRetry(v => v + 1)}/> : !data ? <Loading/> : <><TicketTable tickets={data.items}/><div className="pagination"><span>{data.total ? `${(page - 1) * size + 1}–${Math.min(page * size, data.total)} of ${data.total} tickets` : '0 tickets'}</span><div className="pagination-controls"><select aria-label="Tickets per page" value={size} onChange={e => { setSize(Number(e.target.value)); setPage(1) }}><option value="10">10 per page</option><option value="25">25 per page</option><option value="50">50 per page</option></select><button aria-label="Previous page" className="icon-button" disabled={page <= 1} onClick={() => setPage(p => p - 1)}><ChevronLeft size={18}/></button><span>Page {page} of {Math.max(1, data.total_pages)}</span><button aria-label="Next page" className="icon-button" disabled={page >= data.total_pages} onClick={() => setPage(p => p + 1)}><ChevronRight size={18}/></button></div></div></>}
    </section>
  </>
}
