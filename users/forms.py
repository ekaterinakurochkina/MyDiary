from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import UserCreationForm

from diary.forms import StyleFormMixin
from .models import User


class StyledPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            self.fields[field].help_text = None


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


from django import forms
from .models import User

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['display_name', 'email', 'phone']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'display_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ваше имя'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+79998887766'
            })
        }
        labels = {
            'display_name': 'Имя для отображения',
            'email': 'Email',
            'phone': 'Телефон'
        }
        help_texts = {
            'display_name': 'Как к вам обращаться в системе',
            'phone': 'Формат: +79998887766'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Устанавливаем начальное значение для display_name
        if self.instance and self.instance.display_name:
            self.fields['display_name'].initial = self.instance.display_name

class PasswordRecoveryForm(StyleFormMixin, forms.Form):
    email = forms.EmailField(label="Укажите Email")


class UserLoginForm(StyleFormMixin, AuthenticationForm):
    model = User
