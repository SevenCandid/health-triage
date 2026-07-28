import { Card } from '@/components/ui/Card'

export function AssessmentNotice() {
  return (
    <Card className="border-blue-500/20 bg-blue-500/5 p-4 flex gap-3 items-start text-left rounded-2xl shadow-sm">
      <span className="text-xl">🩺</span>
      <div>
        <p className="text-xs font-bold text-foreground mb-1">Health Guidance</p>
        <p className="text-xs text-muted-foreground leading-relaxed">
          This assessment offers health guidance based on the information you share and is not a medical diagnosis. If your symptoms become severe, worsen, or you are concerned, seek care from a qualified healthcare professional.
        </p>
      </div>
    </Card>
  )
}
