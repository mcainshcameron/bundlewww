import os
import httpx
from typing import List, Dict, Any, Optional, AsyncGenerator
import json


class OpenRouterService:
    """Service for interacting with OpenRouter API"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTERAPIKEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key not found in environment")

        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/bundlewww",
            "Content-Type": "application/json",
        }

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "anthropic/claude-3.5-sonnet",
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> str:
        """Make a chat completion request"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()

            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        model: str = "anthropic/claude-3.5-sonnet",
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> AsyncGenerator[str, None]:
        """Make a streaming chat completion request"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
            }

            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break

                        try:
                            data = json.loads(data_str)
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue


# Utility functions for common model selections
class ModelConfig:
    """Configuration for available LLM models"""

    # Available models from Available Models and Price.csv
    MODEL_NAMES = {
        "x-ai/grok-code-fast-1": "xAI: Grok Code Fast",
        "google/gemini-2.5-flash": "Google: Gemini 2.5 Flash",
        "anthropic/claude-sonnet-4.5": "Anthropic: Claude Sonnet 4.5",
        "xiaomi/mimo-v2-flash:free": "Xiaomi: MiMo-V2-Flash (Free)",
        "deepseek/deepseek-v3.2": "DeepSeek: DeepSeek V3.2",
        "google/gemini-3-flash-preview": "Google: Gemini 3 Flash Preview",
        "x-ai/grok-4.1-fast": "xAI: Grok 4.1 Fast",
        "anthropic/claude-opus-4.5": "Anthropic: Claude Opus 4.5",
        "google/gemini-2.5-flash-lite": "Google: Gemini 2.5 Flash Lite",
    }

    # Model pricing information ($/1M tokens) - from CSV
    MODEL_PRICING = {
        "x-ai/grok-code-fast-1": {"input": 0.20, "output": 1.50, "context": 256_000},
        "google/gemini-2.5-flash": {"input": 0.30, "output": 2.50, "context": 1_048_576},
        "anthropic/claude-sonnet-4.5": {"input": 3.00, "output": 15.00, "context": 1_000_000},
        "xiaomi/mimo-v2-flash:free": {"input": 0.00, "output": 0.00, "context": 262_144},
        "deepseek/deepseek-v3.2": {"input": 0.25, "output": 0.38, "context": 163_840},
        "google/gemini-3-flash-preview": {"input": 0.50, "output": 3.00, "context": 1_048_576},
        "x-ai/grok-4.1-fast": {"input": 0.20, "output": 0.50, "context": 2_000_000},
        "anthropic/claude-opus-4.5": {"input": 5.00, "output": 25.00, "context": 200_000},
        "google/gemini-2.5-flash-lite": {"input": 0.10, "output": 0.40, "context": 1_048_576},
    }

    @classmethod
    def get_model_for_project(cls, model_name: str) -> str:
        """Get OpenRouter model ID from display name"""
        # Map display names to model IDs
        name_to_id = {v: k for k, v in cls.MODEL_NAMES.items()}

        # Return model ID if found, otherwise return first model as fallback
        model_id = name_to_id.get(model_name, model_name)

        # CRITICAL: Verify the model is in our approved list
        if model_id not in cls.MODEL_NAMES:
            # Fallback to first model if somehow an invalid model was requested
            return list(cls.MODEL_NAMES.keys())[0]

        return model_id

    @classmethod
    def get_available_models(cls) -> dict:
        """Get list of available models with display names"""
        return cls.MODEL_NAMES

    @classmethod
    def get_model_pricing(cls, model_id: str) -> dict:
        """Get pricing information for a model"""
        return cls.MODEL_PRICING.get(model_id, {"input": 0, "output": 0, "context": 0})
