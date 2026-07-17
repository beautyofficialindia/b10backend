from django.db.models import Count, Avg, F
from django.db.models.functions import TruncDate
from apps.platform_settings.services import SettingsService
from apps.knowledge_base.models import KnowledgeEntry, Category, Tag, KnowledgeEntryVersion
from apps.analytics.utils import build_metric, build_trend, format_labels

class KnowledgeAnalyticsService:
    
    @staticmethod
    def _is_tracking_enabled():
        return (SettingsService.is_feature_enabled("ENABLE_ANALYTICS") and 
                SettingsService.is_feature_enabled("ENABLE_KNOWLEDGE_BASE"))
                
    @staticmethod
    def _get_disabled_response():
        return {
            "executive_metrics": {"enabled": False, "data": {}},
            "knowledge_growth": {"enabled": False, "data": None},
            "published_growth": {"enabled": False, "data": None},
            "draft_growth": {"enabled": False, "data": None},
            "category_distribution": {"enabled": False, "data": None},
            "tag_distribution": {"enabled": False, "data": None},
            "knowledge_insights": {"enabled": False, "data": []}
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
        q = KnowledgeAnalyticsService._get_filtered_queryset(KnowledgeEntry, 'created_at', context)
        
        total = q.count()
        published = q.filter(status='published').count()
        draft = q.filter(status='draft').count()
        archived = q.filter(status='archived').count()
        
        # Categories and Tags don't have created_at usually, we can just return totals or bounded by entry created_at? 
        # The prompt says "Total Categories", "Total Tags". I'll just return absolute totals since they don't have created_at.
        total_cats = Category.objects.count()
        total_tags = Tag.objects.count()
        
        data = {
            "total_entries": build_metric("Total Knowledge Entries", total),
            "published_entries": build_metric("Published Entries", published),
            "draft_entries": build_metric("Draft Entries", draft),
            "archived_entries": build_metric("Archived Entries", archived),
            "total_categories": build_metric("Total Categories", total_cats),
            "total_tags": build_metric("Total Tags", total_tags),
        }
        return {"enabled": True, "data": data}

    @staticmethod
    def get_knowledge_growth(context):
        q = KnowledgeAnalyticsService._get_filtered_queryset(KnowledgeEntry, 'created_at', context)
        trends = q.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
        labels, values = format_labels(trends)
        return {"enabled": True, "data": build_trend("Knowledge Growth", labels, values)}

    @staticmethod
    def get_published_growth(context):
        q = KnowledgeAnalyticsService._get_filtered_queryset(KnowledgeEntry, 'published_at', context).filter(status='published', published_at__isnull=False)
        trends = q.annotate(date=TruncDate('published_at')).values('date').annotate(count=Count('id')).order_by('date')
        labels, values = format_labels(trends)
        return {"enabled": True, "data": build_trend("Published Growth", labels, values)}

    @staticmethod
    def get_draft_growth(context):
        q = KnowledgeAnalyticsService._get_filtered_queryset(KnowledgeEntry, 'created_at', context).filter(status='draft')
        trends = q.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
        labels, values = format_labels(trends)
        return {"enabled": True, "data": build_trend("Draft Growth", labels, values)}

    @staticmethod
    def get_category_distribution(context):
        q = KnowledgeAnalyticsService._get_filtered_queryset(KnowledgeEntry, 'created_at', context)
        cats = q.values('category__name').annotate(count=Count('id')).order_by('-count')
        labels = [c['category__name'] for c in cats if c['category__name']]
        values = [c['count'] for c in cats if c['category__name']]
        return {"enabled": True, "data": build_trend("Category Distribution", labels, values)}
        
    @staticmethod
    def get_tag_distribution(context):
        q = KnowledgeAnalyticsService._get_filtered_queryset(KnowledgeEntry, 'created_at', context)
        tags = q.values('tags__name').annotate(count=Count('id')).order_by('-count')
        labels = [t['tags__name'] for t in tags if t['tags__name']]
        values = [t['count'] for t in tags if t['tags__name']]
        return {"enabled": True, "data": build_trend("Tag Usage Distribution", labels, values)}

    @staticmethod
    def get_knowledge_insights(context):
        insights = []
        
        q = KnowledgeAnalyticsService._get_filtered_queryset(KnowledgeEntry, 'created_at', context)
        
        top_cat = q.values('category__name').annotate(count=Count('id')).order_by('-count').first()
        if top_cat and top_cat['category__name']:
            insights.append({"title": "Most Used Category", "value": f"{top_cat['category__name']} ({top_cat['count']} entries)", "enabled": True})
            
        top_tag = q.values('tags__name').annotate(count=Count('id')).order_by('-count').first()
        if top_tag and top_tag['tags__name']:
            insights.append({"title": "Most Used Tag", "value": f"{top_tag['tags__name']} ({top_tag['count']} entries)", "enabled": True})
            
        top_day = KnowledgeAnalyticsService._get_filtered_queryset(KnowledgeEntry, 'published_at', context).filter(status='published', published_at__isnull=False).annotate(date=TruncDate('published_at')).values('date').annotate(count=Count('id')).order_by('-count').first()
        if top_day and top_day['date']:
            insights.append({"title": "Highest Publishing Day", "value": f"{top_day['date'].strftime('%b %d')} ({top_day['count']} published)", "enabled": True})
            
        total_entries = q.count()
        total_versions = KnowledgeAnalyticsService._get_filtered_queryset(KnowledgeEntryVersion, 'created_at', context).count()
        if total_entries > 0:
            avg_v = round(total_versions / total_entries, 1)
            insights.append({"title": "Average Versions Per Entry", "value": str(avg_v), "enabled": True})
            
        return {"enabled": True, "data": insights}

    @staticmethod
    def build_response(context):
        if not KnowledgeAnalyticsService._is_tracking_enabled():
            return KnowledgeAnalyticsService._get_disabled_response()
            
        return {
            "executive_metrics": KnowledgeAnalyticsService.get_executive_metrics(context),
            "knowledge_growth": KnowledgeAnalyticsService.get_knowledge_growth(context),
            "published_growth": KnowledgeAnalyticsService.get_published_growth(context),
            "draft_growth": KnowledgeAnalyticsService.get_draft_growth(context),
            "category_distribution": KnowledgeAnalyticsService.get_category_distribution(context),
            "tag_distribution": KnowledgeAnalyticsService.get_tag_distribution(context),
            "knowledge_insights": KnowledgeAnalyticsService.get_knowledge_insights(context)
        }
