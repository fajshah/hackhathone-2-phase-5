from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from uuid import UUID
import json

class ConversationContext:
    def __init__(self, user_id: UUID, conversation_id: UUID):
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.messages: List[Dict[str, Any]] = []
        self.context_data: Dict[str, Any] = {}
        self.created_at = datetime.utcnow()
        self.last_updated = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(hours=24)  # Context expires after 24 hours

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation context."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.messages.append(message)
        self.last_updated = datetime.utcnow()
        
        # Keep only the last 20 messages to prevent context from growing too large
        if len(self.messages) > 20:
            self.messages = self.messages[-20:]

    def update_context_data(self, key: str, value: Any) -> None:
        """Update context data with a key-value pair."""
        self.context_data[key] = value
        self.last_updated = datetime.utcnow()

    def get_context_data(self, key: str, default: Any = None) -> Any:
        """Get context data for a specific key."""
        return self.context_data.get(key, default)

    def get_recent_messages(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get the most recent messages from the context."""
        return self.messages[-count:] if len(self.messages) >= count else self.messages[:]

    def is_expired(self) -> bool:
        """Check if the context has expired."""
        return datetime.utcnow() > self.expires_at

    def refresh_expiration(self) -> None:
        """Refresh the context expiration time."""
        self.expires_at = datetime.utcnow() + timedelta(hours=24)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the context to a dictionary for serialization."""
        return {
            "user_id": str(self.user_id),
            "conversation_id": str(self.conversation_id),
            "messages": self.messages,
            "context_data": self.context_data,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "expires_at": self.expires_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationContext':
        """Create a ConversationContext from a dictionary."""
        context = cls.__new__(cls)
        context.user_id = UUID(data["user_id"])
        context.conversation_id = UUID(data["conversation_id"])
        context.messages = data["messages"]
        context.context_data = data["context_data"]
        context.created_at = datetime.fromisoformat(data["created_at"])
        context.last_updated = datetime.fromisoformat(data["last_updated"])
        context.expires_at = datetime.fromisoformat(data["expires_at"])
        return context


class ContextManager:
    def __init__(self):
        self.contexts: Dict[str, ConversationContext] = {}  # Key: f"{user_id}:{conversation_id}"

    def get_context(self, user_id: UUID, conversation_id: UUID) -> Optional[ConversationContext]:
        """Get an existing conversation context."""
        key = f"{user_id}:{conversation_id}"
        context = self.contexts.get(key)
        
        if context and context.is_expired():
            del self.contexts[key]
            return None
        
        return context

    def create_context(self, user_id: UUID, conversation_id: UUID) -> ConversationContext:
        """Create a new conversation context."""
        context = ConversationContext(user_id, conversation_id)
        key = f"{user_id}:{conversation_id}"
        self.contexts[key] = context
        return context

    def get_or_create_context(self, user_id: UUID, conversation_id: UUID) -> ConversationContext:
        """Get an existing context or create a new one."""
        context = self.get_context(user_id, conversation_id)
        if context is None:
            context = self.create_context(user_id, conversation_id)
        else:
            context.refresh_expiration()
        return context

    def update_context(self, user_id: UUID, conversation_id: UUID, role: str, content: str) -> ConversationContext:
        """Update the conversation context with a new message."""
        context = self.get_or_create_context(user_id, conversation_id)
        context.add_message(role, content)
        return context

    def cleanup_expired_contexts(self) -> None:
        """Remove expired contexts from memory."""
        expired_keys = []
        for key, context in self.contexts.items():
            if context.is_expired():
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.contexts[key]

    def clear_context(self, user_id: UUID, conversation_id: UUID) -> bool:
        """Clear a specific conversation context."""
        key = f"{user_id}:{conversation_id}"
        if key in self.contexts:
            del self.contexts[key]
            return True
        return False

# Global instance
context_manager = ContextManager()

def get_context(user_id: UUID, conversation_id: UUID) -> Optional[ConversationContext]:
    """Get conversation context for the given user and conversation."""
    return context_manager.get_context(user_id, conversation_id)

def update_context_with_message(user_id: UUID, conversation_id: UUID, role: str, content: str) -> ConversationContext:
    """Update conversation context with a new message."""
    return context_manager.update_context(user_id, conversation_id, role, content)

def get_or_create_context(user_id: UUID, conversation_id: UUID) -> ConversationContext:
    """Get or create conversation context for the given user and conversation."""
    return context_manager.get_or_create_context(user_id, conversation_id)