import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_ai.settings')
django.setup()

from chat.providers.openai_provider import OpenAIProvider

def main():
    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        return

    # Create provider instance
    provider = OpenAIProvider(api_key)

    # Get available models
    try:
        models = provider.get_available_models()
        print("Available OpenAI models:")
        for model in models:
            print(f"- {model}")
    except Exception as e:
        print(f"Error fetching models: {str(e)}")

if __name__ == "__main__":
    main()