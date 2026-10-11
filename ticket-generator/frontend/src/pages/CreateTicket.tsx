import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, ArrowRight, Info, LoaderCircle } from 'lucide-react'
import { api } from '../services/api'
import { categories, priorities, label, type Category, type Priority } from '../types'
import { useWorkspace } from '../components/Workspace'

export default function CreateTicket() {
  const { user, notify } = useWorkspace(); const navigate = useNavigate()
  const [title, setTitle] = useState(''); const [description, setDescription] = useState('')
  const [category, setCategory] = useState<Category | ''>(''); const [priority, setPriority] = useState<Priority>('MEDIUM')
  const [error, setError] = useState(''); const [busy, setBusy] = useState(false)
  async function submit(e: FormEvent) {
    e.preventDefault(); setError('')
    if (!title.trim() || !description.trim() || !category) { setError('Please fill in the title, description, and category.'); return }
    setBusy(true)
    try { const ticket = await api.create(user.id, { title: title.trim(), description: description.trim(), category, priority, created_by: user.id }); notify(`Ticket #${ticket.id} created. Your IT team will take it from here.`); navigate(`/tickets/${ticket.id}`) }
    catch (e) { setError(e instanceof Error ? e.message : 'Unable to create ticket') }
    finally { setBusy(false) }
  }
  if (user.role !== 'EMPLOYEE') return <div className="panel state"><h2>Ticket creation is for employees</h2><p>Choose an employee account in the demo user selector to submit a request.</p><Link className="button secondary" to="/tickets">View all tickets</Link></div>
  return <><Link className="back-link" to="/tickets"><ArrowLeft size={16}/>Back to tickets</Link><div className="page-heading"><div><p className="eyebrow">WE’RE HERE TO HELP</p><h1>Create a ticket</h1><p>Tell us what’s happening. We’ll help you get it sorted.</p></div></div>
    <div className="form-layout"><form className="panel ticket-form" onSubmit={submit}><h2>Request details</h2><p className="muted form-intro">Fields marked with * are required.</p>
      <label>Title *<input required maxLength={200} value={title} onChange={e => setTitle(e.target.value)} placeholder="A brief summary of the issue"/><span className="field-hint">Keep it short and specific. {title.length}/200</span></label>
      <label>Description *<textarea required maxLength={20000} rows={7} value={description} onChange={e => setDescription(e.target.value)} placeholder="What happened? Include any error messages and steps you’ve already tried."/></label>
      <div className="form-grid"><label>Category *<select required value={category} onChange={e => setCategory(e.target.value as Category)}><option value="">Select a category</option>{categories.map(v => <option key={v} value={v}>{label(v)}</option>)}</select></label><label>Priority<select value={priority} onChange={e => setPriority(e.target.value as Priority)}>{priorities.map(v => <option key={v} value={v}>{label(v)}</option>)}</select></label></div>
      {error && <div className="inline-error" role="alert">{error}</div>}
      <div className="form-footer"><span>Submitting as <strong>{user.name}</strong></span><button className="button primary" disabled={busy}>{busy ? <LoaderCircle className="spin" size={17}/> : <ArrowRight size={17}/>} {busy ? 'Submitting…' : 'Submit ticket'}</button></div>
    </form><aside className="help-card"><Info size={23}/><h3>A little detail goes a long way</h3><p>Include the device or application involved, when the issue started, and how it affects your work.</p><hr/><h4>Choosing a priority</h4><p><strong>Low</strong> · A minor issue or general request.</p><p><strong>Medium</strong> · Work is affected, but there’s a workaround.</p><p><strong>High</strong> · You’re blocked from important work.</p><p><strong>Critical</strong> · A widespread outage or urgent business impact.</p></aside></div>
  </>
}
