from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField


class AuthForm(AuthenticationForm):
    username = UsernameField(label='Username', widget=forms.TextInput(attrs={
        "autofocus": True,
        "class": 'form-control',
        "dir": 'auto'
    }))
    password = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput(attrs={
            "autocomplete": "current-password",
            "class": 'form-control',
            "dir": 'ltr'
        }),
    )
