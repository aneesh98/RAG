import type { Stats, Ticket, TicketCreate, TicketPage, TicketUpdate, User } from '../types'
const base = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001').replace(/\/$/, '')

async function request<T>(path: string, userId?: number, init: RequestInit = {}, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${base}/api${path}`, {
    ...init, signal, headers: { 'Content-Type': 'application/json', ...(userId ? { 'X-Demo-User-Id': String(userId) } : {}), ...init.headers },
  })
  if (!response.ok) {
    const payload = await response.json().catch(() => null)
    const details = payload?.error?.details?.map((d: { location: (string | number)[]; message: string }) => `${d.location.join('.')}: ${d.message}`).join('; ')
    throw new Error(details || payload?.error?.message || `Request failed (${response.status})`)
  }
  return response.json()
}

export const api = {
  users: (signal?: AbortSignal) => request<User[]>('/users', undefined, {}, signal),
  tickets: (id: number, params: Record<string, string | number> = {}, signal?: AbortSignal) => {
    const query = new URLSearchParams(Object.entries(params).filter(([, v]) => String(v) !== '').map(([k, v]) => [k, String(v)]))
    return request<TicketPage>(`/tickets?${query}`, id, {}, signal)
  },
  stats: (id: number, signal?: AbortSignal) => request<Stats>('/tickets/stats', id, {}, signal),
  ticket: (id: number, ticketId: string, signal?: AbortSignal) => request<Ticket>(`/tickets/${ticketId}`, id, {}, signal),
  create: (id: number, data: TicketCreate) => request<Ticket>('/tickets', id, { method: 'POST', body: JSON.stringify(data) }),
  update: (id: number, ticketId: number, data: TicketUpdate) => request<Ticket>(`/tickets/${ticketId}`, id, { method: 'PATCH', body: JSON.stringify(data) }),
}
