from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
import json
from .models import Chat, Message, UserProfile
from .services.chat_service import ChatService
from django.conf import settings
import json as json_module

def index(request):
    if request.user.is_authenticated:
        chats = Chat.objects.filter(user=request.user).order_by('-updated_at')
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(user=request.user)
    else:
        chats = []
        user_profile = None

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

    # Collect models used in existing chats (for this user) so they always appear in UI
    used_model_ids = set()
    try:
        # Collect from messages for current user's chats
        if request.user.is_authenticated:
            used_model_ids = set(
                Message.objects.filter(chat__user=request.user)
                .exclude(model__isnull=True)
                .exclude(model__exact='')
                .values_list('model', flat=True)
            )

    except Exception:
        used_model_ids = set()

    # Try to fetch live OpenAI models from the provider and show them in UI.
    try:
        from .providers import get_provider
        openai_provider = get_provider('openai')
        live_model_ids = set(openai_provider.get_available_models())

        # Build model objects from live models. Provide friendly names where possible.
        live_models = []
        for mid in sorted(live_model_ids):
            # Use the id as a fallback name; you can map nicer names here if desired
            name = mid
            # Some heuristics for prettier names
            if mid.startswith('gpt-'):
                name = mid.replace('-', ' ').upper()
            live_models.append({'id': mid, 'name': name, 'available': True})

        # Merge used model ids so that any model referenced in chats is present in the UI
        merged_ids = set(live_model_ids) | set(used_model_ids)

        merged_models = []
        for mid in sorted(merged_ids):
            name = mid
            if mid.startswith('gpt-'):
                name = mid.replace('-', ' ').upper()
            # If mid in live_model_ids then available True, otherwise False (used-only)
            merged_models.append({'id': mid, 'name': name, 'available': mid in live_model_ids})

        if merged_models:
            available_providers['openai']['models'] = merged_models
        else:
            # Fallback to configured models and mark availability based on the live ids set
            for m in available_providers['openai']['models']:
                m_id = m.get('id')
                m['available'] = m_id in live_model_ids
    except Exception:
        # If fetching live models fails, fallback to settings list but mark a small stable set as available
        stable = {'gpt-4o', 'gpt-4'}
        for m in available_providers['openai']['models']:
            m['available'] = m.get('id') in stable

    return render(request, 'chat/index.html', {
        'chats': chats,
        'available_providers': available_providers,
        'available_providers_json': json_module.dumps(available_providers),
        'default_provider': 'openai',
        'user_profile': user_profile
    })

@login_required
@csrf_exempt
@require_POST
def create_chat(request):
    try:
        chat = ChatService.create_chat(request.user)
        return JsonResponse({'chat_id': chat.id, 'title': chat.title})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@csrf_exempt
@require_POST
def send_message(request):
    data = json.loads(request.body)
    chat_id = data['chat_id']
    content = data['content']
    provider = data.get('provider', 'openai')
    model = data.get('model', 'gpt-4o')

    try:
        result = ChatService.send_message(chat_id, content, provider, model, request.user)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_messages(request, chat_id):
    try:
        result = ChatService.get_messages(chat_id, request.user)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@csrf_exempt
@require_POST
def update_chat_title(request, chat_id):
    try:
        data = json.loads(request.body)
        ChatService.update_chat_title(chat_id, data['title'], request.user)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@csrf_exempt
@require_POST
def delete_chat(request, chat_id):
    try:
        ChatService.delete_chat(chat_id, request.user)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def user_profile_view(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    return JsonResponse({
        'username': request.user.username,
        'balance': str(user_profile.balance)
    })

@login_required
@require_POST
def top_up_balance(request):
    try:
        amount = float(request.POST.get('amount', 0))
        if amount <= 0:
            return JsonResponse({'error': 'Invalid amount'}, status=400)
        
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_profile.balance += amount
        user_profile.save()
        return JsonResponse({'success': True, 'new_balance': str(user_profile.balance)})
    except ValueError:
        return JsonResponse({'error': 'Invalid amount'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
