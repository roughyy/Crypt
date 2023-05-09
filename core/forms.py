from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Your Username",
                "class": "px-5 py-3 rounded-lg w-96 text-base-dark ",
            }
        )
    )
    email = forms.CharField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Your Email Address",
                "class": "px-5 py-3 rounded-lg w-96 text-base-dark ",
            }
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Your Password",
                "class": "px-5 py-3 rounded-lg w-96 text-base-dark ",
            }
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Repeat Your Password",
                "class": "px-5 py-3 rounded-lg w-96 text-base-dark",
            }
        )
    )


class UploadFile(forms.Form):
    file = forms.FileField()
