from .base_provider import BaseProvider
from openai import OpenAI
from typing import List, Dict, Any


class OpenAIProvider(BaseProvider):
    """Провайдер для OpenAI"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = OpenAI(api_key=api_key)

    def get_response(self, messages: List[Dict[str, str]], model: str, **kwargs) -> str:
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

    def get_available_models(self) -> List[str]:
        # В реальности можно получить список моделей через API
        # Для простоты возвращаем статический список
        return ['gpt-4o', 'gpt-4', 'gpt-3.5-turbo']

    def validate_config(self) -> bool:
        try:
            # Простая проверка - попытка создать клиента
            OpenAI(api_key=self.api_key)
            return True
        except Exception:
            return False