import { apiClient } from '@/lib/axios'
import type {
  UserProfile,
  StartAssessmentResponse,
  SymptomsSubmitResponse,
  AnswerSubmitResponse,
  AssessmentResult,
  AssessmentSession,
  PaginatedResponse,
  EmergencyContact,
  HealthProfile,
  EmergencyContactRequest,
  AuthResponse,
} from '@/types'

// ── Auth API ──────────────────────────────────────────────────────────────────

export const authApi = {
  login: (data: { identifier: string; password: string }) =>
    apiClient.post<AuthResponse>('/auth/login', data),

  register: (data: {
    full_name: string
    phone_number: string
    email?: string
    password: string
    preferred_language: string
  }) => apiClient.post<AuthResponse>('/auth/register', data),

  refreshToken: (data: { refresh_token: string }) =>
    apiClient.post<AuthResponse>('/auth/refresh', data),
    
  logout: () => apiClient.post('/auth/logout'),

  getProfile: () => apiClient.get<UserProfile>('/auth/me'),

  updateProfile: (data: Partial<UserProfile>) =>
    apiClient.put<UserProfile>('/auth/me', data),

  getEmergencyContacts: () =>
    apiClient.get<EmergencyContact[]>('/users/me/emergency-contacts'),
}

// ── Profile API ───────────────────────────────────────────────────────────────

export const profileApi = {
  getProfile: () =>
    apiClient.get<HealthProfile>('/users/me/profile'),

  upsertProfile: (data: Partial<HealthProfile>) =>
    apiClient.put<HealthProfile>('/users/me/profile', data),

  getEmergencyContacts: () =>
    apiClient.get<EmergencyContact[]>('/users/me/emergency-contacts'),

  addEmergencyContact: (data: EmergencyContactRequest) =>
    apiClient.post<EmergencyContact>('/users/me/emergency-contacts', data),
}

// ── Assessment API ────────────────────────────────────────────────────────────

export const assessmentApi = {
  start: (mode: 'TEXT' | 'VOICE' = 'TEXT') =>
    apiClient.post<StartAssessmentResponse>('/assessment/start', {
      language_code: 'en',
      consultation_mode: mode,
      created_offline: false,
    }),

  submitSymptoms: (sessionId: string, symptoms: string[], userText?: string) => {
    const slug = symptoms[0] ? symptoms[0].toLowerCase().replace(/\s+/g, '-') : 'unknown';
    return apiClient.post<SymptomsSubmitResponse>('/assessment/symptoms', {
      session_id: sessionId,
      symptom_slug: slug,
      user_text: userText || symptoms[0],
    });
  },

  submitAnswer: (sessionId: string, questionId: string, answer: string | string[]) =>
    apiClient.post<AnswerSubmitResponse>('/assessment/answer', {
      session_id: sessionId,
      node_id: questionId,
      answer_value: Array.isArray(answer) ? answer.join(',') : answer,
    }),

  resolveSession: (sessionId: string) =>
    apiClient.post(`/assessment/${sessionId}/resolve`),

  getConversationTranscript: (sessionId: string) =>
    apiClient.get<{
      session_id: string
      status: string
      symptom_name: string | null
      symptom_slug: string | null
      messages: { role: 'USER' | 'SYSTEM'; content: string }[]
    }>(`/assessment/${sessionId}/conversation`),

  getSession: (sessionId: string) =>
    apiClient.get<AssessmentSession>(`/assessment/${sessionId}`),

  getResult: (sessionId: string) =>
    apiClient.get<AssessmentResult>(`/assessment/${sessionId}/result`),

  restart: (sessionId: string) =>
    apiClient.post<StartAssessmentResponse>('/assessment/restart', { session_id: sessionId }),

  getHistory: (page = 1, size = 20) =>
    apiClient.get<PaginatedResponse<AssessmentSession>>('/assessment/history', {
      params: { page, size },
    }),
}
