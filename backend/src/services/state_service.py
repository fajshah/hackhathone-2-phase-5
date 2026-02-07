"""
State management service using Dapr State Store for conversation state.
Handles storing and retrieving session data using Dapr's state management.
"""
from typing import Dict, Any, Optional, Union
import json
import asyncio
from datetime import datetime, timedelta


class StateService:
    """
    Service class for managing state using Dapr State Store
    """

    def __init__(self, dapr_client=None, state_store_name: str = "statestore"):
        self.state_store_name = state_store_name
        self.dapr_client = dapr_client

        # If no client is provided, we'll create one lazily when needed
        if self.dapr_client is None:
            # We'll initialize it when it's first needed
            pass

    async def save_state(self, key: str, data: Any, ttl_seconds: Optional[int] = None) -> bool:
        """
        Save data to the state store with an optional TTL.

        Args:
            key: The key to store the data under
            data: The data to store (will be serialized as JSON)
            ttl_seconds: Optional time-to-live in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            # Initialize Dapr client if not already done
            if self.dapr_client is None:
                try:
                    from dapr.clients import DaprClient
                    self.dapr_client = DaprClient()
                except ImportError:
                    print("Dapr client not available. Install dapr.")
                    return False

            # Serialize the data to JSON string
            serialized_data = json.dumps(data, default=str)  # Use str() for non-serializable objects like datetime

            # Prepare options for TTL if provided
            options = {}
            if ttl_seconds:
                # Dapr uses expiration time in seconds
                options = {"ttlInSeconds": ttl_seconds}

            # Save to state store
            with self.dapr_client as client:
                client.save_state(
                    store_name=self.state_store_name,
                    key=key,
                    value=serialized_data,
                    options=options
                )

            return True
        except Exception as e:
            print(f"Error saving state for key {key}: {str(e)}")
            return False

    async def get_state(self, key: str) -> Optional[Any]:
        """
        Retrieve data from the state store.

        Args:
            key: The key to retrieve data for

        Returns:
            The retrieved data or None if not found
        """
        try:
            # Initialize Dapr client if not already done
            if self.dapr_client is None:
                try:
                    from dapr.clients import DaprClient
                    self.dapr_client = DaprClient()
                except ImportError:
                    print("Dapr client not available. Install dapr.")
                    return None

            # Get from state store
            with self.dapr_client as client:
                response = client.get_state(
                    store_name=self.state_store_name,
                    key=key
                )

                if response.data:
                    # Deserialize the JSON string
                    return json.loads(response.data.decode('utf-8'))
                else:
                    return None
        except Exception as e:
            print(f"Error getting state for key {key}: {str(e)}")
            return None

    async def delete_state(self, key: str) -> bool:
        """
        Delete data from the state store.

        Args:
            key: The key to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            # Initialize Dapr client if not already done
            if self.dapr_client is None:
                try:
                    from dapr.clients import DaprClient
                    self.dapr_client = DaprClient()
                except ImportError:
                    print("Dapr client not available. Install dapr.")
                    return False

            # Delete from state store
            with self.dapr_client as client:
                client.delete_state(
                    store_name=self.state_store_name,
                    key=key
                )

            return True
        except Exception as e:
            print(f"Error deleting state for key {key}: {str(e)}")
            return False

    async def save_session(self, session_id: str, user_id: str, context: str,
                         expires_in_hours: int = 24) -> bool:
        """
        Save a user session with context.

        Args:
            session_id: Unique session identifier
            user_id: User identifier
            context: Current conversational context
            expires_in_hours: Hours until session expires (default 24)

        Returns:
            True if successful, False otherwise
        """
        session_data = {
            "user_id": user_id,
            "context": context,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=expires_in_hours)).isoformat()
        }

        ttl_seconds = expires_in_hours * 3600  # Convert hours to seconds
        return await self.save_state(session_id, session_data, ttl_seconds)

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a user session.

        Args:
            session_id: Unique session identifier

        Returns:
            Session data dictionary or None if not found/expired
        """
        session_data = await self.get_state(session_id)

        if session_data:
            # Check if session has expired
            expires_at_str = session_data.get("expires_at")
            if expires_at_str:
                try:
                    expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
                    if datetime.utcnow() > expires_at:
                        # Session has expired, delete it
                        await self.delete_state(session_id)
                        return None
                except ValueError:
                    # If date parsing fails, continue with the data
                    pass

            return session_data

        return None

    async def update_session_context(self, session_id: str, context: str) -> bool:
        """
        Update the context of an existing session.

        Args:
            session_id: Unique session identifier
            context: New context to save

        Returns:
            True if successful, False otherwise
        """
        session_data = await self.get_session(session_id)

        if session_data:
            session_data["context"] = context
            # Extend the expiration time
            session_data["expires_at"] = (datetime.utcnow() + timedelta(hours=24)).isoformat()

            # Calculate TTL based on the difference between new expires_at and created_at
            created_at = datetime.fromisoformat(session_data["created_at"].replace('Z', '+00:00'))
            expires_at = datetime.fromisoformat(session_data["expires_at"].replace('Z', '+00:00'))
            ttl_seconds = int((expires_at - created_at).total_seconds())

            return await self.save_state(session_id, session_data, ttl_seconds)

        return False

    async def save_conversation_state(self, user_id: str, conversation_data: Dict[str, Any],
                                    ttl_hours: int = 24) -> bool:
        """
        Save conversation state for a specific user.

        Args:
            user_id: User identifier
            conversation_data: Dictionary containing conversation state
            ttl_hours: Time-to-live in hours

        Returns:
            True if successful, False otherwise
        """
        key = f"conversation:{user_id}"
        ttl_seconds = ttl_hours * 3600
        return await self.save_state(key, conversation_data, ttl_seconds)

    async def get_conversation_state(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve conversation state for a specific user.

        Args:
            user_id: User identifier

        Returns:
            Conversation state dictionary or None if not found
        """
        key = f"conversation:{user_id}"
        return await self.get_state(key)

    async def clear_conversation_state(self, user_id: str) -> bool:
        """
        Clear conversation state for a specific user.

        Args:
            user_id: User identifier

        Returns:
            True if successful, False otherwise
        """
        key = f"conversation:{user_id}"
        return await self.delete_state(key)