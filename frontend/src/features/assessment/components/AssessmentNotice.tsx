import { Card } from '@/components/ui/Card'

export function AssessmentNotice() {
  return (
    <Card className="border-blue-500/20 bg-blue-500/5 p-3 flex gap-2 items-start text-left rounded-lg shadow-sm w-full">
      <span className="text-base shrink-0 mt-0.5">🩺</span>
      <div className="flex-1 min-w-0">
        <p className="text-[11px] sm:text-xs font-bold text-foreground mb-0.5">Health Guidance</p>
        <p className="text-[10px] sm:text-xs text-muted-foreground leading-tight">
          This assessment offers health guidance based on the information you share and is not a medical diagnosis. If your symptoms become severe, worsen, or you are concerned, seek care from a qualified healthcare professional.
        </p>
      </div>
    </Card>
  )
}
