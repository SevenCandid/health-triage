import { useSettingsStore } from '@/stores/settings-store'
import en from '../locales/en.json'
import tw from '../locales/tw.json'

const translations: Record<string, any> = { en, tw }

export function useTranslation() {
  const { appLanguage } = useSettingsStore()

  const t = (key: string) => {
    const keys = key.split('.')
    let current = translations[appLanguage] || translations['en']
    
    for (const k of keys) {
      if (current[k] === undefined) {
         // Fallback to english
         let fallback = translations['en']
         for (const fk of keys) {
             if (fallback[fk] === undefined) return key
             fallback = fallback[fk]
         }
         return fallback as string
      }
      current = current[k]
    }
    return current as string
  }

  return { t, language: appLanguage }
}
