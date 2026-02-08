"""
Todo AI Agent for the Todo AI Chatbot.
Handles natural language processing and task operations using OpenAI API.
"""
from typing import Dict, Any, List, Optional
import openai
import json
import logging
from datetime import datetime

from ..config import settings
from ..mcp.server import mcp_server

# Initialize AI client based on provider
if settings.AI_PROVIDER == "openrouter":
    client = openai.OpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )
    model = settings.OPENROUTER_MODEL
else:
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    model = settings.OPENAI_MODEL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set OpenAI API key
openai.api_key = settings.OPENAI_API_KEY

class TodoAgent:
    """
    AI Agent for handling todo-related operations through natural language.
    Uses OpenAI API to interpret user requests and execute appropriate MCP tools.
    """

    def __init__(self):
        """
        Initialize the Todo Agent with configuration settings.
        """
        # Use the model based on the configured AI provider
        if settings.AI_PROVIDER == "openrouter":
            self.model = settings.OPENROUTER_MODEL
        else:
            self.model = settings.OPENAI_MODEL
        # Maintain conversation states in memory (in production, this would be in a cache like Redis)
        self.conversation_states = {}
        logger.info(f"Todo Agent initialized with model: {self.model} using provider: {settings.AI_PROVIDER}")

    def process_request(
        self,
        session,
        user_input: str,
        user_token: str,
        conversation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process a user request and return an appropriate response.

        Args:
            session: Database session
            user_input: The natural language input from the user
            user_token: The authentication token for the user
            conversation_id: Optional conversation ID for context

        Returns:
            Dictionary with response and any tool calls executed
        """
        logger.info(f"Processing user request: {user_input[:50]}...")

        # Get the user from the token for conversation history
        from ..auth import auth_service
        from ..models.user import User
        from sqlmodel import select

        user_payload = auth_service.decode_access_token(user_token)
        if not user_payload:
            raise ValueError("Invalid or expired token")

        user_id = user_payload.get("sub")
        user_stmt = select(User).where(User.id == int(user_id))
        user = session.exec(user_stmt).first()

        # Prepare the prompt for the AI model
        prompt = self._construct_prompt(session, user_input, user, conversation_id)

        # Check for ambiguous requests before processing
        clarification_needed = self._detect_ambiguous_request(user_input, session, user)
        if clarification_needed:
            return {
                "response": clarification_needed,
                "tool_calls": [],
                "tool_results": [],
                "requires_clarification": True
            }

        try:
            # Validate that API key is properly configured based on the provider
            if settings.AI_PROVIDER == "openrouter":
                if not settings.OPENROUTER_API_KEY or settings.OPENROUTER_API_KEY == "":
                    logger.error("OpenRouter API key not configured properly")
                    return {
                        "response": "I'm sorry, I'm not properly configured to process your request. Please contact the administrator to set up the OpenRouter API key.",
                        "tool_calls": [],
                        "error": "OpenRouter API key not configured"
                    }
            else:  # openai provider
                if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "" or settings.OPENAI_API_KEY == "your_openai_api_key_here":
                    logger.error("OpenAI API key not configured properly")
                    return {
                        "response": "I'm sorry, I'm not properly configured to process your request. Please contact the administrator to set up the OpenAI API key.",
                        "tool_calls": [],
                        "error": "OpenAI API key not configured"
                    }

            # Call the OpenAI API to determine the appropriate action
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for more deterministic responses
                max_tokens=500,
                tools=[{"type": "function", "function": func} for func in self._get_available_functions()],
                tool_choice="auto"  # Let the model decide when to call functions
            )

            # Process the response
            return self._process_ai_response(response, user_token)

        except openai.AuthenticationError as e:
            logger.error(f"OpenAI Authentication Error: {str(e)}")
            return {
                "response": "I'm sorry, there's an issue with my AI configuration. Please contact the administrator.",
                "tool_calls": [],
                "error": f"Authentication error: {str(e)}"
            }
        except openai.RateLimitError as e:
            logger.error(f"OpenAI Rate Limit Error: {str(e)}")
            return {
                "response": "I'm sorry, I'm currently experiencing high demand. Please try again in a moment.",
                "tool_calls": [],
                "error": f"Rate limit exceeded: {str(e)}"
            }
        except openai.APIConnectionError as e:
            logger.error(f"OpenAI Connection Error: {str(e)}")
            return {
                "response": "I'm sorry, I'm having trouble connecting to my AI services. Please try again later.",
                "tool_calls": [],
                "error": f"Connection error: {str(e)}"
            }
        except openai.APIError as e:
            logger.error(f"OpenAI API Error: {str(e)}")
            # Return a helpful mock response when API fails
            error_msg = str(e)
            if "402" in error_msg or "limit exceeded" in error_msg.lower() or "payment required" in error_msg.lower():
                # This is a billing/token limit issue - return a helpful response
                return {
                    "response": "I'm sorry, I've reached my AI service usage limits. As a backup, I can still help you manage your tasks. Try asking me to create, list, update, or complete tasks!",
                    "tool_calls": [],
                    "error": f"API usage limit reached: {error_msg}"
                }
            else:
                return {
                    "response": "I'm sorry, I encountered an error with my AI services. Please try again.",
                    "tool_calls": [],
                    "error": f"API error: {error_msg}"
                }
        except Exception as e:
            logger.error(f"Unexpected error processing request: {str(e)}", exc_info=True)
            return {
                "response": "I'm sorry, I encountered an error processing your request. Please try again.",
                "tool_calls": [],
                "error": str(e)
            }

    def _construct_prompt(self, session, user_input: str, user, conversation_id: Optional[int]) -> str:
        """
        Construct the prompt to send to the AI model.

        Args:
            session: Database session
            user_input: The user's natural language input
            user: The authenticated user object
            conversation_id: Optional conversation ID for context

        Returns:
            Formatted prompt string
        """
        # If we have a conversation ID, retrieve conversation history for context
        if conversation_id:
            # Import here to avoid circular imports
            from ..services.conversation_service import ConversationService

            try:
                # Get the conversation history using the service
                messages = ConversationService.get_conversation_history(
                    session=session,
                    conversation_id=conversation_id,
                    user=user,
                    limit=10  # Get last 10 messages for context
                )

                # Format the conversation history
                history_text = ""
                if messages:
                    history_text = "Previous conversation:\n"
                    for msg in messages[-10:]:  # Last 10 messages
                        role = getattr(msg, 'role', 'unknown')
                        content = getattr(msg, 'content', '')
                        history_text += f"{role.capitalize()}: {content}\n"
                    history_text += "\n"

                return f"{history_text}User request: {user_input}"
            except Exception as e:
                logger.warning(f"Could not retrieve conversation history: {e}")
                # Fall back to just the user input if history retrieval fails
                return f"User request: {user_input}"
        else:
            return f"User request: {user_input}"

    def _resolve_contextual_reference(self, session, user, user_input: str, conversation_id: Optional[int] = None) -> Optional[int]:
        """
        Resolve contextual references like "the last one", "that task", etc.

        Args:
            session: Database session
            user: Authenticated user object
            user_input: The user's input that may contain contextual references
            conversation_id: Optional conversation ID for additional context

        Returns:
            Task ID if a specific task is identified, None otherwise
        """
        # Check for common contextual reference patterns
        import re

        # Look for patterns indicating reference to a specific task
        last_task_patterns = [
            r"(?:the\s+)?last\s+(?:one|task)",
            r"(?:the\s+)?previous\s+task",
            r"that\s+task",
            r"the\s+first\s+(?:one|task)",
            r"the\s+most\s+recent\s+(?:one|task)"
        ]

        for pattern in last_task_patterns:
            if re.search(pattern, user_input.lower()):
                # Get the user's tasks to determine which one they mean
                from ..services.task_service import TaskService

                # Get all tasks, ordered by creation date (most recent first for "last" reference)
                all_tasks = TaskService.get_user_tasks(session, user)

                if not all_tasks:
                    return None

                if "last" in pattern or "previous" in pattern or "that" in pattern or "recent" in pattern:
                    # Return the most recently created task
                    return max(all_tasks, key=lambda t: t.created_at).id
                elif "first" in pattern:
                    # Return the earliest created task
                    return min(all_tasks, key=lambda t: t.created_at).id

        # Look for numbered references like "task #2" or "task 2"
        number_match = re.search(r"task\s+#?(\d+)", user_input.lower())
        if number_match:
            task_number = int(number_match.group(1))

            # Get all tasks and find the one with the specified number/index
            from ..services.task_service import TaskService
            all_tasks = TaskService.get_user_tasks(session, user)

            # Sort tasks by ID to match the user's numbering
            sorted_tasks = sorted(all_tasks, key=lambda t: t.id)

            if 1 <= task_number <= len(sorted_tasks):
                return sorted_tasks[task_number - 1].id

        return None

    def _detect_ambiguous_request(self, user_input: str, session, user) -> Optional[str]:
        """
        Detect if the user's request is ambiguous and needs clarification.

        Args:
            user_input: The user's natural language input
            session: Database session
            user: The authenticated user object

        Returns:
            String with clarification request if ambiguous, None otherwise
        """
        import re

        # Check for ambiguous references like "the first task" when multiple tasks exist
        ambiguous_patterns = [
            (r"first\s+task", "first_task"),
            (r"first\s+one", "first_one"),
            (r"last\s+task", "last_task"),
            (r"last\s+one", "last_one"),
            (r"that\s+task", "that_task"),
            (r"the\s+other\s+one", "other_one"),
            (r"another\s+task", "another_task")
        ]

        user_input_lower = user_input.lower()

        for pattern, category in ambiguous_patterns:
            if re.search(pattern, user_input_lower):
                # Check if the user has multiple tasks that could match this reference
                from ..services.task_service import TaskService
                user_tasks = TaskService.get_tasks_by_user(session, user)

                if len(user_tasks) > 1:
                    # For "first" or "last" references, check if the intent is clear
                    if category in ["first_task", "first_one", "last_task", "last_one"]:
                        # These might be okay if context is clear, so don't always flag as ambiguous
                        pass
                    else:
                        # For other ambiguous references, ask for clarification
                        return f"I found {len(user_tasks)} tasks in your list. Could you be more specific about which task you mean?"

        # Check for ambiguous task identification like "task #2" when it's unclear
        number_matches = re.findall(r"task\s+#?(\d+)", user_input_lower)
        for num_str in number_matches:
            task_num = int(num_str)
            from ..services.task_service import TaskService
            user_tasks = TaskService.get_tasks_by_user(session, user)

            # Sort tasks by ID to match the user's numbering
            sorted_tasks = sorted(user_tasks, key=lambda t: t.id)

            if task_num > len(sorted_tasks):
                return f"I couldn't find task #{task_num}. You currently have {len(sorted_tasks)} tasks. Could you clarify which task you mean?"

        # Check for requests that could apply to multiple tasks
        action_patterns = [
            r"complete.*all",
            r"delete.*all",
            r"mark.*all.*done",
            r"remove.*all"
        ]

        for pattern in action_patterns:
            if re.search(pattern, user_input_lower):
                from ..services.task_service import TaskService
                user_tasks = TaskService.get_tasks_by_user(session, user)

                if len(user_tasks) > 1:
                    return f"You have {len(user_tasks)} tasks. Are you sure you want to perform this action on all of them?"

        # No ambiguity detected
        return None

    def _update_conversation_state(self, conversation_id: int, state_data: dict):
        """
        Update the state for a specific conversation.

        Args:
            conversation_id: The ID of the conversation
            state_data: Dictionary containing state information to update
        """
        if conversation_id not in self.conversation_states:
            self.conversation_states[conversation_id] = {}

        # Update the conversation state with new data
        self.conversation_states[conversation_id].update(state_data)

    def _get_conversation_state(self, conversation_id: int) -> dict:
        """
        Get the current state for a specific conversation.

        Args:
            conversation_id: The ID of the conversation

        Returns:
            Dictionary containing the conversation state (empty if none exists)
        """
        return self.conversation_states.get(conversation_id, {})

    def _clear_conversation_state(self, conversation_id: int):
        """
        Clear the state for a specific conversation.

        Args:
            conversation_id: The ID of the conversation
        """
        if conversation_id in self.conversation_states:
            del self.conversation_states[conversation_id]

    def _get_system_prompt(self) -> str:
        """
        Get the system prompt that defines the agent's behavior.

        Returns:
            System prompt string
        """
        return """
        You are a helpful todo list assistant. Your job is to interpret user requests and
        call the appropriate functions to manage their tasks. Here are the functions available:

        1. add_task: Use this when the user wants to create/add a new task.
           Parameters: title (required), description (optional)

        2. list_tasks: Use this when the user wants to see their tasks.
           Parameters: status (optional, values: all, pending, in_progress, completed, cancelled),
                      priority (optional, values: low, medium, high, urgent),
                      sort_by (optional, values: created_at, due_date, priority, status),
                      order (optional, values: asc, desc),
                      due_date_start (optional, ISO format date-time),
                      due_date_end (optional, ISO format date-time)

        3. complete_task: Use this when the user wants to mark a task as completed.
           Parameters: task_id (required), confirm (optional boolean for important tasks)

        4. delete_task: Use this when the user wants to remove a task.
           Parameters: task_id (required), confirm (optional boolean for important tasks)

        5. update_task: Use this when the user wants to modify a task.
           Parameters: task_id (required), title (optional), description (optional)

        6. create_conversation: Use this when starting a new conversation.
           Parameters: title (optional), description (optional)

        7. get_conversation_history: Use this to get conversation history.
           Parameters: conversation_id (required)

        8. store_message: Use this to store messages in the conversation.
           Parameters: conversation_id (required), role (required), content (required)

        When the user makes a request using contextual references like "the last one",
        "that task", "the previous task", "the first one", etc., you should first call
        list_tasks to get the user's tasks and then determine which task they are referring to.

        For example:
        - If a user says "Complete the last task", first call list_tasks to get all tasks,
          then identify the most recently created task and call complete_task with its ID.
        - If a user says "Update that task", first call list_tasks, then identify the
          task they're referring to based on the conversation context, then call update_task.

        Choose the most appropriate function based on the user's request.
        For ambiguous requests, ask the user for clarification.
        """

    def _get_available_functions(self) -> List[Dict[str, Any]]:
        """
        Define the functions available to the AI model.

        Returns:
            List of function definitions
        """
        return [
            {
                "name": "add_task",
                "description": "Add a new task to the user's todo list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The title of the task"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional description of the task"
                        }
                    },
                    "required": ["title"]
                }
            },
            {
                "name": "list_tasks",
                "description": "List the user's tasks with optional filtering and sorting",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["all", "pending", "in_progress", "completed", "cancelled"],
                            "description": "Filter tasks by status"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "Filter tasks by priority"
                        },
                        "sort_by": {
                            "type": "string",
                            "enum": ["created_at", "due_date", "priority", "status"],
                            "description": "Field to sort tasks by"
                        },
                        "order": {
                            "type": "string",
                            "enum": ["asc", "desc"],
                            "description": "Sort order (ascending or descending)"
                        },
                        "due_date_start": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Filter tasks with due date on or after this date (ISO format)"
                        },
                        "due_date_end": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Filter tasks with due date on or before this date (ISO format)"
                        }
                    }
                }
            },
            {
                "name": "complete_task",
                "description": "Mark a task as completed",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to complete"
                        },
                        "confirm": {
                            "type": "boolean",
                            "description": "Whether to require confirmation before completing the task (use for important tasks)"
                        }
                    },
                    "required": ["task_id"]
                }
            },
            {
                "name": "delete_task",
                "description": "Delete a task from the user's list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to delete"
                        },
                        "confirm": {
                            "type": "boolean",
                            "description": "Whether to require confirmation before deleting the task (recommended for important tasks)"
                        }
                    },
                    "required": ["task_id"]
                }
            },
            {
                "name": "update_task",
                "description": "Update the title or description of a task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "The new title for the task (optional)"
                        },
                        "description": {
                            "type": "string",
                            "description": "The new description for the task (optional)"
                        }
                    },
                    "required": ["task_id"]
                }
            },
            {
                "name": "create_conversation",
                "description": "Create a new conversation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Optional title for the conversation"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional description for the conversation"
                        }
                    }
                }
            },
            {
                "name": "get_conversation_history",
                "description": "Get the history of a conversation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "conversation_id": {
                            "type": "integer",
                            "description": "The ID of the conversation to retrieve"
                        }
                    },
                    "required": ["conversation_id"]
                }
            },
            {
                "name": "store_message",
                "description": "Store a message in a conversation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "conversation_id": {
                            "type": "integer",
                            "description": "The ID of the conversation"
                        },
                        "role": {
                            "type": "string",
                            "enum": ["user", "assistant", "system"],
                            "description": "The role of the message sender"
                        },
                        "content": {
                            "type": "string",
                            "description": "The content of the message"
                        }
                    },
                    "required": ["conversation_id", "role", "content"]
                }
            }
        ]

    def _process_ai_response(self, response: Any, user_token: str) -> Dict[str, Any]:
        """
        Process the response from the AI model and execute any function calls.

        Args:
            response: The response from the OpenAI API
            user_token: The user's authentication token

        Returns:
            Dictionary with the agent's response and any tool calls executed
        """
        # Extract the response message
        choice = response.choices[0]
        message = choice.message

        result = {
            "response": "",
            "tool_calls": [],
            "tool_results": []
        }

        # Check if the model wanted to call a function
        if message.tool_calls:
            # Process each tool call
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                logger.info(f"Tool call requested: {function_name} with args: {function_args}")

                # Execute the tool via the MCP server
                try:
                    tool_result = mcp_server.execute_tool(function_name, function_args, user_token)
                    result["tool_calls"].append({
                        "name": function_name,
                        "arguments": function_args,
                        "result": tool_result
                    })
                    result["tool_results"].append(tool_result)

                    # Generate a response based on the tool result
                    result["response"] = self._generate_response_from_tool_result(tool_result, function_name)

                except Exception as e:
                    logger.error(f"Error executing tool {function_name}: {str(e)}", exc_info=True)
                    result["response"] = f"I'm sorry, I encountered an error executing that command: {str(e)}"
        else:
            # If no tool call was made, use the model's message content
            result["response"] = message.content or "I processed your request."

        return result

    def _generate_response_from_tool_result(self, tool_result: Dict[str, Any], function_name: str) -> str:
        """
        Generate a natural language response based on the tool result.

        Args:
            tool_result: The result from executing an MCP tool
            function_name: The name of the function that was called

        Returns:
            Natural language response string
        """
        if not tool_result.get("success", True):
            error_msg = tool_result.get("error", "Unknown error occurred")
            return f"I'm sorry, I couldn't complete that action: {error_msg}"

        result = tool_result.get("result", {})

        # Generate response based on the function that was called
        if function_name == "add_task":
            return f"I've added the task '{result.get('title', 'unnamed task')}' to your list."
        elif function_name == "list_tasks":
            tasks = result.get("tasks", [])
            if not tasks:
                return "You don't have any tasks on your list."

            task_list = []
            for task in tasks[:5]:  # Show first 5 tasks to avoid verbosity
                status = "✓" if task.get("completed", False) else "○"
                task_list.append(f"{status} {task.get('title', 'unnamed task')}")

            if len(tasks) > 5:
                return f"You have {len(tasks)} tasks. Here are the first 5:\n" + "\n".join(task_list) + f"\n\nAnd {len(tasks) - 5} more..."
            else:
                return f"You have {len(tasks)} tasks:\n" + "\n".join(task_list)
        elif function_name == "complete_task":
            if result.get("success", False):
                return f"I've marked the task as completed."
            else:
                return result.get("error", "I couldn't complete that task.")
        elif function_name == "delete_task":
            return f"I've removed the task from your list."
        elif function_name == "update_task":
            return f"I've updated the task for you."
        elif function_name == "create_conversation":
            return f"I've started a new conversation for you."
        elif function_name == "get_conversation_history":
            msg_count = result.get("message_count", 0)
            return f"I retrieved the conversation history with {msg_count} messages."
        elif function_name == "store_message":
            return f"I've saved your message."
        else:
            return "I've completed the requested action."


# Create a singleton instance of the Todo Agent
todo_agent = TodoAgent()