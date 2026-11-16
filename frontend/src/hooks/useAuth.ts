import { createContext, useContext } from 'react'
import type { Credentials } from '../api/auth'
import type { User } from '../api/client'

export interface AuthState {
  /** 'loading' while a stored token is being checked on page load. */
  status: 'loading' | 'signedOut' | 'signedIn'
  user: User | null
  token: string | null
  signIn: (credentials: Credentials) => Promise<void>
  signUp: (credentials: Credentials) => Promise<void>
  signOut: () => void
  /** Record consent to store a profile (FR-02). */
  acceptConsent: () => Promise<void>
  /** Delete the account and all data, then sign out. Cannot be undone. */
  removeAccount: () => Promise<void>
}

export const AuthContext = createContext<AuthState | null>(null)

export function useAuth(): AuthState {
  const value = useContext(AuthContext)
  if (!value) throw new Error('useAuth must be used inside <AuthProvider>')
  return value
}
