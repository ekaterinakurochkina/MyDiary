from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator, EmailValidator
from django.db import models


class User(AbstractUser):
    """ Модель пользователя """
    username = None

    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        help_text="Укажите Ваш email",
        validators=[EmailValidator(message="Введите корректный email")],
        error_messages={
            'unique': 'Пользователь с таким email уже существует',
        }
    )

    display_name = models.CharField(
        max_length=150,
        verbose_name="Имя для отображения",
        help_text="Как мы будем к Вам обращаться",
    )

    phone = models.CharField(
        max_length=35,
        verbose_name="Телефон",
        blank=True,
        null=True,
        help_text="Введите номер телефона",
        validators=[
            RegexValidator(
                r'^\+?[0-9]{9,15}$',
                message="Номер телефона должен быть в формате: '+999999999'"
            )
        ]
    )
    token = models.CharField(
        max_length=100,
        verbose_name="Token",
        blank=True,
        null=True
    )

    avatar = models.ImageField(
        upload_to="static/avatars",
        verbose_name="Аватар",
        blank=True,
        null=True,
        help_text='Загрузите свой аватар'
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["display_name"]

    # Решение проблемы с related_name
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',  # Уникальное имя
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',  # Уникальное имя
        related_query_name='user',
    )

    def __str__(self):
        return f"{self.display_name} ({self.email})"

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['email']
        permissions = [
            ('can_inactivate', 'Может блокировать пользователя'),
        ]

    @property
    def is_moderator(self) -> bool:
        return self.groups.filter(name='Менеджер').exists()
