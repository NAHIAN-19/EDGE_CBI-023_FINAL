from rest_framework import serializers
from .models import Task
from django.utils import timezone
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'user', 'title', 'description', 'status', 'choices', 'due_date', 'created_at', 'updated_at')
        
    def validate_due_date(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value
    def validate_title(self, value):
        if len(value) > 100:
            raise serializers.ValidationError("Title cannot be more than 100 characters.")
        return value