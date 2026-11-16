import { useState } from 'react'
import type { FormEvent } from 'react'
import { ApiError } from '../api/client'
import { useAuth } from '../hooks/useAuth'

type Mode = 'signIn' | 'signUp'

function messageFor(error: unknown): string {
  if (!(error instanceof ApiError)) return 'Something went wrong. Please try again.'
  switch (error.code) {
    case 'invalid_credentials':
      return 'Wrong email or password.'
    case 'email_taken':
      return 'An account with this email already exists. Sign in instead.'
    case 'rate_limited':
      return `Too many attempts. Try again in ${Math.ceil((error.retryAfter ?? 60) / 60)} minute(s).`
    case 'validation_error':
      return 'Enter a valid email address and a password of at least 8 characters.'
    default:
      return error.message
  }
}

export function AuthPage() {
  const { signIn, signUp } = useAuth()
  const [mode, setMode] = useState<Mode>('signIn')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const signingUp = mode === 'signUp'

  async function submit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setBusy(true)
    try {
      await (signingUp ? signUp : signIn)({ email: email.trim(), password })
    } catch (caught) {
      setError(messageFor(caught))
      setBusy(false)
    }
  }

  function switchMode() {
    setMode(signingUp ? 'signIn' : 'signUp')
    setError(null)
  }

  return (
    <main className="card">
      <h1>Ask the Circular</h1>
      <h2>{signingUp ? 'Create your account' : 'Sign in'}</h2>
      <form onSubmit={submit} noValidate={false}>
        <label>
          Email
          <input
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </label>
        <label>
          Password
          <input
            type="password"
            autoComplete={signingUp ? 'new-password' : 'current-password'}
            required
            minLength={signingUp ? 8 : undefined}
            maxLength={128}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {signingUp && <small>At least 8 characters. There is no password reset yet.</small>}
        </label>
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
        <button type="submit" disabled={busy}>
          {busy ? 'Please wait…' : signingUp ? 'Create account' : 'Sign in'}
        </button>
      </form>
      <p className="switch">
        {signingUp ? 'Already have an account?' : 'New here?'}{' '}
        <button type="button" className="link" onClick={switchMode}>
          {signingUp ? 'Sign in' : 'Create an account'}
        </button>
      </p>
    </main>
  )
}
