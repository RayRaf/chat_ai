from .base_provider import BaseProvider
from openai import OpenAI
from typing import List, Dict, Any, Optional
import time


class _ModelCache:
    """Simple in-memory cache for model listing to avoid frequent API calls."""
    models: Optional[list] = None
    fetched_at: float = 0.0
    ttl: int = 300  # seconds

    @classmethod
    def get(cls):
        if cls.models and (time.time() - cls.fetched_at) < cls.ttl:
            return cls.models
        return None

    @classmethod
    def set(cls, models):
        cls.models = models
        cls.fetched_at = time.time()


class OpenAIProvider(BaseProvider):
    """Провайдер для OpenAI"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = OpenAI(api_key=api_key)

    def get_response(self, messages: List[Dict[str, str]], model: str, **kwargs) -> str:
        try:
            # Validate model first
            available = self.get_available_models()
            if model not in available:
                return f"Error: Model '{model}' is not available for this API key."
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

    def get_available_models(self) -> List[str]:
        # Try to retrieve and cache models from the OpenAI API.
        cached = _ModelCache.get()
        if cached is not None:
            return cached
        try:
            # Newer OpenAI Python SDK exposes models list via client.models.list()
            models = self.client.models.list()
            # Extract ids
            model_ids = sorted({m.id for m in models.data})
            _ModelCache.set(model_ids)
            return model_ids
        except Exception:
            # Fallback to a conservative static list if API call fails
            return ['gpt-4o', 'gpt-4', 'gpt-3.5-turbo']

    def validate_config(self) -> bool:
        try:
            # Простая проверка - попытка создать клиента
            OpenAI(api_key=self.api_key)
            return True
        except Exception:
            return False