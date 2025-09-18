from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseProvider(ABC):
    """Базовый класс для всех LLM провайдеров"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    @abstractmethod
    def get_response(self, messages: List[Dict[str, str]], model: str, **kwargs) -> str:
        """Получить ответ от LLM"""
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Получить список доступных моделей"""
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Проверить конфигурацию провайдера"""
        pass