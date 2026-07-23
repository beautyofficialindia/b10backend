from apps.platform_settings.services import SettingsService
from apps.analytics.models import AnalyticsEvent
from apps.leads.models import Lead, LeadNote
from apps.knowledge_base.models import KnowledgeEntry
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg
from django.db.models.functions import TruncDate

from apps.analytics.utils import build_metric, build_health, build_trend, format_labels, calculate_growth, calculate_percentage
from apps.analytics.constants import HealthStatus

User = get_user_model()

class OverviewAnalyticsService:
    
    @staticmethod
    def get_executive_metrics(context):
        start_date = context.get('start_date')
        end_date = context.get('end_date')
        
        chat_q = AnalyticsEvent.objects.filter(event_type='chat_started')
        leads_q = Lead.objects.all()
        notes_q = LeadNote.objects.all()
        kb_q = KnowledgeEntry.objects.filter(is_deleted=False)
        users_q = User.objects.filter(is_active=True)
        event_q = AnalyticsEvent.objects.all()
        
        if start_date:
            chat_q = chat_q.filter(created_at__gte=start_date)
            leads_q = leads_q.filter(created_at__gte=start_date)
            notes_q = notes_q.filter(created_at__gte=start_date)
            kb_q = kb_q.filter(created_at__gte=start_date)
            users_q = users_q.filter(date_joined__gte=start_date)
            event_q = event_q.filter(created_at__gte=start_date)
        if end_date:
            chat_q = chat_q.filter(created_at__lte=end_date)
            leads_q = leads_q.filter(created_at__lte=end_date)
            notes_q = notes_q.filter(created_at__lte=end_date)
            kb_q = kb_q.filter(created_at__lte=end_date)
            users_q = users_q.filter(date_joined__lte=end_date)
            event_q = event_q.filter(created_at__lte=end_date)

        qualified_leads = leads_q.filter(status__in=['qualified', 'converted', 'lost', 'escalated']).count()
        conversion_rate = calculate_percentage(leads_q.filter(status='converted').count(), qualified_leads)

        data = {
            "conversations": build_metric("Conversations", chat_q.count()),
            "leads": build_metric("Leads Captured", leads_q.count()),
            "qualified_leads": build_metric("Qualified Leads", qualified_leads),
            "conversion_rate": build_metric("Conversion Rate", conversion_rate),
            "active_users": build_metric("Active Users", users_q.count()),
            "knowledge_articles": build_metric("Knowledge Articles", kb_q.count()),
            "crm_activities": build_metric("CRM Activities", notes_q.count()),
            "analytics_events": build_metric("Analytics Events", event_q.count())
        }
        return {"enabled": True, "data": data}
    
    @staticmethod
    def get_growth_metrics(context):
        start_date = context.get('start_date')
        end_date = context.get('end_date')
        prev_start = context.get('previous_start_date')
        prev_end = context.get('previous_end_date')

        if not start_date or not end_date or not prev_start or not prev_end:
            return {"enabled": False, "data": {}}
        
        def compute_growth(model_class, date_field='created_at', is_event=False, event_type=None, status_filter=None):
            if is_event: q = model_class.objects.filter(event_type=event_type)
            else:
                q = model_class.objects.all()
                if status_filter: q = q.filter(status=status_filter)
            
            curr_val = q.filter(**{f"{date_field}__gte": start_date, f"{date_field}__lte": end_date}).count()
            prev_val = q.filter(**{f"{date_field}__gte": prev_start, f"{date_field}__lte": prev_end}).count()
            return curr_val, prev_val

        curr_qual = Lead.objects.filter(status__in=['qualified', 'converted', 'lost', 'escalated'], created_at__gte=start_date, created_at__lte=end_date).count()
        prev_qual = Lead.objects.filter(status__in=['qualified', 'converted', 'lost', 'escalated'], created_at__gte=prev_start, created_at__lte=prev_end).count()
        curr_conv = Lead.objects.filter(status='converted', created_at__gte=start_date, created_at__lte=end_date).count()
        prev_conv = Lead.objects.filter(status='converted', created_at__gte=prev_start, created_at__lte=prev_end).count()
        
        curr_conv_rate = calculate_percentage(curr_conv, curr_qual)
        prev_conv_rate = calculate_percentage(prev_conv, prev_qual)
        
        curr_leads, prev_leads = compute_growth(Lead)
        curr_chat, prev_chat = compute_growth(AnalyticsEvent, is_event=True, event_type='chat_started')
        curr_kb, prev_kb = compute_growth(KnowledgeEntry)
        curr_crm, prev_crm = compute_growth(LeadNote)

        data = {
            "leads": build_metric("Leads", curr_leads, prev_leads),
            "conversations": build_metric("Conversations", curr_chat, prev_chat),
            "conversion_rate": build_metric("Conversion Rate", curr_conv_rate, prev_conv_rate),
            "knowledge_entries": build_metric("Knowledge Entries", curr_kb, prev_kb),
            "crm_activities": build_metric("CRM Activities", curr_crm, prev_crm)
        }
        return {"enabled": True, "data": data}
        
    @staticmethod
    def get_module_health():
        # Chatbot
        chatbot_enabled = SettingsService.is_feature_enabled("ENABLE_AI_CHATBOT")
        chatbot_health = build_health("Chatbot", HealthStatus.HEALTHY if chatbot_enabled else HealthStatus.DISABLED, chatbot_enabled, chatbot_enabled)
        
        # CRM
        crm_enabled = SettingsService.is_feature_enabled("ENABLE_CRM")
        crm_health = build_health("CRM", HealthStatus.HEALTHY if crm_enabled else HealthStatus.DISABLED, crm_enabled, crm_enabled)
        
        # Knowledge
        kb_enabled = SettingsService.is_feature_enabled("ENABLE_KNOWLEDGE_BASE")
        kb_health = build_health("Knowledge Base", HealthStatus.HEALTHY if kb_enabled else HealthStatus.DISABLED, kb_enabled, kb_enabled)
        
        # Analytics Tracking
        analytics_enabled = SettingsService.is_feature_enabled("ENABLE_ANALYTICS")
        analytics_tracking = SettingsService.get_boolean("ANALYTICS", "TRACK_CONVERSATIONS") # rough proxy
        
        analytics_health_status = HealthStatus.HEALTHY
        if not analytics_enabled:
            analytics_health_status = HealthStatus.DISABLED
        elif not analytics_tracking:
            analytics_health_status = HealthStatus.WARNING
            
        analytics_health = build_health(
            "Analytics", 
            analytics_health_status, 
            analytics_enabled, 
            analytics_tracking,
            "Tracking disabled" if not analytics_tracking and analytics_enabled else ""
        )
        
        data = {
            "chatbot": chatbot_health,
            "crm": crm_health,
            "knowledge_base": kb_health,
            "analytics_tracking": analytics_health,
            "settings": build_health("Settings", HealthStatus.HEALTHY, True, True),
            "users_roles": build_health("Users & Roles", HealthStatus.HEALTHY, True, True)
        }
        return {"enabled": True, "data": data}
        
    @staticmethod
    def get_recent_trends(context):
        start_date = context.get('start_date')
        end_date = context.get('end_date')

        def compute_trend(model_class, title, date_field='created_at', is_event=False, event_type=None):
            if is_event: q = model_class.objects.filter(event_type=event_type)
            else: q = model_class.objects.all()
            
            if start_date: q = q.filter(**{f"{date_field}__gte": start_date})
            if end_date: q = q.filter(**{f"{date_field}__lte": end_date})
            
            trends = q.annotate(date=TruncDate(date_field)).values('date').annotate(count=Count('id')).order_by('date')
            labels, values = format_labels(trends)
            return build_trend(title, labels, values)

        data = {
            "leads": compute_trend(Lead, "Lead Growth"),
            "conversations": compute_trend(AnalyticsEvent, "Conversation Growth", is_event=True, event_type='chat_started'),
            "knowledge_entries": compute_trend(KnowledgeEntry, "Knowledge Growth"),
            "crm_activities": compute_trend(LeadNote, "CRM Growth")
        }
        return {"enabled": True, "data": data}
        
    @staticmethod
    def get_platform_insights(context):
        start_date = context.get('start_date')
        end_date = context.get('end_date')
        insights = []
        
        leads_q = Lead.objects.all()
        if start_date: leads_q = leads_q.filter(created_at__gte=start_date)
        if end_date: leads_q = leads_q.filter(created_at__lte=end_date)
        
        # 1. Top Lead Source
        top_source = leads_q.values('source').annotate(count=Count('id')).order_by('-count').first()
        if top_source and top_source['source']:
            insights.append({"title": "Top Lead Source", "value": f"{top_source['source'].title()} ({top_source['count']})", "enabled": True})
            
        # 2. Average Lead Score
        avg_score = leads_q.aggregate(avg=Avg('lead_score'))['avg']
        if avg_score is not None:
            insights.append({"title": "Average Lead Score", "value": str(round(avg_score, 1)), "enabled": True})
            
        # 3. Highest Lead Generation Day
        top_day = leads_q.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('-count').first()
        if top_day and top_day['date']:
            insights.append({"title": "Highest Lead Generation Day", "value": f"{top_day['date'].strftime('%b %d')} ({top_day['count']} leads)", "enabled": True})

        # 4. Most Used Knowledge Category
        kb_q = KnowledgeEntry.objects.filter(is_deleted=False)
        if start_date: kb_q = kb_q.filter(created_at__gte=start_date)
        if end_date: kb_q = kb_q.filter(created_at__lte=end_date)
        
        top_cat = kb_q.values('category__name').annotate(count=Count('id')).order_by('-count').first()
        if top_cat and top_cat['category__name']:
            insights.append({"title": "Most Used KB Category", "value": f"{top_cat['category__name'].title()} ({top_cat['count']})", "enabled": True})
            
        # 5. Most Active CRM User
        notes_q = LeadNote.objects.all()
        if start_date: notes_q = notes_q.filter(created_at__gte=start_date)
        if end_date: notes_q = notes_q.filter(created_at__lte=end_date)
        
        top_user_q = notes_q.values('author_id').annotate(count=Count('id')).order_by('-count').first()
        if top_user_q and top_user_q['author_id']:
            author = User.objects.filter(id=top_user_q['author_id']).first()
            if author:
                insights.append({"title": "Most Active CRM User", "value": f"{author.get_full_name() or author.email} ({top_user_q['count']} activities)", "enabled": True})

        return {"enabled": True, "data": insights}
        
    @staticmethod
    def build_response(context):
        return {
            "executive_metrics": OverviewAnalyticsService.get_executive_metrics(context),
            "growth_metrics": OverviewAnalyticsService.get_growth_metrics(context),
            "module_health": OverviewAnalyticsService.get_module_health(),
            "recent_trends": OverviewAnalyticsService.get_recent_trends(context),
            "platform_insights": OverviewAnalyticsService.get_platform_insights(context)
        }
