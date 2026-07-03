from django.urls import path
from .views import ChatAPIView, HealthAPIView

urlpatterns = [
    path('chat/', ChatAPIView.as_view(), name='chat'),
    path('health/', HealthAPIView.as_view(), name='health'),
]
