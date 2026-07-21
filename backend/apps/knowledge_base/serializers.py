from rest_framework import serializers

from apps.knowledge_base.models import KnowledgeEntry, Category, Tag, KnowledgeEntryVersion


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'color', 'icon', 'sort_order', 'is_active']
        read_only_fields = ['id', 'slug']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'is_active']
        read_only_fields = ['id', 'slug']


class KnowledgeEntryListSerializer(serializers.ModelSerializer):
    """Read-only serializer for list views (subset of fields)."""
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = KnowledgeEntry
        fields = [
            'id', 'category', 'tags', 'title', 'slug', 'status', 'source',
            'sort_order', 'published_at', 'created_at', 'updated_at',
        ]
        read_only_fields = fields


class KnowledgeEntryDetailSerializer(serializers.ModelSerializer):
    """Read-only serializer for detail views (full fields)."""
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()

    class Meta:
        model = KnowledgeEntry
        fields = [
            'id', 'category', 'tags', 'title', 'slug', 'status', 'source',
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

    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=False,
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
    change_summary = serializers.CharField(required=False, default='', allow_blank=True)

    def __init__(self, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        super().__init__(*args, **kwargs)
        if partial:
            # For PATCH: make all fields optional
            for field_name in self.fields:
                self.fields[field_name].required = False

    def validate(self, attrs):
        # In partial mode, only return fields that were actually submitted
        if hasattr(self, 'initial_data'):
            submitted_keys = set(self.initial_data.keys())
            attrs = {k: v for k, v in attrs.items() if k in submitted_keys}
        return attrs


class KnowledgeEntryVersionListSerializer(serializers.ModelSerializer):
    """Serializer for listing versions of a knowledge entry."""
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = KnowledgeEntryVersion
        fields = [
            'id', 'knowledge_entry', 'version_number', 'status',
            'created_by', 'created_at', 'change_summary'
        ]
        read_only_fields = fields

    def get_created_by(self, obj):
        return obj.created_by.username if obj.created_by else None


class KnowledgeEntryVersionDetailSerializer(serializers.ModelSerializer):
    """Serializer for retrieving a specific version detail."""
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = KnowledgeEntryVersion
        fields = [
            'id', 'knowledge_entry', 'version_number', 'title', 'content',
            'structured_data', 'status', 'category_snapshot', 'tags_snapshot',
            'created_by', 'created_at', 'change_summary'
        ]
        read_only_fields = fields

    def get_created_by(self, obj):
        return obj.created_by.username if obj.created_by else None

