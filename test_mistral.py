#!/usr/bin/env python
"""
Скрипт для тестирования Mistral AI API
Запустите: python test_mistral.py
"""

import os
from dotenv import load_dotenv
from mistralai import Mistral, SDKError

load_dotenv()

def test_mistral_api():
    api_key = os.getenv('MISTRAL_API_KEY')

    if not api_key:
        print("❌ MISTRAL_API_KEY не найден в .env файле")
        return

    print("🔄 Тестирую Mistral AI API...")

    try:
        client = Mistral(api_key=api_key)

        # Тест 1: Получить список моделей
        print("📋 Получаю список доступных моделей...")
        models_response = client.models.list()
        models = [model.id for model in models_response.data]
        print(f"✅ Доступные модели: {models}")

        # Тест 2: Проверить каждую модель на capacity
        print("\n🔍 Проверяю доступность моделей...")
        test_models = ['mistral-small', 'mistral-medium', 'mistral-large-latest']

        for model in test_models:
            if model in models:
                try:
                    print(f"  Тестирую {model}...")
                    response = client.chat.complete(
                        model=model,
                        messages=[{"role": "user", "content": "Hello"}],
                        max_tokens=10
                    )
                    print(f"  ✅ {model}: Доступен")
                except SDKError as e:
                    if "capacity" in str(e).lower():
                        print(f"  ⚠️  {model}: Превышен лимит capacity")
                    elif "rate limit" in str(e).lower():
                        print(f"  ⚠️  {model}: Превышен rate limit")
                    else:
                        print(f"  ❌ {model}: Ошибка - {e}")
                except Exception as e:
                    print(f"  ❌ {model}: Неожиданная ошибка - {e}")

        print("\n🎉 Тестирование завершено!")

    except SDKError as e:
        if "401" in str(e):
            print("❌ Неверный API ключ")
        else:
            print(f"❌ Ошибка API: {e}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")

if __name__ == "__main__":
    test_mistral_api()