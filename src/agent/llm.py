import requests
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class OllamaClient:
    """
    Client for interacting with a local Ollama instance.
    """

    def __init__(
        self, base_url: str = "http://localhost:11434", model: str = "gemma:2b"
    ):
        self.base_url = base_url
        self.model = model

    def chat(self, messages: List[Dict[str, str]], json_mode: bool = False) -> str:
        """
        Send a chat request to Ollama.
        """
        url = f"{self.base_url}/api/chat"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }

        if json_mode:
            payload["format"] = "json"

        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")

        except Exception as e:
            logger.error(f"Ollama chat failed: {e}")
            raise e

    def generate_plan(self, user_goal: str) -> Dict[str, Any]:
        """
        Specific helper to generate a structured scraping plan.
        """
        system_prompt = """
        You are the Brain of an autonomous scraping agent.
        Your goal is to convert a user request into a structured JSON execution plan.
        
        The plan should include:
        1. interpretation: A brief summary of what you understood.
        2. search_queries: A list of 1-5 specific Google search queries to find the target URLs.
        3. target_description: A description of what kind of URLs we are looking for.
        4. force_js (boolean): Set to true if the user implies dynamic sites (SPA, React, Twitter, etc).
        
        Output ONLY valid JSON.
        Example:
        {
            "interpretation": "User wants to find coffee shops in NYC.",
            "search_queries": ["best coffee shops nyc", "top rated cafes manhattan", "coffee roasters brooklyn"],
            "target_description": "Coffee shop websites and directories",
            "force_js": false
        }
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_goal},
        ]

        response_text = self.chat(messages, json_mode=True)

        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback simple repair if model chatters
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end != -1:
                return json.loads(response_text[start:end])
            raise ValueError("Could not parse JSON from LLM response")
