from rest_framework import serializers
from .models import ChatMessage

class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['question', 'answer', 'created_at']
