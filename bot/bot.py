"""
Telegram bot entry point with --test mode support.

Usage:
    uv run bot.py              # Start Telegram bot
    uv run bot.py --test "/command"  # Test mode (no Telegram connection)
    uv run bot.py --test "question"  # Natural language query via LLM
"""

import argparse
import asyncio
import os
import sys

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

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


def build_main_keyboard() -> InlineKeyboardMarkup:
    """Create discoverable buttons for common bot actions."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Health", callback_data="cmd:/health"),
                InlineKeyboardButton(text="Labs", callback_data="cmd:/labs"),
            ],
            [
                InlineKeyboardButton(text="Scores Lab 1", callback_data="cmd:/scores lab-01"),
                InlineKeyboardButton(text="What can you do?", callback_data="cmd:/help"),
            ],
        ]
    )


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


async def run_telegram_bot() -> None:
    """Start the Telegram bot with command, callback, and plain-text handlers."""
    token = os.getenv("BOT_TOKEN", "")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set in .env.bot.secret")

    bot = Bot(token=token)
    dispatcher = Dispatcher()

    @dispatcher.message(CommandStart())
    async def start_command(message: Message) -> None:
        await message.answer(
            handle_start(),
            reply_markup=build_main_keyboard(),
        )

    @dispatcher.message(F.text == "/help")
    async def help_command(message: Message) -> None:
        await message.answer(
            handle_help(),
            reply_markup=build_main_keyboard(),
        )

    @dispatcher.message(F.text == "/health")
    async def health_command(message: Message) -> None:
        await message.answer(handle_health())

    @dispatcher.message(F.text == "/labs")
    async def labs_command(message: Message) -> None:
        await message.answer(handle_labs())

    @dispatcher.message(F.text.startswith("/scores"))
    async def scores_command(message: Message) -> None:
        command_text = message.text or ""
        await message.answer(handle_message(command_text))

    @dispatcher.callback_query(F.data.startswith("cmd:"))
    async def callback_command(callback: CallbackQuery) -> None:
        command_text = callback.data.removeprefix("cmd:")
        response = handle_message(command_text)
        await callback.message.answer(response)
        await callback.answer()

    @dispatcher.message(F.text)
    async def natural_language_message(message: Message) -> None:
        await message.answer(handle_message(message.text or ""))

    await dispatcher.start_polling(bot)


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

    asyncio.run(run_telegram_bot())


if __name__ == "__main__":
    main()
