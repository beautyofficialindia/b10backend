from django.db.models import Count, Avg, F
from django.db.models.functions import TruncDate
from django.contrib.auth.models import User, Group, Permission
from apps.platform_settings.services import SettingsService
from apps.analytics.utils import build_metric, build_trend, format_labels

class UserAnalyticsService:
    
    @staticmethod
    def _is_tracking_enabled():
        return SettingsService.is_feature_enabled("ENABLE_ANALYTICS")
                
    @staticmethod
    def _get_disabled_response():
        return {
            "executive_metrics": {"enabled": False, "data": {}},
            "user_growth": {"enabled": False, "data": None},
            "role_distribution": {"enabled": False, "data": None},
            "permission_distribution": {"enabled": False, "data": None},
            "user_insights": {"enabled": False, "data": []}
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
        q = UserAnalyticsService._get_filtered_queryset(User, 'date_joined', context)
        
        total_users = q.count()
        active_users = q.filter(is_active=True).count()
        staff_users = q.filter(is_staff=True).count()
        super_users = q.filter(is_superuser=True).count()
        
        total_roles = Group.objects.count()
        total_permissions = Permission.objects.count()
        
        data = {
            "total_users": build_metric("Total Users", total_users),
            "total_roles": build_metric("Total Roles", total_roles),
            "total_permissions": build_metric("Total Permissions", total_permissions),
            "active_users": build_metric("Active Users", active_users),
            "staff_users": build_metric("Staff Users", staff_users),
            "super_users": build_metric("Super Users", super_users),
        }
        return {"enabled": True, "data": data}

    @staticmethod
    def get_user_growth(context):
        q = UserAnalyticsService._get_filtered_queryset(User, 'date_joined', context)
        trends = q.annotate(date=TruncDate('date_joined')).values('date').annotate(count=Count('id')).order_by('date')
        labels, values = format_labels(trends)
        return {"enabled": True, "data": build_trend("User Growth", labels, values)}

    @staticmethod
    def get_role_distribution(context):
        q = UserAnalyticsService._get_filtered_queryset(User, 'date_joined', context)
        roles = q.values('groups__name').annotate(count=Count('id')).order_by('-count')
        labels = [r['groups__name'] if r['groups__name'] else 'No Role' for r in roles]
        values = [r['count'] for r in roles]
        return {"enabled": True, "data": build_trend("Role Distribution", labels, values)}

    @staticmethod
    def get_permission_distribution(context):
        q = UserAnalyticsService._get_filtered_queryset(User, 'date_joined', context)
        perms = q.values('user_permissions__name').annotate(count=Count('id')).order_by('-count')[:20] # top 20 to avoid huge charts
        labels = [p['user_permissions__name'] if p['user_permissions__name'] else 'Group Perms Only' for p in perms]
        values = [p['count'] for p in perms]
        return {"enabled": True, "data": build_trend("Permission Distribution", labels, values)}

    @staticmethod
    def get_user_insights(context):
        insights = []
        
        q = UserAnalyticsService._get_filtered_queryset(User, 'date_joined', context)
        
        top_role = q.values('groups__name').annotate(count=Count('id')).order_by('-count').first()
        if top_role and top_role['groups__name']:
            insights.append({"title": "Most Used Role", "value": f"{top_role['groups__name']} ({top_role['count']} users)", "enabled": True})
            
        top_day = q.annotate(date=TruncDate('date_joined')).values('date').annotate(count=Count('id')).order_by('-count').first()
        if top_day and top_day['date']:
            insights.append({"title": "Newest User Creation Day", "value": f"{top_day['date'].strftime('%b %d')} ({top_day['count']} users)", "enabled": True})
            
        total_users = q.count()
        super_users = q.filter(is_superuser=True).count()
        if total_users > 0:
            admin_ratio = round((super_users / total_users) * 100, 1)
            insights.append({"title": "Admin Ratio", "value": f"{admin_ratio}%", "enabled": True})
            
        return {"enabled": True, "data": insights}

    @staticmethod
    def build_response(context):
        if not UserAnalyticsService._is_tracking_enabled():
            return UserAnalyticsService._get_disabled_response()
            
        return {
            "executive_metrics": UserAnalyticsService.get_executive_metrics(context),
            "user_growth": UserAnalyticsService.get_user_growth(context),
            "role_distribution": UserAnalyticsService.get_role_distribution(context),
            "permission_distribution": UserAnalyticsService.get_permission_distribution(context),
            "user_insights": UserAnalyticsService.get_user_insights(context)
        }
