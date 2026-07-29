import { useNetworkStore } from '../stores/network-store'
import { dbService } from './DatabaseService'
import { apiClient } from '../lib/axios'

class ConnectivityService {
  /**
   * Initializes network listeners and triggers sync if online.
   */
  init() {
    window.addEventListener('online', () => {
      useNetworkStore.getState().setOnline(true)
      this.syncOfflineData()
    })

    window.addEventListener('offline', () => {
      useNetworkStore.getState().setOnline(false)
    })
  }

  /**
   * Syncs the knowledge base for offline use.
   */
  async syncKnowledgeBase() {
    if (useNetworkStore.getState().isOnline) {
      try {
        const response = await apiClient.get('/sync/knowledge')
        const data = response.data
        await dbService.setKnowledgeBase(data)
      } catch (error) {
        console.error('Failed to sync knowledge base:', error)
      }
    } else {
      // Offline fallback: if DB is empty, try to load bundled JSON
      const existing = await dbService.getKnowledgeBase()
      if (!existing) {
        try {
          const fallbackData = await import('../../public/data/knowledge.json');
          await dbService.setKnowledgeBase(fallbackData.default || fallbackData);
          console.log("Seeded knowledge base from bundled JSON.");
        } catch (e) {
          console.error('Failed to load bundled knowledge base fallback:', e);
        }
      }
    }
  }

  /**
   * Syncs offline conversations back to the server.
   */
  async syncOfflineData() {
    if (useNetworkStore.getState().hasPendingSync) return
    useNetworkStore.getState().setPendingSync(true)

    try {
      const unsynced = await dbService.getUnsyncedConversations()
      if (unsynced.length === 0) {
        useNetworkStore.getState().setPendingSync(false)
        return
      }

      const batchId = crypto.randomUUID()
      const payload = {
        batch_id: batchId,
        sessions: unsynced.map(conv => ({
          local_id: conv.local_id,
          urgency_level: conv.urgency_level || 'GREEN',
          primary_symptom: conv.primary_symptom,
          symptom_details: conv.symptom_details,
          language_code: conv.language_code,
          conducted_at: conv.conducted_at,
        }))
      }

      const response = await apiClient.post('/sync/outbox', payload)
      
      // Update local db with server IDs
      for (const pair of response.data.synced_ids) {
        await dbService.markConversationSynced(pair.local_id, pair.server_id)
      }

      useNetworkStore.getState().setLastSyncAt(new Date())
    } catch (error) {
      console.error('Offline sync failed:', error)
    } finally {
      useNetworkStore.getState().setPendingSync(false)
    }
  }
}

export const connectivityService = new ConnectivityService()
