"""
Command handlers for the LMS bot.

Handlers are plain functions that take input and return text.
They don't know about Telegram - same function works in --test mode,
unit tests, and the real Telegram bot.
"""


def handle_start(user_input: str = "") -> str:
    """Handle /start command - welcome message."""
    return "Welcome! I'm your LMS assistant bot. Use /help to see available commands."


def handle_help(user_input: str = "") -> str:
    """Handle /help command - list available commands."""
    return """Available commands:
/start - Welcome message
/help - Show this help
/health - Check backend status
/labs - List available labs
/scores <lab> - Get scores for a lab"""


def handle_health(user_input: str = "") -> str:
    """Handle /health command - check backend health."""
    # TODO: Task 2 - call backend API
    return "Backend status: OK (placeholder)"


def handle_labs(user_input: str = "") -> str:
    """Handle /labs command - list available labs."""
    # TODO: Task 2 - call backend API
    return "Available labs: (placeholder)"


def handle_scores(user_input: str = "") -> str:
    """Handle /scores command - get scores for a lab."""
    # TODO: Task 2 - call backend API
    if user_input:
        return f"Scores for {user_input}: (placeholder)"
    return "Please specify a lab, e.g., /scores lab-04"
