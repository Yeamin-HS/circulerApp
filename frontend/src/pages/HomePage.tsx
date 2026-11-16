import { ConsentCard } from '../components/ConsentCard'
import { DeleteAccount } from '../components/DeleteAccount'
import { useAuth } from '../hooks/useAuth'

/** Signed-in area. CV upload and the profile review arrive in Story 2.3. */
export function HomePage() {
  const { user, signOut } = useAuth()
  if (!user) return null
  const consentDate = user.consent_at && new Date(user.consent_at).toLocaleDateString()

  return (
    <main className="card">
      <h1>Ask the Circular</h1>
      <h2>Your account</h2>
      <dl className="facts">
        <dt>Email</dt>
        <dd>{user.email}</dd>
        <dt>Role</dt>
        <dd>{user.role}</dd>
        <dt>Consent</dt>
        <dd>{consentDate ? `Given on ${consentDate}` : 'Not given yet'}</dd>
        <dt>Profile</dt>
        <dd>{user.has_confirmed_profile ? 'Confirmed' : 'Not set up yet'}</dd>
      </dl>
      {user.consent_at ? <p>Uploading your CV comes next.</p> : <ConsentCard />}
      <button type="button" className="quiet" onClick={signOut}>
        Sign out
      </button>
      <div className="footer">
        <DeleteAccount />
      </div>
    </main>
  )
}
