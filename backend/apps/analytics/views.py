from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from django.db.models.functions import TruncDate
from .models import AnalyticsEvent
from apps.leads.models import Lead

class AnalyticsDashboardAPIView(APIView):
    def get(self, request, *args, **kwargs):
        total_chats = AnalyticsEvent.objects.filter(event_type='chat_started').count()
        total_messages = AnalyticsEvent.objects.filter(event_type='message_sent').count()
        
        total_leads = Lead.objects.count()
        # Anybody past 'gathering' is considered qualified at some point
        qualified_leads = Lead.objects.filter(status__in=['qualified', 'converted', 'lost', 'escalated']).count()
        converted_leads = Lead.objects.filter(status='converted').count()
        lost_leads = Lead.objects.filter(status='lost').count()
        
        qualification_rate = (qualified_leads / total_leads * 100) if total_leads > 0 else 0
        conversion_rate = (converted_leads / qualified_leads * 100) if qualified_leads > 0 else 0
        
        data = {
            "total_chats": total_chats,
            "total_messages": total_messages,
            "total_leads": total_leads,
            "qualified_leads": qualified_leads,
            "converted_leads": converted_leads,
            "lost_leads": lost_leads,
            "qualification_rate": round(qualification_rate, 2),
            "conversion_rate": round(conversion_rate, 2)
        }
        return Response(data, status=status.HTTP_200_OK)

class AnalyticsTimelineAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Group by date and event_type
        events = (
            AnalyticsEvent.objects
            .annotate(date=TruncDate('created_at'))
            .values('date', 'event_type')
            .annotate(count=Count('id'))
            .order_by('date')
        )
        
        timeline = {}
        for event in events:
            date_str = str(event['date'])
            if date_str not in timeline:
                timeline[date_str] = {}
            timeline[date_str][event['event_type']] = event['count']
            
        return Response(timeline, status=status.HTTP_200_OK)

class AnalyticsFunnelAPIView(APIView):
    def get(self, request, *args, **kwargs):
        total_chats = AnalyticsEvent.objects.filter(event_type='chat_started').count()
        total_leads = Lead.objects.count()
        qualified_leads = Lead.objects.filter(status__in=['qualified', 'converted', 'lost', 'escalated']).count()
        converted_leads = Lead.objects.filter(status='converted').count()
        
        funnel = [
            {"stage": "Chats Started", "value": total_chats},
            {"stage": "Leads Captured", "value": total_leads},
            {"stage": "Leads Qualified", "value": qualified_leads},
            {"stage": "Leads Converted", "value": converted_leads}
        ]
        return Response(funnel, status=status.HTTP_200_OK)
