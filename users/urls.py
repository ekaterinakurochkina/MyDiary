from django.urls import path
from .views import email_verification

app_name = 'users'

urlpatterns = [
    # path('register/', UserCreateView.as_view(template_name="register.html"), name='register'),
    # path('login/', LoginView.as_view(template_name="login.html"), name='login'),
    # path('logout/', logout_view, name='logout'),
    # path('delete/', DeleteAccountView.as_view(template_name="user_confirm_delete.html"), name='delete'),
    path('email-confirm/<str:token>/', email_verification, name='email-confirm'),
    # path('', UserListView.as_view(), name='home')
]