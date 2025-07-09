from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError


class CustomLoginForm(AuthenticationForm):
    """Custom login form using email instead of username."""

    username = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter your email", "autofocus": True}),
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter your password"}),
    )

    error_messages = {
        "invalid_login": "Please enter a correct email and password. Note that both fields may be case-sensitive.",
        "inactive": "This account is inactive.",
    }

    def clean(self):
        """Clean the form."""
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if email and password:
            self.user_cache = authenticate(self.request, username=email, password=password)
            if self.user_cache is None:
                raise ValidationError(self.error_messages["invalid_login"], code="invalid_login")
            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data
