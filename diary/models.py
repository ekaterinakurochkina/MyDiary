from django.db import models
from taggit.managers import TaggableManager

from users.models import User


class DiaryEntry(models.Model):
    """ Модель записи дневника """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diary_entries')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    text = models.TextField('Основной текст')
    targets = models.CharField(max_length=255, blank=True, help_text='Напишите здесь свои цели')
    tags = TaggableManager(blank=True, help_text='Введите теги через запятую')


class CustomField(models.Model):
    """ Модель пользовательских полей дневника """
    entry = models.ForeignKey(DiaryEntry, on_delete=models.CASCADE, related_name='custom_fields')
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=255)


class DiarySettings(models.Model):
    """ Модель настроек вида дневника """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    show_targets = models.BooleanField(default=True, verbose_name="Показывать цели")
    show_tags = models.BooleanField(default=True, verbose_name="Показывать теги")
    theme = models.CharField(
        max_length=20,
        choices=[('light', 'Светлая'), ('dark', 'Тёмная')],
        default='light'
    )
    default_targets = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Цели по умолчанию",
        help_text="Эти цели будут автоматически подставляться в новые записи"
    )
    custom_fields_names = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Названия кастомных полей",
        help_text="Список названий дополнительных полей для записей"
    )
