import { useState } from 'react'
import { ApiError } from '../api/client'
import { useAuth } from '../hooks/useAuth'

/** Account deletion (FR-06). Two steps, because it cannot be undone. */
export function DeleteAccount() {
  const { removeAccount } = useAuth()
  const [confirming, setConfirming] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function confirm() {
    setBusy(true)
    setError(null)
    try {
      await removeAccount() // signs out on success, which unmounts this component
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : 'Something went wrong. Try again.')
      setBusy(false)
    }
  }

  if (!confirming) {
    return (
      <button type="button" className="link danger" onClick={() => setConfirming(true)}>
        Delete my account and all data
      </button>
    )
  }

  return (
    <section className="panel danger" role="alertdialog" aria-labelledby="delete-title">
      <h3 id="delete-title">Delete your account?</h3>
      <p>
        This removes your account, your profile and every circular you uploaded. It cannot be
        undone.
      </p>
      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}
      <div className="row">
        <button type="button" className="danger" disabled={busy} onClick={confirm}>
          {busy ? 'Deleting…' : 'Yes, delete everything'}
        </button>
        <button type="button" className="quiet" disabled={busy} onClick={() => setConfirming(false)}>
          Cancel
        </button>
      </div>
    </section>
  )
}
