import secrets

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from django.views.generic import UpdateView
from django.views.generic.edit import CreateView, DeleteView

from config.settings import EMAIL_HOST_USER
from users.forms import UserRegisterForm
from .forms import ProfileUpdateForm
from .models import User


def logout_view(request):
    logout(request)
    return redirect('diary:home')


class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """ Список всех пользователей приложения (доступен менеджерам и суперюзеру) """
    model = User
    template_name = "user_list.html"
    context_object_name = "users"

    def test_func(self):
        """ Проверяет, является ли пользователь менеджером или суперюзером """
        return self.request.user.is_superuser or self.request.user.groups.filter(name="Менеджер").exists()

    def handle_no_permission(self):
        """ Обработка случая, когда у пользователя нет прав """
        from django.shortcuts import redirect
        return redirect('home')  # Перенаправляем на главную страницу

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем всех пользователей и добавляем информацию о принадлежности к группе
        for user in context['users']:
            user.is_manager = user.groups.filter(name="Менеджер").exists()
        return context


class UserCreateView(CreateView):
    """ Регистрация (создание) нового пользователя """
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        """ функция для подтверждения регистрации через электронную почту """
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)  # генерируем токен
        user.token = token
        user.save()
        host = self.request.get_host()  # получаем хост, откуда пришел пользователь
        url = f'http://{host}/users/email-confirm/{token}/'
        try:
            send_mail(
                subject="Подтверждение почты",
                message=f"""Спасибо, что зарегистрировались в нашем сервисе!
                Для подтверждения регистрации перейдите по ссылке {url}""",
                from_email=EMAIL_HOST_USER,
                recipient_list=[user.email]
            )
        except Exception as e:
            print(f'Error sending email: {e}')
        return super().form_valid(form)


def email_verification(request, token):
    """ Функция, перенаправляющая зарегистрированного пользователя на вход
    после его перехода по указанной в письме ссылки. Активирует этого пользователя """
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.token = None  # очищаем токен после использования
    user.save()
    return redirect(reverse_lazy("users:login"))


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    Представление для обновления профиля пользователя
    """
    template_name = 'users/profile_update.html'
    form_class = ProfileUpdateForm
    success_url = reverse_lazy('users:profile')  # Убедитесь, что у вас есть этот URL

    def get_object(self, queryset=None):
        """Получаем текущего пользователя"""
        return self.request.user

    def form_valid(self, form):
        """Обработка успешной валидации формы"""
        response = super().form_valid(form)

        # Получаем обновленные данные
        updated_name = form.cleaned_data.get('display_name')
        updated_phone = form.cleaned_data.get('phone')

        # Обновляем поля в базе данных
        user = self.request.user
        if updated_name and user.display_name != updated_name:
            user.display_name = updated_name
        if updated_phone and user.phone != updated_phone:
            user.phone = updated_phone

        user.save()
        messages.success(self.request, 'Профиль успешно обновлен!')
        return response

    def form_invalid(self, form):
        """Обработка невалидной формы"""
        messages.error(
            self.request,
            'Ошибка обновления профиля. Пожалуйста, исправьте отмеченные поля.'
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """Добавляем дополнительные данные в контекст"""
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Редактирование профиля',
            'user': self.request.user  # Добавляем пользователя в контекст
        })
        return context


class DeleteAccountView(LoginRequiredMixin, DeleteView):
    """ Удаление аккаунта с сайта """
    model = User
    template_name = 'user_confirm_delete.html'
    success_url = reverse_lazy('users:login')

    def get_object(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        password = request.POST.get('password')
        user = authenticate(email=request.user.email, password=password)

        if user is not None:
            messages.success(request, 'Ваш аккаунт был успешно удален')
            return super().post(request, *args, **kwargs)

        messages.error(request, 'Неверный пароль')
        return self.get(request, *args, **kwargs)


@login_required
@require_POST
def remove_avatar(request):
    """ Функция для удаления аватара """
    user = request.user
    if user.avatar:
        user.avatar.delete()
        user.avatar = None  # Очищаем ссылку на файл
        user.save()
        messages.success(request, 'Аватар успешно удален!')
    return redirect('users:profile')
