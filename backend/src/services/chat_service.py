"""
Chat service for processing natural language input and generating responses.
Handles task creation and management through conversational interface.
"""
from typing import Dict, Any, Optional
import re
from datetime import datetime, timedelta
from enum import Enum


class ChatIntent(Enum):
    CREATE_TASK = "create_task"
    UPDATE_TASK = "update_task"
    DELETE_TASK = "delete_task"
    COMPLETE_TASK = "complete_task"
    LIST_TASKS = "list_tasks"
    UNKNOWN = "unknown"


class ChatService:
    """
    Service class for handling chat interactions and natural language processing
    """

    def __init__(self):
        # Compile regex patterns for different intents
        self.patterns = {
            ChatIntent.CREATE_TASK: [
                r"(?:create|add|make|new)\s+(?:a\s+)?(?:task|todo|to-do)\s+(?:to\s+)?(.+)",
                r"(?:task|todo|to-do):\s*(.+)",
                r"(.+)\s+(?:please|pls)",
                r"(?:remind|remember)\s+me\s+to\s+(.+)",
                r"(?:need\s+to|have\s+to|i\s+need\s+to|i\s+have\s+to)\s+(.+)",
            ],
            ChatIntent.COMPLETE_TASK: [
                r"(?:complete|done|finish|mark as complete|mark as done)\s+(?:task|the\s+task)\s*(?:\")?([^\"\.]+)(?:\"|\.)?",
                r"(?:complete|done|finish|mark as complete|mark as done)\s+(?:\")?([^\"\.]+)(?:\"|\.)?",
                r"(?:task|the\s+task)\s+(?:is\s+)?(?:complete|done|finished)\s+(?:\")?([^\"\.]+)(?:\"|\.)?",
            ],
            ChatIntent.LIST_TASKS: [
                r"(?:show|list|display|view|see)\s+(?:my\s+)?(?:tasks|todos|to-dos|todo list|task list)",
                r"what\s+(?:tasks|todos|to-dos)\s+do\s+i\s+have",
                r"my\s+(?:tasks|todos|to-dos)",
                r"what's\s+(?:next|up)",
            ],
            ChatIntent.DELETE_TASK: [
                r"(?:delete|remove|erase|cancel)\s+(?:task|the\s+task)\s+(?:\")?([^\"\.]+)(?:\"|\.)?",
                r"(?:never mind|forget|cancel)\s+(?:about\s+)?(?:the\s+)?(?:task|todo)\s+(?:\")?([^\"\.]+)(?:\"|\.)?",
            ],
        }

    def process_message(self, message: str, user_id: str) -> Dict[str, Any]:
        """
        Process a user message and determine the intent and parameters.
        """
        message_lower = message.lower().strip()

        # Identify the intent
        intent = self._identify_intent(message_lower)

        # Extract relevant parameters based on intent
        params = {}
        if intent == ChatIntent.CREATE_TASK:
            params = self._extract_task_params(message_lower, intent)
            params['user_id'] = user_id
        elif intent == ChatIntent.COMPLETE_TASK:
            params = self._extract_task_identification(message_lower)
        elif intent == ChatIntent.DELETE_TASK:
            params = self._extract_task_identification(message_lower)
        elif intent == ChatIntent.UPDATE_TASK:
            params = self._extract_task_params(message_lower, intent)

        return {
            "intent": intent.value,
            "parameters": params,
            "original_message": message
        }

    def _identify_intent(self, message: str) -> ChatIntent:
        """
        Identify the user's intent from the message.
        """
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    return intent

        # If no specific intent is found, check for generic keywords
        if any(word in message for word in ["complete", "done", "finish"]):
            return ChatIntent.COMPLETE_TASK
        elif any(word in message for word in ["list", "show", "view", "what", "tasks"]):
            return ChatIntent.LIST_TASKS
        elif any(word in message for word in ["delete", "remove", "cancel"]):
            return ChatIntent.DELETE_TASK

        # Default to create task if it seems like a request to do something
        if self._looks_like_task_creation(message):
            return ChatIntent.CREATE_TASK

        return ChatIntent.UNKNOWN

    def _looks_like_task_creation(self, message: str) -> bool:
        """
        Determine if a message looks like a task creation request.
        """
        # Check if message contains common action verbs
        action_verbs = [
            "buy", "call", "email", "write", "schedule", "organize", "prepare",
            "arrange", "plan", "research", "learn", "review", "submit", "attend",
            "read", "watch", "buy", "get", "pick up", "drop off", "pay", "order"
        ]

        words = message.lower().split()
        if len(words) > 1:  # At least 2 words
            for verb in action_verbs:
                if verb in words[:3]:  # Check first few words for action verbs
                    return True

        # Check if message starts with an infinitive (to + verb)
        if message.startswith("to ") or message.startswith("i need to ") or message.startswith("i have to "):
            return True

        return False

    def _extract_task_params(self, message: str, intent: ChatIntent) -> Dict[str, Any]:
        """
        Extract task parameters from the message.
        """
        params = {}

        # For create task intent
        if intent == ChatIntent.CREATE_TASK:
            # Try to extract the task title/description
            for pattern in self.patterns[ChatIntent.CREATE_TASK]:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    title = match.group(1).strip()
                    # Remove common prefixes that aren't part of the task
                    title = re.sub(r"^(?:to|that|the)\s+", "", title, flags=re.IGNORECASE)
                    params['title'] = title
                    break
            else:
                # If no pattern matched, use the full message as title
                params['title'] = message.strip()

            # Try to extract due date/time
            due_date = self._extract_datetime(message)
            if due_date:
                params['due_date'] = due_date

            # Try to extract priority
            priority = self._extract_priority(message)
            if priority:
                params['priority'] = priority

        return params

    def _extract_task_identification(self, message: str) -> Dict[str, Any]:
        """
        Extract task identification parameters (like title or partial title).
        """
        params = {}

        # Look for task name/description in the message
        patterns = [
            r"(?:complete|done|finish|mark as complete|mark as done)\s+(?:task|the\s+task)?\s*(?:\")?([^\"\.]+)(?:\"|\.)?",
            r"(?:delete|remove|erase|cancel)\s+(?:task|the\s+task)?\s*(?:\")?([^\"\.]+)(?:\"|\.)?",
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                task_identifier = match.group(1).strip()
                if task_identifier:
                    params['task_identifier'] = task_identifier
                break

        # If we didn't find a specific identifier, look for other clues
        if 'task_identifier' not in params:
            # Maybe the user just mentioned the task name
            # Extract the most likely task name based on context
            words = message.split()
            # Skip common words at the beginning
            start_idx = 0
            common_starters = ["the", "a", "an", "this", "that", "my"]
            while start_idx < len(words) and words[start_idx].lower() in common_starters:
                start_idx += 1

            if start_idx < len(words):
                # Take the remaining words as the task identifier
                identifier = " ".join(words[start_idx:])
                # Clean it up
                identifier = re.sub(r"[^a-zA-Z0-9\s]", "", identifier).strip()
                if identifier:
                    params['task_identifier'] = identifier

        return params

    def _extract_datetime(self, message: str) -> Optional[datetime]:
        """
        Extract date/time information from the message.
        """
        # Pattern for time expressions like "tomorrow", "next week", "in 2 days", etc.
        relative_patterns = [
            (r"tomorrow", timedelta(days=1)),
            (r"next\s+week", timedelta(weeks=1)),
            (r"in\s+(\d+)\s+days?", lambda m: timedelta(days=int(m.group(1)))),
            (r"in\s+(\d+)\s+hours?", lambda m: timedelta(hours=int(m.group(1)))),
            (r"(\d+)\s+days?\s+from\s+now", lambda m: timedelta(days=int(m.group(1)))),
            (r"(\d+)\s+hours?\s+from\s+now", lambda m: timedelta(hours=int(m.group(1)))),
        ]

        message_lower = message.lower()

        for pattern, delta_func in relative_patterns:
            match = re.search(pattern, message_lower)
            if match:
                if callable(delta_func):
                    delta = delta_func(match)
                else:
                    delta = delta_func
                return datetime.now() + delta

        # Pattern for absolute dates like "2023-12-25", "Dec 25", etc.
        absolute_patterns = [
            r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
            r"\d{2}/\d{2}/\d{4}",  # MM/DD/YYYY
            r"\d{2}-\d{2}-\d{4}",  # MM-DD-YYYY
            r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}(?:,\s+\d{4})?",  # Month DD, YYYY
        ]

        for pattern in absolute_patterns:
            match = re.search(pattern, message)
            if match:
                date_str = match.group(0)
                try:
                    # Attempt to parse the date - this is a simplification
                    # In a real implementation, you'd use a more robust date parser
                    return datetime.strptime(date_str.replace(',', ''), "%Y-%m-%d")
                except ValueError:
                    # If the first format fails, try another format
                    try:
                        return datetime.strptime(date_str.replace(',', ''), "%m/%d/%Y")
                    except ValueError:
                        try:
                            # Handle month day formats
                            if "2023" in date_str:
                                return datetime.strptime(date_str, "%b %d, %Y")
                            else:
                                return datetime.strptime(date_str + " 2023", "%b %d %Y")
                        except ValueError:
                            continue

        return None

    def _extract_priority(self, message: str) -> Optional[str]:
        """
        Extract priority information from the message.
        """
        message_lower = message.lower()

        if any(word in message_lower for word in ["urgent", "asap", "important", "high priority", "critical"]):
            return "high"
        elif any(word in message_lower for word in ["low priority", "not urgent", "whenever", "later"]):
            return "low"

        return None

    def generate_response(self, intent: str, parameters: Dict[str, Any]) -> str:
        """
        Generate a natural language response based on the intent and parameters.
        """
        if intent == "create_task":
            if "title" in parameters:
                return f"Okay, I've created a task for '{parameters['title']}'!"
            else:
                return "I'm sorry, I couldn't understand what task you want to create."
        elif intent == "complete_task":
            if "task_identifier" in parameters:
                return f"I've marked the task '{parameters['task_identifier']}' as complete!"
            else:
                return "Which task would you like to mark as complete?"
        elif intent == "list_tasks":
            return "Here are your tasks..."
        elif intent == "delete_task":
            if "task_identifier" in parameters:
                return f"I've deleted the task '{parameters['task_identifier']}'."
            else:
                return "Which task would you like to delete?"
        elif intent == "unknown":
            return "I'm sorry, I didn't understand that. Could you rephrase your request?"
        else:
            return "Okay, I'll take care of that for you."