"""
Command handlers for the LMS bot.

Handlers are plain functions that take input and return text.
They don't know about Telegram - same function works in --test mode,
unit tests, and the real Telegram bot.
"""

from .basic import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
]
