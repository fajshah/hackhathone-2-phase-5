from typing import Dict, List, Tuple
import re
from enum import Enum

class Intent(Enum):
    CREATE_TASK = "create_task"
    UPDATE_TASK = "update_task"
    DELETE_TASK = "delete_task"
    LIST_TASKS = "list_tasks"
    COMPLETE_TASK = "complete_task"
    ADD_REMINDER = "add_reminder"
    GENERAL_CHAT = "general_chat"
    HELP = "help"

class IntentRecognizer:
    def __init__(self):
        # Define patterns for different intents
        self.patterns = {
            Intent.CREATE_TASK: [
                r'\b(add|create|make|new)\s+(a\s+)?(task|todo|item|thing|note)\b',
                r'\b(task|todo)\s+(to|for)\s+\w+',
                r'\bneed\s+to\s+(do|complete|finish|start)\b',
                r'\bremember\s+to\b',
                r'\bput\s+(on|in)\s+my\s+(list|tasks)\b',
                r'\bset\s+up\s+(a\s+)?(task|todo)\b'
            ],
            Intent.LIST_TASKS: [
                r'\b(list|show|display|view|see)\s+(my\s+)?(tasks|todos|list|items)\b',
                r'\bwhat\s+(do\s+i\s+have|am\s+i\s+supposed\s+to)\s+(do|complete)\b',
                r'\bmy\s+(current|pending|active)\s+(tasks|todos)\b',
                r'\b(check|review)\s+(my\s+)?(tasks|list)\b'
            ],
            Intent.UPDATE_TASK: [
                r'\b(update|change|modify|edit)\s+(a\s+)?(task|todo)\b',
                r'\b(change|update)\s+(the|my)\s+(priority|status|due\s+date)\b',
                r'\b(mark|set)\s+(as\s+)?(in\s+progress|done|completed|finished)\b',
                r'\bmove\s+(to|from)\s+(in\s+progress|done|todo)\b'
            ],
            Intent.COMPLETE_TASK: [
                r'\b(complete|finish|done|completed|finished)\s+(a\s+)?(task|todo)\b',
                r'\b(check\s+off|tick|mark)\s+(as\s+)?(done|completed|finished)\b',
                r'\bcross\s+(off|out)\s+(a\s+)?(task|todo)\b',
                r'\bfinish\s+(up|off)\s+(a\s+)?(task|todo)\b'
            ],
            Intent.DELETE_TASK: [
                r'\b(delete|remove|clear|cancel)\s+(a\s+)?(task|todo)\b',
                r'\bget\s+rid\s+of\s+(a\s+)?(task|todo)\b',
                r'\bthrow\s+away\s+(a\s+)?(task|todo)\b',
                r'\btrash\s+(a\s+)?(task|todo)\b'
            ],
            Intent.ADD_REMINDER: [
                r'\b(remind|reminder)\s+(me\s+)?(to|about)\s+\w+',
                r'\b(set\s+a\s+)?(remind|reminder)\s+(for|at|on)\s+\w+',
                r'\bdon\'t\s+forget\s+to\b',
                r'\balert\s+me\s+(to|about)\b'
            ],
            Intent.HELP: [
                r'\b(help|support|assist|guide|tutorial)\b',
                r'\b(how\s+do\s+i|can\s+i|what\s+can\s+i)\s+(use|do|add|create)\b',
                r'\bwhat\s+(can|does)\s+this\s+(app|system|bot)\s+(do|help|manage)\b',
                r'\btell\s+me\s+(more|about)\s+(this|how\s+it\s+works)\b'
            ]
        }
        
        # Compile regex patterns for efficiency
        self.compiled_patterns = {}
        for intent, patterns in self.patterns.items():
            self.compiled_patterns[intent] = [re.compile(p, re.IGNORECASE) for p in patterns]

    def recognize_intent(self, text: str) -> Tuple[Intent, float]:
        """
        Recognize the intent from the given text and return confidence score.
        """
        text_lower = text.lower()
        
        # Check for exact matches first
        if any(word in text_lower for word in ['help', 'support', 'tutorial']):
            return Intent.HELP, 1.0
        
        if any(word in text_lower for word in ['list', 'show', 'view', 'see'] 
               if any(task_word in text_lower for task_word in ['tasks', 'todos', 'list'])):
            return Intent.LIST_TASKS, 1.0
        
        # Check all patterns
        best_intent = Intent.GENERAL_CHAT
        best_score = 0.0
        
        for intent, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(text)
                if matches:
                    # Calculate score based on number of matches and pattern length
                    score = len(matches) * 0.5 + (1.0 / len(pattern.pattern)) * 0.3
                    if score > best_score:
                        best_score = score
                        best_intent = intent
        
        # Normalize score to 0-1 range
        if best_score > 1.0:
            best_score = min(best_score, 1.0)
        
        return best_intent, best_score

# Global instance
intent_recognizer = IntentRecognizer()

def get_intent(text: str) -> Tuple[Intent, float]:
    """
    Get the recognized intent and confidence score for the given text.
    """
    return intent_recognizer.recognize_intent(text)