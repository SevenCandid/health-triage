import { openDB, type DBSchema, type IDBPDatabase } from 'idb'

export interface KnowledgeBaseData {
  rule_set_version: string
  symptoms: any[]
  questions: any[]
  triage_rules: any[]
  recommendations: any[]
}

interface HealthTriageDB extends DBSchema {
  knowledge_base: {
    key: string // e.g., 'latest'
    value: KnowledgeBaseData
  }
  conversations: {
    key: string
    value: {
      id: string
      local_id: string
      user_id?: string
      urgency_level?: string
      primary_symptom: string
      symptom_details: any
      language_code: string
      conducted_at: string
      synced: number // 0 for false, 1 for true
    }
    indexes: { 'by-sync': number }
  }
  auth_session: {
    key: string
    value: any
  }
  profile: {
    key: string
    value: any
  }
}

class DatabaseService {
  private dbPromise: Promise<IDBPDatabase<HealthTriageDB>>

  constructor() {
    this.dbPromise = openDB<HealthTriageDB>('HealthTriageDB', 1, {
      upgrade(db) {
        if (!db.objectStoreNames.contains('knowledge_base')) {
          db.createObjectStore('knowledge_base')
        }
        if (!db.objectStoreNames.contains('conversations')) {
          const store = db.createObjectStore('conversations', { keyPath: 'local_id' })
          store.createIndex('by-sync', 'synced')
        }
        if (!db.objectStoreNames.contains('auth_session')) {
          db.createObjectStore('auth_session')
        }
        if (!db.objectStoreNames.contains('profile')) {
          db.createObjectStore('profile')
        }
      },
    })
  }

  // --- Knowledge Base ---
  async setKnowledgeBase(data: KnowledgeBaseData) {
    const db = await this.dbPromise
    await db.put('knowledge_base', data, 'latest')
  }

  async getKnowledgeBase(): Promise<KnowledgeBaseData | undefined> {
    const db = await this.dbPromise
    return db.get('knowledge_base', 'latest')
  }

  // --- Conversations ---
  async saveConversation(conversation: any) {
    const db = await this.dbPromise
    await db.put('conversations', conversation)
  }

  async getUnsyncedConversations() {
    const db = await this.dbPromise
    return db.getAllFromIndex('conversations', 'by-sync', 0)
  }

  async markConversationSynced(local_id: string, server_id: string) {
    const db = await this.dbPromise
    const tx = db.transaction('conversations', 'readwrite')
    const store = tx.objectStore('conversations')
    const conv = await store.get(local_id)
    if (conv) {
      conv.synced = 1
      conv.id = server_id
      await store.put(conv)
    }
    await tx.done
  }

  async getAllConversations() {
    const db = await this.dbPromise
    return db.getAll('conversations')
  }

  async getConversation(local_id: string) {
    const db = await this.dbPromise
    return db.get('conversations', local_id)
  }

  // --- Auth Session ---
  async saveAuthSession(session: any) {
    const db = await this.dbPromise
    await db.put('auth_session', session, 'current')
  }

  async getAuthSession() {
    const db = await this.dbPromise
    return db.get('auth_session', 'current')
  }

  async clearAuthSession() {
    const db = await this.dbPromise
    await db.delete('auth_session', 'current')
  }

  // --- Profile ---
  async saveProfile(profile: any) {
    const db = await this.dbPromise
    await db.put('profile', profile, 'current')
  }

  async getProfile() {
    const db = await this.dbPromise
    return db.get('profile', 'current')
  }
}

export const dbService = new DatabaseService()
