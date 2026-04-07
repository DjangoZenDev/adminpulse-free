from django.contrib import admin
from .models import UserProfile, Activity, Metric, MetricHistory, Notification, DashboardLayout


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "dark_mode", "sidebar_color", "accent_color", "compact_mode", "created_at")
    list_filter = ("role", "dark_mode", "compact_mode")
    search_fields = ("user__username", "user__email")


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "target", "timestamp")
    list_filter = ("timestamp", "user")
    search_fields = ("action", "target", "user__username")
    date_hierarchy = "timestamp"


@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ("name", "value", "previous_value", "unit", "updated_at")
    list_filter = ("unit",)
    search_fields = ("name",)


@admin.register(MetricHistory)
class MetricHistoryAdmin(admin.ModelAdmin):
    list_display = ("metric", "value", "recorded_at")
    list_filter = ("metric",)
    search_fields = ("metric__name",)
    date_hierarchy = "recorded_at"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "notification_type", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("message", "user__username")
    date_hierarchy = "created_at"


@admin.register(DashboardLayout)
class DashboardLayoutAdmin(admin.ModelAdmin):
    list_display = ("user", "updated_at")
    search_fields = ("user__username",)
