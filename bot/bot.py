"""
Telegram bot entry point with --test mode support.

Usage:
    uv run bot.py              # Start Telegram bot
    uv run bot.py --test "/command"  # Test mode (no Telegram connection)
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

# Load environment variables from .env.bot.secret
load_config()


def handle_message(message: str) -> str:
    """Route message to appropriate handler."""
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
        return "Unknown command. Use /help to see available commands."


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
