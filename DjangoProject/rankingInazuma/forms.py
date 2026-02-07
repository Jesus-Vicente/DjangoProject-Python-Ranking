from django import forms
from django.contrib.auth.forms import AuthenticationForm

from rankingInazuma.models import Usuario


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    repeat_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Usuario
        fields = ('nombre', 'email', 'password')

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username")