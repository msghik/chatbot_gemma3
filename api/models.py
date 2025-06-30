from django.db import models
from django.contrib.auth.models import User

class ChatSession(models.Model):
    """
    Represents a single, distinct conversation between a user and the chatbot.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_sessions")
    title = models.CharField(max_length=200, default="New Chat")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"'{self.title}' for {self.user.username}"