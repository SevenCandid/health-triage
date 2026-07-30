import { useSettingsStore, type AppLanguage } from '@/stores/settings-store'
import { Globe } from 'lucide-react'

export function LanguageSwitcher() {
  const { appLanguage, setLanguage } = useSettingsStore()

  const languages: { code: AppLanguage; label: string }[] = [
    { code: 'en', label: 'English' },
    { code: 'tw', label: 'Twi' }
  ]

  return (
    <div className="flex items-center space-x-2 bg-white/50 dark:bg-gray-800/50 px-3 py-1.5 rounded-full border border-gray-200 dark:border-gray-700 shadow-sm backdrop-blur-md">
      <Globe className="w-4 h-4 text-gray-500 dark:text-gray-400" />
      <select
        value={appLanguage}
        onChange={(e) => setLanguage(e.target.value as AppLanguage)}
        className="bg-transparent text-sm font-medium focus:outline-none cursor-pointer appearance-none outline-none text-gray-700 dark:text-gray-200"
      >
        {languages.map((l) => (
          <option key={l.code} value={l.code} className="text-gray-900 bg-white dark:bg-gray-900 dark:text-white">
            {l.label}
          </option>
        ))}
      </select>
    </div>
  )
}
