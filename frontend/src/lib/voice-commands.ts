import { match } from 'path-to-regexp'; // Not using path-to-regexp, doing custom matching

export type VoiceCommandAction =
  | 'CONVERSATION_CONTINUE'
  | 'CONVERSATION_FINISH'
  | 'CONVERSATION_START_OVER'
  | 'CONVERSATION_CANCEL'
  | 'SPEECH_STOP'
  | 'SPEECH_PAUSE'
  | 'SPEECH_RESUME'
  | 'SPEECH_REPEAT'
  | 'SPEECH_SLOWER'
  | 'SPEECH_FASTER'
  | 'NAV_BACK'
  | 'NAV_NEXT'
  | 'NAV_RESULTS'
  | 'NAV_HISTORY'
  | 'NAV_EMERGENCY'
  | 'NAV_PROFILE'
  | 'NAV_SETTINGS'
  | 'HELP';

interface CommandDefinition {
  action: VoiceCommandAction;
  phrases: string[];
}

const COMMAND_DICTIONARY: CommandDefinition[] = [
  // Conversation Control
  {
    action: 'CONVERSATION_CONTINUE',
    phrases: ['continue', 'continue talking', 'go on', 'keep going'],
  },
  {
    action: 'CONVERSATION_FINISH',
    phrases: ['finish assessment', 'end assessment', 'im done', 'i am done', 'finish', 'complete assessment'],
  },
  {
    action: 'CONVERSATION_START_OVER',
    phrases: ['start over', 'new assessment', 'restart', 'begin again'],
  },
  {
    action: 'CONVERSATION_CANCEL',
    phrases: ['cancel', 'cancel assessment', 'stop assessment'],
  },

  // Speech Control
  {
    action: 'SPEECH_STOP',
    phrases: ['stop speaking', 'be quiet', 'stop talking', 'shush', 'quiet'],
  },
  {
    action: 'SPEECH_PAUSE',
    phrases: ['pause', 'wait', 'hold on'],
  },
  {
    action: 'SPEECH_RESUME',
    phrases: ['resume', 'continue speaking'],
  },
  {
    action: 'SPEECH_REPEAT',
    phrases: ['repeat', 'repeat that', 'say that again', 'what was that', 'pardon'],
  },
  {
    action: 'SPEECH_SLOWER',
    phrases: ['speak slower', 'slow down'],
  },
  {
    action: 'SPEECH_FASTER',
    phrases: ['speak faster', 'speed up'],
  },

  // Navigation
  {
    action: 'NAV_BACK',
    phrases: ['go back', 'back'],
  },
  {
    action: 'NAV_NEXT',
    phrases: ['next', 'go forward'],
  },
  {
    action: 'NAV_RESULTS',
    phrases: ['open results', 'show my results', 'go to results', 'see results'],
  },
  {
    action: 'NAV_HISTORY',
    phrases: ['go to my history', 'open history', 'show history'],
  },
  {
    action: 'NAV_EMERGENCY',
    phrases: ['open emergency', 'go to emergency', 'emergency center'],
  },
  {
    action: 'NAV_PROFILE',
    phrases: ['open profile', 'go to profile', 'my profile'],
  },
  {
    action: 'NAV_SETTINGS',
    phrases: ['open settings', 'go to settings'],
  },

  // Help
  {
    action: 'HELP',
    phrases: ['help', 'what can i say', 'voice commands', 'what are the commands'],
  },
];

const cleanText = (text: string) => text.toLowerCase().replace(/[^\w\s]/g, '').trim();

/**
 * Parses a transcript to determine if it is a local voice command.
 * Uses exact matching and simple containment with high confidence to avoid false positives with symptoms.
 */
export function parseVoiceCommand(transcript: string): VoiceCommandAction | null {
  const cleaned = cleanText(transcript);
  
  // Try exact match first
  for (const cmd of COMMAND_DICTIONARY) {
    if (cmd.phrases.includes(cleaned)) {
      return cmd.action;
    }
  }

  // Try containment match for longer transcripts (e.g. "please repeat that")
  // Only if the transcript is relatively short to avoid triggering on long symptom descriptions
  if (cleaned.split(' ').length <= 6) {
    for (const cmd of COMMAND_DICTIONARY) {
      for (const phrase of cmd.phrases) {
        if (cleaned.includes(phrase)) {
          return cmd.action;
        }
      }
    }
  }

  return null;
}
