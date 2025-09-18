from ..models import Chat, Message
from ..providers import get_provider
from typing import List, Dict, Any


class ChatService:
    """Сервис для управления чатами и сообщениями"""

    @staticmethod
    def create_chat() -> Chat:
        """Создать новый чат"""
        return Chat.objects.create()

    @staticmethod
    def send_message(chat_id: int, content: str, provider: str = 'openai', model: str = 'gpt-4o') -> Dict[str, Any]:
        """Отправить сообщение и получить ответ от AI"""
        chat = Chat.objects.get(id=chat_id)

        # Сохранить сообщение пользователя
        user_message = Message.objects.create(
            chat=chat,
            content=content,
            is_user=True,
            provider=provider,
            model=model
        )

        # Получить все сообщения для контекста
        all_messages = chat.messages.all().order_by('created_at')
        messages_for_api = []
        for msg in all_messages:
            role = "user" if msg.is_user else "assistant"
            messages_for_api.append({"role": role, "content": msg.content})

        # Получить провайдера и ответ
        provider_instance = get_provider(provider)
        ai_content = provider_instance.get_response(messages_for_api, model)

        # Сохранить ответ AI
        ai_message = Message.objects.create(
            chat=chat,
            content=ai_content,
            is_user=False,
            provider=provider,
            model=model
        )

        # Автоматически сгенерировать заголовок, если это первое сообщение
        if chat.messages.count() == 2:  # пользователь + AI
            ChatService._generate_title(chat, content)

        return {
            'user_message': {
                'id': user_message.id,
                'content': user_message.content
            },
            'ai_message': {
                'id': ai_message.id,
                'content': ai_message.content
            },
            'chat_title': chat.title
        }

    @staticmethod
    def _generate_title(chat: Chat, first_message: str):
        """Сгенерировать заголовок для чата"""
        try:
            provider_instance = get_provider('openai')  # Используем OpenAI для генерации заголовка
            title_prompt = f"Generate a short title for this conversation in the same language as the first message: {first_message[:100]}"
            title = provider_instance.get_response(
                [{"role": "user", "content": title_prompt}],
                "gpt-4o"
            )
            chat.title = title.strip()
            chat.save()
        except:
            pass  # Если не удалось сгенерировать, оставляем пустым

    @staticmethod
    def get_messages(chat_id: int) -> Dict[str, Any]:
        """Получить все сообщения чата"""
        chat = Chat.objects.get(id=chat_id)
        messages = chat.messages.all().order_by('created_at')
        data = [{
            'id': msg.id,
            'content': msg.content,
            'is_user': msg.is_user,
            'provider': msg.provider,
            'model': msg.model,
            'created_at': msg.created_at.isoformat()
        } for msg in messages]
        return {'messages': data, 'title': chat.title}

    @staticmethod
    def update_chat_title(chat_id: int, title: str):
        """Обновить заголовок чата"""
        chat = Chat.objects.get(id=chat_id)
        chat.title = title
        chat.save()

    @staticmethod
    def delete_chat(chat_id: int):
        """Удалить чат"""
        chat = Chat.objects.get(id=chat_id)
        chat.delete()