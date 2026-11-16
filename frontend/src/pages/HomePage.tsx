import { useAuth } from '../hooks/useAuth'

/** Placeholder for the signed-in area. Consent and CV upload arrive in Stories 2.2 and 2.3. */
export function HomePage() {
  const { user, signOut } = useAuth()
  if (!user) return null

  return (
    <main className="card">
      <h1>Ask the Circular</h1>
      <h2>You are signed in</h2>
      <dl className="facts">
        <dt>Email</dt>
        <dd>{user.email}</dd>
        <dt>Role</dt>
        <dd>{user.role}</dd>
        <dt>Profile</dt>
        <dd>{user.has_confirmed_profile ? 'Confirmed' : 'Not set up yet'}</dd>
      </dl>
      <p>Uploading your CV and circulars comes next.</p>
      <button type="button" onClick={signOut}>
        Sign out
      </button>
    </main>
  )
}
