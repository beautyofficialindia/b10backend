from django.db.models import Count, Avg
from django.db.models.functions import TruncDate
from apps.platform_settings.services import SettingsService
from apps.leads.models import Lead
from apps.analytics.utils import build_metric, build_trend, format_labels, calculate_percentage

class LeadAnalyticsService:
    
    @staticmethod
    def _is_tracking_enabled():
        return (SettingsService.is_feature_enabled("ENABLE_ANALYTICS") and 
                SettingsService.get_boolean("ANALYTICS", "TRACK_LEADS"))
                
    @staticmethod
    def _get_disabled_response():
        return {
            "executive_metrics": {"enabled": False, "data": {}},
            "lead_funnel": {"enabled": False, "data": None},
            "lead_sources": {"enabled": False, "data": None},
            "status_distribution": {"enabled": False, "data": None},
            "score_distribution": {"enabled": False, "data": None},
            "growth_trend": {"enabled": False, "data": None},
            "lead_insights": {"enabled": False, "data": []}
        }
        
    @staticmethod
    def _get_base_queryset(context):
        q = Lead.objects.all()
        start_date = context.get('start_date')
        end_date = context.get('end_date')
        if start_date:
            q = q.filter(created_at__gte=start_date)
        if end_date:
            q = q.filter(created_at__lte=end_date)
        return q

    @staticmethod
    def get_executive_metrics(context, q):
        total = q.count()
        qualified = q.filter(status__in=['qualified', 'converted', 'lost', 'escalated']).count()
        converted = q.filter(status='converted').count()
        lost = q.filter(status='lost').count()
        
        qualification_rate = calculate_percentage(qualified, total)
        conversion_rate = calculate_percentage(converted, qualified)
        loss_rate = calculate_percentage(lost, qualified)
        
        avg_score_dict = q.aggregate(avg=Avg('lead_score'))
        avg_score = avg_score_dict['avg'] if avg_score_dict['avg'] else 0.0
        
        data = {
            "total_leads": build_metric("Total Leads", total),
            "qualified_leads": build_metric("Qualified Leads", qualified),
            "converted_leads": build_metric("Converted Leads", converted),
            "qualification_rate": build_metric("Qualification Rate", qualification_rate),
            "conversion_rate": build_metric("Conversion Rate", conversion_rate),
            "loss_rate": build_metric("Loss Rate", loss_rate),
            "average_lead_score": build_metric("Average Lead Score", round(avg_score, 1))
        }
        return {"enabled": True, "data": data}

    @staticmethod
    def get_lead_funnel(context, q):
        total = q.count()
        qualified = q.filter(status__in=['qualified', 'converted', 'lost', 'escalated']).count()
        converted = q.filter(status='converted').count()
        lost = q.filter(status='lost').count()
        
        return {
            "enabled": True,
            "data": build_trend("Lead Funnel", ["Total", "Qualified", "Converted", "Lost"], [total, qualified, converted, lost])
        }

    @staticmethod
    def get_lead_sources(context, q):
        sources = q.values('source').annotate(count=Count('id')).order_by('-count')
        labels = []
        values = []
        for s in sources:
            name = s['source'] if s['source'] else "Unknown"
            labels.append(name.title())
            values.append(s['count'])
            
        return {
            "enabled": True,
            "data": build_trend("Lead Sources", labels, values)
        }

    @staticmethod
    def get_status_distribution(context, q):
        statuses = q.values('status').annotate(count=Count('id')).order_by('-count')
        labels = []
        values = []
        for s in statuses:
            name = s['status'] if s['status'] else "Unknown"
            labels.append(name.replace('_', ' ').title())
            values.append(s['count'])
            
        return {
            "enabled": True,
            "data": build_trend("Lead Status Distribution", labels, values)
        }

    @staticmethod
    def get_score_distribution(context, q):
        # Buckets: 0-25, 26-50, 51-75, 76-100
        buckets = {"0-25": 0, "26-50": 0, "51-75": 0, "76-100": 0}
        
        # A simple evaluation in python rather than complex DB Case/When for now, 
        # given it's typically fine for an MVP dashboard unless we have millions of records.
        # Alternatively, we can use DB queries:
        buckets["0-25"] = q.filter(lead_score__gte=0, lead_score__lte=25).count()
        buckets["26-50"] = q.filter(lead_score__gte=26, lead_score__lte=50).count()
        buckets["51-75"] = q.filter(lead_score__gte=51, lead_score__lte=75).count()
        buckets["76-100"] = q.filter(lead_score__gte=76, lead_score__lte=100).count()
        
        labels = list(buckets.keys())
        values = list(buckets.values())
        
        return {
            "enabled": True,
            "data": build_trend("Lead Score Distribution", labels, values)
        }

    @staticmethod
    def get_growth_trend(context, q):
        trends = q.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
        labels, values = format_labels(trends)
        return {
            "enabled": True, 
            "data": build_trend("Lead Growth Trend", labels, values)
        }

    @staticmethod
    def get_lead_insights(context, q):
        insights = []
        
        # 1. Highest Lead Generation Day
        top_day = q.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('-count').first()
        if top_day and top_day['date']:
            insights.append({"title": "Highest Lead Generation Day", "value": f"{top_day['date'].strftime('%b %d')} ({top_day['count']} leads)", "enabled": True})
            
        # 2. Highest Average Lead Score Day
        top_score_day = q.annotate(date=TruncDate('created_at')).values('date').annotate(avg_score=Avg('lead_score')).order_by('-avg_score').first()
        if top_score_day and top_score_day['date'] and top_score_day['avg_score'] is not None:
            insights.append({"title": "Highest Avg Score Day", "value": f"{top_score_day['date'].strftime('%b %d')} (Avg: {round(top_score_day['avg_score'], 1)})", "enabled": True})

        # 3. Top Lead Source
        top_source = q.values('source').annotate(count=Count('id')).order_by('-count').first()
        if top_source and top_source['source']:
            insights.append({"title": "Top Lead Source", "value": f"{top_source['source'].title()} ({top_source['count']} leads)", "enabled": True})
            
        # 4. Average Lead Score
        avg_score_dict = q.aggregate(avg=Avg('lead_score'))
        if avg_score_dict['avg'] is not None:
            insights.append({"title": "Average Lead Score", "value": str(round(avg_score_dict['avg'], 1)), "enabled": True})

        return {"enabled": True, "data": insights}

    @staticmethod
    def build_response(context):
        if not LeadAnalyticsService._is_tracking_enabled():
            return LeadAnalyticsService._get_disabled_response()
            
        q = LeadAnalyticsService._get_base_queryset(context)
            
        return {
            "executive_metrics": LeadAnalyticsService.get_executive_metrics(context, q),
            "lead_funnel": LeadAnalyticsService.get_lead_funnel(context, q),
            "lead_sources": LeadAnalyticsService.get_lead_sources(context, q),
            "status_distribution": LeadAnalyticsService.get_status_distribution(context, q),
            "score_distribution": LeadAnalyticsService.get_score_distribution(context, q),
            "growth_trend": LeadAnalyticsService.get_growth_trend(context, q),
            "lead_insights": LeadAnalyticsService.get_lead_insights(context, q)
        }
