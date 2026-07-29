export type UrgencyCode = 'RED' | 'ORANGE' | 'YELLOW' | 'GREEN'

export interface RuleCondition {
  node_id: string
  answer_value: string | boolean | number
  negated: boolean
}

export interface TriageRule {
  id: string
  symptom_id: string
  health_concern_id: string
  rule_name: string
  rule_conditions: RuleCondition[]
  logic_operator: 'AND' | 'OR'
  priority_order: number
  is_red_flag_override: boolean
  is_active: boolean
  severity_code: UrgencyCode
}

export class ClientRuleEngine {
  private rules: TriageRule[]

  constructor(rules: TriageRule[]) {
    // Sort rules by priority order, ignoring inactive or red flag overrides for general scoring
    this.rules = rules
      .filter((r) => r.is_active && !r.is_red_flag_override)
      .sort((a, b) => a.priority_order - b.priority_order)
  }

  /**
   * Evaluates a single rule condition against the given answers.
   */
  private evaluateCondition(condition: RuleCondition, answers: Record<string, any>): boolean {
    const userAnswer = answers[condition.node_id]
    
    // Treat undefined/null as empty
    if (userAnswer === undefined || userAnswer === null) {
      return condition.negated ? true : false
    }

    let isMatch = false
    
    // Handle array answers (e.g. multi-select options)
    if (Array.isArray(userAnswer)) {
      isMatch = userAnswer.includes(condition.answer_value)
    } else {
      isMatch = String(userAnswer) === String(condition.answer_value)
    }

    return condition.negated ? !isMatch : isMatch
  }

  /**
   * Evaluates all conditions for a rule using the specified logic operator (AND/OR).
   */
  private evaluateRuleLogic(rule: TriageRule, answers: Record<string, any>): boolean {
    if (!rule.rule_conditions || rule.rule_conditions.length === 0) {
      return false
    }

    if (rule.logic_operator === 'AND') {
      return rule.rule_conditions.every((cond) => this.evaluateCondition(cond, answers))
    } else {
      // OR
      return rule.rule_conditions.some((cond) => this.evaluateCondition(cond, answers))
    }
  }

  /**
   * Calculates the overall triage score by finding the first matching rule.
   * Returns [UrgencyCode, matchedRuleId]
   */
  public calculateScore(answers: Record<string, any>): { severity: UrgencyCode; ruleId?: string } {
    for (const rule of this.rules) {
      if (this.evaluateRuleLogic(rule, answers)) {
        return { severity: rule.severity_code, ruleId: rule.id }
      }
    }
    
    // Default fallback
    return { severity: 'GREEN' }
  }
}
