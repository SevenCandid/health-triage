import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { authApi } from '@/services/api'
import { useOnlineStatus } from '@/hooks/use-online-status'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { PageLoader } from '@/components/common/LoadingSpinner'

const DEFAULT_EMERGENCY_NUMBER = '112'

export default function EmergencyPage() {
  const navigate = useNavigate()
  const isOnline = useOnlineStatus()
  const [confirmingEmergency, setConfirmingEmergency] = useState(false)
  const [confirmingContact, setConfirmingContact] = useState<{ name: string; phone: string } | null>(null)

  const { data: contactsData, isLoading } = useQuery({
    queryKey: ['emergencyContacts'],
    queryFn: () => authApi.getEmergencyContacts(),
  })

  const contacts = contactsData?.data || []
  const doctorContact = contacts.find(c => c.relationship_type === 'HEALTHCARE_PROVIDER')
  const primaryContact = contacts.find(c => c.is_primary && c.relationship_type !== 'HEALTHCARE_PROVIDER')
  const generalContact = primaryContact || contacts.find(c => c.relationship_type !== 'HEALTHCARE_PROVIDER')

  const handleCallEmergency = () => {
    window.location.href = `tel:${DEFAULT_EMERGENCY_NUMBER}`
    setConfirmingEmergency(false)
  }

  const handleCallContact = (phone: string) => {
    window.location.href = `tel:${phone}`
    setConfirmingContact(null)
  }

  if (isLoading) return <PageLoader />

  return (
    <div className="mx-auto max-w-md px-3 pt-3 pb-20 space-y-3">

      {/* Header */}
      <div className="flex items-center gap-2">
        <button onClick={() => navigate(-1)} className="text-muted-foreground hover:text-foreground transition-colors p-1 -ml-1">
          ← 
        </button>
        <h1 className="text-base font-bold text-foreground">Emergency Centre</h1>
        {!isOnline && (
          <span className="ml-auto text-[10px] font-medium px-2 py-0.5 rounded-full bg-yellow-500/10 text-yellow-600 border border-yellow-500/20">
            Offline
          </span>
        )}
      </div>

      {!isOnline && (
        <div className="rounded-lg bg-yellow-500/10 border border-yellow-500/30 px-3 py-2 flex gap-2 items-center text-xs text-yellow-700 dark:text-yellow-400">
          <span>⚠️</span>
          <span>Phone calls still work offline via your cellular network.</span>
        </div>
      )}

      {/* Big Emergency Button */}
      <Card className="overflow-hidden border-2 border-red-500/40 p-0">
        <div className="bg-red-500/5 px-4 py-5 flex flex-col items-center text-center gap-3">
          <div className="h-14 w-14 rounded-full bg-red-500/15 flex items-center justify-center">
            <span className="text-3xl leading-none">🚨</span>
          </div>
          <div>
            <p className="text-sm font-bold text-foreground">Emergency Services</p>
            <p className="text-[11px] text-muted-foreground mt-0.5">Tap to call national emergency line</p>
          </div>
          <button
            onClick={() => setConfirmingEmergency(true)}
            className="w-full bg-red-600 hover:bg-red-700 active:scale-[0.98] text-white font-bold text-base rounded-xl py-3.5 transition-all shadow-md shadow-red-500/30"
          >
            CALL {DEFAULT_EMERGENCY_NUMBER}
          </button>
        </div>
      </Card>

      {/* Contact Cards */}
      <div className="grid grid-cols-2 gap-2">

        {/* Doctor */}
        <Card className="flex flex-col gap-3 p-3 border border-primary/20">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-base flex-shrink-0">👨‍⚕️</div>
            <div className="min-w-0">
              <p className="text-xs font-semibold text-foreground">Doctor</p>
              <p className="text-[10px] text-muted-foreground truncate">
                {doctorContact ? doctorContact.contact_name : 'Not saved'}
              </p>
            </div>
          </div>
          {doctorContact ? (
            <button
              onClick={() => setConfirmingContact({ name: doctorContact.contact_name, phone: doctorContact.phone_number })}
              className="w-full bg-primary hover:bg-primary/90 text-primary-foreground text-xs font-semibold rounded-lg py-2 transition-all"
            >
              Call Doctor
            </button>
          ) : (
            <button
              onClick={() => navigate('/profile')}
              className="w-full border border-dashed border-border text-muted-foreground text-xs rounded-lg py-2 hover:bg-accent transition-all"
            >
              + Add Doctor
            </button>
          )}
        </Card>

        {/* Emergency Contact */}
        <Card className="flex flex-col gap-3 p-3 border border-primary/20">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-base flex-shrink-0">👤</div>
            <div className="min-w-0">
              <p className="text-xs font-semibold text-foreground">Contact</p>
              <p className="text-[10px] text-muted-foreground truncate">
                {generalContact ? generalContact.contact_name : 'Not saved'}
              </p>
            </div>
          </div>
          {generalContact ? (
            <button
              onClick={() => setConfirmingContact({ name: generalContact.contact_name, phone: generalContact.phone_number })}
              className="w-full bg-primary hover:bg-primary/90 text-primary-foreground text-xs font-semibold rounded-lg py-2 transition-all"
            >
              Call Contact
            </button>
          ) : (
            <button
              onClick={() => navigate('/profile')}
              className="w-full border border-dashed border-border text-muted-foreground text-xs rounded-lg py-2 hover:bg-accent transition-all"
            >
              + Add Contact
            </button>
          )}
        </Card>
      </div>

      {/* All contacts list */}
      {contacts.length > 0 && (
        <Card className="p-0 overflow-hidden">
          <p className="text-xs font-semibold text-foreground px-3 pt-2.5 pb-2 border-b border-border">All Contacts</p>
          <div className="divide-y divide-border">
            {contacts.map((c) => (
              <div key={c.id} className="flex items-center justify-between gap-2 px-3 py-2.5">
                <div className="min-w-0">
                  <p className="text-xs font-medium text-foreground truncate">{c.contact_name}</p>
                  <p className="text-[10px] text-muted-foreground capitalize">{c.relationship_type?.toLowerCase().replace('_', ' ')}</p>
                </div>
                <button
                  onClick={() => setConfirmingContact({ name: c.contact_name, phone: c.phone_number })}
                  className="shrink-0 text-[10px] font-semibold px-2.5 py-1 rounded-lg bg-primary/10 text-primary hover:bg-primary/20 transition-all"
                >
                  📞 Call
                </button>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Confirmation Modals */}
      <AnimatePresence>
        {confirmingEmergency && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
          >
            <motion.div
              initial={{ y: 40, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: 40, opacity: 0 }}
              className="w-full max-w-sm rounded-2xl bg-background p-5 shadow-2xl border-2 border-red-500/60"
            >
              <div className="text-center space-y-3">
                <span className="text-4xl block">🚨</span>
                <h2 className="text-base font-bold text-foreground">Call Emergency Services?</h2>
                <p className="text-xs text-muted-foreground">
                  Are you sure you want to dial <strong>{DEFAULT_EMERGENCY_NUMBER}</strong> now?
                </p>
                <div className="flex flex-col gap-2 pt-2">
                  <button
                    onClick={handleCallEmergency}
                    className="w-full bg-red-600 hover:bg-red-700 text-white font-bold text-sm rounded-xl py-3 transition-all shadow-md"
                  >
                    Yes, Call Now
                  </button>
                  <Button variant="outline" className="w-full" onClick={() => setConfirmingEmergency(false)}>Cancel</Button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}

        {confirmingContact && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
          >
            <motion.div
              initial={{ y: 40, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: 40, opacity: 0 }}
              className="w-full max-w-sm rounded-2xl bg-background p-5 shadow-2xl border border-border"
            >
              <div className="text-center space-y-3">
                <span className="text-3xl block">📞</span>
                <h2 className="text-base font-bold text-foreground">Call {confirmingContact.name}?</h2>
                <p className="text-xs text-muted-foreground font-mono">{confirmingContact.phone}</p>
                <div className="flex flex-col gap-2 pt-2">
                  <Button className="w-full" onClick={() => handleCallContact(confirmingContact.phone)}>
                    Yes, Call Now
                  </Button>
                  <Button variant="outline" className="w-full" onClick={() => setConfirmingContact(null)}>Cancel</Button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
