from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import ActivityViewSet, MetricViewSet, NotificationViewSet, MetricHistoryViewSet

router = DefaultRouter()
router.register(r"activities", ActivityViewSet)
router.register(r"metrics", MetricViewSet)
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(r"metrichistory", MetricHistoryViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
