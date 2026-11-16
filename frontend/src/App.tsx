import { AuthProvider } from './components/AuthProvider'
import { useAuth } from './hooks/useAuth'
import { AuthPage } from './pages/AuthPage'
import { HomePage } from './pages/HomePage'

function Screen() {
  const { status } = useAuth()
  if (status === 'loading') return <p className="loading">Loading…</p>
  return status === 'signedIn' ? <HomePage /> : <AuthPage />
}

function App() {
  return (
    <AuthProvider>
      <Screen />
    </AuthProvider>
  )
}

export default App
