import csv
import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import (
    Activity,
    AVAILABLE_WIDGETS,
    DashboardLayout,
    DEFAULT_LAYOUTS,
    Metric,
    MetricHistory,
    Notification,
    UserProfile,
)


ROLE_TEMPLATE_MAP = {
    "admin": "dashboard/home.html",
    "manager": "dashboard/home_manager.html",
    "analyst": "dashboard/home_analyst.html",
    "viewer": "dashboard/home_viewer.html",
}


@login_required
def dashboard_home(request):
    metrics = Metric.objects.all()
    activities = Activity.objects.select_related("user")[:15]
    user_count = User.objects.count()

    try:
        profile = request.user.profile
        role = profile.role
    except UserProfile.DoesNotExist:
        role = "viewer"

    default_layout = DEFAULT_LAYOUTS.get(role, DEFAULT_LAYOUTS["viewer"])
    layout, _created = DashboardLayout.objects.get_or_create(
        user=request.user,
        defaults={"layout": default_layout},
    )

    context = {
        "metrics": metrics,
        "activities": activities,
        "user_count": user_count,
        "layout": layout.layout,
        "available_widgets": AVAILABLE_WIDGETS,
        "role": role,
    }

    template = ROLE_TEMPLATE_MAP.get(role, "dashboard/home.html")

    if request.headers.get("HX-Request"):
        return render(request, template, context)

    return render(request, template, context)


@login_required
def activity_feed(request):
    activities = Activity.objects.select_related("user")[:20]
    return render(
        request, "dashboard/partials/activity_feed.html", {"activities": activities}
    )


@login_required
def kpi_cards(request):
    import json as json_mod
    metrics = list(Metric.objects.all())
    for metric in metrics:
        history = list(
            MetricHistory.objects.filter(metric=metric)
            .order_by("-recorded_at")[:30]
            .values_list("value", flat=True)
        )
        history.reverse()
        metric.history_data = json_mod.dumps([float(v) for v in history])
    return render(
        request, "dashboard/partials/kpi_cards.html", {"metrics": metrics}
    )


@login_required
def search_view(request):
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "all")
    page_number = request.GET.get("page", 1)
    results = {"users": [], "activities": [], "metrics": []}
    counts = {"users": 0, "activities": 0, "metrics": 0, "total": 0}

    if query:
        if category in ("all", "users"):
            users_qs = User.objects.filter(
                Q(username__icontains=query)
                | Q(email__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
            )
            counts["users"] = users_qs.count()
            if category == "users":
                paginator = Paginator(users_qs, 10)
                results["users"] = paginator.get_page(page_number)
            else:
                results["users"] = users_qs[:5]

        if category in ("all", "activities"):
            activities_qs = Activity.objects.filter(
                Q(action__icontains=query) | Q(target__icontains=query)
            ).select_related("user")
            counts["activities"] = activities_qs.count()
            if category == "activities":
                paginator = Paginator(activities_qs, 10)
                results["activities"] = paginator.get_page(page_number)
            else:
                results["activities"] = activities_qs[:5]

        if category in ("all", "metrics"):
            metrics_qs = Metric.objects.filter(Q(name__icontains=query))
            counts["metrics"] = metrics_qs.count()
            if category == "metrics":
                paginator = Paginator(metrics_qs, 10)
                results["metrics"] = paginator.get_page(page_number)
            else:
                results["metrics"] = metrics_qs[:5]

        counts["total"] = counts["users"] + counts["activities"] + counts["metrics"]

    return render(
        request,
        "dashboard/partials/search_results.html",
        {
            "results": results,
            "query": query,
            "category": category,
            "counts": counts,
        },
    )


@login_required
def users_list(request):
    users = User.objects.all().select_related("profile").order_by("-date_joined")
    context = {"users": users, "total_users": users.count()}
    return render(request, "dashboard/users.html", context)


@login_required
def settings_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()
        messages.success(request, "Settings updated successfully.")
        return redirect("dashboard:settings")

    return render(request, "dashboard/settings.html")


# --- Theme / Preferences ---


@login_required
@require_POST
def toggle_dark_mode(request):
    profile, _created = UserProfile.objects.get_or_create(user=request.user)
    profile.dark_mode = not profile.dark_mode
    profile.save(update_fields=["dark_mode"])
    return HttpResponse(status=204)


@login_required
@require_POST
def update_theme(request):
    profile, _created = UserProfile.objects.get_or_create(user=request.user)

    sidebar_color = request.POST.get("sidebar_color")
    accent_color = request.POST.get("accent_color")
    compact_mode = request.POST.get("compact_mode")

    update_fields = []
    if sidebar_color is not None:
        profile.sidebar_color = sidebar_color
        update_fields.append("sidebar_color")
    if accent_color is not None:
        profile.accent_color = accent_color
        update_fields.append("accent_color")
    if compact_mode is not None:
        profile.compact_mode = compact_mode == "on" or compact_mode == "true"
        update_fields.append("compact_mode")

    if update_fields:
        profile.save(update_fields=update_fields)

    referer = request.META.get("HTTP_REFERER", "/")
    return redirect(referer)


# --- Notifications ---


@login_required
def notifications_dropdown(request):
    notifications = Notification.objects.filter(
        user=request.user, is_read=False
    )[:10]
    return render(
        request,
        "dashboard/partials/notifications_dropdown.html",
        {"notifications": notifications},
    )


@login_required
@require_POST
def mark_notification_read(request, pk):
    Notification.objects.filter(user=request.user, pk=pk).update(is_read=True)
    return HttpResponse(status=204)


@login_required
@require_POST
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return HttpResponse(status=204)


@login_required
def notification_count(request):
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return HttpResponse(str(count), content_type="text/plain")


# --- Charts / JSON endpoints ---


@login_required
def chart_revenue_trend(request):
    since = timezone.now() - timedelta(days=90)
    revenue_metric = Metric.objects.filter(name="Revenue").first()

    labels = []
    values = []
    if revenue_metric:
        entries = MetricHistory.objects.filter(
            metric=revenue_metric, recorded_at__gte=since
        ).order_by("recorded_at")
        for entry in entries:
            labels.append(entry.recorded_at.strftime("%Y-%m-%d"))
            values.append(float(entry.value))

    return JsonResponse({"labels": labels, "values": values})


@login_required
def chart_activity_summary(request):
    since = timezone.now() - timedelta(days=30)
    activity_data = (
        Activity.objects.filter(timestamp__gte=since)
        .extra(select={"day": "date(timestamp)"})
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    labels = []
    values = []
    for row in activity_data:
        labels.append(str(row["day"]))
        values.append(row["count"])

    return JsonResponse({"labels": labels, "values": values})


@login_required
def chart_metric_comparison(request):
    metrics = Metric.objects.all()
    labels = []
    current_values = []
    previous_values = []

    for metric in metrics:
        labels.append(metric.name)
        current_values.append(float(metric.value))
        previous_values.append(float(metric.previous_value))

    return JsonResponse({
        "labels": labels,
        "current_values": current_values,
        "previous_values": previous_values,
    })


# --- CSV Exports ---


@login_required
def export_users_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="users.csv"'

    writer = csv.writer(response)
    writer.writerow(["ID", "Username", "Email", "First Name", "Last Name", "Date Joined", "Is Active", "Role"])

    users = User.objects.all().select_related("profile").order_by("id")
    for user in users:
        role = ""
        try:
            role = user.profile.get_role_display()
        except UserProfile.DoesNotExist:
            pass
        writer.writerow([
            user.id,
            user.username,
            user.email,
            user.first_name,
            user.last_name,
            user.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
            user.is_active,
            role,
        ])

    return response


@login_required
def export_activities_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="activities.csv"'

    writer = csv.writer(response)
    writer.writerow(["ID", "User", "Action", "Target", "Timestamp"])

    activities = Activity.objects.select_related("user").all()
    for activity in activities:
        writer.writerow([
            activity.id,
            activity.user.username,
            activity.action,
            activity.target,
            activity.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        ])

    return response


# --- Dashboard Layout ---


@login_required
@require_POST
def save_layout(request):
    try:
        layout_data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return HttpResponse(status=400)

    layout, _created = DashboardLayout.objects.get_or_create(user=request.user)
    layout.layout = layout_data
    layout.save(update_fields=["layout"])
    return HttpResponse(status=204)


@login_required
@require_POST
def reset_layout(request):
    try:
        role = request.user.profile.role
    except UserProfile.DoesNotExist:
        role = "viewer"

    default_layout = DEFAULT_LAYOUTS.get(role, DEFAULT_LAYOUTS["viewer"])
    layout, _created = DashboardLayout.objects.get_or_create(user=request.user)
    layout.layout = default_layout
    layout.save(update_fields=["layout"])
    return HttpResponse(status=204)
