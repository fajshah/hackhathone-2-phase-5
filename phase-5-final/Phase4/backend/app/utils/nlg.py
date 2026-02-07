from typing import Dict, List
import random

class NLGenerator:
    def __init__(self):
        # Templates for different types of responses
        self.templates = {
            "acknowledgment": [
                "I've noted that: {message}",
                "Got it! I'll remember: {message}",
                "Understood. I've added that to your tasks.",
                "Thanks for letting me know about: {message}",
                "Noted! I'll keep track of: {message}"
            ],
            "confirmation": [
                "Your request has been processed successfully!",
                "I've completed that action for you.",
                "All set! I've taken care of that.",
                "Done! I've handled your request.",
                "Success! Your task has been updated."
            ],
            "help": [
                "I can help you manage your tasks! You can ask me to create, update, list, or complete tasks.",
                "To create a task, just tell me what you need to do. For example: 'Add a task to buy groceries'",
                "You can ask me to list your tasks, mark them as complete, or set reminders.",
                "Try saying things like 'What are my tasks?' or 'Mark the meeting task as done'"
            ],
            "error": [
                "I'm sorry, I didn't quite understand that. Could you rephrase?",
                "Hmm, I'm having trouble with that request. Could you try again?",
                "I'm not sure how to handle that. Try asking in a different way.",
                "I couldn't process that. Could you be more specific?"
            ],
            "greeting": [
                "Hello! I'm your AI assistant for managing tasks. How can I help you today?",
                "Hi there! Ready to tackle your tasks? How can I assist?",
                "Greetings! I'm here to help you manage your tasks efficiently.",
                "Hey! I'm your personal task assistant. What would you like to do?"
            ],
            "task_created": [
                "I've created the task: '{task}'. It's now on your list!",
                "New task added: '{task}'. You can check it in your list.",
                "Task '{task}' has been added to your list. Don't forget to complete it!",
                "I've put '{task}' on your to-do list. Good luck!"
            ],
            "task_listed": [
                "Here are your tasks: {tasks}",
                "Your current tasks are: {tasks}",
                "I found these tasks for you: {tasks}",
                "Here's what you need to do: {tasks}"
            ],
            "task_completed": [
                "Great job! I've marked '{task}' as completed.",
                "Well done! '{task}' has been checked off your list.",
                "Task '{task}' is done! Nice work.",
                "I've marked '{task}' as finished. On to the next one!"
            ]
        }

    def generate_response(self, template_type: str, **kwargs) -> str:
        """Generate a response using the specified template type."""
        if template_type in self.templates:
            template = random.choice(self.templates[template_type])
            return template.format(**kwargs)
        else:
            return kwargs.get("message", "I understand.")

    def generate_task_response(self, intent: str, task_details: Dict = None) -> str:
        """Generate a response specific to task management."""
        if intent == "create_task" and task_details:
            return self.generate_response("task_created", task=task_details.get("title", "your task"))
        elif intent == "list_tasks":
            tasks = task_details.get("tasks", []) if task_details else []
            if tasks:
                task_list = ", ".join([task.get("title", "unnamed task") for task in tasks])
                return self.generate_response("task_listed", tasks=task_list)
            else:
                return "You don't have any tasks on your list right now."
        elif intent == "complete_task" and task_details:
            return self.generate_response("task_completed", task=task_details.get("title", "your task"))
        elif intent == "help":
            return self.generate_response("help")
        elif intent == "greeting":
            return self.generate_response("greeting")
        else:
            return self.generate_response("acknowledgment", message=task_details.get("title", "your request") if task_details else "your request")

# Global instance
nl_generator = NLGenerator()

def generate_response(template_type: str, **kwargs) -> str:
    """Generate a response using the specified template type."""
    return nl_generator.generate_response(template_type, **kwargs)

def generate_task_response(intent: str, task_details: Dict = None) -> str:
    """Generate a response specific to task management."""
    return nl_generator.generate_task_response(intent, task_details)