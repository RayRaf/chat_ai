from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import Chat, Message
from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def index(request):
    chats = Chat.objects.all().order_by('-updated_at')
    return render(request, 'chat/index.html', {'chats': chats})

@csrf_exempt
@require_POST
def create_chat(request):
    chat = Chat.objects.create()
    return JsonResponse({'chat_id': chat.id, 'title': chat.title})

@csrf_exempt
@require_POST
def send_message(request):
    data = json.loads(request.body)
    chat_id = data['chat_id']
    content = data['content']
    provider = data.get('provider', 'openai')
    model = data.get('model', 'gpt-3.5-turbo')

    chat = get_object_or_404(Chat, id=chat_id)

    # Save user message
    user_message = Message.objects.create(
        chat=chat,
        content=content,
        is_user=True,
        provider=provider,
        model=model
    )

    # Get AI response
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": content}]
        )
        ai_content = response.choices[0].message.content
    except Exception as e:
        ai_content = f"Error: {str(e)}"

    # Save AI message
    ai_message = Message.objects.create(
        chat=chat,
        content=ai_content,
        is_user=False,
        provider=provider,
        model=model
    )

    # Auto-generate title if first message
    if chat.messages.count() == 2:  # user + ai
        try:
            title_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"Generate a short title for this conversation: {content[:100]}"}]
            )
            chat.title = title_response.choices[0].message.content.strip()
            chat.save()
        except:
            pass

    return JsonResponse({
        'user_message': {'id': user_message.id, 'content': user_message.content},
        'ai_message': {'id': ai_message.id, 'content': ai_message.content},
        'chat_title': chat.title
    })

def get_messages(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    messages = chat.messages.all().order_by('created_at')
    data = [{
        'id': msg.id,
        'content': msg.content,
        'is_user': msg.is_user,
        'provider': msg.provider,
        'model': msg.model,
        'created_at': msg.created_at.isoformat()
    } for msg in messages]
    return JsonResponse({'messages': data, 'title': chat.title})

@csrf_exempt
@require_POST
def update_chat_title(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    data = json.loads(request.body)
    chat.title = data['title']
    chat.save()
    return JsonResponse({'success': True})
