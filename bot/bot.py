"""
Telegram bot entry point with --test mode support.

Usage:
    uv run bot.py              # Start Telegram bot
    uv run bot.py --test "/command"  # Test mode (no Telegram connection)
    uv run bot.py --test "question"  # Natural language query via LLM
"""

import argparse
import sys

from config import load_config
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)
from handlers.intent_router import route as route_intent

# Load environment variables from .env.bot.secret
load_config()


def handle_message(message: str) -> str:
    """Route message to appropriate handler or LLM intent router."""
    # Slash commands go to specific handlers
    if message.startswith("/start"):
        return handle_start(message[7:].strip())
    elif message.startswith("/help"):
        return handle_help(message[6:].strip())
    elif message.startswith("/health"):
        return handle_health(message[8:].strip())
    elif message.startswith("/labs"):
        return handle_labs(message[6:].strip())
    elif message.startswith("/scores"):
        return handle_scores(message[8:].strip())
    else:
        # Natural language queries go through LLM intent router
        return route_intent(message)


def main():
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="MESSAGE",
        help="Test mode: process a message and print response to stdout"
    )
    args = parser.parse_args()

    if args.test:
        # Test mode: call handler directly and print result
        response = handle_message(args.test)
        print(response)
        sys.exit(0)

    # TODO: Task 2+ - Start Telegram bot
    print("Telegram bot starting (not implemented yet)")
    print("Run with --test mode for offline testing")


if __name__ == "__main__":
    main()
