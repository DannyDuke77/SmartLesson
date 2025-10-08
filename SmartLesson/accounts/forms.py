from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import Profile

from django.contrib.auth import get_user_model
User = get_user_model()

INPUT_CLASSES = (
    "w-full px-3 py-2 rounded-lg border border-gray-300 "
    "focus:outline-none focus:ring-2 focus:ring-blue-500 "
    "focus:border-blue-500 text-gray-700 placeholder-gray-400"
)
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g., +254712345678'}))
    tsc_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'TSC Number'}))
    id_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'ID Number'}))
    user_role = forms.ChoiceField(choices=Profile.USER_ROLES, required=True, widget=forms.Select(attrs={'class': INPUT_CLASSES}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2', 'email']
        

    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = INPUT_CLASSES

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Save profile data
            Profile.objects.filter(user=user).update_or_create(
                user=user,
                defaults={
                    'phone_number': self.cleaned_data['phone_number'],
                    'tsc_number': self.cleaned_data['tsc_number'],
                    'id_number': self.cleaned_data['id_number'],
                    'user_role': self.cleaned_data['user_role'],
                }
            )
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': INPUT_CLASSES})
        self.fields['password'].widget.attrs.update({'class': INPUT_CLASSES})