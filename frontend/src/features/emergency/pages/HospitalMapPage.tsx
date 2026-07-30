import { useNavigate } from 'react-router-dom'
import { ArrowLeft, MapPin } from 'lucide-react'

export default function HospitalMapPage() {
  const navigate = useNavigate()

  return (
    <div className="flex flex-col h-[calc(100vh-64px)] w-full max-w-md mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-3 border-b border-border bg-background z-10 shrink-0 shadow-sm">
        <button
          onClick={() => navigate(-1)}
          className="p-1.5 -ml-1.5 rounded-full hover:bg-accent text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-blue-500/10 text-blue-600">
            <MapPin className="w-4 h-4" />
          </div>
          <h1 className="text-sm font-bold text-foreground">Nearby Hospitals</h1>
        </div>
      </div>

      {/* Map iframe */}
      <div className="flex-1 w-full bg-muted/20 relative">
        <iframe
          title="Hospitals Near Me"
          src="https://maps.google.com/maps?q=hospital+near+me&output=embed"
          width="100%"
          height="100%"
          style={{ border: 0 }}
          allowFullScreen
          loading="lazy"
          referrerPolicy="no-referrer-when-downgrade"
          className="absolute inset-0 w-full h-full"
        />
      </div>
    </div>
  )
}
