from django import forms
from django.db.models import BooleanField

from .models import DiaryEntry, DiarySettings


class StyleFormMixin:
    """ Стилизация форм для правильного отображения """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs['class'] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["placeholder"] = field.label


class DiaryEntryForm(forms.ModelForm):
    """ Форма записи дневника """
    class Meta:
        model = DiaryEntry
        fields = ['text', 'targets', 'tags']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 10, 'class': 'form-control'}),
            'targets': forms.TextInput(attrs={'class': 'form-control'}),
        }


class DiarySettingsForm(forms.ModelForm):
    """ Форма настроек отображения дневника """
    class Meta:
        model = DiarySettings
        fields = ['show_targets', 'show_tags', 'default_targets']
        widgets = {
            'default_targets': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Прочитать книгу, Пробежать 5км'
            }),
            'show_targets': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'show_tags': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'show_targets': '',
            'show_tags': '',
            'default_targets': ''
        }
