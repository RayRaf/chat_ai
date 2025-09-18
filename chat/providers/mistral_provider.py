from .base_provider import BaseProvider
from mistralai import Mistral, SDKError
from typing import List, Dict, Any


class MistralProvider(BaseProvider):
    """Провайдер для Mistral AI"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = Mistral(api_key=api_key)

    def get_response(self, messages: List[Dict[str, str]], model: str, **kwargs) -> str:
        try:
            # Преобразовать сообщения в формат Mistral
            mistral_messages = []
            for msg in messages:
                role = msg["role"]
                if role == "assistant":
                    role = "assistant"
                elif role == "system":
                    role = "system"
                else:
                    role = "user"
                mistral_messages.append({"role": role, "content": msg["content"]})

            response = self.client.chat.complete(
                model=model,
                messages=mistral_messages,
                **kwargs
            )
            return response.choices[0].message.content

        except SDKError as e:
            # Обработка специфичных ошибок Mistral AI
            error_code = getattr(e, 'status_code', None) or getattr(e, 'code', None)
            error_message = getattr(e, 'message', str(e)) or str(e)

            if error_code == 429 or "capacity" in error_message.lower() or "rate limit" in error_message.lower():
                return "❌ Mistral AI Capacity Exceeded\n\n" \
                       "The selected model is currently at full capacity. Solutions:\n" \
                       "• Switch to 'Mistral Medium' or 'Mistral Small' models\n" \
                       "• Upgrade your Mistral AI subscription plan\n" \
                       "• Try again in a few minutes\n" \
                       "• Use OpenAI provider as alternative"

            elif error_code == 401 or "unauthorized" in error_message.lower():
                return "❌ Invalid API Key\n\n" \
                       "Please check your MISTRAL_API_KEY in the .env file.\n" \
                       "Get your API key from: https://mistral.ai/"

            elif error_code == 400:
                return "❌ Bad Request\n\n" \
                       "Please check your message format and try again."

            elif error_code == 403:
                return "❌ Forbidden\n\n" \
                       "Access denied. Please check your account permissions."

            else:
                return f"❌ Mistral AI Error ({error_code})\n\n{error_message}"

        except Exception as e:
            return f"Error: Unexpected error with Mistral AI: {str(e)}"

    def get_available_models(self) -> List[str]:
        return [
            'mistral-small',        # Самая доступная модель
            'mistral-medium',       # Средняя производительность
            'mistral-large-latest', # Самая мощная (может быть ограничена)
            'mistral-7b-instruct',  # 7B параметров
            'mistral-8x7b-instruct' # 8x7B параметров
        ]

    def validate_config(self) -> bool:
        try:
            # Попробуем получить список моделей для проверки API ключа
            self.client.models.list()
            return True
        except Exception as e:
            print(f"Mistral API validation failed: {e}")
            return False