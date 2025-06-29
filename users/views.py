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
from users.forms import UserRegisterForm, UserUpdateForm

from config.settings import EMAIL_HOST_USER
from users.models import User


def logout_view(request):
    logout(request)
    return redirect('diary:home')


# ______________________блокировка пользователя
# @permission_required("users.can_inactivate")
# def block_user(self, pk):accounts
#     user = get_object_or_404(User, pk=pk)
#     user.is_active = False
#     user.save()
#     return redirect(reverse("users:user_list"))
#
# # ______________________разблокировка пользователя
# @permission_required("users.can_inactivate")
# def unblock_user(self, pk):
#     user = get_object_or_404(User, pk=pk)
#     user.is_active = True
#     user.save()
#     return redirect(reverse("users:user_list"))
# ______________________

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
    user.save()
    return redirect(reverse_lazy("users:login"))


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """ Обновление данных пользователя """
    model = User
    form_class = UserUpdateForm
    template_name = "users:user_form.html"
    success_url = reverse_lazy("users:user_edit")

    # def get_object(self, queryset=None):
    #     self.object = super().get_object(queryset)
    #     if not self.request.user.is_superuser:
    #         raise PermissionDenied
    #     return self.object
    def dispatch(self, request, *args, **kwargs):
        # Проверяем, является ли текущий пользователь суперпользователем
        if not request.user.is_superuser:
            raise PermissionDenied("У вас нет прав для редактирования этого пользователя.")
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        # Загружаем объект, но проверка прав уже выполнена в dispatch
        return super().get_object(queryset)


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
