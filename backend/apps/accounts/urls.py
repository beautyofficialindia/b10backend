from django.urls import path
from .views import LoginAPIView, LogoutAPIView, MeAPIView, RefreshAPIView, ChangePasswordAPIView

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('refresh/', RefreshAPIView.as_view(), name='token_refresh'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('me/', MeAPIView.as_view(), name='me'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change_password'),
]
