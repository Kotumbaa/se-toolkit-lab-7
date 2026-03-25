"""
LLM client for tool-based interactions.

Communicates with the LLM API using OpenAI-compatible format.
Supports tool calling and multi-turn conversations.
"""

import json
import os
from typing import Any, Optional

import httpx


class LLMClient:
    """Client for LLM API with tool calling support."""

    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self._client: Optional[httpx.Client] = None

    @classmethod
    def from_env(cls) -> "LLMClient":
        """Create client from environment variables."""
        base_url = os.getenv("LLM_API_BASE_URL", "http://localhost:42005/v1")
        api_key = os.getenv("LLM_API_KEY", "")
        model = os.getenv("LLM_API_MODEL", "coder-model")
        return cls(base_url=base_url, api_key=api_key, model=model)

    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client with auth headers."""
        if self._client is None:
            self._client = httpx.Client(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=60.0,
            )
        return self._client

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        """
        Send a chat request to the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Optional list of tool schemas

        Returns:
            Response dict with 'content' and/or 'tool_calls'
        """
        client = self._get_client()
        
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        response = client.post(
            f"{self.base_url}/chat/completions",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        
        return data["choices"][0]["message"]

    def execute_tool_call(
        self,
        tool_calls: list[dict[str, Any]],
        tools_registry: dict[str, callable],
    ) -> list[dict[str, Any]]:
        """
        Execute tool calls and return results.

        Args:
            tool_calls: List of tool call dicts from LLM
            tools_registry: Dict mapping tool names to functions

        Returns:
            List of tool result messages for the conversation
        """
        results = []
        for tool_call in tool_calls:
            function = tool_call["function"]
            tool_name = function["name"]
            tool_args = json.loads(function["arguments"])
            
            print(f"[tool] LLM called: {tool_name}({tool_args})", file=__import__("sys").stderr)
            
            if tool_name in tools_registry:
                try:
                    result = tools_registry[tool_name](**tool_args)
                    result_str = json.dumps(result, default=str)
                    print(f"[tool] Result: {result_str[:100]}...", file=__import__("sys").stderr)
                except Exception as e:
                    result_str = f"Error: {e}"
                    print(f"[tool] Error: {e}", file=__import__("sys").stderr)
            else:
                result_str = f"Unknown tool: {tool_name}"
            
            results.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": result_str,
            })
        
        return results
