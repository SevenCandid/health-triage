// Global shared TypeScript types for the Health Triage Assistant frontend.

// Backend uses RED/ORANGE/YELLOW/GREEN; frontend legacy used EMERGENCY/HIGH/MEDIUM/LOW
export type UrgencyLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'EMERGENCY' | 'GREEN' | 'YELLOW' | 'ORANGE' | 'RED'

export interface UrgencyColor {
  bg: string
  text: string
  border: string
  badge: string
}

export const URGENCY_STYLES: Record<string, UrgencyColor> = {
  // Backend codes
  RED: {
    bg: 'bg-urgency-emergency',
    text: 'text-urgency-emergency',
    border: 'border-urgency-emergency',
    badge: 'bg-urgency-emergency text-white',
  },
  ORANGE: {
    bg: 'bg-urgency-urgent',
    text: 'text-urgency-urgent',
    border: 'border-urgency-urgent',
    badge: 'bg-urgency-urgent text-white',
  },
  YELLOW: {
    bg: 'bg-urgency-elevated',
    text: 'text-urgency-elevated',
    border: 'border-urgency-elevated',
    badge: 'bg-urgency-elevated text-white',
  },
  GREEN: {
    bg: 'bg-urgency-routine',
    text: 'text-urgency-routine',
    border: 'border-urgency-routine',
    badge: 'bg-urgency-routine text-white',
  },
  // Legacy frontend aliases
  EMERGENCY: {
    bg: 'bg-urgency-emergency',
    text: 'text-urgency-emergency',
    border: 'border-urgency-emergency',
    badge: 'bg-urgency-emergency text-white',
  },
  HIGH: {
    bg: 'bg-urgency-urgent',
    text: 'text-urgency-urgent',
    border: 'border-urgency-urgent',
    badge: 'bg-urgency-urgent text-white',
  },
  MEDIUM: {
    bg: 'bg-urgency-elevated',
    text: 'text-urgency-elevated',
    border: 'border-urgency-elevated',
    badge: 'bg-urgency-elevated text-white',
  },
  LOW: {
    bg: 'bg-urgency-routine',
    text: 'text-urgency-routine',
    border: 'border-urgency-routine',
    badge: 'bg-urgency-routine text-white',
  },
}

// ── API Response Types ────────────────────────────────────────────────────────

export interface ApiErrorResponse {
  detail: string
  type?: string
  status?: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// ── Auth Types ────────────────────────────────────────────────────────────────

export interface AuthTokenResponse {
  access_token: string
  refresh_token: string
  token_type: 'bearer'
  expires_in_minutes: number
}

export interface UserProfile {
  id: string
  phone_number: string
  email?: string
  role: 'PATIENT' | 'HEALTH_WORKER' | 'ADMIN'
  full_name: string
  age?: number
  biological_sex?: 'MALE' | 'FEMALE' | 'OTHER' | 'PREFER_NOT_TO_SAY'
  blood_group?: string
  preferred_language_code: string
  profile_completed: boolean
}

export interface AuthResponse extends AuthTokenResponse {
  user: Omit<UserProfile, 'role'>
}

export interface EmergencyContact {
  id: string
  contact_name: string
  phone_number: string
  relationship_type: string
  is_primary: boolean
  notes?: string
}

export interface EmergencyContactRequest {
  id?: string
  contact_name: string
  phone_number: string
  relationship_type: string
  is_primary: boolean
}

export interface HealthProfile {
  id?: string
  user_id?: string
  full_name: string
  age: number
  biological_sex: 'MALE' | 'FEMALE' | 'OTHER'
  blood_group?: string
  chronic_conditions: string[]
  known_allergies: string[]
  updated_at?: string
  emergency_contacts?: EmergencyContact[]
}

// ── Assessment Types ──────────────────────────────────────────────────────────

export interface AssessmentSession {
  id: string
  title?: string
  status: 'ACTIVE' | 'COMPLETED' | 'ARCHIVED' | 'SYNCED'
  severity_level_id?: string | null
  severity_code?: string | null
  consultation_mode?: string | null
  created_at: string
}

export interface QuestionOption {
  id: string
  option_value: string
  label_en: string
  label_tw?: string
}

export interface FollowUpQuestion {
  id: string
  node_id: string
  question_text_en: string
  question_text_tw?: string
  question_type: string
  options?: QuestionOption[]
}

export interface AssessmentResult {
  session_id: string
  severity: UrgencyLevel
  recommendations: string[]
  explanation: string
  is_emergency: boolean
  conducted_at: string
  symptom_name?: string | null
  raw_answers?: Record<string, string> | null
}

export interface StartAssessmentResponse {
  session_id: string
  status: string
  language_code: string
  consultation_mode: string
  created_at: string
  pending_symptom?: string | null
  pending_symptom_slug?: string | null
  pending_session_id?: string | null
}

export interface SymptomsSubmitResponse {
  session_id: string
  symptom_slug: string
  next_question: FollowUpQuestion | null
  is_completed: boolean
  is_emergency: boolean
  severity?: UrgencyLevel
}

export interface AnswerSubmitResponse {
  session_id: string
  is_completed: boolean
  next_question: FollowUpQuestion | null
  result?: AssessmentResult
}

// ── Navigation Types ──────────────────────────────────────────────────────────

export interface NavItem {
  label: string
  to: string
  icon?: React.ComponentType<{ className?: string }>
  requiresAuth?: boolean
}
