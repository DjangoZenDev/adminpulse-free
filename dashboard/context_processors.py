from .models import Notification, UserProfile


ACCENT_COLORS = {
    "indigo": "#6366f1",
    "blue": "#3b82f6",
    "emerald": "#10b981",
    "amber": "#f59e0b",
    "rose": "#f43f5e",
    "violet": "#8b5cf6",
}

SIDEBAR_COLORS = {
    "slate-900": "#0f172a",
    "gray-900": "#111827",
    "zinc-900": "#18181b",
    "blue-900": "#1e3a5f",
    "indigo-900": "#312e81",
}


def user_preferences(request):
    context = {
        "dark_mode": False,
        "sidebar_color": "slate-900",
        "accent_color": "indigo",
        "accent_hex": "#6366f1",
        "sidebar_hex": "#0f172a",
        "compact_mode": False,
        "user_role": "viewer",
        "unread_notification_count": 0,
        "accent_colors": ACCENT_COLORS,
        "sidebar_colors": SIDEBAR_COLORS,
    }

    if not request.user.is_authenticated:
        return context

    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        return context

    context["dark_mode"] = profile.dark_mode
    context["sidebar_color"] = profile.sidebar_color
    context["accent_color"] = profile.accent_color
    context["accent_hex"] = ACCENT_COLORS.get(profile.accent_color, "#6366f1")
    context["sidebar_hex"] = SIDEBAR_COLORS.get(profile.sidebar_color, "#0f172a")
    context["compact_mode"] = profile.compact_mode
    context["user_role"] = profile.role

    context["unread_notification_count"] = Notification.objects.filter(
        user=request.user, is_read=False
    ).count()

    return context
