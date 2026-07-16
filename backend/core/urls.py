"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.views import APIView
from rest_framework.response import Response

class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, *args, **kwargs):
        return Response({"status": "ok"})

from apps.knowledge_base.urls import admin_urlpatterns as kb_admin_urls, public_urlpatterns as kb_public_urls

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/', include('apps.chatbot.urls')),
    path('api/v1/admin/', include('apps.leads.urls')),
    path('api/v1/admin/analytics/', include('apps.analytics.urls')),
    path('api/v1/admin/crm/', include('apps.crm.urls')),
    path('api/v1/kb/', include((kb_public_urls, 'kb_public'))),
    path('api/v1/admin/kb/', include((kb_admin_urls, 'kb_admin'))),
    path('api/v1/admin/users/', include('apps.user_management.urls')),
    path('api/v1/admin/roles/', include('apps.role_management.urls')),
    path('api/v1/admin/settings/', include('apps.platform_settings.urls')),
]
