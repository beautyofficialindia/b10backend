from rest_framework import serializers

class MetricSerializer(serializers.Serializer):
    title = serializers.CharField()
    value = serializers.FloatField(allow_null=True, required=False)
    previous_value = serializers.FloatField(allow_null=True, required=False)
    difference = serializers.FloatField(allow_null=True, required=False)
    growth_percentage = serializers.FloatField(allow_null=True, required=False)
    enabled = serializers.BooleanField(default=True)

class TrendSerializer(serializers.Serializer):
    title = serializers.CharField()
    labels = serializers.ListField(child=serializers.CharField())
    values = serializers.ListField(child=serializers.FloatField())

class HealthSerializer(serializers.Serializer):
    module = serializers.CharField()
    status = serializers.ChoiceField(choices=["healthy", "warning", "error", "disabled"])
    enabled = serializers.BooleanField()
    tracking_enabled = serializers.BooleanField()
    message = serializers.CharField(allow_blank=True)

class InsightSerializer(serializers.Serializer):
    title = serializers.CharField()
    value = serializers.CharField()
    enabled = serializers.BooleanField(default=True)

# Wrapper Sections
class ExecutiveMetricsSectionSerializer(serializers.Serializer):
    enabled = serializers.BooleanField()
    data = serializers.DictField(child=MetricSerializer())

class GrowthMetricsSectionSerializer(serializers.Serializer):
    enabled = serializers.BooleanField()
    data = serializers.DictField(child=MetricSerializer())

class ModuleHealthSectionSerializer(serializers.Serializer):
    enabled = serializers.BooleanField()
    data = serializers.DictField(child=HealthSerializer())

class RecentTrendsSectionSerializer(serializers.Serializer):
    enabled = serializers.BooleanField()
    data = serializers.DictField(child=TrendSerializer())

class PlatformInsightsSectionSerializer(serializers.Serializer):
    enabled = serializers.BooleanField()
    data = serializers.ListField(child=InsightSerializer())

class TrendSectionSerializer(serializers.Serializer):
    enabled = serializers.BooleanField()
    data = TrendSerializer(allow_null=True, required=False)

class OverviewResponseSerializer(serializers.Serializer):
    executive_metrics = ExecutiveMetricsSectionSerializer()
    growth_metrics = GrowthMetricsSectionSerializer()
    module_health = ModuleHealthSectionSerializer()
    recent_trends = RecentTrendsSectionSerializer()
    platform_insights = PlatformInsightsSectionSerializer()

class LeadAnalyticsResponseSerializer(serializers.Serializer):
    executive_metrics = ExecutiveMetricsSectionSerializer()
    lead_funnel = TrendSectionSerializer()
    lead_sources = TrendSectionSerializer()
    status_distribution = TrendSectionSerializer()
    score_distribution = TrendSectionSerializer()
    growth_trend = TrendSectionSerializer()
    lead_insights = PlatformInsightsSectionSerializer()

class CrmAnalyticsResponseSerializer(serializers.Serializer):
    executive_metrics = ExecutiveMetricsSectionSerializer()
    crm_funnel = TrendSectionSerializer()
    followup_analytics = TrendSectionSerializer()
    status_distribution = TrendSectionSerializer()
    activity_trends = TrendSectionSerializer()
    user_performance = PlatformInsightsSectionSerializer()
    crm_insights = PlatformInsightsSectionSerializer()

class ChatAnalyticsResponseSerializer(serializers.Serializer):
    executive_metrics = ExecutiveMetricsSectionSerializer()
    conversation_growth = TrendSectionSerializer()
    message_growth = TrendSectionSerializer()
    lead_generation_growth = TrendSectionSerializer()
    qualification_growth = TrendSectionSerializer()
    chat_insights = PlatformInsightsSectionSerializer()

class KnowledgeAnalyticsResponseSerializer(serializers.Serializer):
    executive_metrics = ExecutiveMetricsSectionSerializer()
    knowledge_growth = TrendSectionSerializer()
    published_growth = TrendSectionSerializer()
    draft_growth = TrendSectionSerializer()
    category_distribution = TrendSectionSerializer()
    tag_distribution = TrendSectionSerializer()
    knowledge_insights = PlatformInsightsSectionSerializer()

class UserAnalyticsResponseSerializer(serializers.Serializer):
    executive_metrics = ExecutiveMetricsSectionSerializer()
    user_growth = TrendSectionSerializer()
    role_distribution = TrendSectionSerializer()
    permission_distribution = TrendSectionSerializer()
    user_insights = PlatformInsightsSectionSerializer()
