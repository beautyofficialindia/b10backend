from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from apps.platform_settings.services import SettingsService
from apps.crm.models import LeadActivity, LeadFollowUp, LeadStatusHistory
from apps.leads.models import Lead
from apps.analytics.utils import build_metric, build_trend, format_labels

class CrmAnalyticsService:
    
    @staticmethod
    def _is_tracking_enabled():
        return (SettingsService.is_feature_enabled("ENABLE_ANALYTICS") and 
                SettingsService.is_feature_enabled("ENABLE_CRM") and
                SettingsService.get_boolean("ANALYTICS", "TRACK_CRM_ACTIONS"))
                
    @staticmethod
    def _get_disabled_response():
        return {
            "executive_metrics": {"enabled": False, "data": {}},
            "crm_funnel": {"enabled": False, "data": None},
            "followup_analytics": {"enabled": False, "data": None},
            "status_distribution": {"enabled": False, "data": None},
            "activity_trends": {"enabled": False, "data": None},
            "user_performance": {"enabled": False, "data": []},
            "crm_insights": {"enabled": False, "data": []}
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
        # Lead Assignments: count of activities of type assignment
        assignments = CrmAnalyticsService._get_filtered_queryset(LeadActivity, 'created_at', context).filter(activity_type='assignment').count()
        
        # Followups and completed followups
        followups_q = CrmAnalyticsService._get_filtered_queryset(LeadFollowUp, 'created_at', context)
        total_followups = followups_q.count()
        completed_followups = followups_q.filter(status='completed').count()
        
        # CRM Activities
        activities = CrmAnalyticsService._get_filtered_queryset(LeadActivity, 'created_at', context).count()
        
        # Status Changes
        status_changes = CrmAnalyticsService._get_filtered_queryset(LeadStatusHistory, 'changed_at', context).count()
        
        data = {
            "assignments": build_metric("Assignments", assignments),
            "total_followups": build_metric("Followups", total_followups),
            "completed_followups": build_metric("Completed Followups", completed_followups),
            "crm_activities": build_metric("CRM Activities", activities),
            "status_changes": build_metric("Status Changes", status_changes),
        }
        return {"enabled": True, "data": data}

    @staticmethod
    def get_crm_funnel(context):
        # The CRM Funnel follows the lead through created -> assigned -> followed up -> qualified -> converted
        # Using Leads to derive these states in the current period.
        q = CrmAnalyticsService._get_filtered_queryset(Lead, 'created_at', context)
        
        total = q.count()
        assigned = q.filter(assigned_admin__isnull=False).count()
        followed_up = q.filter(followups__isnull=False).distinct().count()
        qualified = q.filter(status__in=['qualified', 'converted']).count()
        converted = q.filter(status='converted').count()
        
        return {
            "enabled": True,
            "data": build_trend("CRM Funnel", 
                                ["Created", "Assigned", "Followed Up", "Qualified", "Converted"], 
                                [total, assigned, followed_up, qualified, converted])
        }

    @staticmethod
    def get_followup_analytics(context):
        q = CrmAnalyticsService._get_filtered_queryset(LeadFollowUp, 'created_at', context)
        pending = q.filter(status='pending').count()
        completed = q.filter(status='completed').count()
        cancelled = q.filter(status='cancelled').count()
        
        return {
            "enabled": True,
            "data": build_trend("Followup Analytics", 
                                ["Pending", "Completed", "Cancelled"], 
                                [pending, completed, cancelled])
        }

    @staticmethod
    def get_status_distribution(context):
        q = CrmAnalyticsService._get_filtered_queryset(LeadStatusHistory, 'changed_at', context)
        statuses = q.values('new_status').annotate(count=Count('id')).order_by('-count')
        
        labels = []
        values = []
        for s in statuses:
            name = s['new_status'] if s['new_status'] else "Unknown"
            labels.append(name.replace('_', ' ').title())
            values.append(s['count'])
            
        return {
            "enabled": True,
            "data": build_trend("Status Distribution", labels, values)
        }

    @staticmethod
    def get_activity_trends(context):
        q = CrmAnalyticsService._get_filtered_queryset(LeadActivity, 'created_at', context)
        trends = q.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
        labels, values = format_labels(trends)
        
        return {
            "enabled": True,
            "data": build_trend("Activity Trends", labels, values)
        }

    @staticmethod
    def get_user_performance(context):
        insights = []
        
        # User Performance is tracked based on CRM interactions
        q_activities = CrmAnalyticsService._get_filtered_queryset(LeadActivity, 'created_at', context)
        # Assuming lead has assigned_admin (we might have to check LeadActivity's actor if we add one, but currently LeadActivity doesn't have an actor field)
        # But wait, LeadActivity has no user field in the model? 
        # Ah, looking at the model LeadActivity, it only has lead, activity_type, notes, created_at. No user/actor field!
        # Leads have assigned_admin.
        
        q_leads = CrmAnalyticsService._get_filtered_queryset(Lead, 'created_at', context)
        
        most_assignments = q_leads.filter(assigned_admin__isnull=False).values('assigned_admin__first_name', 'assigned_admin__last_name', 'assigned_admin__username').annotate(count=Count('id')).order_by('-count').first()
        
        if most_assignments:
            name = f"{most_assignments.get('assigned_admin__first_name', '')} {most_assignments.get('assigned_admin__last_name', '')}".strip()
            if not name: name = most_assignments.get('assigned_admin__username')
            insights.append({
                "title": "Most Assignments",
                "value": f"{name} ({most_assignments['count']} leads)",
                "enabled": True
            })
            
        return {"enabled": True, "data": insights}

    @staticmethod
    def get_crm_insights(context):
        insights = []
        
        q_activities = CrmAnalyticsService._get_filtered_queryset(LeadActivity, 'created_at', context)
        q_followups = CrmAnalyticsService._get_filtered_queryset(LeadFollowUp, 'created_at', context)
        q_status = CrmAnalyticsService._get_filtered_queryset(LeadStatusHistory, 'changed_at', context)
        
        top_activity_day = q_activities.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('-count').first()
        if top_activity_day and top_activity_day['date']:
            insights.append({"title": "Highest Activity Day", "value": f"{top_activity_day['date'].strftime('%b %d')} ({top_activity_day['count']} activities)", "enabled": True})
            
        top_status = q_status.values('new_status').annotate(count=Count('id')).order_by('-count').first()
        if top_status and top_status['new_status']:
            insights.append({"title": "Most Used CRM Status", "value": f"{top_status['new_status'].title()} ({top_status['count']} times)", "enabled": True})
            
        total_f = q_followups.count()
        comp_f = q_followups.filter(status='completed').count()
        if total_f > 0:
            rate = round((comp_f / total_f) * 100, 1)
            insights.append({"title": "Average Followup Completion Rate", "value": f"{rate}%", "enabled": True})
            
        return {"enabled": True, "data": insights}

    @staticmethod
    def build_response(context):
        if not CrmAnalyticsService._is_tracking_enabled():
            return CrmAnalyticsService._get_disabled_response()
            
        return {
            "executive_metrics": CrmAnalyticsService.get_executive_metrics(context),
            "crm_funnel": CrmAnalyticsService.get_crm_funnel(context),
            "followup_analytics": CrmAnalyticsService.get_followup_analytics(context),
            "status_distribution": CrmAnalyticsService.get_status_distribution(context),
            "activity_trends": CrmAnalyticsService.get_activity_trends(context),
            "user_performance": CrmAnalyticsService.get_user_performance(context),
            "crm_insights": CrmAnalyticsService.get_crm_insights(context)
        }
