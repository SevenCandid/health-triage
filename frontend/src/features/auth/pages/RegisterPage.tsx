import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/auth-store'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { authApi } from '@/services/api'
import { Activity } from 'lucide-react'

export default function RegisterPage() {
  const [fullName, setFullName] = useState('')
  const [countryCode, setCountryCode] = useState('+233')
  const [phone, setPhone] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const setAuth = useAuthStore((s) => s.setAuth)
  const navigate = useNavigate()

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long.')
      return
    }

    setIsLoading(true)
    try {
      const response = await authApi.register({
        full_name: fullName,
        phone_number: `${countryCode}${phone.replace(/^0+/, '').replace(/\s+/g, '')}`,
        email: email || undefined,
        password: password,
        preferred_language: 'en',
      })

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
      console.error('Registration error:', err)
      
      let errorMessage = 'Registration failed. Please try again.'
      if (err.response?.data?.detail) {
        // Handle FastAPI validation error array or string
        if (Array.isArray(err.response.data.detail)) {
          errorMessage = err.response.data.detail.map((e: any) => e.msg).join(' ')
        } else {
          errorMessage = err.response.data.detail
        }
      } else if (err.message) {
        errorMessage = `Registration failed: ${err.message}`
      }
      
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col items-center justify-center w-full">
      <div className="w-full max-w-md rounded-2xl border border-border bg-card p-6 sm:p-10 shadow-lg">
        <div className="mb-8 text-center flex flex-col items-center">
          <div className="mb-4 rounded-full bg-primary/10 p-3">
            <Activity className="h-8 w-8 text-primary" />
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-foreground">Create Account</h2>
          <p className="text-sm text-muted-foreground mt-2">Join to securely manage your health</p>
        </div>

        <form onSubmit={handleRegister} className="space-y-4">
          <Input
            label="Full Name"
            type="text"
            placeholder="Seven Frank"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
            autoComplete="name"
          />
          <div>
            <label className="text-sm font-medium text-foreground mb-1.5 block">
              Mobile Number
              <span className="ml-1 text-urgency-emergency">*</span>
            </label>
            <div className="flex gap-2">
              <select
                value={countryCode}
                onChange={(e) => setCountryCode(e.target.value)}
                className="flex h-10 w-[110px] rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              >
                <option value="+233">🇬🇭 +233</option>
                <option value="+1">🇺🇸 +1</option>
                <option value="+44">🇬🇧 +44</option>
                <option value="+234">🇳🇬 +234</option>
                <option value="+254">🇰🇪 +254</option>
                <option value="+27">🇿🇦 +27</option>
                <option value="+91">🇮🇳 +91</option>
              </select>
              <Input
                type="tel"
                placeholder="20 123 4567"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                required
                autoComplete="tel"
                className="flex-1"
              />
            </div>
            <p className="text-xs text-muted-foreground mt-1">Enter your number without the country code.</p>
          </div>
          <Input
            label="Email Address (Optional)"
            type="email"
            placeholder="john@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
          />
          <div>
            <Input
              label="Password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="new-password"
            />
            <p className="text-xs text-muted-foreground mt-1">Minimum 8 characters with at least one number and uppercase letter</p>
          </div>
          <Input
            label="Confirm Password"
            type="password"
            placeholder="••••••••"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            autoComplete="new-password"
          />
          
          {error && (
            <div className="text-sm text-destructive bg-destructive/10 p-3 rounded-md">
              {error}
            </div>
          )}

          <Button type="submit" fullWidth className="mt-6 h-12 text-base font-semibold" disabled={isLoading}>
            {isLoading ? 'Creating Account...' : 'Sign Up'}
          </Button>
        </form>

        <p className="mt-8 text-center text-sm text-muted-foreground">
          Already have an account?{' '}
          <button onClick={() => navigate('/login')} className="font-medium text-primary hover:underline transition-all">
            Log in instead
          </button>
        </p>
      </div>
    </div>
  )
}
