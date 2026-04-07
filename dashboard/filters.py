import django_filters
from .models import Activity, Metric, MetricHistory, Notification


class ActivityFilter(django_filters.FilterSet):
    action = django_filters.CharFilter(lookup_expr="icontains")
    target = django_filters.CharFilter(lookup_expr="icontains")
    user = django_filters.NumberFilter(field_name="user__id")
    timestamp_after = django_filters.DateTimeFilter(
        field_name="timestamp", lookup_expr="gte"
    )
    timestamp_before = django_filters.DateTimeFilter(
        field_name="timestamp", lookup_expr="lte"
    )

    class Meta:
        model = Activity
        fields = ["action", "target", "user", "timestamp_after", "timestamp_before"]


class MetricFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    unit = django_filters.ChoiceFilter(choices=Metric.UNIT_CHOICES)

    class Meta:
        model = Metric
        fields = ["name", "unit"]


class NotificationFilter(django_filters.FilterSet):
    notification_type = django_filters.ChoiceFilter(choices=Notification.TYPE_CHOICES)
    is_read = django_filters.BooleanFilter()
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )

    class Meta:
        model = Notification
        fields = ["notification_type", "is_read", "created_after", "created_before"]


class MetricHistoryFilter(django_filters.FilterSet):
    metric = django_filters.NumberFilter(field_name="metric__id")
    metric_name = django_filters.CharFilter(field_name="metric__name", lookup_expr="icontains")
    recorded_after = django_filters.DateTimeFilter(
        field_name="recorded_at", lookup_expr="gte"
    )
    recorded_before = django_filters.DateTimeFilter(
        field_name="recorded_at", lookup_expr="lte"
    )

    class Meta:
        model = MetricHistory
        fields = ["metric", "metric_name", "recorded_after", "recorded_before"]
