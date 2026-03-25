# Bot Development Plan

## Overview

This document outlines the development plan for building a Telegram bot that interfaces with the LMS backend. The bot allows users to check system health, browse labs and scores, and ask questions in natural language using an LLM for intent routing.

## Architecture

### Task 1: Scaffold and Test Mode

**Goal:** Create a testable handler architecture where command logic is separated from the Telegram transport layer.

**Approach:**
- Create `bot/bot.py` as the entry point with `--test` mode support
- Handlers are plain functions that take a command string and return text
- The same handler functions work in `--test` mode, unit tests, and Telegram
- This pattern is called **Separation of Concerns** — business logic doesn't know about the transport layer

**Deliverables:**
- `bot/bot.py` — entry point with CLI argument parsing
- `bot/handlers/` — directory for command handlers
- `bot/config.py` — environment variable loading
- `bot/pyproject.toml` — bot dependencies
- `bot/PLAN.md` — this file

### Task 2: Backend Integration

**Goal:** Connect handlers to the LMS backend to fetch real data.

**Approach:**
- Create `bot/services/lms_api.py` — API client with Bearer token authentication
- Update handlers to call the API client instead of returning placeholders
- Handle errors gracefully (backend down, network issues)
- All configuration (URLs, keys) comes from environment variables

**Deliverables:**
- Working `/health`, `/labs`, `/scores` commands with real data
- Error handling with user-friendly messages

### Task 3: Natural Language Intent Routing

**Goal:** Allow users to ask questions in plain text, not just slash commands.

**Approach:**
- Create `bot/services/llm_client.py` — LLM client for tool calling
- Define tool descriptions for each backend endpoint
- Create `bot/handlers/intent_router.py` — uses LLM to determine user intent
- The LLM reads tool descriptions and decides which function to call
- **Key insight:** Description quality matters more than prompt engineering

**Deliverables:**
- LLM-powered intent router
- All 9 backend endpoints exposed as LLM tools
- Natural language queries like "what labs are available?"

### Task 4: Containerization and Deployment

**Goal:** Deploy the bot alongside the backend on the VM.

**Approach:**
- Create `bot/Dockerfile` — container image for the bot
- Add bot service to `docker-compose.yml`
- Configure Docker networking (containers use service names, not localhost)
- Document deployment process

**Deliverables:**
- Dockerized bot
- Updated `docker-compose.yml`
- Deployment documentation

## Testing Strategy

- **Unit tests:** Test handlers in isolation (mock API responses)
- **Test mode:** `uv run bot.py --test "/command"` for manual verification
- **Integration tests:** Test full flow through Telegram (manual)

## Dependencies

- `aiogram` or `python-telegram-bot` — Telegram client
- `httpx` or `aiohttp` — HTTP client for API calls
- `pydantic` — settings validation
- `python-dotenv` — environment file loading
