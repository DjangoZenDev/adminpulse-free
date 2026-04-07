from rest_framework import viewsets
from .models import Activity, Metric, MetricHistory, Notification
from .serializers import (
    ActivitySerializer,
    MetricSerializer,
    MetricHistorySerializer,
    NotificationSerializer,
)
from .filters import ActivityFilter, MetricFilter, MetricHistoryFilter, NotificationFilter


class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.select_related("user").all()
    serializer_class = ActivitySerializer
    filterset_class = ActivityFilter
    search_fields = ["action", "target", "user__username"]
    ordering_fields = ["timestamp", "action"]
    ordering = ["-timestamp"]


class MetricViewSet(viewsets.ModelViewSet):
    queryset = Metric.objects.all()
    serializer_class = MetricSerializer
    filterset_class = MetricFilter
    search_fields = ["name"]
    ordering_fields = ["name", "value", "updated_at"]
    ordering = ["name"]


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    filterset_class = NotificationFilter
    search_fields = ["message"]
    ordering_fields = ["created_at", "notification_type", "is_read"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class MetricHistoryViewSet(viewsets.ModelViewSet):
    queryset = MetricHistory.objects.select_related("metric").all()
    serializer_class = MetricHistorySerializer
    filterset_class = MetricHistoryFilter
    search_fields = ["metric__name"]
    ordering_fields = ["recorded_at", "value"]
    ordering = ["-recorded_at"]
