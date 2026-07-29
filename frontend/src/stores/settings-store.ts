import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type AppLanguage = 'en' | 'tw' | 'fr' | 'ar' | 'pt'
export type FontSize = 'normal' | 'large' | 'xl'
export type ColorScheme = 'system' | 'light' | 'dark'

export interface AppSettings {
  // Voice
  preferredVoiceURI: string | null
  voiceRate: number
  voicePitch: number
  voiceVolume: number
  autoReadResponses: boolean
  handsFreeMode: boolean
  // Language
  appLanguage: AppLanguage
  // Accessibility
  fontSize: FontSize
  highContrast: boolean
  reduceMotion: boolean
  // Notifications
  notificationsEnabled: boolean
  notifyEmergencyAlerts: boolean
  notifyAssessmentReminders: boolean
  // Offline
  offlineModeEnabled: boolean
}

interface SettingsActions {
  setVoice: (uri: string) => void
  setVoiceRate: (rate: number) => void
  setVoicePitch: (pitch: number) => void
  setVoiceVolume: (volume: number) => void
  setAutoReadResponses: (v: boolean) => void
  setHandsFreeMode: (v: boolean) => void
  setLanguage: (lang: AppLanguage) => void
  setFontSize: (size: FontSize) => void
  setHighContrast: (v: boolean) => void
  setReduceMotion: (v: boolean) => void
  setNotificationsEnabled: (v: boolean) => void
  setNotifyEmergencyAlerts: (v: boolean) => void
  setNotifyAssessmentReminders: (v: boolean) => void
  setOfflineModeEnabled: (v: boolean) => void
}

const defaults: AppSettings = {
  preferredVoiceURI: null,
  voiceRate: 1.0,
  voicePitch: 1.0,
  voiceVolume: 1.0,
  autoReadResponses: true,
  handsFreeMode: true,
  appLanguage: 'en',
  fontSize: 'normal',
  highContrast: false,
  reduceMotion: false,
  notificationsEnabled: true,
  notifyEmergencyAlerts: true,
  notifyAssessmentReminders: false,
  offlineModeEnabled: true,
}

export const useSettingsStore = create<AppSettings & SettingsActions>()(
  persist(
    (set) => ({
      ...defaults,
      setVoice: (uri) => set({ preferredVoiceURI: uri }),
      setVoiceRate: (voiceRate) => set({ voiceRate }),
      setVoicePitch: (voicePitch) => set({ voicePitch }),
      setVoiceVolume: (voiceVolume) => set({ voiceVolume }),
      setAutoReadResponses: (autoReadResponses) => set({ autoReadResponses }),
      setHandsFreeMode: (handsFreeMode) => set({ handsFreeMode }),
      setLanguage: (appLanguage) => set({ appLanguage }),
      setFontSize: (fontSize) => set({ fontSize }),
      setHighContrast: (highContrast) => set({ highContrast }),
      setReduceMotion: (reduceMotion) => set({ reduceMotion }),
      setNotificationsEnabled: (notificationsEnabled) => set({ notificationsEnabled }),
      setNotifyEmergencyAlerts: (notifyEmergencyAlerts) => set({ notifyEmergencyAlerts }),
      setNotifyAssessmentReminders: (notifyAssessmentReminders) => set({ notifyAssessmentReminders }),
      setOfflineModeEnabled: (offlineModeEnabled) => set({ offlineModeEnabled }),
    }),
    { name: 'health-triage-settings' }
  )
)
