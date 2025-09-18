from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import Chat, Message
from .services.chat_service import ChatService
from django.conf import settings
import json as json_module

def index(request):
    chats = Chat.objects.all().order_by('-updated_at')

    # Собираем все доступные модели по провайдерам
    available_providers = {
        'openai': {
            'name': 'OpenAI',
            'models': getattr(settings, 'OPENAI_MODELS', [])
        },
        'anthropic': {
            'name': 'Anthropic',
            'models': getattr(settings, 'ANTHROPIC_MODELS', [])
        },
        'google': {
            'name': 'Google',
            'models': getattr(settings, 'GOOGLE_MODELS', [])
        },
        'mistral': {
            'name': 'Mistral AI',
            'models': getattr(settings, 'MISTRAL_MODELS', [])
        }
    }

    return render(request, 'chat/index.html', {
        'chats': chats,
        'available_providers': available_providers,
        'available_providers_json': json_module.dumps(available_providers),
        'default_provider': 'openai'
    })

@csrf_exempt
@require_POST
def create_chat(request):
    try:
        chat = ChatService.create_chat()
        return JsonResponse({'chat_id': chat.id, 'title': chat.title})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def send_message(request):
    data = json.loads(request.body)
    chat_id = data['chat_id']
    content = data['content']
    provider = data.get('provider', 'openai')
    model = data.get('model', 'gpt-4o')

    try:
        result = ChatService.send_message(chat_id, content, provider, model)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_messages(request, chat_id):
    try:
        result = ChatService.get_messages(chat_id)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def update_chat_title(request, chat_id):
    try:
        data = json.loads(request.body)
        ChatService.update_chat_title(chat_id, data['title'])
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def delete_chat(request, chat_id):
    try:
        ChatService.delete_chat(chat_id)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
