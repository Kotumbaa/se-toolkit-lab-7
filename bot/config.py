"""
Configuration loading from environment files.

Loads secrets from .env.bot.secret using python-dotenv.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


def load_config():
    """Load environment variables from .env.bot.secret."""
    # Find the .env.bot.secret file in the bot directory
    bot_dir = Path(__file__).parent
    env_file = bot_dir / ".env.bot.secret"
    
    if env_file.exists():
        load_dotenv(env_file)
    
    # Also try loading from parent directory (for VM deployment)
    parent_env = bot_dir.parent / ".env.bot.secret"
    if parent_env.exists():
        load_dotenv(parent_env)
