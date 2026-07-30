import { HeartPulse, Stethoscope, Hospital, Heart } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuthStore } from '@/stores/auth-store'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Activity, Shield, WifiOff, Globe, PhoneCall, MessageSquare } from 'lucide-react'

// ── Feature Card Component ───────────────────────────────────────────────────

function FeatureCard({ icon: Icon, title, description, delay }: {
  icon: React.ComponentType<any>
  title: string
  description: string
  delay: number
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-40px' }}
      transition={{ duration: 0.4, delay, ease: 'easeOut' }}
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
    >
      <Card className="h-full border border-border bg-card p-5 flex flex-col gap-3 shadow-sm hover:shadow-md transition-shadow">
        <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary flex-shrink-0">
          <Icon className="h-5 w-5" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-foreground">{title}</h3>
          <p className="text-xs text-muted-foreground mt-1 leading-relaxed">{description}</p>
        </div>
      </Card>
    </motion.div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function LandingPage() {
  const navigate = useNavigate()
  const { isAuthenticated, setAuth } = useAuthStore()
  const [showModal, setShowModal] = useState(false)

  const handleGuest = () => {
    setAuth('guest-token', 'guest-refresh', 'guest-id', 'GUEST', false)
    navigate('/dashboard')
  }

  const handleGetStarted = () => {
    if (isAuthenticated) {
      navigate('/dashboard')
    } else {
      setShowModal(true)
    }
  }

  const features = [
    { icon: Activity, title: 'Smart Health Assessment', description: 'Interactive clinical decision tree triage designed by healthcare experts.', delay: 0 },
    { icon: MessageSquare, title: 'Voice Consultation', description: 'Hands-free voice mode powered by natural speech-to-text integration.', delay: 0.05 },
    { icon: WifiOff, title: 'Offline Support', description: 'Fully functional assessment flows and recommendations without internet.', delay: 0.1 },
    { icon: Globe, title: 'Multiple Languages', description: 'Available in English, Twi (Akan), and others to make healthcare inclusive.', delay: 0.15 },
    { icon: PhoneCall, title: 'Emergency Assistance', description: 'Quick access to national emergency dialer and primary health contacts.', delay: 0.2 },
    { icon: Shield, title: 'Privacy First', description: 'Your health data is stored securely and never shared without consent.', delay: 0.25 },
  ]

  return (
    <div className="min-h-screen bg-background flex flex-col justify-between overflow-x-hidden">
      
      {/* ── Navbar / Header ────────────────────────────────────── */}
      <header className="sticky top-0 z-40 border-b border-border bg-background/80 backdrop-blur-sm">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-2 font-bold text-foreground">
            <span className="text-2xl"><HeartPulse className="w-4 h-4" /></span>
            <span>FirstAid+</span>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => navigate('/login')}>Sign In</Button>
            <Button size="sm" onClick={() => navigate('/register')}>Sign Up</Button>
          </div>
        </div>
      </header>

      {/* ── Hero Section ───────────────────────────────────────── */}
      <main className="flex-1 max-w-5xl mx-auto px-4 py-12 sm:py-20 flex flex-col items-center text-center gap-10">
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
          className="space-y-4 max-w-3xl"
        >
          <span className="inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1 rounded-full bg-primary/10 text-primary border border-primary/20">
            <Hospital className="w-4 h-4" /> Professional Triage Companion
          </span>
          <h1 className="text-3xl sm:text-5xl font-extrabold text-foreground tracking-tight leading-tight">
            Your Personal Health Companion
          </h1>
          <p className="text-sm sm:text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Get quick health guidance, complete symptom assessments, and access emergency support—even when you're offline.
          </p>
        </motion.div>

        {/* CTAs */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4, delay: 0.15 }}
          className="flex flex-col sm:flex-row gap-3 w-full max-w-md justify-center"
        >
          <button
            onClick={handleGetStarted}
            className="flex-1 bg-primary hover:bg-primary/95 text-primary-foreground font-bold text-base rounded-xl py-3.5 shadow-lg transition-transform active:scale-[0.98]"
          >
            Get Started
          </button>
          <button
            onClick={handleGuest}
            className="flex-1 border border-border bg-background hover:bg-accent text-foreground font-semibold text-base rounded-xl py-3.5 transition-transform active:scale-[0.98]"
          >
            Continue as Guest
          </button>
        </motion.div>

        {/* Secondary Login/Register CTAs */}
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.6 }}
          transition={{ delay: 0.3 }}
          className="text-xs text-muted-foreground"
        >
          Have an account?{' '}
          <button onClick={() => navigate('/login')} className="text-primary font-semibold hover:underline">Sign In</button>
          {' '}or{' '}
          <button onClick={() => navigate('/register')} className="text-primary font-semibold hover:underline">Create Account</button>
        </motion.p>

        {/* ── Feature Cards Grid ─────────────────────────────────── */}
        <div className="w-full pt-10 border-t border-border/60">
          <h2 className="text-lg font-bold text-foreground mb-6 text-left">Key System Features</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {features.map((feat, idx) => (
              <FeatureCard 
                key={idx} 
                icon={feat.icon} 
                title={feat.title} 
                description={feat.description} 
                delay={feat.delay} 
              />
            ))}
          </div>
        </div>
      </main>

      {/* ── Get Started Modal ──────────────────────────────────── */}
      <AnimatePresence>
        {showModal && (
          <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
            <motion.div
              initial={{ y: 50, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: 50, opacity: 0 }}
              className="w-full max-w-sm rounded-2xl bg-background p-6 shadow-2xl border border-border"
            >
              <div className="text-center space-y-4">
                <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center text-xl mx-auto">
                  <Stethoscope className="w-4 h-4" />
                </div>
                <div>
                  <h2 className="text-base font-bold text-foreground">Welcome to FirstAid+</h2>
                  <p className="text-xs text-muted-foreground mt-1 leading-relaxed">
                    Choose how you would like to proceed with your health assessment.
                  </p>
                </div>
                <div className="flex flex-col gap-2 pt-2">
                  <Button onClick={() => { setShowModal(false); handleGuest() }} className="w-full py-3 text-xs font-bold">
                    Continue as Guest
                  </Button>
                  <Button variant="outline" onClick={() => { setShowModal(false); navigate('/login') }} className="w-full py-3 text-xs font-semibold">
                    Sign In
                  </Button>
                  <Button variant="outline" onClick={() => { setShowModal(false); navigate('/register') }} className="w-full py-3 text-xs font-semibold">
                    Create Account
                  </Button>
                  <Button variant="ghost" onClick={() => setShowModal(false)} className="w-full text-xs text-muted-foreground mt-1">
                    Cancel
                  </Button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ── Footer ─────────────────────────────────────────────── */}
      <footer className="border-t border-border bg-muted/20 py-4 text-center text-[10px] text-muted-foreground">
        Made with <Heart className="w-4 h-4" />️ by SEVEN
      </footer>

    </div>
  )
}
