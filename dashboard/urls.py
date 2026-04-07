from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="home"),
    path("users/", views.users_list, name="users"),
    path("settings/", views.settings_view, name="settings"),
    path("activity-feed/", views.activity_feed, name="activity_feed"),
    path("kpi-cards/", views.kpi_cards, name="kpi_cards"),
    path("search/", views.search_view, name="search"),
    # Theme / Preferences
    path("toggle-dark-mode/", views.toggle_dark_mode, name="toggle_dark_mode"),
    path("update-theme/", views.update_theme, name="update_theme"),
    # Notifications
    path("notifications/dropdown/", views.notifications_dropdown, name="notifications_dropdown"),
    path("notifications/<int:pk>/read/", views.mark_notification_read, name="mark_notification_read"),
    path("notifications/mark-all-read/", views.mark_all_notifications_read, name="mark_all_notifications_read"),
    path("notifications/count/", views.notification_count, name="notification_count"),
    # Charts / JSON
    path("charts/revenue-trend/", views.chart_revenue_trend, name="chart_revenue_trend"),
    path("charts/activity-summary/", views.chart_activity_summary, name="chart_activity_summary"),
    path("charts/metric-comparison/", views.chart_metric_comparison, name="chart_metric_comparison"),
    # CSV Exports
    path("export/users/", views.export_users_csv, name="export_users_csv"),
    path("export/activities/", views.export_activities_csv, name="export_activities_csv"),
    # Dashboard Layout
    path("layout/save/", views.save_layout, name="save_layout"),
    path("layout/reset/", views.reset_layout, name="reset_layout"),
]
