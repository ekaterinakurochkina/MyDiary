from django.db.models import BooleanField
from django import forms
from .models import DiaryEntry, CustomField, DiarySettings


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs['class'] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["placeholder"] = field.label


class DiaryEntryForm(forms.ModelForm):
    class Meta:
        model = DiaryEntry
        fields = ['text', 'targets', 'tags']
        widgets = {
            'targets': forms.Textarea(attrs={'rows': 3}),
            'text': forms.Textarea(attrs={'rows': 10}),
        }

class CustomFieldForm(forms.ModelForm):
    class Meta:
        model = CustomField
        fields = ['name', 'value']
        widgets = {
            'value': forms.TextInput(attrs={'class': 'form-control'}),
        }

CustomFieldFormSet = forms.inlineformset_factory(
    DiaryEntry,
    CustomField,
    form=CustomFieldForm,
    extra=1,  # Количество пустых форм по умолчанию
    can_delete=True  # Разрешить удаление полей
)

class DiarySettingsForm(forms.ModelForm):
    class Meta:
        model = DiarySettings
        fields = ['show_targets', 'show_tags', 'theme']
