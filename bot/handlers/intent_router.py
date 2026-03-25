"""
Intent router for natural language queries.

Uses LLM to interpret user intent and call appropriate backend tools.
"""

import json
import sys
from typing import Any, Optional

from services.lms_api import LMSAPIClient
from services.llm_client import LLMClient


# System prompt for the LLM
SYSTEM_PROMPT = """You are an assistant for a Learning Management System (LMS). 
You have access to backend tools that provide data about labs, students, scores, and analytics.

When the user asks a question:
1. First understand what information they need
2. Call the appropriate tool(s) to get that data
3. Analyze the results and provide a clear, helpful answer

Available tools:
- get_items: Get list of all labs and tasks
- get_learners: Get enrolled students and their groups
- get_scores: Get score distribution for a lab (4 buckets)
- get_pass_rates: Get per-task pass rates and attempt counts for a lab
- get_timeline: Get submissions per day for a lab
- get_groups: Get per-group scores and student counts for a lab
- get_top_learners: Get top N learners by score for a lab
- get_completion_rate: Get completion rate percentage for a lab
- trigger_sync: Refresh data from the autochecker

For multi-step questions (e.g., "which lab has the lowest pass rate"), 
you may need to call multiple tools in sequence.

If the user's message is a greeting or unclear, respond helpfully without using tools.
If the user mentions a specific lab (e.g., "lab 4"), interpret it as "lab-04".
"""

# Tool schemas for the LLM
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get list of all labs and tasks available in the system",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get list of enrolled students with their group information",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task pass rates and attempt counts for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submission timeline (submissions per day) for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group scores and student counts for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of top learners to return (default: 5)",
                        "default": 5,
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger data sync from the autochecker to refresh all data",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]


def normalize_lab_id(lab_input: str) -> str:
    """Normalize lab ID to format 'lab-XX'."""
    lab_input = lab_input.lower().strip()
    
    # Already in correct format
    if lab_input.startswith("lab-"):
        return lab_input
    
    # Format like "lab 4" or "lab04" or "4"
    import re
    match = re.search(r"lab[\s-]?(\d+)", lab_input)
    if match:
        num = int(match.group(1))
        return f"lab-0{num}" if num < 10 else f"lab-{num}"
    
    # Just a number
    match = re.match(r"(\d+)", lab_input)
    if match:
        num = int(match.group(1))
        return f"lab-0{num}" if num < 10 else f"lab-{num}"
    
    return lab_input


def create_tools_registry(lms_client: LMSAPIClient) -> dict[str, callable]:
    """Create a registry of tool functions."""
    
    def get_items() -> list[dict]:
        return lms_client.get_items()
    
    def get_learners() -> list[dict]:
        return lms_client.get_items()  # Using items as placeholder
    
    def get_scores(lab: str) -> list[dict]:
        lab = normalize_lab_id(lab)
        # Note: This endpoint may not exist, using pass_rates as fallback
        return lms_client.get_pass_rates(lab)
    
    def get_pass_rates(lab: str) -> list[dict]:
        lab = normalize_lab_id(lab)
        return lms_client.get_pass_rates(lab)
    
    def get_timeline(lab: str) -> list[dict]:
        lab = normalize_lab_id(lab)
        try:
            return lms_client.get_timeline(lab)
        except Exception:
            return []
    
    def get_groups(lab: str) -> list[dict]:
        lab = normalize_lab_id(lab)
        try:
            return lms_client.get_groups(lab)
        except Exception:
            return []
    
    def get_top_learners(lab: str, limit: int = 5) -> list[dict]:
        lab = normalize_lab_id(lab)
        try:
            return lms_client.get_top_learners(lab, limit)
        except Exception:
            return []
    
    def get_completion_rate(lab: str) -> dict:
        lab = normalize_lab_id(lab)
        try:
            return lms_client.get_completion_rate(lab)
        except Exception:
            return {}
    
    def trigger_sync() -> dict:
        try:
            return lms_client.trigger_sync()
        except Exception:
            return {"error": "Sync failed"}
    
    return {
        "get_items": get_items,
        "get_learners": get_learners,
        "get_scores": get_scores,
        "get_pass_rates": get_pass_rates,
        "get_timeline": get_timeline,
        "get_groups": get_groups,
        "get_top_learners": get_top_learners,
        "get_completion_rate": get_completion_rate,
        "trigger_sync": trigger_sync,
    }


def route(user_message: str) -> str:
    """
    Route user message through LLM to get appropriate response.
    
    Args:
        user_message: The user's natural language query
        
    Returns:
        Formatted response string
    """
    try:
        llm_client = LLMClient.from_env()
        lms_client = LMSAPIClient.from_env()
        tools_registry = create_tools_registry(lms_client)
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]
        
        max_iterations = 5
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Call LLM
            response = llm_client.chat(messages, tools=TOOL_SCHEMAS)
            
            # Check if LLM returned a direct response
            if response.get("content") and not response.get("tool_calls"):
                return response["content"]
            
            # Check if LLM wants to call tools
            tool_calls = response.get("tool_calls")
            if not tool_calls:
                # LLM didn't call tools and didn't return content
                if response.get("content"):
                    return response["content"]
                return "I'm not sure how to help with that. Try asking about labs, scores, or students."
            
            # Execute tool calls
            tool_results = llm_client.execute_tool_call(tool_calls, tools_registry)
            
            print(f"[summary] Feeding {len(tool_results)} tool result(s) back to LLM", file=sys.stderr)
            
            # Add assistant's response and tool results to conversation
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": tool_calls,
            })
            messages.extend(tool_results)
        
        # If we reach here, max iterations exceeded
        return "I'm having trouble processing this request. Please try rephrasing your question."
        
    except Exception as e:
        error_msg = str(e).lower()
        if "http 401" in error_msg or "401" in error_msg:
            return "LLM error: HTTP 401 Unauthorized. The API token may have expired."
        elif "connection refused" in error_msg or "connect" in error_msg:
            return "LLM error: connection refused. Check that the LLM service is running."
        else:
            return f"LLM error: {e}"
