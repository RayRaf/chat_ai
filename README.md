# LLM Chat Aggregator

A Django-based single-page application for aggregating interactions with various LLM providers, starting with OpenAI.

## Features

- Single-page interface with chat list on the left and chat area on the right
- Support for multiple LLM providers and models (currently OpenAI)
- Automatic chat title generation after first message
- Manual chat title editing
- Persistent chat history using SQLite database

## Setup

1. Clone or create the project in a directory.

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
   - Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_openai_api_key_here
   ```

6. Run migrations:
   ```
   python manage.py migrate
   ```

7. Start the development server:
   ```
   python manage.py runserver
   ```

8. Open your browser and go to `http://127.0.0.1:8000/`

## Usage

- Click "New Chat" to create a new conversation
- Select a chat from the list to view and continue the conversation
- Choose the LLM provider and model from the dropdowns
- Type your message and press Enter or click Send
- The chat title will be automatically generated after the first message
- Click "Edit Title" to manually change the chat title

## Project Structure

- `chat_ai/` - Main Django project directory
- `chat/` - Django app for chat functionality
- `chat/models.py` - Database models for Chat and Message
- `chat/views.py` - Views for handling requests
- `chat/templates/chat/index.html` - Main template
- `.env` - Environment variables (add your API key here)

## Future Enhancements

- Add support for more LLM providers (Anthropic, Google, etc.)
- Implement user authentication
- Add chat export/import functionality
- Improve UI/UX with better styling
- Add message editing and deletion
- Implement real-time updates with WebSockets