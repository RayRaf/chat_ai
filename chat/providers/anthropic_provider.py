from .base_provider import BaseProvider
from anthropic import Anthropic
from typing import List, Dict, Any


class AnthropicProvider(BaseProvider):
    """Провайдер для Anthropic Claude"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = Anthropic(api_key=api_key)

    def get_response(self, messages: List[Dict[str, str]], model: str, **kwargs) -> str:
        try:
            # Преобразовать сообщения в формат Anthropic
            system_message = ""
            conversation_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    conversation_messages.append(msg)

            response = self.client.messages.create(
                model=model,
                max_tokens=1024,
                system=system_message,
                messages=conversation_messages,
                **kwargs
            )
            return response.content[0].text
        except Exception as e:
            return f"Error: {str(e)}"

    def get_available_models(self) -> List[str]:
        return ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307']

    def validate_config(self) -> bool:
        try:
            Anthropic(api_key=self.api_key)
            return True
        except Exception:
            return False