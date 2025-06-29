from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm


from diary.forms import StyleFormMixin
from .models import User


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    display_name = forms.CharField(
        label='Как к вам обращаться?',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Ваше имя или псевдоним'})
    )

    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'example@mail.com'})
    )

    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'})
    )

    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={"placeholder": "Повторите пароль"})
    )

    avatar = forms.ImageField(
        label='Аватар',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control-file'})
    )

    class Meta:
        model = User
        fields = ("email", "display_name", "password1", "password2", "avatar")


class UserUpdateForm(StyleFormMixin, ModelForm):
    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "phone",
            "avatar",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        phone = self.fields["phone"].widget

        self.fields["password"].widget = forms.HiddenInput()
        phone.attrs["class"] = "form-control bfh-phone"
        phone.attrs["data-format"] = "+7 (ddd) ddd-dd-dd"


class PasswordRecoveryForm(StyleFormMixin, forms.Form):
    email = forms.EmailField(label="Укажите Email")

class UserLoginForm(StyleFormMixin, AuthenticationForm):
    model = User
