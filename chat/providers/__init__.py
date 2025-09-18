# Providers package
from .base_provider import BaseProvider
from .openai_provider import OpenAIProvider
# from .anthropic_provider import AnthropicProvider  # Раскомментируйте после установки anthropic
# from .google_provider import GoogleProvider  # Раскомментируйте после установки google-generativeai
from .mistral_provider import MistralProvider  # Раскомментируйте после установки mistralai
from typing import Dict, Type
from django.conf import settings


# Реестр провайдеров
PROVIDER_REGISTRY: Dict[str, Type[BaseProvider]] = {
    'openai': OpenAIProvider,
    # Добавляйте новые провайдеры здесь
    # 'anthropic': AnthropicProvider,  # Раскомментируйте после установки anthropic
    # 'google': GoogleProvider,  # Раскомментируйте после установки google-generativeai
    'mistral': MistralProvider,  # Раскомментируйте после установки mistralai
}


def get_provider(provider_name: str) -> BaseProvider:
    """Получить экземпляр провайдера по имени"""
    provider_class = PROVIDER_REGISTRY.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider_name}")

    # Получить API ключ из настроек
    api_key_attr = f"{provider_name.upper()}_API_KEY"
    api_key = getattr(settings, api_key_attr, None)
    if not api_key:
        raise ValueError(f"API key not found for provider: {provider_name}")

    return provider_class(api_key=api_key)