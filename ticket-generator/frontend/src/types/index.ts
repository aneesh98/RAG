export const categories = ['HARDWARE', 'SOFTWARE', 'NETWORK', 'ACCESS', 'OTHER'] as const
export const priorities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'] as const
export const statuses = ['OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED'] as const
export type Category = typeof categories[number]
export type Priority = typeof priorities[number]
export type Status = typeof statuses[number]
export interface User { id: number; name: string; email: string; role: 'EMPLOYEE' | 'SUPPORT_AGENT' }
export interface Ticket { id: number; title: string; description: string; category: Category; priority: Priority; status: Status; created_by: number; assigned_to: number | null; created_at: string; updated_at: string; creator: User; assignee: User | null }
export interface TicketPage { items: Ticket[]; total: number; page: number; page_size: number; total_pages: number }
export interface Stats { total: number; open: number; in_progress: number; resolved: number; closed: number }
export interface TicketCreate { title: string; description: string; category: Category; priority: Priority; created_by: number }
export interface TicketUpdate { status?: Status; priority?: Priority; assigned_to?: number | null }
export const label = (value: string) => value.toLowerCase().replaceAll('_', ' ').replace(/\b\w/g, c => c.toUpperCase())
export const date = (value: string) => new Date(value).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
