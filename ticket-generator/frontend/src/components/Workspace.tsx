import { createContext, useContext } from 'react'
import type { User } from '../types'
export interface WorkspaceValue { user: User; users: User[]; notify: (message: string, type?: 'success' | 'error') => void }
export const Workspace = createContext<WorkspaceValue | null>(null)
export function useWorkspace() { const value = useContext(Workspace); if (!value) throw new Error('Workspace missing'); return value }
