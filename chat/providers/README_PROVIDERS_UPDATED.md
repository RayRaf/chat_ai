# Добавление новых LLM провайдеров

## Структура

- `base_provider.py` - Абстрактный базовый класс для всех провайдеров
- `openai_provider.py` - Реализация для OpenAI
- `anthropic_provider.py` - Пример реализации для Anthropic Claude
- `google_provider.py` - Пример реализации для Google Gemini
- `mistral_provider.py` - Реализация для Mistral AI
- `__init__.py` - Реестр провайдеров и фабричная функция
- `README_PROVIDERS.md` - Подробная инструкция по добавлению новых провайдеров

## Быстрый старт с Mistral AI

1. **Установите пакет:**
   ```bash
   pip install mistralai
   ```

2. **Добавьте API ключ в `.env`:**
   ```
   MISTRAL_API_KEY=your_mistral_api_key_here
   ```

3. **Раскомментируйте в `providers/__init__.py`:**
   ```python
   from .mistral_provider import MistralProvider
   PROVIDER_REGISTRY['mistral'] = MistralProvider
   ```

4. **Готово!** Mistral AI теперь доступен в интерфейсе вашего аггрегатора.

## Доступные модели Mistral AI

- `mistral-large-latest` - Самая мощная модель
- `mistral-medium` - Средняя модель
- `mistral-small` - Быстрая модель
- `mistral-7b-instruct` - 7B параметров
- `mistral-8x7b-instruct` - 8x7B параметров

## Шаги по добавлению нового провайдера

### 1. Создайте файл провайдера

Создайте новый файл `your_provider_provider.py` в папке `providers/`.

Пример структуры:

```python
from .base_provider import BaseProvider
from your_library import YourClient
from typing import List, Dict, Any


class YourProviderProvider(BaseProvider):
    """Провайдер для Your Provider"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = YourClient(api_key=api_key)

    def get_response(self, messages, model, **kwargs):
        # Ваш код для получения ответа
        response = self.client.generate(messages, model=model, **kwargs)
        return response.text

    def get_available_models(self):
        return ['model1', 'model2', 'model3']

    def validate_config(self):
        try:
            YourClient(api_key=self.api_key)
            return True
        except:
            return False
```

### 2. Добавьте API ключ в settings.py

```python
# В chat_ai/settings.py
YOURPROVIDER_API_KEY = os.getenv('YOURPROVIDER_API_KEY')
```

### 3. Зарегистрируйте провайдера

В `providers/__init__.py`:

```python
from .your_provider_provider import YourProviderProvider

PROVIDER_REGISTRY: Dict[str, Type[BaseProvider]] = {
    'openai': OpenAIProvider,
    'yourprovider': YourProviderProvider,  # Добавьте сюда
}
```

### 4. Установите необходимые пакеты

```bash
pip install your-library
```

### 5. Использование

В коде вы можете использовать провайдера:

```python
from chat.providers import get_provider

provider = get_provider('yourprovider')
response = provider.get_response(messages, model)
```

## Примечания

- Все провайдеры наследуются от `BaseProvider`
- API ключи хранятся в переменных окружения
- Сообщения передаются в стандартном формате OpenAI (role: user/assistant, content)
- Обработка ошибок должна возвращать строку с описанием ошибки