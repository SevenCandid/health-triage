import React from 'react'
import { CheckCircle2, Check, Mic, Settings, Accessibility, Info, AlertTriangle } from 'lucide-react'
import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { useSettingsStore } from '@/stores/settings-store'
import { useNetworkStore } from '@/stores/network-store'
import { Card } from '@/components/ui/Card'
import type { AppLanguage, FontSize } from '@/stores/settings-store'

// ── Helpers ───────────────────────────────────────────────────────────────────

function SettingsSection({ icon, title, children }: { icon: React.ReactNode | string; title: string; children: React.ReactNode }) {
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }}>
      <Card className="overflow-hidden" padding="none">
        <div className="flex items-center gap-3 px-5 py-4 border-b border-border bg-accent/20">
          <span className="text-xl">{icon}</span>
          <h2 className="font-semibold text-foreground">{title}</h2>
        </div>
        <div className="divide-y divide-border">
          {children}
        </div>
      </Card>
    </motion.div>
  )
}

function SettingsRow({ label, description, children }: { label: string; description?: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-4 px-5 py-4">
      <div>
        <p className="text-sm font-medium text-foreground">{label}</p>
        {description && <p className="text-xs text-muted-foreground mt-0.5">{description}</p>}
      </div>
      <div className="flex-shrink-0">{children}</div>
    </div>
  )
}

function Toggle({ value, onChange }: { value: boolean; onChange: (v: boolean) => void }) {
  return (
    <button
      role="switch"
      aria-checked={value}
      onClick={() => onChange(!value)}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
        value ? 'bg-primary' : 'bg-muted-foreground/30'
      }`}
    >
      <span className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${value ? 'translate-x-6' : 'translate-x-1'}`} />
    </button>
  )
}

// ── Language ──────────────────────────────────────────────────────────────────

const LANGUAGES: { code: AppLanguage; label: string; native: string; flag: string }[] = [
  { code: 'en', label: 'English', native: 'English', flag: '🇬🇧' },
  { code: 'tw', label: 'Twi (Akan)', native: 'Twi', flag: '🇬🇭' },
  { code: 'fr', label: 'French', native: 'Français', flag: '🇫🇷' },
  { code: 'ar', label: 'Arabic', native: 'العربية', flag: '🇸🇦' },
  { code: 'pt', label: 'Portuguese', native: 'Português', flag: '🇵🇹' },
]

function LanguageSelector() {
  const { appLanguage, setLanguage } = useSettingsStore()
  return (
    <div className="grid grid-cols-1 gap-2 p-4">
      {LANGUAGES.map(lang => (
        <button
          key={lang.code}
          onClick={() => setLanguage(lang.code)}
          className={`flex items-center gap-3 rounded-lg px-4 py-3 text-left transition-all border ${
            appLanguage === lang.code
              ? 'border-primary bg-primary/10 text-primary font-medium'
              : 'border-border bg-background text-foreground hover:bg-accent'
          }`}
        >
          <span className="text-xl">{lang.flag}</span>
          <div>
            <p className="text-sm font-medium">{lang.label}</p>
            {lang.native !== lang.label && <p className="text-xs opacity-70">{lang.native}</p>}
          </div>
          {appLanguage === lang.code && <span className="ml-auto"><Check className="w-4 h-4" /></span>}
        </button>
      ))}
    </div>
  )
}

// ── Accessibility ─────────────────────────────────────────────────────────────

const FONT_SIZES: { value: FontSize; label: string; desc: string }[] = [
  { value: 'normal', label: 'Normal', desc: 'Standard text size' },
  { value: 'large', label: 'Large', desc: '125% text scaling' },
  { value: 'xl', label: 'Extra Large', desc: '150% text scaling' },
]

function FontSizeSelector() {
  const { fontSize, setFontSize } = useSettingsStore()
  return (
    <div className="flex gap-2 p-4">
      {FONT_SIZES.map(s => (
        <button
          key={s.value}
          onClick={() => setFontSize(s.value)}
          className={`flex-1 rounded-lg border py-3 px-2 text-center transition-all ${
            fontSize === s.value
              ? 'border-primary bg-primary/10 text-primary font-semibold'
              : 'border-border bg-background text-muted-foreground hover:bg-accent'
          }`}
        >
          <p className="text-sm font-medium">{s.label}</p>
          <p className="text-xs mt-0.5 opacity-70">{s.desc}</p>
        </button>
      ))}
    </div>
  )
}

// ── Voice ─────────────────────────────────────────────────────────────────────

function VoiceSettings() {
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([])
  const { 
    preferredVoiceURI, setVoice,
    voiceRate, setVoiceRate,
    voicePitch, setVoicePitch,
    voiceVolume, setVoiceVolume,
    autoReadResponses, setAutoReadResponses,
    handsFreeMode, setHandsFreeMode,
    appLanguage
  } = useSettingsStore()

  useEffect(() => {
    const load = () => {
      const all = window.speechSynthesis.getVoices()
      // Filter voices based on appLanguage. If tw, there might not be any, so fallback to all or en.
      let filtered = all.filter(v => v.lang.toLowerCase().startsWith(appLanguage))
      if (filtered.length === 0 && appLanguage !== 'en') {
        // Fallback to English if no voices for selected language
        filtered = all.filter(v => v.lang.toLowerCase().startsWith('en'))
      }
      if (filtered.length === 0) {
         filtered = all // Ultimate fallback
      }
      setVoices(filtered)
    }
    load()
    window.speechSynthesis.onvoiceschanged = load
    return () => { window.speechSynthesis.onvoiceschanged = null }
  }, [appLanguage])

  const testVoice = () => {
    window.speechSynthesis.cancel()
    const u = new SpeechSynthesisUtterance("Hi! I'm FirstAid+.")
    u.rate = voiceRate
    u.pitch = voicePitch
    u.volume = voiceVolume
    if (preferredVoiceURI) {
      const v = voices.find(v => v.voiceURI === preferredVoiceURI)
      if (v) u.voice = v
    }
    window.speechSynthesis.speak(u)
  }

  return (
    <>
      <SettingsRow label="Assistant Voice" description="Voice used during hands-free triage sessions">
        <select
          className="w-44 rounded-md border border-input bg-background px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          value={preferredVoiceURI ?? ''}
          onChange={e => setVoice(e.target.value)}
        >
          <option value="">Device Default</option>
          {voices.map(v => (
            <option key={v.voiceURI} value={v.voiceURI}>{v.name.slice(0, 22)}</option>
          ))}
        </select>
      </SettingsRow>
      <div className="px-5 py-3 border-b border-border/50">
         <div className="flex justify-between text-sm font-medium mb-2">
            <span>Speech Rate</span>
            <span className="text-muted-foreground">{voiceRate.toFixed(1)}x</span>
         </div>
         <input type="range" min="0.5" max="2.0" step="0.1" value={voiceRate} onChange={e => setVoiceRate(parseFloat(e.target.value))} className="w-full accent-primary" />
      </div>
      <div className="px-5 py-3 border-b border-border/50">
         <div className="flex justify-between text-sm font-medium mb-2">
            <span>Pitch</span>
            <span className="text-muted-foreground">{voicePitch.toFixed(1)}</span>
         </div>
         <input type="range" min="0.0" max="2.0" step="0.1" value={voicePitch} onChange={e => setVoicePitch(parseFloat(e.target.value))} className="w-full accent-primary" />
      </div>
      <div className="px-5 py-3 border-b border-border/50">
         <div className="flex justify-between text-sm font-medium mb-2">
            <span>Volume</span>
            <span className="text-muted-foreground">{Math.round(voiceVolume * 100)}%</span>
         </div>
         <input type="range" min="0.0" max="1.0" step="0.1" value={voiceVolume} onChange={e => setVoiceVolume(parseFloat(e.target.value))} className="w-full accent-primary" />
      </div>
      <SettingsRow label="Auto Read Responses" description="Automatically speak assistant replies">
         <Toggle value={autoReadResponses} onChange={setAutoReadResponses} />
      </SettingsRow>
      <SettingsRow label="Hands-Free Mode" description="Automatically start listening after speaking">
         <Toggle value={handsFreeMode} onChange={setHandsFreeMode} />
      </SettingsRow>
      <SettingsRow label="Test Voice" description="Hear how the assistant will sound">
        <button onClick={testVoice} className="text-sm text-primary font-medium hover:underline">
          🔊 Play
        </button>
      </SettingsRow>
    </>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────

import { useAuthStore } from '@/stores/auth-store'
import { GuestBlock } from '@/components/common/GuestBlock'

export default function SettingsPage() {
  const { userRole } = useAuthStore()

  const {
    highContrast, setHighContrast,
    reduceMotion, setReduceMotion,
    notificationsEnabled, setNotificationsEnabled,
    notifyEmergencyAlerts, setNotifyEmergencyAlerts,
    notifyAssessmentReminders, setNotifyAssessmentReminders,
    offlineModeEnabled, setOfflineModeEnabled,
  } = useSettingsStore()

  const { isOnline } = useNetworkStore()

  if (userRole === 'GUEST') {
    return <GuestBlock featureName="Settings" icon=<Settings className="w-4 h-4" /> />
  }

  return (
    <div className="mx-auto max-w-2xl px-4 pt-4 sm:pt-8 pb-24 space-y-6">

      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <h1 className="text-3xl font-bold text-foreground">Settings</h1>
        <div className={`flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full ${isOnline ? 'bg-green-500/10 text-green-600' : 'bg-yellow-500/10 text-yellow-600'}`}>
          <div className={`h-2 w-2 rounded-full animate-pulse ${isOnline ? 'bg-green-500' : 'bg-yellow-500'}`} />
          {isOnline ? 'Online' : 'Offline'}
        </div>
      </div>

      {/* Language */}
      <SettingsSection icon="🌍" title="Preferred Language">
        <LanguageSelector />
      </SettingsSection>

      {/* Voice */}
      <SettingsSection icon=<Mic className="w-4 h-4" /> title="Voice Consultation">
        <VoiceSettings />
      </SettingsSection>

      {/* Accessibility */}
      <SettingsSection icon=<Accessibility className="w-4 h-4" /> title="Accessibility">
        <div className="p-4 border-b border-border">
          <p className="text-sm font-medium text-foreground mb-3">Text Size</p>
          <FontSizeSelector />
        </div>
        <SettingsRow label="High Contrast Mode" description="Increases colour contrast for better readability">
          <Toggle value={highContrast} onChange={setHighContrast} />
        </SettingsRow>
        <SettingsRow label="Reduce Motion" description="Minimises animations and transitions">
          <Toggle value={reduceMotion} onChange={setReduceMotion} />
        </SettingsRow>
      </SettingsSection>

      {/* Offline Mode */}
      <SettingsSection icon="📡" title="Offline Mode">
        <SettingsRow
          label="Enable Offline Mode"
          description="Cache assessments and data for use without internet"
        >
          <Toggle value={offlineModeEnabled} onChange={setOfflineModeEnabled} />
        </SettingsRow>
        <SettingsRow label="Current Status" description="Live network connectivity">
          <span className={`text-sm font-semibold flex items-center gap-1.5 ${isOnline ? 'text-green-600' : 'text-yellow-600'}`}>
            {isOnline ? <><CheckCircle2 className="w-4 h-4" /> Connected</> : <><AlertTriangle className="w-4 h-4" /> Offline</>}
          </span>
        </SettingsRow>
      </SettingsSection>

      {/* Notifications */}
      <SettingsSection icon="🔔" title="Notifications">
        <SettingsRow label="Enable Notifications" description="Allow the app to send you alerts">
          <Toggle value={notificationsEnabled} onChange={setNotificationsEnabled} />
        </SettingsRow>
        <SettingsRow label="Emergency Alerts" description="Critical urgency triage results">
          <Toggle value={notifyEmergencyAlerts} onChange={v => notificationsEnabled && setNotifyEmergencyAlerts(v)} />
        </SettingsRow>
        <SettingsRow label="Assessment Reminders" description="Reminders to complete unfinished assessments">
          <Toggle value={notifyAssessmentReminders} onChange={v => notificationsEnabled && setNotifyAssessmentReminders(v)} />
        </SettingsRow>
      </SettingsSection>

      {/* About */}
      <SettingsSection icon=<Info className="w-4 h-4" /> title="About">
        <SettingsRow label="App Version" description="FirstAid+">
          <span className="text-sm text-muted-foreground">v1.0.0</span>
        </SettingsRow>
        <SettingsRow label="Backend Status" description="API server connectivity">
          <span className={`text-sm font-medium ${isOnline ? 'text-green-600' : 'text-muted-foreground'}`}>
            {isOnline ? 'Reachable' : 'Unreachable'}
          </span>
        </SettingsRow>
      </SettingsSection>

    </div>
  )
}
