import secrets

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from config.settings import EMAIL_HOST_USER
from users.forms import UserRegisterForm, ProfileUpdateForm
from users.models import User


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
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.token = None  # очищаем токен после использования
    user.save()
    return redirect(reverse_lazy("users:login"))


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    Представление для обновления профиля пользователя
    с обработкой аватара и валидацией данных
    """
    template_name = 'users/profile_update.html'
    form_class = ProfileUpdateForm
    success_url = reverse_lazy('users:profile_update')

    def get_object(self, queryset=None):
        """Получаем текущего пользователя"""
        return self.request.user

    def dispatch(self, request, *args, **kwargs):
        """Дополнительная проверка доступа"""
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Обработка успешной валидации формы"""
        user = form.save(commit=False)

        # Обработка аватара
        if 'avatar' in form.changed_data and form.cleaned_data['avatar']:
            avatar = form.cleaned_data['avatar']
            try:
                # Оптимизация изображения
                img = Image.open(avatar)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)

                    # Сохранение в том же формате
                    temp_file = avatar.temporary_file_path()
                    img.save(temp_file, quality=70)

                # Проверка MIME-типа
                valid_mime_types = ['image/jpeg', 'image/png', 'image/gif']
                file_mime_type = avatar.content_type

                if file_mime_type not in valid_mime_types:
                    form.add_error('avatar', 'Неподдерживаемый формат изображения')
                    return self.form_invalid(form)

            except Exception as e:
                form.add_error('avatar', f'Ошибка обработки изображения: {str(e)}')
                return self.form_invalid(form)

        user.save()
        messages.success(self.request, 'Профиль успешно обновлен!')
        return super().form_valid(form)

    def form_invalid(self, form):
        """Обработка невалидной формы"""
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """Добавляем дополнительные данные в контекст"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование профиля'
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

