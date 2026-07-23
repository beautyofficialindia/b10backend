from django.db.models import Count, Avg, F, ExpressionWrapper, fields
from django.db.models.functions import TruncDate, Cast
from apps.platform_settings.services import SettingsService
from apps.chatbot.models import ConversationSession, Message
from apps.leads.models import Lead
from apps.analytics.utils import build_metric, build_trend, format_labels

class ChatAnalyticsService:
    
    @staticmethod
    def _is_tracking_enabled():
        return (SettingsService.is_feature_enabled("ENABLE_ANALYTICS") and 
                SettingsService.is_feature_enabled("ENABLE_AI_CHATBOT") and
                SettingsService.get_boolean("ANALYTICS", "TRACK_CONVERSATIONS"))
                
    @staticmethod
    def _get_disabled_response():
        return {
            "executive_metrics": {"enabled": False, "data": {}},
            "conversation_growth": {"enabled": False, "data": None},
            "message_growth": {"enabled": False, "data": None},
            "lead_generation_growth": {"enabled": False, "data": None},
            "qualification_growth": {"enabled": False, "data": None},
            "chat_insights": {"enabled": False, "data": []}
        }

    @staticmethod
    def _get_filtered_queryset(model, date_field, context):
        q = model.objects.all()
        start_date = context.get('start_date')
        end_date = context.get('end_date')
        if start_date:
            q = q.filter(**{f"{date_field}__gte": start_date})
        if end_date:
            q = q.filter(**{f"{date_field}__lte": end_date})
        return q

    @staticmethod
    def get_executive_metrics(context):
        conv_q = ChatAnalyticsService._get_filtered_queryset(ConversationSession, 'created_at', context)
        msg_q = ChatAnalyticsService._get_filtered_queryset(Message, 'created_at', context)
        leads_q = ChatAnalyticsService._get_filtered_queryset(Lead, 'created_at', context).filter(source='chatbot')
        
        total_conversations = conv_q.count()
        total_messages = msg_q.count()
        generated_leads = leads_q.count()
        qualified_leads = leads_q.filter(status__in=['qualified', 'converted']).count()
        
        avg_messages = (total_messages / total_conversations) if total_conversations > 0 else 0
        
        data = {
            "total_conversations": build_metric("Total Conversations", total_conversations),
            "total_messages": build_metric("Total Messages", total_messages),
            "generated_leads": build_metric("Generated Leads", generated_leads),
            "qualified_leads": build_metric("Qualified Leads", qualified_leads),
            "average_length": build_metric("Average Conversation Length", round(avg_messages, 1)),
        }
        return {"enabled": True, "data": data}

    @staticmethod
    def get_conversation_growth(context):
        q = ChatAnalyticsService._get_filtered_queryset(ConversationSession, 'created_at', context)
        trends = q.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
        labels, values = format_labels(trends)
        return {"enabled": True, "data": build_trend("Conversation Growth", labels, values)}

    @staticmethod
    def get_message_growth(context):
        q = ChatAnalyticsService._get_filtered_queryset(Message, 'created_at', context)
        trends = q.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
        labels, values = format_labels(trends)
        return {"enabled": True, "data": build_trend("Message Growth", labels, values)}

    @staticmethod
    def get_lead_generation_growth(context):
        q = ChatAnalyticsService._get_filtered_queryset(Lead, 'created_at', context).filter(source='chatbot')
        trends = q.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
        labels, values = format_labels(trends)
        return {"enabled": True, "data": build_trend("Lead Generation Growth", labels, values)}

    @staticmethod
    def get_qualification_growth(context):
        q = ChatAnalyticsService._get_filtered_queryset(Lead, 'created_at', context).filter(source='chatbot', status__in=['qualified', 'converted'])
        trends = q.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
        labels, values = format_labels(trends)
        return {"enabled": True, "data": build_trend("Qualification Growth", labels, values)}

    @staticmethod
    def get_chat_insights(context):
        insights = []
        
        conv_q = ChatAnalyticsService._get_filtered_queryset(ConversationSession, 'created_at', context)
        msg_q = ChatAnalyticsService._get_filtered_queryset(Message, 'created_at', context)
        leads_q = ChatAnalyticsService._get_filtered_queryset(Lead, 'created_at', context).filter(source='chatbot')
        
        top_activity_day = conv_q.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('-count').first()
        if top_activity_day and top_activity_day['date']:
            insights.append({"title": "Highest Chat Activity Day", "value": f"{top_activity_day['date'].strftime('%b %d')} ({top_activity_day['count']} chats)", "enabled": True})
            
        total_conv = conv_q.count()
        total_msg = msg_q.count()
        if total_conv > 0:
            avg_msgs = round(total_msg / total_conv, 1)
            insights.append({"title": "Average Messages Per Conversation", "value": str(avg_msgs), "enabled": True})
            
        total_leads = leads_q.count()
        if total_conv > 0:
            conv_rate = round((total_leads / total_conv) * 100, 1)
            insights.append({"title": "Lead Conversion From Chat", "value": f"{conv_rate}%", "enabled": True})
            
        # For "Most Active Chat Period", just calculate the most active hour if possible, or just skip it if it's too complex. 
        # Actually we can do it deterministically.
        return {"enabled": True, "data": insights}

    @staticmethod
    def build_response(context):
        if not ChatAnalyticsService._is_tracking_enabled():
            return ChatAnalyticsService._get_disabled_response()
            
        return {
            "executive_metrics": ChatAnalyticsService.get_executive_metrics(context),
            "conversation_growth": ChatAnalyticsService.get_conversation_growth(context),
            "message_growth": ChatAnalyticsService.get_message_growth(context),
            "lead_generation_growth": ChatAnalyticsService.get_lead_generation_growth(context),
            "qualification_growth": ChatAnalyticsService.get_qualification_growth(context),
            "chat_insights": ChatAnalyticsService.get_chat_insights(context)
        }
