from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, CustomerProfile, CaregiverProfile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone_number = forms.CharField(required=False)
    user_type = forms.ChoiceField(choices=User.USER_TYPES, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'phone_number', 'user_type', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['address', 'emergency_contact', 'number_of_children', 'children_ages', 'special_needs', 'profile_picture']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'number_of_children': forms.NumberInput(attrs={'class': 'form-control'}),
            'children_ages': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 3, 5, 8'}),
            'special_needs': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

class CaregiverProfileForm(forms.ModelForm):
    class Meta:
        model = CaregiverProfile
        fields = ['bio', 'years_of_experience', 'hourly_rate', 'location', 'available', 'profile_picture', 'certifications', 'languages']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'years_of_experience': forms.Select(attrs={'class': 'form-control'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'certifications': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'languages': forms.TextInput(attrs={'class': 'form-control'}),
        }