from typing import List, Any

from rest_framework import serializers


class TaskSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    due_date = serializers.DateField(required=False, allow_null=True)
    estimated_hours = serializers.FloatField(required=False, allow_null=True)
    importance = serializers.IntegerField(required=False, min_value=1, max_value=10)
    dependencies = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )
    id = serializers.CharField(required=False)


class AnalyzeRequestSerializer(serializers.Serializer):
    strategy = serializers.CharField(required=False, allow_blank=True)
    tasks = TaskSerializer(many=True)


class AnalyzeResponseTaskSerializer(TaskSerializer):
    calculated_score = serializers.FloatField()
    priority_label = serializers.CharField()
    strategy = serializers.CharField()
    explanation = serializers.CharField()
    metadata = serializers.JSONField()


class SuggestQuerySerializer(serializers.Serializer):
    strategy = serializers.CharField(required=False, allow_blank=True)
    limit = serializers.IntegerField(required=False, min_value=1, max_value=50)


class SuggestResponseSerializer(serializers.Serializer):
    tasks = AnalyzeResponseTaskSerializer(many=True)
