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

  getProfile: async () => {
    if (!useNetworkStore.getState().isOnline) {
      const profile = await dbService.getAuthSession()
      return { data: profile } as any
    }
    const response = await apiClient.get<UserProfile>('/auth/me')
    await dbService.saveAuthSession(response.data)
    return response
  },

  updateProfile: (data: Partial<UserProfile>) =>
    apiClient.put<UserProfile>('/auth/me', data),

  getEmergencyContacts: () =>
    apiClient.get<EmergencyContact[]>('/users/me/emergency-contacts'),
}

// ── Profile API ───────────────────────────────────────────────────────────────

export const profileApi = {
  getProfile: async () => {
    if (!useNetworkStore.getState().isOnline) {
      const profile = await dbService.getProfile()
      return { data: profile } as any
    }
    const response = await apiClient.get<HealthProfile>('/users/me/profile')
    await dbService.saveProfile(response.data)
    return response
  },

  upsertProfile: (data: Partial<HealthProfile>) =>
    apiClient.put<HealthProfile>('/users/me/profile', data),

  getEmergencyContacts: () =>
    apiClient.get<EmergencyContact[]>('/users/me/emergency-contacts'),

  addEmergencyContact: (data: EmergencyContactRequest) =>
    apiClient.post<EmergencyContact>('/users/me/emergency-contacts', data),
}

// ── Assessment API ────────────────────────────────────────────────────────────

import { useNetworkStore } from '../stores/network-store'
import { ClientTriageService } from '../features/assessment/services/ClientTriageService'
import { dbService } from './DatabaseService'

export const assessmentApi = {
  start: async (mode: 'TEXT' | 'VOICE' = 'TEXT') => {
    const doOffline = async () => {
      const result = await ClientTriageService.startConversation('Offline Start', 'en')
      return { data: result } as any
    }
    if (!useNetworkStore.getState().isOnline) {
      return doOffline()
    }
    try {
      return await apiClient.post<StartAssessmentResponse>('/assessment/start', {
        language_code: 'en',
        consultation_mode: mode,
        created_offline: false,
      })
    } catch (e: any) {
      if (e.code === 'ERR_NETWORK' || e.message === 'Network Error' || e.code === 'ECONNABORTED' || (e.message && e.message.includes('timeout'))) {
        useNetworkStore.getState().setOnline(false)
        return doOffline()
      }
      throw e
    }
  },

  submitSymptoms: async (sessionId: string, symptoms: string[], userText?: string) => {
    const slug = symptoms[0] ? symptoms[0].toLowerCase().replace(/\s+/g, '-') : 'unknown';
    const doOffline = async () => {
      const conv = await dbService.getConversation(sessionId)
      if (conv) {
        conv.primary_symptom = symptoms[0] || 'unknown'
        await dbService.saveConversation(conv)
      }
      const result = await ClientTriageService.answerQuestion(sessionId, '__symptom_submit', null)
      return { data: result } as any
    }

    if (!useNetworkStore.getState().isOnline) {
      return doOffline()
    }
    try {
      return await apiClient.post<SymptomsSubmitResponse>('/assessment/symptoms', {
        session_id: sessionId,
        symptom_slug: slug,
        user_text: userText || symptoms[0],
      });
    } catch (e: any) {
      if (e.code === 'ERR_NETWORK' || e.message === 'Network Error' || e.code === 'ECONNABORTED' || (e.message && e.message.includes('timeout'))) {
        useNetworkStore.getState().setOnline(false)
        return doOffline()
      }
      throw e
    }
  },

  submitAnswer: async (sessionId: string, questionId: string, answerValue: string | string[], answerRawText: string) => {
    const doOffline = async () => {
      const result = await ClientTriageService.answerQuestion(sessionId, questionId, Array.isArray(answerValue) ? answerValue.join(',') : answerValue)
      return { data: result } as any
    }

    if (!useNetworkStore.getState().isOnline) {
      return doOffline()
    }
    try {
      return await apiClient.post<AnswerSubmitResponse>('/assessment/answer', {
        session_id: sessionId,
        node_id: questionId,
        answer_value: Array.isArray(answerValue) ? answerValue.join(',') : answerValue,
        answer_raw_text: answerRawText
      })
    } catch (e: any) {
      if (e.code === 'ERR_NETWORK' || e.message === 'Network Error' || e.code === 'ECONNABORTED' || (e.message && e.message.includes('timeout'))) {
        useNetworkStore.getState().setOnline(false)
        return doOffline()
      }
      throw e
    }
  },

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
