# Добавление новых LLM провайдеров

## Структура

Каждый провайдер должен:

1. Наследоваться от `BaseProvider`
2. Реализовывать методы:
   - `get_response(messages, model, **kwargs)` - получить ответ от LLM
   - `get_available_models()` - список доступных моделей
   - `validate_config()` - проверка конфигурации

## Шаги по добавлению нового провайдера

### 1. Создать файл провайдера

Создайте новый файл в папке `providers/`, например `anthropic_provider.py`:

```python
from .base_provider import BaseProvider
from your_library import YourClient

class YourProvider(BaseProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = YourClient(api_key=api_key)

    def get_response(self, messages, model, **kwargs):
        # Ваша логика получения ответа
        pass

    def get_available_models(self):
        return ['model1', 'model2']

    def validate_config(self):
        try:
            YourClient(api_key=self.api_key)
            return True
        except:
            return False
```

### 2. Добавить в реестр

В `__init__.py` добавьте импорт и регистрацию:

```python
from .your_provider import YourProvider

PROVIDER_REGISTRY = {
    'openai': OpenAIProvider,
    'your_provider': YourProvider,
}
```

### 3. Добавить настройки

В `settings.py` добавьте API ключ:

```python
YOUR_PROVIDER_API_KEY = os.getenv('YOUR_PROVIDER_API_KEY')
```

И список моделей:

```python
YOUR_PROVIDER_MODELS = [
    {'id': 'model1', 'name': 'Model 1'},
    {'id': 'model2', 'name': 'Model 2'},
]
```

### 4. Установить зависимости

Добавьте необходимые пакеты в `requirements.txt`:

```
your-library==1.0.0
```

### 5. Протестировать

Проверьте, что провайдер работает корректно в вашем приложении.

## Примеры

- `openai_provider.py` - пример для OpenAI
- `anthropic_provider.py` - пример для Anthropic (требует установки `anthropic`)

## Преимущества этой структуры

- **Модульность**: каждый провайдер в отдельном файле
- **Расширяемость**: легко добавлять новые провайдеры
- **Единообразие**: общий интерфейс для всех провайдеров
- **Изоляция**: ошибки в одном провайдере не влияют на другие