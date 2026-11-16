import { useCallback, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { deleteAccount, getMe, giveConsent, login, register } from '../api/auth'
import type { Credentials } from '../api/auth'
import { ApiError } from '../api/client'
import type { TokenResponse, User } from '../api/client'
import { AuthContext } from '../hooks/useAuth'
import type { AuthState } from '../hooks/useAuth'

// ADR-012: the token lives in React state, mirrored to sessionStorage so a refresh keeps
// the session. It is cleared when the tab closes, on sign-out, on a 401 and at expiry.
const STORAGE_KEY = 'atc.session'

interface Session {
  token: string
  expiresAt: number // epoch milliseconds
}

function readStored(): Session | null {
  try {
    const session = JSON.parse(sessionStorage.getItem(STORAGE_KEY) ?? 'null') as Session | null
    return session && session.expiresAt > Date.now() ? session : null
  } catch {
    return null
  }
}

function store(session: Session | null) {
  try {
    if (session) sessionStorage.setItem(STORAGE_KEY, JSON.stringify(session))
    else sessionStorage.removeItem(STORAGE_KEY)
  } catch {
    // Storage can be unavailable (private mode); the in-memory session still works.
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(readStored)
  const [user, setUser] = useState<User | null>(null)

  const signOut = useCallback(() => {
    store(null)
    setSession(null)
    setUser(null)
  }, [])

  // Load the user for a token (after sign-in, or a stored token on page load).
  useEffect(() => {
    if (!session || user) return
    let cancelled = false
    getMe(session.token)
      .then((me) => {
        if (!cancelled) setUser(me)
      })
      .catch((error: unknown) => {
        // Only a rejected token ends the session; a sleeping server must not sign people out.
        if (!cancelled && error instanceof ApiError && error.status === 401) signOut()
      })
    return () => {
      cancelled = true
    }
  }, [session, user, signOut])

  // Sign out at the moment the token expires.
  useEffect(() => {
    if (!session) return
    const timer = setTimeout(signOut, Math.max(0, session.expiresAt - Date.now()))
    return () => clearTimeout(timer)
  }, [session, signOut])

  const start = useCallback(async (request: Promise<TokenResponse>) => {
    const reply = await request
    const next = { token: reply.access_token, expiresAt: Date.now() + reply.expires_in * 1000 }
    const me = await getMe(next.token)
    store(next)
    setUser(me)
    setSession(next)
  }, [])

  const token = session?.token ?? null

  const acceptConsent = useCallback(async () => {
    if (token) setUser(await giveConsent(token))
  }, [token])

  const removeAccount = useCallback(async () => {
    if (!token) return
    await deleteAccount(token)
    signOut()
  }, [token, signOut])

  const value = useMemo<AuthState>(
    () => ({
      status: !session ? 'signedOut' : user ? 'signedIn' : 'loading',
      user,
      token,
      signIn: (credentials: Credentials) => start(login(credentials)),
      signUp: (credentials: Credentials) => start(register(credentials)),
      signOut,
      acceptConsent,
      removeAccount,
    }),
    [session, user, token, start, signOut, acceptConsent, removeAccount],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
