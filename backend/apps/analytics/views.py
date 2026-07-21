from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from apps.accounts.permissions import IsAdminUser
from django.utils import timezone

from .services.overview_service import OverviewAnalyticsService
from .services.lead_analytics_service import LeadAnalyticsService
from .services.crm_analytics_service import CrmAnalyticsService
from .services.chat_analytics_service import ChatAnalyticsService
from .services.knowledge_analytics_service import KnowledgeAnalyticsService
from .services.user_analytics_service import UserAnalyticsService
from .services.export_service import AnalyticsExportService
from .services.filter_service import AnalyticsFilterService
from .serializers import (
    OverviewResponseSerializer, 
    LeadAnalyticsResponseSerializer, 
    CrmAnalyticsResponseSerializer,
    ChatAnalyticsResponseSerializer,
    KnowledgeAnalyticsResponseSerializer,
    UserAnalyticsResponseSerializer
)

class BaseAnalyticsAPIView(APIView):
    permission_classes = [IsAdminUser]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        from apps.platform_settings.services import SettingsService
        from rest_framework.exceptions import PermissionDenied
        if not SettingsService.is_feature_enabled("ENABLE_ANALYTICS"):
            raise PermissionDenied("Analytics module is disabled.")

class AnalyticsOverviewAPIView(BaseAnalyticsAPIView):

    def get(self, request, *args, **kwargs):
        try:
            context = AnalyticsFilterService.build_filter_context(request)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        data = OverviewAnalyticsService.build_response(context)
        
        serializer = OverviewResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class AnalyticsLeadsAPIView(BaseAnalyticsAPIView):

    def get(self, request, *args, **kwargs):
        try:
            context = AnalyticsFilterService.build_filter_context(request)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        data = LeadAnalyticsService.build_response(context)
        
        serializer = LeadAnalyticsResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class AnalyticsCRMAPIView(BaseAnalyticsAPIView):

    def get(self, request, *args, **kwargs):
        try:
            context = AnalyticsFilterService.build_filter_context(request)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        data = CrmAnalyticsService.build_response(context)
        
        serializer = CrmAnalyticsResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class AnalyticsChatAPIView(BaseAnalyticsAPIView):

    def get(self, request, *args, **kwargs):
        try:
            context = AnalyticsFilterService.build_filter_context(request)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        data = ChatAnalyticsService.build_response(context)
        serializer = ChatAnalyticsResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class AnalyticsKnowledgeAPIView(BaseAnalyticsAPIView):

    def get(self, request, *args, **kwargs):
        try:
            context = AnalyticsFilterService.build_filter_context(request)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        data = KnowledgeAnalyticsService.build_response(context)
        serializer = KnowledgeAnalyticsResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class AnalyticsUsersAPIView(BaseAnalyticsAPIView):

    def get(self, request, *args, **kwargs):
        try:
            context = AnalyticsFilterService.build_filter_context(request)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        data = UserAnalyticsService.build_response(context)
        serializer = UserAnalyticsResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class AnalyticsExportAPIView(BaseAnalyticsAPIView):

    def get(self, request, *args, **kwargs):
        try:
            context = AnalyticsFilterService.build_filter_context(request)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        module = request.query_params.get('module', 'overview')
        valid_modules = ['overview', 'leads', 'crm', 'chat', 'knowledge', 'users']
        
        if module not in valid_modules:
            return Response({"error": f"Invalid module. Must be one of {valid_modules}"}, status=status.HTTP_400_BAD_REQUEST)
            
        response = AnalyticsExportService.generate_csv(module, context)
        if not response:
            return Response({"error": "Failed to generate export"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return response
