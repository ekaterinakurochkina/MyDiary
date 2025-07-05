from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from django.urls import path
from django.urls import reverse_lazy

from .forms import StyledPasswordChangeForm
from .views import (email_verification, UserListView, UserCreateView,
                    DeleteAccountView, logout_view, ProfileUpdateView, remove_avatar)

app_name = 'users'

urlpatterns = [
    path('', UserListView.as_view(), name='home'),
    path('register/', UserCreateView.as_view(template_name="register.html"), name='register'),
    path('login/', LoginView.as_view(template_name="login.html"), name='login'),
    path('logout/', logout_view, name='logout'),
    path('delete/', DeleteAccountView.as_view(template_name="user_confirm_delete.html"), name='delete'),
    path('email-confirm/<str:token>/', email_verification, name='email-confirm'),
    path('profile/', ProfileUpdateView.as_view(), name='profile'),
    path('avatar/remove/', remove_avatar, name='avatar_remove'),
    path('password/change/',
         auth_views.PasswordChangeView.as_view(
             template_name='users/password_change.html',
             form_class=StyledPasswordChangeForm,
             success_url=reverse_lazy('users:password_change_done')
         ),
         name='password_change'),
    path('password/change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='users/password_change_done.html'
         ),
         name='password_change_done'),
]
