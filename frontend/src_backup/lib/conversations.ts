export const CONVERSATION_PROMPTS = {
  greetings: [
    "Hi! I'm your Triage Assistant. What symptoms are you experiencing today?",
    "Hello. I'm here to help. How are you feeling today?",
    "Hi there. I'm your health companion. What's bothering you today?",
    "Welcome back. How can I help you today?"
  ],
  
  acknowledgements: [
    "Thank you, that's helpful.",
    "I understand. Let's look into this further.",
    "Got it. I'd like to understand a little more.",
    "Thank you for sharing that.",
    "I see. That helps me understand what you're experiencing."
  ],
  
  empatheticResponses: [
    "I'm sorry you're not feeling well.",
    "That sounds uncomfortable. Let's figure this out.",
    "I know dealing with these symptoms can be stressful.",
    "Let's see if we can understand what's going on."
  ],

  sufficientInfo: [
    "Thank you. I think I have enough information to prepare your assessment. Is there anything else you'd like to mention before we review?",
    "That gives me a good picture. Before I summarize everything, is there anything else you've noticed?",
    "I believe I have what I need to provide some guidance. Is there anything else you want to share first?"
  ],

  errors: [
    "I couldn't quite catch that. Could you try selecting a symptom from the list or rephrasing?",
    "I'm having a little trouble understanding that. Could you describe it differently?",
    "Sorry about that. Could you try phrasing your symptom another way?"
  ],
  
  transitions: [
    "Let's review everything together...",
    "Give me a moment while I put together your health summary...",
    "I'm preparing your guidance now..."
  ]
}

export function getRandomPrompt(category: keyof typeof CONVERSATION_PROMPTS): string {
  const options = CONVERSATION_PROMPTS[category]
  const randomIndex = Math.floor(Math.random() * options.length)
  return options[randomIndex]
}
