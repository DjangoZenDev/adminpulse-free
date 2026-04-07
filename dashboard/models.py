from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("admin", "Administrator"),
        ("manager", "Manager"),
        ("analyst", "Analyst"),
        ("viewer", "Viewer"),
    ]

    SIDEBAR_COLOR_CHOICES = [
        ("slate-900", "Slate"),
        ("gray-900", "Gray"),
        ("zinc-900", "Zinc"),
        ("blue-900", "Blue"),
        ("indigo-900", "Indigo"),
    ]

    ACCENT_COLOR_CHOICES = [
        ("indigo", "Indigo"),
        ("blue", "Blue"),
        ("emerald", "Emerald"),
        ("amber", "Amber"),
        ("rose", "Rose"),
        ("violet", "Violet"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.URLField(
        max_length=500,
        blank=True,
        default="https://ui-avatars.com/api/?name=User&background=6366f1&color=fff",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="viewer")
    dark_mode = models.BooleanField(default=False)
    sidebar_color = models.CharField(max_length=20, choices=SIDEBAR_COLOR_CHOICES, default="slate-900")
    accent_color = models.CharField(max_length=20, choices=ACCENT_COLOR_CHOICES, default="indigo")
    compact_mode = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    class Meta:
        ordering = ["-created_at"]


class Activity(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="activities"
    )
    action = models.CharField(max_length=255)
    target = models.CharField(max_length=255, blank=True, default="")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.action}"

    class Meta:
        ordering = ["-timestamp"]
        verbose_name_plural = "Activities"


class Metric(models.Model):
    UNIT_CHOICES = [
        ("count", "Count"),
        ("currency", "Currency ($)"),
        ("percent", "Percentage (%)"),
        ("rate", "Rate"),
    ]

    name = models.CharField(max_length=100, unique=True)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    previous_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default="count")
    icon = models.CharField(max_length=50, blank=True, default="chart-bar")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}: {self.value}"

    @property
    def change_percent(self):
        if self.previous_value and self.previous_value != 0:
            return round(
                ((self.value - self.previous_value) / self.previous_value) * 100, 1
            )
        return 0

    @property
    def trend(self):
        if self.value > self.previous_value:
            return "up"
        elif self.value < self.previous_value:
            return "down"
        return "flat"

    class Meta:
        ordering = ["name"]


class MetricHistory(models.Model):
    metric = models.ForeignKey(Metric, on_delete=models.CASCADE, related_name="history")
    value = models.DecimalField(max_digits=12, decimal_places=2)
    recorded_at = models.DateTimeField()

    class Meta:
        ordering = ["recorded_at"]
        unique_together = ["metric", "recorded_at"]

    def __str__(self):
        return f"{self.metric.name}: {self.value} @ {self.recorded_at}"


class Notification(models.Model):
    TYPE_CHOICES = [
        ("info", "Information"),
        ("success", "Success"),
        ("warning", "Warning"),
        ("error", "Error"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=500)
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="info")
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=500, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.notification_type}] {self.message[:50]}"


class DashboardLayout(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="dashboard_layout")
    layout = models.JSONField(default=list)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Layout for {self.user.username}"


# Available widgets for the customizable dashboard
AVAILABLE_WIDGETS = {
    "kpi_cards": {
        "label": "KPI Cards",
        "template": "dashboard/partials/kpi_cards.html",
        "default_width": "full",
        "icon": "chart-bar",
    },
    "activity_feed": {
        "label": "Recent Activity",
        "template": "dashboard/partials/activity_feed.html",
        "default_width": "2/3",
        "icon": "clock",
    },
    "quick_actions": {
        "label": "Quick Actions",
        "template": "dashboard/partials/quick_actions.html",
        "default_width": "1/3",
        "icon": "bolt",
    },
    "chart_revenue": {
        "label": "Revenue Trend",
        "template": "dashboard/partials/chart_revenue.html",
        "default_width": "1/2",
        "icon": "trending-up",
    },
    "chart_activity": {
        "label": "Activity Chart",
        "template": "dashboard/partials/chart_activity.html",
        "default_width": "1/2",
        "icon": "bar-chart",
    },
    "notifications_feed": {
        "label": "Notifications",
        "template": "dashboard/partials/notifications_widget.html",
        "default_width": "1/3",
        "icon": "bell",
    },
}

DEFAULT_LAYOUTS = {
    "admin": [
        {"widget": "kpi_cards", "position": 0, "width": "full", "visible": True},
        {"widget": "chart_revenue", "position": 1, "width": "1/2", "visible": True},
        {"widget": "chart_activity", "position": 2, "width": "1/2", "visible": True},
        {"widget": "activity_feed", "position": 3, "width": "2/3", "visible": True},
        {"widget": "quick_actions", "position": 4, "width": "1/3", "visible": True},
    ],
    "manager": [
        {"widget": "kpi_cards", "position": 0, "width": "full", "visible": True},
        {"widget": "chart_revenue", "position": 1, "width": "full", "visible": True},
        {"widget": "activity_feed", "position": 2, "width": "full", "visible": True},
    ],
    "analyst": [
        {"widget": "kpi_cards", "position": 0, "width": "full", "visible": True},
        {"widget": "chart_revenue", "position": 1, "width": "1/2", "visible": True},
        {"widget": "chart_activity", "position": 2, "width": "1/2", "visible": True},
        {"widget": "activity_feed", "position": 3, "width": "full", "visible": True},
    ],
    "viewer": [
        {"widget": "kpi_cards", "position": 0, "width": "full", "visible": True},
        {"widget": "chart_revenue", "position": 1, "width": "full", "visible": True},
    ],
}
