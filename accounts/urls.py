from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import MyTokenObtainPairView, register_user, profile_view, logout_view, upload_profile_picture, remove_profile_picture


app_name = 'accounts'

urlpatterns = [
    path('register/', register_user, name='register'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', profile_view, name='profile'),
    path('logout/', logout_view, name='logout'),
      path('upload-profile-picture/', upload_profile_picture, name='upload_profile_picture'),
    path('remove-profile-picture/', remove_profile_picture, name='remove_profile_picture'),
]
