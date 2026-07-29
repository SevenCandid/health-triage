import { dbService, type KnowledgeBaseData } from '../../../services/DatabaseService'
import { ClientRuleEngine, type TriageRule, type UrgencyCode } from './ClientRuleEngine'
import fallbackKnowledgeBase from '../../../../public/data/knowledge.json'

export class ClientTriageService {
  /**
   * Starts a new offline conversation.
   */
  static async startConversation(
    primarySymptom: string,
    languageCode: string = 'en',
    userId?: string
  ) {
    const localId = crypto.randomUUID()
    
    // Create conversation record in IndexedDB
    const conversation = {
      id: localId, // Temp ID until sync
      local_id: localId,
      user_id: userId,
      primary_symptom: primarySymptom,
      symptom_details: {},
      language_code: languageCode,
      conducted_at: new Date().toISOString(),
      synced: 0,
    }
    
    await dbService.saveConversation(conversation)
    
    // Get next question
    const result = await this.evaluateConversation(localId)
    return {
      session_id: localId,
      symptoms: [{ name: primarySymptom, is_active: true }],
      ...result
    }
  }

  /**
   * Submits an answer and re-evaluates the conversation.
   */
  static async answerQuestion(sessionId: string, nodeId: string, answerValue: any) {
    const conversation = await dbService.getConversation(sessionId)
    if (!conversation) {
      throw new Error(`Offline conversation ${sessionId} not found`)
    }

    // Update answers
    conversation.symptom_details[nodeId] = answerValue
    await dbService.saveConversation(conversation)

    return await this.evaluateConversation(sessionId)
  }

  /**
   * Evaluates the conversation using the ClientRuleEngine to find red flags, 
   * get next questions, or calculate final score.
   */
  private static async evaluateConversation(sessionId: string) {
    const conversation = await dbService.getConversation(sessionId)
    let kb = await dbService.getKnowledgeBase()

    if (!kb) {
      console.warn("Using bundled static knowledge base for offline triage.")
      if (typeof fallbackKnowledgeBase === 'string') {
        const res = await fetch(fallbackKnowledgeBase)
        kb = await res.json()
      } else {
        kb = (fallbackKnowledgeBase as any).default || fallbackKnowledgeBase
      }
    }

    if (!conversation || !kb) {
      throw new Error('Missing conversation or offline knowledge base data')
    }

    // 1. Find the primary symptom ID from the DB based on the string name
    const symptomRow = kb.symptoms.find((s: any) => 
      s.name.toLowerCase() === conversation.primary_symptom.toLowerCase() ||
      s.snomed_ct_code === conversation.primary_symptom // Fallback
    )

    if (!symptomRow) {
      // If we don't recognize the symptom, just end with GREEN
      return this.buildResult('GREEN', [], 'Symptom unrecognized offline.')
    }

    const symptomId = symptomRow.id
    const answers = conversation.symptom_details
    const symptomRules = kb.triage_rules.filter((r: any) => r.symptom_id === symptomId)

    // 2. Emergency Engine (Red flags)
    const ruleEngine = new ClientRuleEngine(symptomRules as TriageRule[])
    const emergencyRules = symptomRules.filter((r: any) => r.is_red_flag_override)
    const emergencyEngine = new ClientRuleEngine(emergencyRules as TriageRule[])
    
    const { ruleId: redFlagRuleId } = emergencyEngine.calculateScore(answers)
    if (redFlagRuleId) {
      // Short-circuit to RED
      conversation.urgency_level = 'RED'
      await dbService.saveConversation(conversation)
      const recommendations = this.getRecommendations('RED', kb)
      return this.buildResult('RED', recommendations, 'Emergency override rule triggered.', true)
    }

    // 3. Question Engine (Determine next question)
    const symptomQuestions = kb.questions.filter((q: any) => q.symptom_id === symptomId)
    // Sort by order_index
    symptomQuestions.sort((a: any, b: any) => a.order_index - b.order_index)

    let nextQuestion = null
    for (const q of symptomQuestions) {
      if (answers[q.node_id] === undefined) {
        nextQuestion = q
        break
      }
    }

    if (nextQuestion) {
      // Still have questions to ask
      return {
        is_complete: false,
        next_question: nextQuestion
      }
    }

    // 4. Scoring Engine
    const { severity: finalSeverity } = ruleEngine.calculateScore(answers)
    conversation.urgency_level = finalSeverity
    await dbService.saveConversation(conversation)
    
    // 5. Recommendation Engine
    const recommendations = this.getRecommendations(finalSeverity, kb)
    
    return this.buildResult(finalSeverity, recommendations, 'Offline triage evaluation completed.')
  }

  private static getRecommendations(_severity: UrgencyCode, kb: KnowledgeBaseData) {
    // In backend, recommendations are fetched by severity_level_id. 
    // Here we can find the severity_level_id using the UrgencyCode if needed, 
    // or just match recommendations based on the rule. 
    // For MVP, we'll map all recommendations that match the urgency.
    // However, recommendations might not have severity directly if they rely on the mapping.
    // If recommendation models only have `severity_level_id`, we might need a lookup map, 
    // but we can just filter by general guidelines.
    // For now, let's return a stub recommendation text until we port full RecommendationEngine
    const recList = kb.recommendations.filter((r: any) => r.is_general_guideline)
    return recList.map((r: any) => r.recommendation_text_en)
  }

  private static buildResult(severity: UrgencyCode, recommendations: string[], explanation: string, is_emergency = false) {
    return {
      is_complete: true,
      result: {
        severity,
        recommendations,
        explanation,
        is_emergency,
        action_protocol: {
          action: severity === 'RED' ? 'Go to Emergency' : (severity === 'ORANGE' ? 'See Doctor Soon' : 'Self Care'),
          timeframe_hours: severity === 'RED' ? 0 : 24,
          guidance: explanation
        }
      }
    }
  }
}
