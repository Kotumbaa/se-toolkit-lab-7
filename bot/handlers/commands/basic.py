"""
Basic command handlers for the LMS bot.

Handlers are plain functions that take input and return text.
They don't know about Telegram - same function works in --test mode,
unit tests, and the real Telegram bot.
"""

from services.lms_api import LMSAPIClient


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
    try:
        client = LMSAPIClient.from_env()
        result = client.health_check()
        return f"Backend is healthy. {result['items_count']} items available."
    except Exception as e:
        error_msg = str(e).lower()
        if "connection refused" in error_msg or "connect" in error_msg:
            return f"Backend error: connection refused. Check that the services are running."
        elif "http 502" in error_msg or "502" in error_msg:
            return f"Backend error: HTTP 502 Bad Gateway. The backend service may be down."
        elif "http 401" in error_msg or "401" in error_msg:
            return f"Backend error: HTTP 401 Unauthorized. Check your API key."
        else:
            return f"Backend error: {e}"


def handle_labs(user_input: str = "") -> str:
    """Handle /labs command - list available labs."""
    try:
        client = LMSAPIClient.from_env()
        items = client.get_items()
        labs = [item for item in items if item.get("type") == "lab"]
        if not labs:
            return "No labs found."
        lines = ["Available labs:"]
        for lab in labs:
            lines.append(f"- {lab['title']}")
        return "\n".join(lines)
    except Exception as e:
        error_msg = str(e).lower()
        if "connection refused" in error_msg or "connect" in error_msg:
            return f"Backend error: connection refused. Check that the services are running."
        elif "http 502" in error_msg or "502" in error_msg:
            return f"Backend error: HTTP 502 Bad Gateway. The backend service may be down."
        elif "http 401" in error_msg or "401" in error_msg:
            return f"Backend error: HTTP 401 Unauthorized. Check your API key."
        else:
            return f"Backend error: {e}"


def handle_scores(user_input: str = "") -> str:
    """Handle /scores command - get scores for a lab."""
    if not user_input:
        return "Please specify a lab, e.g., /scores lab-04"
    
    try:
        client = LMSAPIClient.from_env()
        pass_rates = client.get_pass_rates(user_input)
        if not pass_rates:
            return f"No scores found for {user_input}."
        lines = [f"Pass rates for {user_input}:"]
        for rate in pass_rates:
            task_name = rate.get("task_title", rate.get("task", "Unknown"))
            pass_rate = rate.get("pass_rate", 0) * 100
            attempts = rate.get("attempts", 0)
            lines.append(f"- {task_name}: {pass_rate:.1f}% ({attempts} attempts)")
        return "\n".join(lines)
    except Exception as e:
        error_msg = str(e).lower()
        if "connection refused" in error_msg or "connect" in error_msg:
            return f"Backend error: connection refused. Check that the services are running."
        elif "http 502" in error_msg or "502" in error_msg:
            return f"Backend error: HTTP 502 Bad Gateway. The backend service may be down."
        elif "http 401" in error_msg or "401" in error_msg:
            return f"Backend error: HTTP 401 Unauthorized. Check your API key."
        elif "not found" in error_msg or "404" in error_msg:
            return f"Lab '{user_input}' not found."
        else:
            return f"Backend error: {e}"
