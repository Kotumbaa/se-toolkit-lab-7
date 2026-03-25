"""
Services for the LMS bot.

Services handle external dependencies (API calls, LLM, etc.).
Handlers call services and format the response for the user.
"""

from .lms_api import LMSAPIClient

__all__ = ["LMSAPIClient"]
