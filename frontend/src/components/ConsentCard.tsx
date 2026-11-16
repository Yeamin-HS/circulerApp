import { useState } from 'react'
import { ApiError } from '../api/client'
import { useAuth } from '../hooks/useAuth'

/** Consent to store a profile (FR-02). Shown until the user agrees; nothing is ticked for them. */
export function ConsentCard() {
  const { acceptConsent } = useAuth()
  const [agreed, setAgreed] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function submit() {
    setBusy(true)
    setError(null)
    try {
      await acceptConsent()
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : 'Something went wrong. Try again.')
      setBusy(false)
    }
  }

  return (
    <section className="panel" aria-labelledby="consent-title">
      <h3 id="consent-title">Before you add your CV</h3>
      <p>To check which posts you qualify for, we need to keep a profile made from your CV.</p>
      <ul>
        <li>We keep your email, a scrambled form of your password, and the profile you confirm.</li>
        <li>Your CV file is deleted as soon as you confirm the profile.</li>
        <li>We do not keep the text of the questions you ask.</li>
        <li>Only you can see your profile and your circulars.</li>
        <li>You can delete your account and all of this data at any time, from this page.</li>
      </ul>
      <label className="check">
        <input type="checkbox" checked={agreed} onChange={(e) => setAgreed(e.target.checked)} />
        I agree to my profile being stored for this purpose.
      </label>
      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}
      <button type="button" disabled={!agreed || busy} onClick={submit}>
        {busy ? 'Saving…' : 'Agree and continue'}
      </button>
    </section>
  )
}
