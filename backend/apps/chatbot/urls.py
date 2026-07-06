from django.urls import path
from .views import (
    ChatAPIView,
    ChatSessionCreateAPIView,
    FeedbackAPIView,
    CompanyAPIView,
    ServicesAPIView,
    ServiceDetailAPIView,
    FAQAPIView,
    HealthAPIView,
)

urlpatterns = [
    path('chat/', ChatAPIView.as_view(), name='chat'),
    path('chat/sessions/', ChatSessionCreateAPIView.as_view(), name='chat-session-create'),
    path('chat/feedback/', FeedbackAPIView.as_view(), name='chat-feedback'),
    path('company/', CompanyAPIView.as_view(), name='company'),
    path('services/', ServicesAPIView.as_view(), name='services'),
    path('services/<slug:slug>/', ServiceDetailAPIView.as_view(), name='service-detail'),
    path('faqs/', FAQAPIView.as_view(), name='faqs'),
    path('health/', HealthAPIView.as_view(), name='health'),
]
