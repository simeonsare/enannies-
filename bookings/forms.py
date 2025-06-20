from django import forms
from .models import BookingRequest, BookingMessage

class BookingRequestForm(forms.ModelForm):
    class Meta:
        model = BookingRequest
        fields = [
            'service_type', 'number_of_children', 'children_ages', 'special_instructions',
            'start_date', 'start_time', 'end_time', 'duration_hours', 'service_address'
        ]
        widgets = {
            'service_type': forms.Select(attrs={'class': 'form-control'}),
            'number_of_children': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'children_ages': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 3, 5, 8'}),
            'special_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'duration_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0.5'}),
            'service_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_date'].widget.attrs['min'] = timezone.now().date().isoformat()

class BookingMessageForm(forms.ModelForm):
    class Meta:
        model = BookingMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Type your message here...'})
        }