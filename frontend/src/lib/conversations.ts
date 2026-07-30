export const CONVERSATION_PROMPTS = {
  greetings: {
    en: [
      "Hi! I'm FirstAid+. What symptoms are you experiencing today?",
      "Hello. I'm here to help. How are you feeling today?",
      "Hi there. I'm your health companion. What's bothering you today?",
      "Welcome back. How can I help you today?"
    ],
    tw: [
      "Akwaaba! Mɛyɛ dɛn atumi aboa wo nnɛ? Ɔhaw bɛn na wote nka?",
      "Nkyia. Maba mɛboa. Wote nka dɛn nnɛ?",
      "Agoo. Meyɛ wo apɔwmuden kwankyerɛfo. Dɛn na ɛhaw wo nnɛ?",
      "Akwaaba. Mɛyɛ dɛn atumi aboa wo nnɛ?"
    ]
  },
  
  acknowledgements: {
    en: [
      "Thank you, that's helpful.",
      "I understand. Let's look into this further.",
      "Got it. I'd like to understand a little more.",
      "Thank you for sharing that.",
      "I see. That helps me understand what you're experiencing."
    ],
    tw: [
      "Meda ase, eyi boa paa.",
      "Mate ase. Ma yɛnhwɛ mu yiye.",
      "Mate. Mepɛ sɛ mete ase yiye.",
      "Meda ase sɛ woaka akyerɛ me.",
      "Mate ase. Ɛboa me ma mete nka a wote no ase."
    ]
  },
  
  empatheticResponses: {
    en: [
      "I'm sorry you're not feeling well.",
      "That sounds uncomfortable. Let's figure this out.",
      "I know dealing with these symptoms can be stressful.",
      "Let's see if we can understand what's going on."
    ],
    tw: [
      "Kafra sɛ wonte apɔw yiye.",
      "Ɛte sɛ nea ɛyɛ yaw. Ma yɛnhwɛ nea ɛyɛ.",
      "Minim sɛ eyi tumi ma adwinnwen.",
      "Ma yɛnhwɛ nea ɛrekɔ so."
    ]
  },

  sufficientInfo: {
    en: [
      "Thank you. I think I have enough information to prepare your assessment. Is there anything else you'd like to mention before we review?",
      "That gives me a good picture. Before I summarize everything, is there anything else you've noticed?",
      "I believe I have what I need to provide some guidance. Is there anything else you want to share first?"
    ],
    tw: [
      "Meda ase. Migye di sɛ manya asɛm no nyinaa de ayɛ wo nhwehwɛmu. Biribi foforo wɔ hɔ a wopɛ sɛ woka anaa?",
      "Eyi ma me hu no yiye. Ansa na mɛyɛ ne nyinaa no, biribi foforo wɔ hɔ a wahu?",
      "Migye di sɛ manya nea ehia na matumi aboa. Biribi foforo wɔ hɔ a wopɛ sɛ woka anaa?"
    ]
  },

  errors: {
    en: [
      "I couldn't quite catch that. Could you try selecting a symptom from the list or rephrasing?",
      "I'm having a little trouble understanding that. Could you describe it differently?",
      "Sorry about that. Could you try phrasing your symptom another way?"
    ],
    tw: [
      "Mante ase yiye. Wubetumi akyerɛkyerɛ mu yiye anaa?",
      "Ɛyɛ den sɛ mɛte ase. Wubetumi akyerɛkyerɛ mu wɔ kwan foforo so anaa?",
      "Kafra. Wubetumi aka no foforo anaa?"
    ]
  },
  
  transitions: {
    en: [
      "Let's review everything together...",
      "Give me a moment while I put together your health summary...",
      "I'm preparing your guidance now..."
    ],
    tw: [
      "Ma yɛnhwɛ ne nyinaa mu...",
      "Ma me bere kakra na menyɛ wo apɔwmuden nsɛm...",
      "Meresiesie w'akwankyerɛ no mprempren..."
    ]
  }
}

export function getRandomPrompt(category: keyof typeof CONVERSATION_PROMPTS, language: 'en' | 'tw' = 'en'): string {
  const options = CONVERSATION_PROMPTS[category][language] || CONVERSATION_PROMPTS[category]['en']
  const randomIndex = Math.floor(Math.random() * options.length)
  return options[randomIndex]
}
