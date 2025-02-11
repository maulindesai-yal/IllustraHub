from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .country_choices import COUNTRY_CHOICES

class CustomUserCreationForm(UserCreationForm):
    user_type = forms.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES, required=True, widget=forms.Select(attrs={'class' : 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2', 'user_type']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
class ProfileUpdateForm(forms.ModelForm):
    country = forms.ChoiceField(choices=COUNTRY_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control country-select'}))
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'biography','country']
        widgets = {
            'first_name' : forms.TextInput(attrs={'class': 'form-control'}),
            'last_name' : forms.TextInput(attrs={'class': 'form-control'}),
            'email' : forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'biography' : forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }