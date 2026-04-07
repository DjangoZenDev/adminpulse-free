from rest_framework import serializers
from .models import Activity, Metric, MetricHistory, Notification


class ActivitySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Activity
        fields = ["id", "user", "username", "action", "target", "timestamp"]
        read_only_fields = ["id", "timestamp"]


class MetricSerializer(serializers.ModelSerializer):
    change_percent = serializers.ReadOnlyField()
    trend = serializers.ReadOnlyField()

    class Meta:
        model = Metric
        fields = [
            "id",
            "name",
            "value",
            "previous_value",
            "unit",
            "icon",
            "change_percent",
            "trend",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "user",
            "message",
            "notification_type",
            "is_read",
            "link",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class MetricHistorySerializer(serializers.ModelSerializer):
    metric_name = serializers.CharField(source="metric.name", read_only=True)

    class Meta:
        model = MetricHistory
        fields = [
            "id",
            "metric",
            "metric_name",
            "value",
            "recorded_at",
        ]
        read_only_fields = ["id"]
