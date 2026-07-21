from django.urls import path
from .views import PublicContactAPIView

urlpatterns = [
    path('contact/', PublicContactAPIView.as_view(), name='public-contact'),
]
