from .base_provider import BaseProvider
import google.generativeai as genai
from typing import List, Dict, Any


class GoogleProvider(BaseProvider):
    """Провайдер для Google Gemini"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        genai.configure(api_key=api_key)
        self.model = None

    def get_response(self, messages: List[Dict[str, str]], model: str, **kwargs) -> str:
        try:
            # Преобразовать сообщения в формат Gemini
            conversation = []
            for msg in messages:
                role = "user" if msg["role"] == "user" else "model"
                conversation.append({"role": role, "parts": [msg["content"]]})

            model_instance = genai.GenerativeModel(model)
            response = model_instance.generate_content(conversation)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"

    def get_available_models(self) -> List[str]:
        return ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-1.0-pro']

    def validate_config(self) -> bool:
        try:
            genai.configure(api_key=self.api_key)
            return True
        except Exception:
            return False