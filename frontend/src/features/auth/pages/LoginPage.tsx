import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/auth-store'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { authApi } from '@/services/api'
import { Activity } from 'lucide-react'

export default function LoginPage() {
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const setAuth = useAuthStore((s) => s.setAuth)
  const navigate = useNavigate()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)
    
    try {
      const response = await authApi.login({ identifier, password })
      const { access_token, refresh_token, user } = response.data
      
      setAuth(
        access_token, 
        refresh_token, 
        user.id, 
        'PATIENT', 
        user.profile_completed
      )
      
      navigate('/dashboard')
    } catch (err: any) {
      if (err.code === 'ERR_NETWORK' || err.message === 'Network Error') {
        setError('You are offline. Please connect to the internet to log in, or continue as a guest.')
      } else {
        setError(err.response?.data?.detail || 'Invalid credentials. Please try again.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleGuestAccess = () => {
    // Set guest role to allow basic app usage without an account
    setAuth('guest-token', 'guest-refresh', 'guest-id', 'GUEST', false)
    navigate('/dashboard')
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh]">
      <div className="w-full max-w-md rounded-2xl border border-border bg-card p-6 sm:p-10 shadow-lg">
        <div className="mb-8 text-center flex flex-col items-center">
          <div className="mb-4 rounded-full bg-primary/10 p-3">
            <Activity className="h-8 w-8 text-primary" />
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-foreground">Welcome Back</h2>
          <p className="text-sm text-muted-foreground mt-2">Log in to access your health profile</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-5">
          <Input
            label="Email or Mobile Number"
            type="text"
            placeholder="example@email.com or +1234567890"
            value={identifier}
            onChange={(e) => setIdentifier(e.target.value)}
            required
            autoComplete="username"
          />
          <Input
            label="Password"
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
          />
          
          {error && (
            <div className="text-sm text-destructive bg-destructive/10 p-3 rounded-md">
              {error}
            </div>
          )}

          <Button type="submit" fullWidth className="mt-4 h-12 text-base font-semibold" disabled={isLoading}>
            {isLoading ? 'Logging in...' : 'Log In'}
          </Button>
        </form>

        <div className="relative my-8">
          <div className="absolute inset-0 flex items-center">
            <span className="w-full border-t border-border" />
          </div>
          <div className="relative flex justify-center text-xs uppercase tracking-wider">
            <span className="bg-card px-3 text-muted-foreground font-medium">Or</span>
          </div>
        </div>

        <Button 
          variant="outline" 
          fullWidth 
          className="h-12"
          onClick={handleGuestAccess}
        >
          Continue as Guest
        </Button>

        <p className="mt-8 text-center text-sm text-muted-foreground">
          Don't have an account?{' '}
          <button onClick={() => navigate('/register')} className="font-medium text-primary hover:underline transition-all">
            Sign up now
          </button>
        </p>
      </div>
    </div>
  )
}
