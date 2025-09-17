from django.db import models

class Chat(models.Model):
    title = models.CharField(max_length=200, default="New Chat")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    is_user = models.BooleanField(default=True)  # True for user, False for AI
    created_at = models.DateTimeField(auto_now_add=True)
    provider = models.CharField(max_length=50, default='openai')
    model = models.CharField(max_length=50, default='gpt-4o')

    def __str__(self):
        return f"{'User' if self.is_user else 'AI'}: {self.content[:50]}"
