import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { profileApi } from '@/services/api'
import { useAuthStore } from '@/stores/auth-store'
import { useNetworkStore } from '@/stores/network-store'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { PageLoader } from '@/components/common/LoadingSpinner'
import type { HealthProfile, EmergencyContact, EmergencyContactRequest } from '@/types'

// ── Tab System ────────────────────────────────────────────────────────────────

type Tab = 'profile' | 'history' | 'contacts'

const TABS: { id: Tab; label: string; icon: string }[] = [
  { id: 'profile', label: 'Health Profile', icon: '🧬' },
  { id: 'history', label: 'History', icon: '📋' },
  { id: 'contacts', label: 'Emergency Contacts', icon: '🆘' },
]

// ── Toggle Switch ─────────────────────────────────────────────────────────────

function SectionHeader({ icon, title }: { icon: string; title: string }) {
  return (
    <div className="flex items-center gap-2 mb-4">
      <span className="text-xl">{icon}</span>
      <h2 className="text-lg font-semibold text-foreground">{title}</h2>
    </div>
  )
}

// ── Profile Tab ───────────────────────────────────────────────────────────────

function ProfileTab({ profile }: { profile: HealthProfile | null }) {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const setProfileCompleted = useAuthStore((s) => s.setProfileCompleted)
  const profileCompleted = useAuthStore((s) => s.profileCompleted)
  const [editing, setEditing] = useState(!profile)
  const [form, setForm] = useState<Partial<HealthProfile>>(profile ?? {
    full_name: '', age: 0, biological_sex: 'MALE', blood_group: '',
    chronic_conditions: [], known_allergies: [],
  })
  const [condInput, setCondInput] = useState('')
  const [allergyInput, setAllergyInput] = useState('')

  const upsertMutation = useMutation({
    mutationFn: (data: Partial<HealthProfile>) => profileApi.upsertProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      setEditing(false)
      // Mark profile as complete in the auth store so route guards unlock
      if (!profileCompleted) {
        setProfileCompleted(true)
        navigate('/dashboard', { replace: true })
      }
    },
  })

  const handleSave = () => {
    upsertMutation.mutate(form)
  }

  const handleSkip = () => {
    navigate('/dashboard', { replace: true })
  }

  const addTag = (field: 'chronic_conditions' | 'known_allergies', value: string, clear: () => void) => {
    if (!value.trim()) return
    setForm(prev => ({ ...prev, [field]: [...(prev[field] ?? []), value.trim()] }))
    clear()
  }

  const removeTag = (field: 'chronic_conditions' | 'known_allergies', index: number) => {
    setForm(prev => ({ ...prev, [field]: (prev[field] ?? []).filter((_, i) => i !== index) }))
  }

  return (
    <div className="space-y-6">
      <Card>
        <SectionHeader icon="👤" title="Personal Information" />
        {!editing && profile ? (
          <div className="space-y-3">
            <InfoRow label="Full Name" value={profile.full_name} />
            <InfoRow label="Age" value={`${profile.age} years`} />
            <InfoRow label="Biological Sex" value={profile.biological_sex} />
            <InfoRow label="Blood Group" value={profile.blood_group ?? '—'} />
            <Button variant="outline" size="sm" className="mt-4" onClick={() => setEditing(true)}>
              ✏️ Edit Profile
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-1">Full Name</label>
              <Input value={form.full_name ?? ''} onChange={e => setForm(p => ({ ...p, full_name: e.target.value }))} placeholder="Your full name" />
            </div>
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-1">Age</label>
              <Input type="number" value={form.age ?? ''} onChange={e => setForm(p => ({ ...p, age: +e.target.value }))} placeholder="Age in years" />
            </div>
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-1">Biological Sex</label>
              <select
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                value={form.biological_sex ?? 'MALE'}
                onChange={e => setForm(p => ({ ...p, biological_sex: e.target.value as HealthProfile['biological_sex'] }))}
              >
                <option value="MALE">Male</option>
                <option value="FEMALE">Female</option>
                <option value="OTHER">Other / Prefer not to say</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-1">Blood Group</label>
              <select
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                value={form.blood_group ?? ''}
                onChange={e => setForm(p => ({ ...p, blood_group: e.target.value }))}
              >
                <option value="">Unknown</option>
                {['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'].map(bg => (
                  <option key={bg} value={bg}>{bg}</option>
                ))}
              </select>
            </div>
            <div className="flex gap-3 pt-2">
              <Button onClick={handleSave} disabled={upsertMutation.isPending}>
                {upsertMutation.isPending ? 'Saving…' : 'Save Profile'}
              </Button>
              {profile && <Button variant="outline" onClick={() => setEditing(false)}>Cancel</Button>}
              {!profile && (
                <Button
                  variant="outline"
                  onClick={handleSkip}
                  className="text-muted-foreground"
                >
                  Skip for now
                </Button>
              )}
            </div>
          </div>
        )}
      </Card>

      <Card>
        <SectionHeader icon="🏥" title="Medical History" />
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-2">Chronic Conditions</label>
            <div className="flex flex-wrap gap-2 mb-2">
              {(form.chronic_conditions ?? []).map((c, i) => (
                <span key={i} className="inline-flex items-center gap-1 rounded-full bg-primary/10 text-primary px-3 py-1 text-sm">
                  {c}
                  <button onClick={() => removeTag('chronic_conditions', i)} className="hover:text-red-500 font-bold">×</button>
                </span>
              ))}
            </div>
            <div className="flex gap-2">
              <Input
                value={condInput}
                onChange={e => setCondInput(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter') { addTag('chronic_conditions', condInput, () => setCondInput('')) } }}
                placeholder="e.g. Diabetes, Hypertension"
                className="flex-1"
              />
              <Button variant="outline" size="sm" onClick={() => addTag('chronic_conditions', condInput, () => setCondInput(''))}>Add</Button>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-2">Known Allergies</label>
            <div className="flex flex-wrap gap-2 mb-2">
              {(form.known_allergies ?? []).map((a, i) => (
                <span key={i} className="inline-flex items-center gap-1 rounded-full bg-urgency-emergency/10 text-urgency-emergency px-3 py-1 text-sm">
                  {a}
                  <button onClick={() => removeTag('known_allergies', i)} className="hover:opacity-70 font-bold">×</button>
                </span>
              ))}
            </div>
            <div className="flex gap-2">
              <Input
                value={allergyInput}
                onChange={e => setAllergyInput(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter') { addTag('known_allergies', allergyInput, () => setAllergyInput('')) } }}
                placeholder="e.g. Penicillin, Peanuts"
                className="flex-1"
              />
              <Button variant="outline" size="sm" onClick={() => addTag('known_allergies', allergyInput, () => setAllergyInput(''))}>Add</Button>
            </div>
          </div>
          {(form.chronic_conditions?.length ?? 0) + (form.known_allergies?.length ?? 0) > 0 && (
            <Button onClick={handleSave} disabled={upsertMutation.isPending}>
              {upsertMutation.isPending ? 'Saving…' : '💾 Save Medical History'}
            </Button>
          )}
        </div>
      </Card>
    </div>
  )
}

// ── History Tab ───────────────────────────────────────────────────────────────

function HistoryTab() {
  const { data, isLoading } = useQuery({
    queryKey: ['assessmentHistory'],
    queryFn: () => import('@/services/api').then(m => m.assessmentApi.getHistory()),
  })
  const sessions = data?.data?.items ?? []



  if (isLoading) return <PageLoader />

  if (!sessions.length) {
    return (
      <Card className="text-center py-12">
        <p className="text-4xl mb-4">📋</p>
        <p className="text-lg font-medium text-foreground">No assessments yet</p>
        <p className="text-muted-foreground mt-2">Your completed triage sessions will appear here.</p>
      </Card>
    )
  }

  return (
    <div className="space-y-3">
      {sessions.map((s) => (
        <Card key={s.id} hover className="flex items-center justify-between gap-4">
          <div>
            <p className="font-medium text-foreground">{new Date(s.created_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })}</p>
            <p className="text-sm text-muted-foreground capitalize">{s.status.toLowerCase()}</p>
          </div>
          <span className="text-xs font-medium px-3 py-1 rounded-full border bg-muted/50 text-muted-foreground capitalize">
            {s.consultation_mode?.toLowerCase() ?? 'text'}
          </span>
        </Card>
      ))}
    </div>
  )
}

// ── Emergency Contacts Tab ────────────────────────────────────────────────────

const RELATIONSHIP_TYPES = ['SPOUSE', 'PARENT', 'CHILD', 'SIBLING', 'FRIEND', 'COLLEAGUE', 'HEALTHCARE_PROVIDER', 'OTHER']

function ContactsTab({ contacts }: { contacts: EmergencyContact[] }) {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState<EmergencyContactRequest>({
    contact_name: '', phone_number: '', relationship_type: 'OTHER', is_primary: false,
  })

  const addMutation = useMutation({
    mutationFn: (data: EmergencyContactRequest) => profileApi.addEmergencyContact(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      setShowForm(false)
      setForm({ contact_name: '', phone_number: '', relationship_type: 'OTHER', is_primary: false })
    },
  })

  return (
    <div className="space-y-4">
      {!contacts.length && !showForm && (
        <Card className="text-center py-8">
          <p className="text-4xl mb-3">🆘</p>
          <p className="text-lg font-medium text-foreground">No emergency contacts</p>
          <p className="text-muted-foreground mt-1 mb-4">Add people who should be contacted in an emergency.</p>
        </Card>
      )}

      {contacts.map((c) => (
        <Card key={c.id} className="flex items-start justify-between gap-4">
          <div className="flex gap-3">
            <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center text-lg flex-shrink-0">
              {c.relationship_type === 'HEALTHCARE_PROVIDER' ? '👨‍⚕️' : '👤'}
            </div>
            <div>
              <p className="font-semibold text-foreground">{c.contact_name}</p>
              <p className="text-sm text-muted-foreground">{c.phone_number}</p>
              <p className="text-xs text-muted-foreground capitalize mt-0.5">{c.relationship_type.replace('_', ' ')}</p>
            </div>
          </div>
          {c.is_primary && (
            <span className="text-xs font-semibold bg-primary/10 text-primary px-2 py-1 rounded-full flex-shrink-0">Primary</span>
          )}
        </Card>
      ))}

      <AnimatePresence>
        {showForm && (
          <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
            <Card className="border-2 border-primary/20">
              <SectionHeader icon="➕" title="New Contact" />
              <div className="space-y-3">
                <Input value={form.contact_name} onChange={e => setForm(p => ({ ...p, contact_name: e.target.value }))} placeholder="Full Name" />
                <Input value={form.phone_number} onChange={e => setForm(p => ({ ...p, phone_number: e.target.value }))} placeholder="Phone Number (e.g. +233201234567)" type="tel" />
                <select
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                  value={form.relationship_type}
                  onChange={e => setForm(p => ({ ...p, relationship_type: e.target.value }))}
                >
                  {RELATIONSHIP_TYPES.map(r => <option key={r} value={r}>{r.replace('_', ' ')}</option>)}
                </select>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" checked={form.is_primary} onChange={e => setForm(p => ({ ...p, is_primary: e.target.checked }))} className="rounded" />
                  <span className="text-sm text-foreground">Set as primary contact</span>
                </label>
                 <div className="flex gap-3 pt-2">
                  <Button onClick={() => addMutation.mutate(form)} disabled={addMutation.isPending || !form.contact_name || !form.phone_number}>
                    {addMutation.isPending ? 'Saving…' : 'Save Contact'}
                  </Button>
                  <Button variant="outline" onClick={() => setShowForm(false)}>Cancel</Button>
                </div>
              </div>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {!showForm && (
        <Button variant="outline" className="w-full border-dashed" onClick={() => setShowForm(true)}>
          + Add Emergency Contact
        </Button>
      )}
    </div>
  )
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-border last:border-0">
      <span className="text-sm text-muted-foreground">{label}</span>
      <span className="text-sm font-medium text-foreground">{value}</span>
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────

import { GuestBlock } from '@/components/common/GuestBlock'
import { authApi } from '@/services/api'

export default function ProfilePage() {
  const [activeTab, setActiveTab] = useState<Tab>('profile')
  const { isOnline } = useNetworkStore()
  const { userRole, profileCompleted } = useAuthStore()

  // Fetch registered user auth details
  const { data: authData, isLoading: authLoading } = useQuery({
    queryKey: ['authProfile'],
    queryFn: () => authApi.getProfile(),
    staleTime: 30_000,
    enabled: userRole !== 'GUEST',
  })

  // Fetch health profile details
  const { data, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: async () => {
      try {
        return await profileApi.getProfile()
      } catch (err: any) {
        if (err?.response?.status === 404) return null
        throw err
      }
    },
    retry: false,
    staleTime: 30_000,
    enabled: userRole !== 'GUEST' && profileCompleted,
  })

  if (userRole === 'GUEST') {
    return <GuestBlock featureName="Profile" icon="👤" />
  }

  if (isLoading || authLoading) return <PageLoader />

  const authUser = authData?.data ?? null
  const profile = data?.data ?? null
  const contacts = profile?.emergency_contacts ?? []

  // Merged profile for prefilling
  const displayProfile = profile || (authUser ? {
    id: authUser.id,
    full_name: authUser.full_name,
    age: undefined,
    biological_sex: 'MALE',
    blood_group: '',
    chronic_conditions: [],
    known_allergies: [],
    emergency_contacts: [],
  } as any : null)

  return (
    <div className="mx-auto max-w-2xl px-4 pt-4 sm:pt-8 pb-24">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">My Profile</h1>
          <p className="text-xs text-muted-foreground mt-1">
            {profile ? 'Manage your medical profile' : 'Set up your health profile'}
          </p>
        </div>
        <div className={`flex items-center gap-1.5 text-[10px] font-medium px-2 py-1 rounded-full ${isOnline ? 'bg-green-500/10 text-green-600' : 'bg-yellow-500/10 text-yellow-600'}`}>
          <div className={`h-1.5 w-1.5 rounded-full ${isOnline ? 'bg-green-500' : 'bg-yellow-500'}`} />
          {isOnline ? 'Online' : 'Offline'}
        </div>
      </div>

      {/* Registered credentials overview */}
      {authUser && (
        <Card className="mb-4 bg-muted/40 p-3" padding="none">
          <div className="flex flex-col gap-1.5 text-xs px-1">
            <div className="flex justify-between py-1 border-b border-border/40">
              <span className="text-muted-foreground">Full Name</span>
              <span className="font-semibold text-foreground">{authUser.full_name}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-border/40">
              <span className="text-muted-foreground">Registered Phone</span>
              <span className="font-mono text-foreground">{authUser.phone_number}</span>
            </div>
            {authUser.email && (
              <div className="flex justify-between py-1">
                <span className="text-muted-foreground">Registered Email</span>
                <span className="font-mono text-foreground">{authUser.email}</span>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Avatar */}
      <div className="flex justify-center mb-6">
        <div className="relative">
          <div className="h-16 w-16 rounded-full bg-gradient-to-br from-primary to-primary/50 flex items-center justify-center text-2xl text-white shadow-md">
            {authUser?.full_name?.[0]?.toUpperCase() ?? '?'}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-accent/30 rounded-xl p-1 mb-6">
        {TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 flex flex-col items-center gap-0.5 py-2 px-1 rounded-lg text-xs font-medium transition-all ${
              activeTab === tab.id
                ? 'bg-background text-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <span>{tab.icon}</span>
            <span className="hidden sm:block">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.15 }}
        >
          {activeTab === 'profile' && <ProfileTab profile={displayProfile} />}
          {activeTab === 'history' && <HistoryTab />}
          {activeTab === 'contacts' && <ContactsTab contacts={contacts} />}
        </motion.div>
      </AnimatePresence>
    </div>
  )
}
