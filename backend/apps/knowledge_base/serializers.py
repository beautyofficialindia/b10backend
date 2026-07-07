from rest_framework import serializers

from apps.knowledge_base.models import KnowledgeEntry


class KnowledgeEntryListSerializer(serializers.ModelSerializer):
    """Read-only serializer for list views (subset of fields)."""

    class Meta:
        model = KnowledgeEntry
        fields = [
            'id', 'category', 'title', 'slug', 'status', 'source',
            'sort_order', 'published_at', 'created_at', 'updated_at',
        ]
        read_only_fields = fields


class KnowledgeEntryDetailSerializer(serializers.ModelSerializer):
    """Read-only serializer for detail views (full fields)."""

    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()

    class Meta:
        model = KnowledgeEntry
        fields = [
            'id', 'category', 'title', 'slug', 'status', 'source',
            'sort_order', 'published_at', 'created_at', 'updated_at',
            'content', 'structured_data', 'created_by', 'updated_by',
        ]
        read_only_fields = fields

    def get_created_by(self, obj):
        return obj.created_by.username if obj.created_by else None

    def get_updated_by(self, obj):
        return obj.updated_by.username if obj.updated_by else None


class KnowledgeEntryWriteSerializer(serializers.Serializer):
    """Write serializer for create/update operations."""

    category = serializers.ChoiceField(
        choices=KnowledgeEntry.CATEGORY_CHOICES,
        required=True,
    )
    title = serializers.CharField(max_length=255, required=True)
    content = serializers.CharField(required=False, default='', allow_blank=True)
    structured_data = serializers.JSONField(required=False, default=dict)
    sort_order = serializers.IntegerField(required=False, default=0, min_value=0)
    source = serializers.ChoiceField(
        choices=KnowledgeEntry.SOURCE_CHOICES,
        required=False,
        default='manual',
    )

    def __init__(self, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        super().__init__(*args, **kwargs)
        if partial:
            # For PATCH: make all fields optional
            for field_name in self.fields:
                self.fields[field_name].required = False
