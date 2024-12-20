from .models import Task
from django import forms
from django.utils import timezone
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'status', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'})
        }
        
    def clean_due_date(self):
        data = self.cleaned_data['due_date']
        if data < timezone.now().date():
            raise forms.ValidationError("Due date cannot be in the past.")
        return data
    def clean_title(self):
        data = self.cleaned_data['title']
        if len(data) > 100:
            raise forms.ValidationError("Title cannot be more than 100 characters.")
        return data
    
