from django.urls import path
from .views import register_user, user_login, user_logout, user_profile

app_name = 'accounts'

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('profile/', user_profile, name='user_profile'),
]